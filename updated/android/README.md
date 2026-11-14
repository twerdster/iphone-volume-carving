# Volume Carving: updated Android frontend

The app reconstructs the supplied 36-view dinosaur sequence on the device using the unchanged recovered `Sculptor<128>` ACCURATE operator through `updated/native/`. It then displays computed observed boundary samples in a GLES20 viewer. No saved geometry is loaded. The original application, source bytes and root README remain separate.

## Build

Use JDK 21, Android SDK API 34/build-tools 34.0.0, NDK 27.2.12479018 and CMake 3.22.1. The wrapper pins Gradle 8.7; Android plugin 8.3.0. API 26 is the declared minimum; arm64-v8a and armeabi-v7a are built. Volume has no OpenCV dependency.

Set `DINOSAUR_DATASET` (or `-PdinosaurDataset`) to the recovered Freehand `source/PointCloudSample/dinosaur` directory, then run:

```sh
export JAVA_HOME=/path/to/jdk-21
export ANDROID_HOME=/path/to/android-sdk
export DINOSAUR_DATASET=/path/to/dinosaur
./gradlew --no-daemon --max-workers=2 assembleDebug lintDebug
```

Gradle copies photographs and masks into generated APK assets without duplicating the raw dataset in Git. Calibration comes from `../assets/dinosaur-calibration.json`, which records the rounded Freehand demoP table. An input manifest records every bundled PNG/calibration SHA-256. Generated outputs normally use `app/build/`; task-private native paths can be supplied with `-PpredatorBuildDir=/native/path/build`, `-PpredatorNativeDir=/native/path/cxx` and `--project-cache-dir /native/path/project-cache`. Those two property names are inherited from the shared frontend build scaffold. Set a task-specific `GRADLE_USER_HOME` to keep caches private. Debug signing stays local.

## Run and inspect

Tap **Run 36 views**. One process-wide FIFO worker and atomic run-ownership guard serialize reconstruction across Activity recreation. A replacement Activity waits for prior native cleanup. Closing an Activity requests cancellation at explicit worker checks. Each input photograph/mask is decoded and supplied to the native operator. The UI shows current inputs, progress, occupancy and FNV hash. After the final view, a separate output filter retains occupied cells projecting inside at least one input image and recomputes six-neighbor boundary samples. Raw occupancy is also retained. Drag to rotate, pinch to zoom, reset the view or enable rotation. Point colors are a display height gradient, not recovered texture; no triangle extraction is provided.

```sh
adb shell am force-stop org.awetzler.volumecarving.updated
adb shell am start -n org.awetzler.volumecarving.updated/.MainActivity --ez autoRun true
adb exec-out run-as org.awetzler.volumecarving.updated \
  cat files/reconstruction/run-result.json
```

`run-result.json` is removed when a new run starts and published atomically **last**, after binary geometry and hashes are written. It includes all 36 per-view counts, pixel-buffer hashes, FNV values and output SHA-256 values. `status: complete` means 36 views were computed natively, structurally checked arrays were saved and output hashes recorded. The app does not gate completion on fixed-fixture baseline counts/FNV; the device runner compares those recorded values externally. This marker is not a `baseline_verified` assertion, unlike the UIKit/host baseline gate. `progress.json` is interim evidence. Output files in the same private directory are `positions.f32le`, `normals.f32le`, `colors.rgba8` and `occupancy.bin`. Float arrays use little-endian float32. Volume normals/colors are empty because the native output consists of positions; renderer colors are presentation only. Logcat tag `CarvingRuntime` also reports progress/completion. A partial trace does not demonstrate completion.

## Checks and scope

[`VALIDATION.json`](VALIDATION.json) records actual build/lint/package checks, source hashes, prepared-source manifests, native symbols and input hashes. Both ABIs compiled; lint reported no errors. This build agent did not install, launch or capture any device. Physical runtime evidence is recorded separately by the device runner. Declared minimum-API/32-bit support remains a compile claim until tested.

The viewer maps Volume world axes to `(y,z,-x)` so native grid Z is displayed vertically, then centers/scales the actual arrays. Saved positions retain native coordinates. Display height colors do not alter the saved points. Native timing includes JNI conversion, reconstruction and statistics; total elapsed time additionally includes PNG decoding, extraction and file writes. Neither is presented as a throughput benchmark. No camera or pose estimation is used; supplied-view consistency is not independent 3D accuracy. The missing original meshing implementation remains absent.

Original project: Sergey Kucher and Alex Povichuk, supervised by Aaron Wetzler. Dinosaur: Wolfgang Niem, Hannover, via [Oxford VGG](https://www.robots.ox.ac.uk/~vgg/data/mview/) and Ben Tordoff’s example in the Freehand archive. Existing source/sample/data terms remain; no blanket new license is assigned. Bundled notices are available through **Credits, limits and notices**. Gradle wrapper Apache license/NOTICE are preserved.
