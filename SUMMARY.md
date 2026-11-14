# iphone-volume-carving: maintenance context

Read SUMMARY.md, then SKILL.md, the reference README and updated documentation. Current results: 2026-11-14.

## Purpose and preservation

Silhouette visual-hull carving by Sergey Kucher and Alex Povichuk, supervised by Aaron Wetzler. All 21 recovered source files remain unchanged. Preserve their notices/credits. The root README is the project reference; new work belongs under updated/.

## Current executable work

The unmodified C++ carver compiles on Mac/Linux through a declaration-only compatibility header for the missing MarchingCubes.h. No numerical carving fix was needed for the tested ACCURATE path. New harness code adds 128³ grids and per-view bit snapshots. New tooling replays 36 real masks with supplied calibrated cameras from the separate Freehand archive, checks occupancy independently and exports PLY boundary samples. Photographs are used only to render the demonstration.

All 16 component tests passed on both platforms without skips, including all three compiled-original comparisons. The full 128³, 36-view offline harness replay exited 0 with no ASan/UBSan reports on both; Linux ASan output text, including mutated-mask hex and final occupancy, is byte-identical to Mac strict output. On Mac, the separate float32 reference agrees at all 2,097,152 voxels after every view. It implements the same rules; this is consistency evidence, not geometric accuracy.

Raw occupancy has 27,310 voxels, including 5,830 that never project inside any image. A separately labeled output filter excludes those, leaving 21,480 voxels and 6,415 recomputed boundary samples. Both raw and observed boundary exports are retained; filtering can expose new boundary samples. The term observed means in-image projection, not occlusion reasoning. Results are specific to Freehand's rounded demoP table and masks; the masks' original creator is not established.

Direct compilation fails at missing MarchingCubes.h. The harness placeholder does not implement meshing. The historical iOS shell, camera/QCAR/Vuforia integration, triangle extraction and texture recovery remain absent. New fixture replay frontends are described below. Historical projection/index/vector-cache quirks remain documented. No held-out-view, physical-capture or reference-surface evaluation was performed.

## Workflow and evidence

See updated/README.md and updated/RUNNING_2026.md for commands and dependencies. updated/VALIDATION.json retains current checks and the earlier notebook record; updated/validation/2026-11-14/ contains environment details, metrics, hashes and logs. Six notebook code cells executed in Jupyter on 2026-11-12 were not rerun here.

Media, PLY samples and a local interactive viewer live under updated/assets/. Preserve GIF <2,000,000 bytes and MP4 <10,000,000 bytes; playback rate is not throughput. Bulk data/intermediates: /Volumes/AgentSSD/agent-work/project-revivals-2026-11-14/volume-carving. Recheck SSD mount/space/write access before large writes; keep builds/environments on native filesystems. Private host/build paths and full logs are recorded in the task handoff.

On 2026-11-13 Alex Povichuk gave Aaron permission to use the project code. This records Alex's response only; preserve correspondence privately, original attribution and existing terms. No repository-wide license is added. Dinosaur data is credited to Wolfgang Niem, Hannover, via Oxford VGG and Ben Tordoff’s example in the Freehand archive.

Earlier documentation received Claude reviews on 2026-11-12 and 2026-11-13. Two tools-disabled Claude editorial reviews also completed on 2026-11-14; useful corrections were checked against code/results and applied. Before every commit reread/synchronize SUMMARY.md and SKILL.md; verify all source hashes and root README identity, changed links/media and diff scope. No package bundles these docs.

## New native replay frontends (2026-11-14)

`updated/native/` exposes the recovered C++ through a C ABI; `updated/ios/` generates
an external UIKit/SceneKit Xcode project, `updated/android/` provides Java/JNI/GLES20,
and `updated/desktop/` starts an actual native replay from a loopback browser UI.
All reconstruct from 36 bundled real inputs and supplied rounded demoP cameras;
no saved geometry substitutes for computation. These are new interfaces, not a
restoration of the historical mobile app or live tracking/capture.

See `updated/PLATFORMS.md` for build/run commands and coordinate formats, and
`updated/validation/native-platforms/` for separate build/source, native result,
repeated-run, cross-platform and capture records. Final host builds and all 36-view
C-ABI runs passed on Mac/Linux; signed iphoneos builds passed. The new apps also completed all 36 views on a physical iPhone 12/iOS 18.0.1 and
Pixel 2/Android 10, with matching recorded fixture counts/FNV. The iOS marker
self-checks its baseline; Android baseline comparison was performed externally.
Physical results/artifact hashes/captures are retained separately in
`ios-result.json`/`android-result.json` and corresponding provenance. Android
ABI compilation and minimum OS settings are not extra runtime coverage. Do not
overwrite the device runner's mobile evidence.

The desktop renderer uses actual computed arrays, supports drag/orbit, rejects
stale results across reruns and retains all per-view native counts. Mac capture is
a headed Chrome viewport; Linux capture is X11 :98 with software WebGL. Display
axis transformations leave saved arrays unchanged. Android stores raw native
coordinates; host/UIKit outputs are normalized as documented. New C ABI/frontend
sanitizer coverage is not inferred from the earlier offline-core sanitizer runs.

Native C ABI final result: 27,310 raw / 21,480 observed voxels and 6,415 filtered
boundary samples; occupancy FNV bc1847c8e8264d3f. Mac/Linux normalized geometry and
display-color bytes match. A new C-ABI analytic-prism regression passed 1/1 on both
hosts, including every packed bit, caller-buffer preservation, rejected-input
atomicity, idempotence and boundary checks. No numerical carver change was made.

Actual tools-disabled Claude code reviews and a focused 59-file follow-up completed
for both native frontend implementations. Useful fixes were verified against code;
the follow-up found no High issues or material regressions. Android completion
baseline semantics are explicitly qualified. An actual 32-record documentation
review also completed and its factual qualifications were applied. Review adds
no runtime coverage; see updated/validation/native-platforms/claude-review.json.


The UIKit display adapter converts a copy of byte RGBA to float4 in [0,1] for
SceneKit; saved byte arrays/native operators are unchanged. The earlier physical
white-color display failure is retained privately. A focused host test checks all
256 byte values in each channel, finite range/error, source preservation and a
known teal/alpha case; see updated/validation/native-platforms/ios-display-colors-test.json. Rebuild and recapture the
iOS app for display changes; desktop/Android builds are unaffected.

The final normalized-color iOS builds completed the same 36-view fixture on the
physical iPhone with unchanged saved positions/colors and occupancy hashes. Actual
recordings visibly show colored Freehand geometry/teal Volume points. The bounded
8-file color-delta Claude review completed without material findings; it is a
separate actual static invocation after the earlier 59-file review. See
updated/validation/native-platforms/platform-status.json for current artifact,
runtime and capture links. Preserve the existing SDK/live-capture limitations.
