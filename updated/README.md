# Updated voxel carving (2026)

A dependency-free Python translation of the recovered **voxel-carving component** by Sergey Kucher and Alex Povichuk, supervised by Aaron Wetzler. The original 21 source files in `../source/` remain unchanged. The new implementation is maintained by Aaron Wetzler.

## Original and updated

The port preserves the bit-packed occupancy grid, float32 projection arithmetic, accurate and fast silhouette-carving loops and bounding-box outline from `Sculptor.h`/`MeshMargins.h`. The historical `Vector3DEx` cache quirks are deliberately reproduced for comparison, including zero cached lengths after addition/cross product. They are not suitable general-purpose vector semantics. New geometry should use a fresh Euclidean norm.

New code adds safe handling of undefined zero/nonfinite projections (outside the map), grid size limits, a synthetic orthographic-silhouette example, an SVG point-cloud view and ASCII PLY export. None of these additions is an original project result. **Marching-cubes mesh extraction, the iPhone app, camera capture, QCAR/Vuforia and OpenGL rendering are not ported.**

## Run

From this `updated/` directory, with Python 3.10 or newer:

```sh
python3 -m unittest discover -s tests -v
python3 demo.py --size 24 --radius 8 --out build
python3 harness/compare_with_original.py
```

The 16 tests check an analytic three-disk intersection, projection, monotonicity, order invariance, idempotence, occupancy packing, exports, original vector regressions and comparisons with the actual compiled C++ carving core. Compiler-dependent tests skip if no C++ compiler exists. No third-party Python packages are needed by the port. Tests run on macOS 15.1.1 arm64, Python 3.14.4 and Apple clang 16 (Xcode 16.1); Linux has not been tested.

The reference harness compiles original source without edits, using C++14, `-Dnil=nullptr`, disabled FP contraction and a documented declaration-only `harness/compat/MarchingCubes.h`. The missing `Polygonise` function has no implementation; trying to use mesh extraction fails to link. Exact occupancy bits and mutated silhouette masks match the original on the bounded synthetic comparison cases. This is component validation, not a full app build.

## Notebook and interactivity

[Open the notebook](notebooks/voxel_carving_demo.ipynb) or [open in Colab](https://colab.research.google.com/github/twerdster/iphone-volume-carving/blob/main/updated/notebooks/voxel_carving_demo.ipynb). It uses a local checkout when available; otherwise it downloads only the small updated modules from this repository. Change the grid/radius, rerun cells, compare carving modes and export a point cloud. The notebook is committed without outputs and is validated/executed in an isolated real Jupyter kernel during maintenance.

A browser or static Space could expose sliders, editable silhouettes and rotating point clouds. That UI has not been built. The existing notebook displays an isometric projection; it does not claim an interactive 3D viewer.

## Attribution and terms

Original source/student attribution and existing terms remain in place. No blanket license is added for original code, the derivative translation or third-party dependencies. The new synthetic scene and exports are explicitly updated 2026 demonstration material, not recovered captures.
