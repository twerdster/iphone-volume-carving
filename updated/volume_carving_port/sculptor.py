"""Faithful Python port of the voxel-carving part of ``source/Sculptor/Sculptor.h``.

Original: Sergey Kucher and Alex Povichuk (supervised by Aaron Wetzler),
``Sculptor<Size>`` template, ``MeshMargins<Size>``. Unmodified in ``../source``.

Ported:
  * bit-packed occupancy grid (``sculpture[x][y][z>>3]``, bit ``z & 7``),
  * ``Reset``, ``TurnOn``/``TurnOff``/``IsOn``,
  * ``Transform`` (voxel index -> world coordinate),
  * ``Project`` with a row-major 3x4 projection matrix and float arithmetic,
  * ``isInMap`` including its side effect of marking map pixels BLUE/RED,
  * ``SculpAccurate`` and ``SculpFast`` (with ``MeshMargins`` bookkeeping),
  * ``CreateOutline`` (12 bounding-box edges).

Not ported: ``ToShape``/``PoligolizeCell``/``BuildCell`` (marching-cubes mesh
extraction). They call ``Polygonise`` from ``MarchingCubes.h``, which is
missing from the recovered source, and their output feeds the OpenGL ``Shape``
singleton. This port exports occupied voxels as a point cloud instead. That is
an addition, not original behaviour.

Undefined-behaviour cases in the original (projection with z == 0, NaN or
out-of-int-range image coordinates) are treated as OUTSIDE here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence, Tuple

from .f32 import c_trunc_to_int, f32, fadd, fdiv, fmul

FULLCELL = 0xFF
ACCURATE = "ACCURATE"
FAST = "FAST"

# VoxelStatus enum values from Sculptor.h
BLACK, BLUE, WHITE, RED, OUTSIDE = 1, 2, 3, 4, 5


@dataclass
class SculptData:
    """Equivalent of ``struct SculptData``: projection + silhouette map.

    ``map`` is row-major ``size_x * size_y`` bytes; 0 means background. The
    original mutates it during carving (BLUE=2 for background hits, RED=4 for
    foreground hits), and so does this port.
    """

    projection: Sequence[float]  # 12 floats, row-major 3x4
    map: bytearray
    size_x: int
    size_y: int

    def __post_init__(self):
        if len(self.projection) != 12:
            raise ValueError("projection must have 12 values (3x4 row-major)")
        self.projection = [f32(v) for v in self.projection]
        if len(self.map) != self.size_x * self.size_y:
            raise ValueError("map size mismatch")
        if not isinstance(self.map, bytearray):
            self.map = bytearray(self.map)


@dataclass
class MeshMargins:
    """Port of ``MeshMargins<Size>`` (byte-valued bounds per x / (x,y))."""

    size: int
    min_x: int = 0
    max_x: int = 0
    min_y_per_x: List[int] = field(default_factory=list)
    max_y_per_x: List[int] = field(default_factory=list)
    min_z_per_xy: List[List[int]] = field(default_factory=list)
    max_z_per_xy: List[List[int]] = field(default_factory=list)

    def __post_init__(self):
        self.reset()

    def reset(self):
        s = self.size
        self.min_x, self.max_x = 0, s - 1
        self.min_y_per_x = [0] * s
        self.max_y_per_x = [s - 1] * s
        self.min_z_per_xy = [[0] * s for _ in range(s)]
        self.max_z_per_xy = [[s - 1] * s for _ in range(s)]

    def _x_in_bounds(self, x):
        return self.min_x if x < self.min_x else self.max_x if x > self.max_x else x

    def _y_in_bounds(self, x, y):
        lo, hi = self.min_y_per_x[x], self.max_y_per_x[x]
        return lo if y < lo else hi if y > hi else y

    def get_min_y_per_x(self, x):
        return self.min_y_per_x[self._x_in_bounds(x)]

    def get_max_y_per_x(self, x):
        return self.max_y_per_x[self._x_in_bounds(x)]

    def get_min_z_per_xy(self, x, y):
        rx = self._x_in_bounds(x)
        return self.min_z_per_xy[rx][self._y_in_bounds(rx, y)]

    def get_max_z_per_xy(self, x, y):
        rx = self._x_in_bounds(x)
        return self.max_z_per_xy[rx][self._y_in_bounds(rx, y)]

    def set_min_y_per_x(self, x, y):
        if self._x_in_bounds(x) == x:
            self.min_y_per_x[x] = y & 0xFF

    def set_max_y_per_x(self, x, y):
        if self._x_in_bounds(x) == x:
            self.max_y_per_x[x] = y & 0xFF

    def set_min_z_per_xy(self, x, y, z):
        if self._x_in_bounds(x) == x and self._y_in_bounds(x, y) == y:
            self.min_z_per_xy[x][y] = z & 0xFF

    def set_max_z_per_xy(self, x, y, z):
        if self._x_in_bounds(x) == x and self._y_in_bounds(x, y) == y:
            self.max_z_per_xy[x][y] = z & 0xFF


class Sculptor:
    """Port of ``template<int Size> class Sculptor`` (carving only)."""

    def __init__(self, size: int, scale_rate: float, translation: Tuple[float, float, float]):
        # Transform() takes a signed `char` index in the original, so indices >= 128
        # wrap negative on Apple (signed-char) ABIs; restrict to the safe range.
        if size % 8 or not (8 <= size <= 128):
            raise ValueError("Size must be a multiple of 8 in [8, 128] (original char/byte index types)")
        self.size = size
        self.scale_rate = fdiv(f32(scale_rate), float(size))  # _scaleRate / Size in float
        self.tx, self.ty, self.tz = (f32(t) for t in translation)
        self.sculpture = bytearray(size * size * (size >> 3))
        self.margins = MeshMargins(size)
        self.reset()

    # ----------------------------------------------------------- bit storage
    def _off(self, x, y, z):
        return (x * self.size + y) * (self.size >> 3) + (z >> 3)

    def reset(self):
        for i in range(len(self.sculpture)):
            self.sculpture[i] = FULLCELL
        self.margins.reset()

    def turn_on(self, x, y, z):
        self.sculpture[self._off(x, y, z)] |= 1 << (z & 7)

    def turn_off(self, x, y, z):
        self.sculpture[self._off(x, y, z)] &= ~(1 << (z & 7)) & 0xFF

    def is_on(self, x, y, z) -> bool:
        return bool(self.sculpture[self._off(x, y, z)] & (1 << (z & 7)))

    def count_on(self) -> int:
        return sum(bin(b).count("1") for b in self.sculpture)

    # ----------------------------------------------------------- geometry
    def transform(self, index: int, translate: float) -> float:
        return fadd(fmul(float(index), self.scale_rate), translate)

    def voxel_position(self, x, y, z) -> Tuple[float, float, float]:
        return (self.transform(x, self.tx), self.transform(y, self.ty), self.transform(z, self.tz))

    @staticmethod
    def project(p: Sequence[float], P: Sequence[float]) -> Tuple[float, float]:
        X, Y, Z = p
        u = fadd(fadd(fadd(fmul(X, P[0]), fmul(Y, P[1])), fmul(Z, P[2])), fmul(1.0, P[3]))
        v = fadd(fadd(fadd(fmul(X, P[4]), fmul(Y, P[5])), fmul(Z, P[6])), fmul(1.0, P[7]))
        w = fadd(fadd(fadd(fmul(X, P[8]), fmul(Y, P[9])), fmul(Z, P[10])), fmul(1.0, P[11]))
        return fdiv(u, w), fdiv(v, w)

    @staticmethod
    def is_in_map(xy: Tuple[float, float], data: SculptData) -> int:
        x = c_trunc_to_int(xy[0])
        y = c_trunc_to_int(xy[1])
        if x is None or y is None:
            return OUTSIDE  # undefined behaviour in the original
        if x < 0 or x >= data.size_x or y < 0 or y >= data.size_y:
            return OUTSIDE
        index = x + data.size_x * y
        if data.map[index] == 0 or data.map[index] == BLUE:
            data.map[index] = BLUE
            return BLACK
        data.map[index] = RED
        return WHITE

    def _status(self, x, y, z, data: SculptData) -> int:
        return self.is_in_map(self.project(self.voxel_position(x, y, z), data.projection), data)

    # ----------------------------------------------------------- carving
    def sculp(self, data: SculptData, mode: str = ACCURATE) -> None:
        if mode == ACCURATE:
            self._sculp_accurate(data)
        elif mode == FAST:
            self._sculp_fast(data)
        else:
            raise ValueError(mode)

    def _sculp_accurate(self, data: SculptData) -> None:
        s = self.size
        for x in range(s):
            for y in range(s):
                for z in range(s):
                    if self._status(x, y, z, data) == BLACK:
                        self.turn_off(x, y, z)

    def _sculp_fast(self, data: SculptData) -> None:
        m = self.margins
        min_x, max_x = m.min_x, m.max_x
        min_x_new, max_x_new = m.min_x, m.max_x
        min_x_dirty = False
        x = min_x
        while x <= max_x:
            min_y, max_y = m.get_min_y_per_x(x), m.get_max_y_per_x(x)
            min_y_new, max_y_new = min_y, max_y
            min_y_dirty = False
            y = min_y
            while y <= max_y:
                min_z, max_z = m.get_min_z_per_xy(x, y), m.get_max_z_per_xy(x, y)
                min_z_new, max_z_new = min_z, max_z
                min_z_dirty = False
                z = min_z
                while z <= max_z:
                    if self._status(x, y, z, data) == BLACK:
                        self.turn_off(x, y, z)
                        if not min_x_dirty:
                            min_x_new = x
                        if not min_y_dirty:
                            min_y_new = y
                        if not min_z_dirty:
                            min_z_new = z
                    else:
                        min_x_dirty = min_y_dirty = min_z_dirty = True
                        max_x_new, max_y_new, max_z_new = x, y, z
                    z += 1
                m.set_min_z_per_xy(x, y, min_z_new)
                m.set_max_z_per_xy(x, y, max_z_new)
                y += 1
            m.set_min_y_per_x(x, min_y_new)
            m.set_max_y_per_x(x, max_y_new)
            x += 1
        m.min_x = min_x_new & 0xFF
        m.max_x = max_x_new & 0xFF

    # ----------------------------------------------------------- outputs
    def create_outline(self):
        """Port of ``CreateOutline``: the 12 edges of the voxel-grid bounding box."""
        s = self.size - 1
        corners = [((0, 0, 0), (0, s, 0)), ((0, 0, 0), (s, 0, 0)), ((0, 0, 0), (0, 0, s)),
                   ((s, s, 0), (0, s, 0)), ((s, s, 0), (s, 0, 0)), ((s, s, 0), (s, s, s)),
                   ((s, 0, s), (s, 0, 0)), ((s, 0, s), (s, s, s)), ((s, 0, s), (0, 0, s)),
                   ((0, s, s), (0, s, 0)), ((0, s, s), (s, s, s)), ((0, s, s), (0, 0, s))]
        return [(self.voxel_position(*a), self.voxel_position(*b)) for a, b in corners]

    def occupied(self):
        s = self.size
        return [(x, y, z) for x in range(s) for y in range(s) for z in range(s) if self.is_on(x, y, z)]

    def to_ply(self) -> str:
        """ASCII PLY point cloud of occupied voxel positions (new export, not original)."""
        pts = [self.voxel_position(*v) for v in self.occupied()]
        head = ["ply", "format ascii 1.0", "comment volume_carving_port occupied voxel positions",
                f"element vertex {len(pts)}", "property float x", "property float y", "property float z",
                "end_header"]
        return "\n".join(head + [f"{x:.7g} {y:.7g} {z:.7g}" for x, y, z in pts]) + "\n"

    def bits_hex(self) -> str:
        return self.sculpture.hex()
