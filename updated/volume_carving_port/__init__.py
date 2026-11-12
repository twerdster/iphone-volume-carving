"""Dependency-free port of the voxel-carving core of the 3D Volume Carving on
iPhone project (Sergey Kucher and Alex Povichuk). See ``updated/README.md``.
"""

from .sculptor import ACCURATE, FAST, SculptData, Sculptor, MeshMargins
from .vector3dex import Vector3DEx, triangle_normal

__all__ = ["ACCURATE", "FAST", "SculptData", "Sculptor", "MeshMargins", "Vector3DEx", "triangle_normal"]
