# iphone-volume-carving: original and updated code

Read README.md before maintenance. Preserve original source, submodule pins and student/third-party attribution; keep generated build output, notebook outputs and private recovery evidence out of Git.

## Updated component — 2026-11-12

`updated/` contains the Python voxel-carving core, its tests and `updated/notebooks/voxel_carving_demo.ipynb`. The original application/source snapshot is not altered. New component validation: 16 unittest tests passed on macOS 15.1.1 arm64 / Python 3.14.4; 6 notebook code cells passed real nbclient/ipykernel execution. Accurate and fast occupancy bits and mutated masks match the compiled original C++ on bounded synthetic cases. Analytic silhouette intersection, monotonicity, exports and old vector-cache regressions are tested. A declaration-only compatibility header allows carving compilation; missing marching-cubes meshing is not implemented. No full mobile/hardware application, original benchmark accuracy or Linux runtime success is claimed. Read `updated/README.md` for exact commands and limitations.

README retains the representative historical figure, three factual badges and Original code section. New runnable code is explicitly separated under Updated code (2026). No blanket license was assigned. Review this summary and any SKILL.md before committing; update actual validation when code or workflows change.
