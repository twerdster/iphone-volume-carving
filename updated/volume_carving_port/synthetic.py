"""SYNTHETIC scenes for exercising the carving port: analytic shapes viewed by
ideal pinhole cameras. The original QCAR/Vuforia poses and phone images are not
available, so nothing here reproduces the original app's captures or results.
"""

from __future__ import annotations

import math
from typing import Callable, List, Sequence, Tuple

from .sculptor import SculptData


def look_at_projection(eye: Sequence[float], target: Sequence[float], f: float,
                       cx: float, cy: float, up=(0.0, 0.0, 1.0)) -> List[float]:
    """Row-major 3x4 P = K [R | -R eye] for a camera at ``eye`` looking at ``target``.

    Image x points right and image y points down, matching the original's
    ``map[x + sizeX * y]`` indexing.
    """
    fwd = [t - e for t, e in zip(target, eye)]
    n = math.sqrt(sum(c * c for c in fwd))
    zc = [c / n for c in fwd]
    xc = [zc[1] * up[2] - zc[2] * up[1], zc[2] * up[0] - zc[0] * up[2], zc[0] * up[1] - zc[1] * up[0]]
    n = math.sqrt(sum(c * c for c in xc))
    xc = [c / n for c in xc]
    yc = [zc[1] * xc[2] - zc[2] * xc[1], zc[2] * xc[0] - zc[0] * xc[2], zc[0] * xc[1] - zc[1] * xc[0]]
    R = [xc, yc, zc]
    t = [-sum(R[i][j] * eye[j] for j in range(3)) for i in range(3)]
    K = [[f, 0.0, cx], [0.0, f, cy], [0.0, 0.0, 1.0]]
    Rt = [R[i] + [t[i]] for i in range(3)]
    return [sum(K[i][k] * Rt[k][j] for k in range(3)) for i in range(3) for j in range(4)]


def ring_cameras(n: int, radius: float, height: float, center=(0.0, 0.0, 0.0), f=60.0,
                 width=64, height_px=48) -> List[List[float]]:
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        eye = (center[0] + radius * math.cos(a), center[1] + radius * math.sin(a), center[2] + height)
        out.append(look_at_projection(eye, center, f, width / 2, height_px / 2))
    return out


def render_silhouette(inside: Callable[[float, float, float], bool], P: Sequence[float],
                      width: int, height: int, bounds: Tuple[float, float], samples: int = 40) -> bytearray:
    """SYNTHETIC silhouette by splatting a dense sample of the shape (255 = object)."""
    lo, hi = bounds
    img = bytearray(width * height)
    step = (hi - lo) / samples
    for i in range(samples + 1):
        X = lo + i * step
        for j in range(samples + 1):
            Y = lo + j * step
            for k in range(samples + 1):
                Z = lo + k * step
                if not inside(X, Y, Z):
                    continue
                w = P[8] * X + P[9] * Y + P[10] * Z + P[11]
                u = (P[0] * X + P[1] * Y + P[2] * Z + P[3]) / w
                v = (P[4] * X + P[5] * Y + P[6] * Z + P[7]) / w
                iu, iv = int(math.floor(u)), int(math.floor(v))
                if 0 <= iu < width and 0 <= iv < height:
                    img[iu + width * iv] = 255
    return img


def sphere(cx=0.0, cy=0.0, cz=0.0, r=0.3):
    return lambda x, y, z: (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 <= r * r


def synthetic_views(shape, n_views=6, width=64, height=48, f=60.0, radius=2.0, cam_height=0.8,
                    bounds=(-0.5, 0.5)) -> List[SculptData]:
    """SYNTHETIC SculptData list for ``shape`` seen from a ring of cameras."""
    views = []
    for P in ring_cameras(n_views, radius, cam_height, f=f, width=width, height_px=height):
        views.append(SculptData(P, render_silhouette(shape, P, width, height, bounds), width, height))
    return views
