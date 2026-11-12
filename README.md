# 3D Volume Carving on iPhone

An iPhone scanning application using Vuforia camera poses, a green base and marker, voxel carving and marching cubes to reconstruct an object's visual hull.

Students: Sergey Kucher, Alex Povichuk.

Supervision: Aaron Wetzler.

## Status

**Partial original source recovered.** The `source/` directory contains 21 original geometry, voxel-sculpting and mesh files, restored without modification. This is not the complete iPhone application and is not a runnable release.

## Running

There is no standalone build command for this partial source snapshot. The original app project targets iOS 4.2, uses Objective-C/Objective-C++, OpenGL ES and the historical Qualcomm QCAR/Vuforia tracking SDK, with UIKit, Foundation, QuartzCore, AVFoundation, CoreMedia and CoreVideo. It also requires its original camera/tracking configuration and resources.

The complete historical archive contains SDK source marked Qualcomm Confidential and Proprietary. Those files, SDK libraries, third-party UI files and generated project state have not been republished. The mesh source also references `MarchingCubes.h`, whose redistribution provenance has not yet been established; that dependency is intentionally absent pending review.

To restore a runnable app, recover appropriately licensed tracking/meshing dependencies, then reconstruct and modernize the Xcode integration. No replacement dependencies or successful build are claimed here. Compilation and device behavior have not been tested on the recovery machine.

## Links

- [Project entry on Aaron Wetzler's website](https://twerdster.github.io/#3d-volume-carving-on-iphone)

## Attribution and Updates

Original project by Sergey Kucher and Alex Povichuk, supervised by Aaron Wetzler. No explicit top-level code license was found, and no new license is assigned by this archive. Source files retain their original contents. Original authors can open an issue to contribute updates or request corrections or removal of their material.

