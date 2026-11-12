"""Faithful binary32 port of the original ``Vector3D``/``Vector3DEx`` classes.

Original: ``source/Sculptor/Vector3D.{h,cpp}`` and ``Vector3DEx.{h,cpp}``. The port
keeps the original's cached-length design, including these behaviours, which
are confirmed against the compiled original in ``harness/``:

* ``Vector3DEx`` caches ``vectorLength`` only in its float/copy constructors.
  ``operator-``, ``operator+`` and ``crossProduct`` build a default-constructed
  result and assign components afterwards, so **their ``length()`` stays 0**.
  A later ``angle()`` divides by zero; ``normalize()`` incorrectly returns its
  zero-length fallback (the unit x vector).
* ``normalize()`` **mutates the receiver** (``_x /= vecMag`` ...) and returns a
  new normalised vector. ``+=``, ``-=`` and ``*=`` also leave the cached length stale.
* ``operator<`` is lexicographic (x, then y, then z).

These semantics matter for code that used the classes (``Triangle`` normals,
``Mesh`` vertex maps). They are reproduced here so regression tests can pin
them down. Do not use this class as a general-purpose vector type.
"""

from __future__ import annotations

import math

from .f32 import f32, fadd, fdiv, fmul, fsqrt, fsub


class Vector3DEx:
    __slots__ = ("x", "y", "z", "vector_length")

    def __init__(self, x: float | None = None, y: float = 0.0, z: float = 0.0, *, _default=False):
        if _default or x is None:
            # Vector3DEx(void): vectorLength(0), components uninitialised in C++;
            # the original immediately assigns them, so zeros are used here.
            self.x = self.y = self.z = 0.0
            self.vector_length = 0.0
            return
        self.x, self.y, self.z = f32(x), f32(y), f32(z)
        self.vector_length = self._sqrt_len()

    def _sqrt_len(self) -> float:
        s = fadd(fadd(fmul(self.x, self.x), fmul(self.y, self.y)), fmul(self.z, self.z))
        return fsqrt(s)

    @classmethod
    def _uncached(cls, x, y, z) -> "Vector3DEx":
        v = cls(_default=True)
        v.x, v.y, v.z = x, y, z
        return v

    def length(self) -> float:
        return self.vector_length

    def dot(self, o: "Vector3DEx") -> float:  # float operator*(const Vector3DEx&)
        return fadd(fadd(fmul(self.x, o.x), fmul(self.y, o.y)), fmul(self.z, o.z))

    def angle(self, o: "Vector3DEx") -> float:
        cos_angle = fdiv(self.dot(o), fmul(self.length(), o.length()))
        if math.isnan(cos_angle) or abs(cos_angle) > 1.0:
            return math.nan
        return f32(math.acos(cos_angle))  # acosf; may differ from libm acosf by <= 1 ulp

    def normalize(self) -> "Vector3DEx":
        mag = self.length()
        if mag == 0.0:
            return Vector3DEx(1.0, 0.0, 0.0)
        self.x = fdiv(self.x, mag)  # receiver is mutated, as in the original
        self.y = fdiv(self.y, mag)
        self.z = fdiv(self.z, mag)
        return Vector3DEx(self.x, self.y, self.z)

    def cross(self, o: "Vector3DEx") -> "Vector3DEx":
        return Vector3DEx._uncached(fsub(fmul(self.y, o.z), fmul(self.z, o.y)),
                                    fsub(fmul(self.z, o.x), fmul(self.x, o.z)),
                                    fsub(fmul(self.x, o.y), fmul(self.y, o.x)))

    def __sub__(self, o):
        return Vector3DEx._uncached(fsub(self.x, o.x), fsub(self.y, o.y), fsub(self.z, o.z))

    def __add__(self, o):
        return Vector3DEx._uncached(fadd(self.x, o.x), fadd(self.y, o.y), fadd(self.z, o.z))

    def scaled(self, alpha: float) -> "Vector3DEx":  # Vector3DEx operator*(float): recomputes length
        a = f32(alpha)
        return Vector3DEx(fmul(self.x, a), fmul(self.y, a), fmul(self.z, a))

    def __eq__(self, o):
        return self.x == o.x and self.y == o.y and self.z == o.z

    def __lt__(self, o):
        if self.x > o.x:
            return False
        if self.x == o.x:
            if self.y > o.y:
                return False
            if self.y == o.y and self.z >= o.z:
                return False
        return True

    def __gt__(self, o):
        return self != o and not self < o

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __repr__(self):
        return f"Vector3DEx({self.x!r}, {self.y!r}, {self.z!r}; cached_length={self.vector_length!r})"


def triangle_normal(p0: Vector3DEx, p1: Vector3DEx, p2: Vector3DEx) -> Vector3DEx:
    """Port of ``Triangle::CalculateNormal``: (p0 - p2) x (p0 - p1), unnormalised."""
    v1 = p0 - p1
    v2 = p0 - p2
    return v2.cross(v1)
