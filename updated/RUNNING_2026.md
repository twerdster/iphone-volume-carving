# Build and replay details

Commands below run from `updated/`.

## Original core and small experiments

No complete app project or implementation of MarchingCubes was recovered. The original `source/Sculptor/Mesh.cpp` cannot compile alone because `MarchingCubes.h` is missing. The existing headless harness uses a newly written declaration-only compatibility header and never calls mesh extraction. It compiles unchanged original files in C++14 with `nil=nullptr`, and disables floating-point contraction for exact comparisons.

```sh
python3 harness/build_original.py strict
python3 harness/build_original.py asan
```

The `asan` variant enables AddressSanitizer and UndefinedBehaviorSanitizer. clang++ or g++ is selected from PATH. Native builds and environments belong on a filesystem with normal Unix semantics; keep data/output separately when using exFAT.

The harness accepts grid sizes 16, 24, 32, 64 and 128. Its third optional argument is an existing snapshot directory, containing exact occupancy bits after each view. After a strict replay creates its input, the recorded sanitizer replay is `build/carve_asan build/dinosaur/native-input.txt build/dinosaur/native-output-asan.txt`. Compare that output with the strict `native-output.txt`; it contains counts, mutated mask hex, final occupancy and margins. Per-view snapshots are checked separately against the reference.

The text input format is documented at the top of `harness/carve_main.cpp`; malformed dimensions/mask hex are rejected. This is new harness behavior, not a change to the carving algorithm.

The Python grid supports multiples of 8 in [8,128]. Its `SculptData` accepts row-major 3×4 matrices and byte masks: byte values 0 and 2 (BLUE) are background; all other values are foreground. Pixel coordinates truncate toward zero, matching the original. Out-of-image points are retained. Occupancy is bit-packed and masks are mutated to mark visited foreground/background pixels. Historical `Vector3DEx` cache quirks remain for comparison, not as recommended geometry utilities. The Python port treats zero/nonfinite projection denominators as out-of-map. That handling and PLY/SVG export are new behavior.

## Real dinosaur replay

Clone with `git clone --recurse-submodules https://github.com/twerdster/freehand-voxel-carving.git`, then use that separate [Freehand Voxel Carving checkout](https://github.com/twerdster/freehand-voxel-carving). Its `source/PointCloudSample/dinosaur` contains the 36 photographs, silhouettes and historical camera table. Camera matrices in `assets/dinosaur-calibration.json` come from the unchanged rounded `demoP` table at original source submodule pin 881f5a8f02d9282d502d4547da0ecb34d5c0f00c; the JSON records its exact SHA-256. Verify `git -C /path/to/freehand/source rev-parse HEAD` matches that pin before replaying. The matrices can be regenerated with `python3 /path/to/freehand/updated/tools/export_calibration.py /path/to/output.json` from that checkout; see its script for the source input path. The cube corner is (-0.1307, -0.1307, -0.7483), side 0.2463 in that calibration’s coordinate units. The original constructor divides side by grid size; samples lie at corner+index×side/size. Physical units are not established here.

```sh
python3 -m venv .venv
.venv/bin/pip install numpy pillow
.venv/bin/python tools/replay_dinosaur.py --dataset /path/to/freehand/source/PointCloudSample/dinosaur --calibration assets/dinosaur-calibration.json --size 128 --out build/dinosaur
.venv/bin/python tools/render_dinosaur.py --results build/dinosaur --dataset /path/to/freehand/source/PointCloudSample/dinosaur --out build/media
```

FFmpeg is required only for video/GIF encoding. The tools were run with NumPy 2.5.4/Pillow 13.0.0 on macOS; native original carving was also replayed on Linux/GCC 11.4 with ASan/UBSan. The 128³ full replay’s 2,097,152 occupancy values match independent float32 projection/mask intersections at every one of 36 views. Reference evaluation follows the original multiply/add order, truncation and out-of-map rule. It does not call the Python port or consume native occupancy to compute expected bits.

The native output and all per-view occupancy snapshots are retained. The optional observed export excludes 5,830 surviving voxels that never project inside any input image, leaving 21,480. This visibility mask is new postprocessing, not recovered behavior or a proof of geometric accuracy. Raw export: [PLY](assets/dinosaur-voxels-raw.ply); observed boundary samples: [PLY](assets/dinosaur-voxels-observed.ply). Both PLY files contain only six-neighbour boundary samples, including grid edges, at corner+index×step, not voxel centers. Filtering can expose new boundary samples. Neither contains triangles or texture. The six-second animation renders the final observed boundary samples from the 36 calibrated viewpoints; it is saved playback, not execution speed. Teal and depth shading are display aids. Open `assets/dinosaur-viewer.html` locally and drag/scroll to inspect the observed cloud; GitHub’s file preview does not execute HTML.

The input is the Oxford/VGG dinosaur toy sequence, credited to Wolfgang Niem, University of Hannover. The recovered Freehand project supplied this copy and masks; the original creator of the masks is not established. The `demoP` table is coarsely rounded (often four decimal places); these results are specific to that table. Freehand's algorithm differs (two-background voting and mesh/texturing); this replay uses Volume’s original one-background `ACCURATE` rule. Do not compare counts between projects as equivalent algorithms. Source/data terms remain as recovered; no blanket license is added.

## Notebook and evidence

The [notebook](notebooks/voxel_carving_demo.ipynb) runs the synthetic Python component and can export a point cloud. Six real Jupyter cells passed on 2026-11-12; it was not changed or rerun for this revival. The Colab version downloads updated modules from unpinned main at runtime when a local checkout is absent. Pin the downloaded module revision for reproducible Colab use. Real-data checks here use the native command-line harness, not that notebook.

`validation/2026-11-14/` records actual Mac/Linux tests, original missing-header build failure, sanitizer status and full replay metrics/hashes. `VALIDATION.json` retains the previous notebook record separately. All 21 recovered source files and the main project-reference README were verified unchanged.

The replay records input-mask/photograph hashes and environment versions. Mask decode uses nonzero PIL luminance on the supplied white-on-black masks. The zero-mismatch list is written only after asserting zero at each view. Native wall time includes startup, hex parsing and snapshot I/O; it is not an isolated kernel benchmark. Dated results are copied from build/dinosaur/metrics.json into validation/2026-11-14/dinosaur-metrics.json after verification.
