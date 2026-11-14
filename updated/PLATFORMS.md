# Native replay interfaces

These new interfaces call the recovered `Sculptor<128>` ACCURATE C++ carver. All 21
original files and the root README remain unchanged. The new UIKit, Android and
local desktop frontends are separate maintenance work; the missing historical
Objective-C shell, camera/QCAR/Vuforia integration and MarchingCubes implementation
remain absent.

## Tested execution and recordings

Each frontend processes all 36 dinosaur masks and supplied rounded Freehand
`demoP` camera matrices at run time. Photographs supply input/progress pictures,
not carving or texture. There is no saved result substituted for computation.
The unchanged carver produces 27,310 raw occupied voxels. A separately labeled
filter retains 21,480 cells that project inside at least one input image and
recomputes 6,415 six-neighbor boundary samples. These are points, not a mesh.
The raw occupancy fingerprint is FNV-1a64 `bc1847c8e8264d3f`; this binds one fixed
fixture result, not collision-resistant proof or geometric accuracy.

[Runtime records and capture provenance](validation/native-platforms/) distinguish
build checks, actual executions and screen captures. Both new apps completed
all 36 views on physical iPhone 12/iOS 18.0.1 and Pixel 2/Android 10, with the counts
and FNV above. Artifact records bind the tested binaries. This does not validate
other devices, live capture or the historical app. Phone recordings:
[iOS GIF](assets/ios-native.gif) / [MP4](assets/ios-native.mp4),
[Android GIF](assets/android-native.gif) / [MP4](assets/android-native.mp4).
Desktop recordings:
[macOS GIF](assets/macos-native.gif) / [MP4](assets/macos-native.mp4),
[Linux GIF](assets/linux-native.gif) / [MP4](assets/linux-native.mp4).
The macOS recording samples the headed Chrome viewport; Linux captures the actual
isolated X11 desktop. Linux uses software WebGL for display, while reconstruction
runs in native C++. Sampling/encoding details are retained with each clip. A run's
elapsed time is an observation, not a cross-platform throughput benchmark.

## macOS and Linux

Requirements: C++14, CMake 3.16+, libpng development files, Python 3 and a WebGL
browser. OpenCV is not required. The borrowed dataset is in the separate
[Freehand archive](https://github.com/twerdster/freehand-voxel-carving), under
`source/PointCloudSample/dinosaur`. From this repository's root:

```sh
cmake -S updated/native -B build/native -DWVC_BUILD_REPLAY=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build/native -j4
ctest --test-dir build/native --output-on-failure
python3 updated/desktop/server.py --project volume \
  --binary build/native/volume_native_replay \
  --dataset /path/to/Freehand/source/PointCloudSample/dinosaur \
  --calibration updated/assets/dinosaur-calibration.json \
  --work output/desktop --port 8785
```

Open `http://127.0.0.1:8785` and choose **Compute 36 views**. The new interface
launches the native executable, shows per-view counts, then displays its computed
boundary points. Drag to rotate or enable display rotation. Teal is a display
color, not recovered texture. See [earlier build/reference checks](RUNNING_2026.md)
for the strict original-source replay, independent occupancy reference and sanitizer
records.

The C ABI regression passed on Mac and Linux. It checks every packed bit for an
analytic carving prism, caller-mask preservation, idempotence, rejected-input
atomicity and boundary count/bounds. The desktop server serializes runs, clears
prior results and rejects foreign Host/Origin values. A deliberately delayed old
geometry response could not replace a new run's result. The server binds loopback
and is intended for local use, not an Internet service. The verified workflow uses one browser tab;
concurrent independent tabs are outside that test.

## iOS

Use Xcode 16.1. Neither OpenCV nor the missing historical SDK is required for this new target. Generate
its Xcode project outside the repository:

```sh
python3 updated/ios/generate_project.py --output /native/path/volume-ios \
  --dataset /path/to/Freehand/source/PointCloudSample/dinosaur \
  --calibration updated/assets/dinosaur-calibration.json
```

Open the generated `VolumeCarvingUpdated.xcodeproj`, select your signing team and
build for your device. The tested target is Release/iphoneos, minimum declared
iOS 16; simulator and other devices require separate verification. The UIKit
interface calls the actual C ABI on a worker, shows per-view counts and renders
computed boundary points with SceneKit. Launch arguments
`--autorun --autorun-delay 2 --orbit` wait two seconds before real computation,
then rotate only the computed display. No artificial per-view delay is added.

Documents contains `positions.f32`, `colors.rgba` and `run-result.json`. The
completion record is written last after checked writes, finite/count/fixed-fixture
occupancy checks and SHA-256 of saved artifacts and calibration. The teal RGBA array
is presentation data. A progress screenshot alone does not prove completion.

SceneKit receives a separate float4 RGBA buffer normalized to [0,1]; this fixes
the earlier white-color display while preserving saved byte colors. The focused
[display conversion test](validation/native-platforms/ios-display-colors-test.json)
checks all 256 byte values per channel and source preservation. To rerun it on a host:

```sh
c++ -std=c++14 -I updated/ios/App updated/ios/tests/display_colors.cpp -o /native/path/display-colors-test
/native/path/display-colors-test
```

## Android and coordinate formats

See [Android instructions](android/README.md) and
[build/package checks](android/VALIDATION.json). Java/JNI calls the same native
carver and GLES20 displays computed points. Native worker ownership serializes
runs across Activity recreation. APKs include input images/calibration and notices,
not saved geometry. Physical-device execution is separate from compile-only ABI
and declared minimum-API support. Android's height gradient is a display color;
its saved native normal/color arrays are empty.

The C ABI is in [volume_carving.h](native/volume_carving.h). It copies caller masks
before the recovered operator mutates them, validates projection bounds for the
fixed grid and retains the raw packed occupancy. The new observed filter is output
processing; it does not modify the original carving rule.

Android saves raw world coordinates in calibration units, without the Z flip. iOS and the host replay map the known cube
to [-1,1] and flip Z before saving; viewers then center, scale and rotate display
axes to show an upright dinosaur without changing those saved arrays. Normalize
coordinates before comparing frontend outputs; raw byte equality is not expected.

Out-of-image cells can survive the original rule, and visual hulls cannot recover
unconstrained concavities. No held-out-view, physical-capture or reference-surface
accuracy evaluation is claimed. Credit Sergey Kucher and Alex Povichuk, supervisor
Aaron Wetzler, and the borrowed Wolfgang Niem / Hannover / Oxford VGG dinosaur
sequence bundled through Ben Tordoff’s example in Freehand. Existing code/data terms and notices remain.

Android's completion marker confirms native processing and saved arrays/counts/hash
records; its fixed-fixture baseline is checked externally by the device runner.
It does not self-gate that baseline as the UIKit and host replay targets do.
The [actual Claude code review record](validation/native-platforms/claude-review.json)
is a static review of the supplied source snapshots and adds no runtime coverage.
