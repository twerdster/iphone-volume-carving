# iphone-volume-carving: maintenance context

Read this file first, then SKILL.md and README.md. This context describes the repository as of 2026-11-12.

## Purpose and current source

Historical silhouette/camera-pose visual-hull reconstruction; updated Python port implements the voxel-carving core and point-cloud export.

21 original source files remain unchanged. Objective-C shell, QCAR/Vuforia integration and MarchingCubes.h are absent. The updated port takes 3x4 projection matrices and byte silhouettes, maintains occupancy bits and mutates visited mask pixels.

## Use and validation

From updated/: python3 demo.py --size 24 --radius 8 --out build; python3 -m unittest discover -s tests -v. See updated/README.md for notebook setup, restrictions and comparison.

updated/VALIDATION.json records 16 component tests and six real notebook code cells passed on 2026-11-12, macOS 15.1.1 arm64 / Python 3.14.4. Bounded synthetic occupancy/mask comparisons match compiled original C++ carving. The declaration-only MarchingCubes compatibility stub is newly written for the harness, not the missing original header, and does not implement or validate mesh extraction. The saved maintenance log confirms all three compiled-original tests passed among the 16, without skips.

No full iOS build/device run, recovered captures, reconstruction benchmark or Linux validation. Demo inputs are synthetic. Grid size is a multiple of eight in [8,128]. Historical vector-cache quirks are retained; point-cloud PLY/SVG output and undefined-projection handling are new.

## Documentation maintenance

The 2026-11-12 documentation revision organizes the README around implementation, available source, setup, recorded checks and limits. It preserves historical visuals and links, with captions separating historical results from updated examples. No runnable code, source provenance, pinned revisions, licenses or validation results changed in this revision. Recorded earlier tests were not rerun for the prose-only edits.

Preserve original source and authorship. New ports belong under updated/ and require their own scope/validation. Do not infer a blanket license from recovery. Review this file and SKILL.md before every commit and synchronize changes to workflow, commands, validation or status. Check relative links and figure rendering; never describe inventory counts or component tests as full-application validation.

Two actual Claude editorial review rounds on 2026-11-12 covered the README and related changed documentation, including context files, component guides and applicable algorithm/build notes or schematic text. Useful qualifications were checked against source, preserved project records and saved validation logs, then applied. Editorial review adds no runtime coverage.
