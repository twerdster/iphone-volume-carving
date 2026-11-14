# Maintaining iphone-volume-carving

Read SUMMARY.md first, then this file, the root project reference, updated/README.md, updated/RUNNING_2026.md, validation records and relevant source.

## Updated-work navigation

Aaron explicitly authorized the root README’s local `New!` badge and exact “Updated and ported for modern hardware” link on 2026-11-14. Keep both linked to `updated/README.md#updated-and-ported-for-modern-hardware`; retain the italic historical-reference qualifier and preserve the rest of the historical root reference. The matching updated README heading must introduce a short, factual account of the actual changes and limitations before the existing visuals, setup and evidence. Keep implementation descriptions and detailed results under `updated/`.

This navigation addition is the authorized exception to older root-README preservation instructions below. Verify the historical body after removing only that block, preserve source hashes/pins and leave historical validation hashes attached to their original freezes. Documentation-only navigation edits do not add runtime coverage or require a package rebuild.

## Preservation and workflow

Keep the root README unchanged unless Aaron explicitly requests edits there. Preserve original source bytes/pins, author/student/third-party attribution, notices and permission scope. Put new code, adapters, behavioral changes, guides and result media under updated/. Never imply that a declaration-only header or headless core is a restored historical app. See the running guide for current commands/dependencies rather than duplicating them here.

## Evidence

Use updated/VALIDATION.json and updated/validation/2026-11-14/ for current results and limits. Keep earlier notebook results dated; do not imply they were rerun. Distinguish original code, native repairs, Python translation, optional behavior/output filters, actual input data, synthetic fixtures and saved playback. State the tested implementation, platform, operator chain, counts, units and reference provenance. One sequence does not establish general correctness, accuracy or device compatibility.

Compare fixes with reproduced failures and affected tests/sanitizers. Retain raw output when new processing changes presentation. Follow SUMMARY.md for SSD data paths; recheck mount identity/space/write access before bulk writes. Keep native builds/environments off exFAT. Preserve private correspondence/contact details outside the public repository; an author's response does not assign a blanket license.

## Before every commit

Reread and synchronize SUMMARY.md and this file whenever behavior, commands, outputs, workflow or status changes. Verify original source hashes/pins and root README identity. Check changed Markdown, links/images, media limits and diff scope; run meaningful affected checks after code changes. These documents are not shipped in APK/app bundles. Keep Claude review claims tied to completed reviews and factual checks; editorial review adds no runtime coverage.


## Native fixture applications

Use updated/PLATFORMS.md for the new C ABI, UIKit/SceneKit, Android/JNI/GLES20 and
localhost desktop interfaces. Preserve original source/root README and build
outside the repository. Android build metadata is in updated/android/VALIDATION.json;
host/iOS source/build records and distinct device runtime/capture evidence are in
updated/validation/native-platforms/. Confirm completion JSON and per-view counts,
not merely a screen image. Only the 36-view supplied-camera fixture is validated;
no live capture/tracking or restored historical app is implied.

For C ABI changes rerun the affected native regression and 36-view host replay.
For frontend changes check artifact writes/counts/finiteness, stale completion
handling, repeated runs and actual geometry interaction. Serialize Android work
across Activity recreation. Keep completion markers last and bind saved artifacts
by hashes. Android completion does not gate the fixed baseline: compare its
recorded counts/FNV externally rather than calling it baseline-verified. Normalize
the documented saved coordinate formats before comparing
platforms. Distinguish native CPU reconstruction from GPU display; optional orbit
is display-only. Do not infer sanitizer coverage for new wrappers/frontends from
prior offline core tests. Tie Claude claims to actual reviewed source snapshots;
check its factual suggestions rather than applying them automatically.


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
