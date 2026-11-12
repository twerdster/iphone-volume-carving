"""IEEE-754 binary32 emulation helpers.

The original Sculptor code computes in C ``float``. Python floats are binary64,
so every original float operation is reproduced as "compute in double, round
to binary32". For +, -, * and / of binary32 operands this gives the correctly
rounded binary32 result: binary64 has at least 2*24+2 bits, so double rounding
is harmless. This matches a C build without fused multiply-add contraction
(``-ffp-contract=off``).
"""

from __future__ import annotations

import math
import struct

_pack = struct.Struct("<f").pack
_unpack = struct.Struct("<f").unpack


def f32(x: float) -> float:
    """Round a Python float to the nearest binary32 value (ties to even)."""
    try:
        return _unpack(_pack(x))[0]
    except OverflowError:  # beyond binary32 range: IEEE rounding gives +/-inf
        return math.copysign(math.inf, x)


def fadd(a: float, b: float) -> float:
    return f32(a + b)


def fsub(a: float, b: float) -> float:
    return f32(a - b)


def fmul(a: float, b: float) -> float:
    return f32(a * b)


def fdiv(a: float, b: float) -> float:
    if b == 0.0:
        if a == 0.0 or math.isnan(a):
            return math.nan
        return math.copysign(math.inf, a) * math.copysign(1.0, b)
    return f32(a / b)


def fsqrt(a: float) -> float:
    return f32(math.sqrt(a)) if a >= 0 else math.nan


def c_trunc_to_int(x: float):
    """C ``(int)`` conversion of a finite float (truncation toward zero).

    Returns None for NaN/inf/out-of-range values, where the original C code
    has undefined behaviour.
    """
    if not math.isfinite(x) or not (-2147483648.0 <= x < 2147483648.0):
        return None
    return int(x)
