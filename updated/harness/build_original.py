#!/usr/bin/env python3
"""Compile the UNMODIFIED original Sculptor carving code and vector classes into
reference executables under updated/build/.

  python3 harness/build_original.py            # strict (-ffp-contract=off) builds
  python3 harness/build_original.py default    # Apple clang default FP contraction

Includes come from ../source/Sculptor and "../source/Drop Shadows" (PixelVector.h
provides the `byte` typedef). The only non-original header is
harness/compat/MarchingCubes.h, a declaration-only placeholder. SculptData.h uses
the Objective-C `nil` in C++, so `-Dnil=nullptr` is passed on the command line.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UPDATED = HERE.parent
SRC = UPDATED.parent / "source"
SCULPTOR = SRC / "Sculptor"
DROP = SRC / "Drop Shadows"
BUILD = UPDATED / "build"

FLAGS = {"strict": ["-O2", "-ffp-contract=off"], "default": ["-O2"]}


def build(variant: str = "strict", verbose: bool = False) -> dict:
    cxx = shutil.which("clang++") or shutil.which("g++")
    if not cxx:
        raise RuntimeError("no C++ compiler found")
    BUILD.mkdir(exist_ok=True)
    # -std=c++14: under C++17, std::byte + the original `using namespace std;`
    # makes the original global `typedef unsigned char byte` ambiguous.
    # -Wno-c++11-narrowing: Sculptor.h GetVertexPosition() brace-initialises an
    # unsigned char from a float, legal in the C++98 dialect of the original
    # era; the function is unused by carving.
    common = ["-std=c++14", "-w", "-Wno-c++11-narrowing", "-Dnil=nullptr", f"-I{HERE / 'compat'}", f"-I{SCULPTOR}", f"-I{DROP}"] + FLAGS[variant]
    lib = [SCULPTOR / n for n in ("Vector3D.cpp", "Vector3DEx.cpp", "Vector2D.cpp", "Triangle.cpp", "Mesh.cpp")]
    exes = {}
    for name, main in (("carve", HERE / "carve_main.cpp"), ("vectors", HERE / "vectors_main.cpp")):
        exe = BUILD / f"{name}_{variant}"
        cmd = [cxx, *common, str(main), *map(str, lib), "-o", str(exe)]
        if verbose:
            print(" ".join(cmd))
        subprocess.run(cmd, check=True)
        exes[name] = exe
    return exes


if __name__ == "__main__":
    for v in sys.argv[1:] or ["strict"]:
        print(build(v, verbose=True))
