# 3D Volume Carving on iPhone

<p align="center">
  <img src="assets/project-preview.jpg" alt="Project title slide reading 'iOS Vision Programming Project: AR assisted shape from Volumetric stereo, GIP Laboratory, Technion Haifa' over a rendered grid of white cubes" width="420">
</p>

![Platform: iOS (iPhone)](https://img.shields.io/badge/platform-iOS%20%2B%20Python%203-lightgrey)
![Code: C++ / Python](https://img.shields.io/badge/code-C%2B%2B%20%2F%20Python-blue)
![Source: partial snapshot](https://img.shields.io/badge/source-partial%20snapshot-orange)

An iPhone scanning application using Vuforia camera poses, a green base and marker, voxel carving and marching cubes to reconstruct an object's visual hull.

Students: Sergey Kucher, Alex Povichuk.

Supervision: Aaron Wetzler.

## Status

**Partial original source recovered.** The `source/` directory contains 21 original geometry, voxel-sculpting and mesh files, restored without modification. This is not the complete iPhone application and is not a runnable release.

## Original code

The 21 recovered files are in [`source/`](source/): voxel-sculpting, geometry and mesh code in [`source/Sculptor/`](source/Sculptor/) and one helper header in [`source/Drop Shadows/`](<source/Drop Shadows/>). The Objective-C app shell and tracking integration are not part of this snapshot.

## Running

There is no standalone build command for this partial source snapshot. The original app project targets iOS 4.2, uses Objective-C/Objective-C++, OpenGL ES and the historical Qualcomm QCAR/Vuforia tracking SDK, with UIKit, Foundation, QuartzCore, AVFoundation, CoreMedia and CoreVideo. It also requires its original camera/tracking configuration and resources.

The complete historical archive contains SDK source marked Qualcomm Confidential and Proprietary. Those files, SDK libraries, third-party UI files and generated project state have not been republished. The mesh source also references `MarchingCubes.h`, whose redistribution provenance has not yet been established; that dependency is intentionally absent pending review.

To restore a runnable app, recover appropriately licensed tracking/meshing dependencies, then reconstruct and modernize the Xcode integration. No replacement dependencies or successful build are claimed here. Compilation and device behavior have not been tested on the recovery machine.

## Updated code (2026)

The separately maintained [`updated/`](updated/) directory adds a runnable Python voxel-carving core. The original source and student attribution remain preserved above. [Open the notebook](updated/notebooks/voxel_carving_demo.ipynb) to explore the synthetic example; it is distinct from the historical application and original results.

On macOS 15.1.1 with Python 3.14.4, **16 component tests pass**, and all 6 notebook code cells execute in an isolated real Jupyter kernel. Accurate and fast occupancy bits and mutated masks match the compiled original C++ on bounded synthetic cases. Analytic silhouette intersection, monotonicity, exports and old vector-cache regressions are tested. A declaration-only compatibility header allows carving compilation; missing marching-cubes meshing is not implemented. Linux and the complete historical app have not been validated. See the [updated setup and limitations](updated/README.md).

## Links

- [Project entry on Aaron Wetzler's website](https://twerdster.github.io/#3d-volume-carving-on-iphone)

- [Partial source](https://github.com/twerdster/iphone-volume-carving/tree/main/source)

## Attribution and Updates

Original project by Sergey Kucher and Alex Povichuk, supervised by Aaron Wetzler. No explicit top-level code license was found, and no new license is assigned by this archive. Source files retain their original contents. Original authors can open an issue to contribute updates or request corrections or removal of their material.

Figure provenance: `assets/project-preview.jpg` is the original student-project title slide from the archived project page on Aaron Wetzler's website, copied without modification. It is a presentation slide, not a reconstruction result.

