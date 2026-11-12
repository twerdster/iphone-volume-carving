# Voxel-carving component (updated Python, 2026)

This standard-library Python translation implements the recovered **voxel-carving component** by Sergey Kucher and Alex Povichuk, supervised by Aaron Wetzler. The original 21 source files in `../source/` remain unchanged. The new implementation is maintained by Aaron Wetzler.

## Inputs, outputs and changes

`SculptData` takes a row-major 3-by-4 projection matrix, a byte-valued silhouette map and its pixel dimensions. Zero/BLUE map values are background; other values are foreground. `Sculptor` removes grid voxels projecting to background and records visited pixels by mutating the map.

The port preserves the bit-packed occupancy grid, float32 projection arithmetic, accurate and fast silhouette-carving loops and bounding-box outline from `Sculptor.h`/`MeshMargins.h`. The historical `Vector3DEx` cache quirks are deliberately reproduced for comparison, including zero cached lengths after addition/cross product. They are not suitable general-purpose vector semantics. New geometry should use a fresh Euclidean norm.

The grid size must be a multiple of eight from 8 to 128, reflecting the original index types. Projection/coordinate units come from the supplied matrix, scale and translation; no camera calibration or physical unit is provided by the demo.

New code adds explicit handling of undefined zero/nonfinite projections (outside the map), grid size limits, a synthetic orthographic-silhouette example, an SVG point-cloud view and ASCII PLY export. None of these additions is an original project result. **Marching-cubes mesh extraction, the iPhone app, camera capture, QCAR/Vuforia and OpenGL rendering are not ported.**

## Run

From this `updated/` directory, with Python 3.10 or newer:

```sh
python3 -m unittest discover -s tests -v
python3 demo.py --size 24 --radius 8 --out build
python3 harness/compare_with_original.py
```

The [2026-11-12 validation record](VALIDATION.json) reports 16 component unit tests and six real notebook code cells passed. The tests check an analytic three-disk intersection, projection, monotonicity, order invariance, idempotence, occupancy packing, exports, original vector regressions and comparisons with the actual compiled C++ carving core. All three compiler-dependent tests passed as part of the recorded 16-test run. They skip if neither clang++ nor g++ exists. No third-party Python packages are needed by the port. Tests run on macOS 15.1.1 arm64, Python 3.14.4 and Apple clang 16 (Xcode 16.1); Linux has not been tested.

The reference harness compiles original source without edits, using C++14, `-Dnil=nullptr`, disabled FP contraction and a new declaration-only `harness/compat/MarchingCubes.h` stub written for the harness, not the missing original header. The missing `Polygonise` function has no implementation; trying to use mesh extraction fails to link. Exact occupancy bits and mutated silhouette masks match the original on the bounded synthetic comparison cases. This is component validation, not a full app build.

## Notebook and interactivity

[Open the notebook](notebooks/voxel_carving_demo.ipynb) or [open in Colab](https://colab.research.google.com/github/twerdster/iphone-volume-carving/blob/main/updated/notebooks/voxel_carving_demo.ipynb). It uses a local checkout when available; otherwise it downloads the small updated modules from this repository's `main` branch at runtime, without a commit pin. Change the grid/radius, rerun cells, compare carving modes and export a point cloud. The notebook is committed without outputs. Its six code cells were executed in an isolated real Jupyter kernel on 2026-11-12.

A future browser or Space interface could accept silhouette edits and display the resulting point cloud. That UI has not been built. The existing notebook displays an isometric projection; it does not claim an interactive 3D viewer.

## Attribution and terms

Claude Code drafted the translation; Codex completed/reviewed/tested it for Aaron Wetzler in 2026. Original source/student attribution and existing terms remain in place. No blanket license is added for original code, the derivative translation or third-party dependencies. The new synthetic scene and exports are explicitly updated 2026 demonstration material, not recovered captures.
