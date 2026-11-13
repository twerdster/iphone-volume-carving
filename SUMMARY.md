# iphone-volume-carving: maintenance context

Read SUMMARY.md, then SKILL.md, the reference README and updated documentation. Current results: 2026-11-14.

## Purpose and preservation

Silhouette visual-hull carving by Sergey Kucher and Alex Povichuk, supervised by Aaron Wetzler. All 21 recovered source files remain unchanged. Preserve their notices/credits. The root README is the project reference; new work belongs under updated/.

## Current executable work

The unmodified C++ carver compiles on Mac/Linux through a declaration-only compatibility header for the missing MarchingCubes.h. No numerical carving fix was needed for the tested ACCURATE path. New harness code adds 128³ grids and per-view bit snapshots. New tooling replays 36 real masks with supplied calibrated cameras from the separate Freehand archive, checks occupancy independently and exports PLY boundary samples. Photographs are used only to render the demonstration.

All 16 component tests passed on both platforms without skips, including all three compiled-original comparisons. Full 128³, 36-view native replay exited 0 with no ASan/UBSan reports on both; Linux ASan output text, including mutated-mask hex and final occupancy, is byte-identical to Mac strict output. On Mac, the separate float32 reference agrees at all 2,097,152 voxels after every view. It implements the same rules; this is consistency evidence, not geometric accuracy.

Raw occupancy has 27,310 voxels, including 5,830 that never project inside any image. A separately labeled output filter excludes those, leaving 21,480 voxels and 6,415 recomputed boundary samples. Both raw and observed boundary exports are retained; filtering can expose new boundary samples. The term observed means in-image projection, not occlusion reasoning. Results are specific to Freehand's rounded demoP table and masks; the masks' original creator is not established.

Direct compilation fails at missing MarchingCubes.h. The harness placeholder does not implement meshing. No full iOS shell, camera/QCAR/Vuforia, triangle extraction or texture recovery is provided. Historical projection/index/vector-cache quirks remain documented. No held-out-view, physical-capture or reference-surface evaluation was performed.

## Workflow and evidence

See updated/README.md and updated/RUNNING_2026.md for commands and dependencies. updated/VALIDATION.json retains current checks and the earlier notebook record; updated/validation/2026-11-14/ contains environment details, metrics, hashes and logs. Six notebook code cells executed in Jupyter on 2026-11-12 were not rerun here.

Media, PLY samples and a local interactive viewer live under updated/assets/. Preserve GIF <2,000,000 bytes and MP4 <10,000,000 bytes; playback rate is not throughput. Bulk data/intermediates: /Volumes/AgentSSD/agent-work/project-revivals-2026-11-14/volume-carving. Recheck SSD mount/space/write access before large writes; keep builds/environments on native filesystems. Private host/build paths and full logs are recorded in the task handoff.

On 2026-11-13 Alex Povichuk gave Aaron permission to use the project code. This records Alex's response only; preserve correspondence privately, original attribution and existing terms. No repository-wide license is added. Dinosaur data is credited to Wolfgang Niem, Hannover, via Oxford VGG and the Freehand archive.

Earlier documentation received Claude reviews on 2026-11-12 and 2026-11-13. Two tools-disabled Claude editorial reviews also completed on 2026-11-14; useful corrections were checked against code/results and applied. Before every commit reread/synchronize SUMMARY.md and SKILL.md; verify all source hashes and root README identity, changed links/media and diff scope. No package bundles these docs.
