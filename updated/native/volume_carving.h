/* New 2026 C interface for the unchanged recovered Sculptor<128> core.
 * Input masks/cameras are supplied by the host application; no camera SDK.
 * Original author/source notices and terms remain in ../../source/.
 */
#ifndef WETZLER_VOLUME_CARVING_H
#define WETZLER_VOLUME_CARVING_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef struct WVCContext WVCContext;
typedef struct {
    uint32_t views;
    uint32_t raw_voxels;
    uint32_t observed_voxels;
    uint32_t observed_boundary_points;
    uint64_t occupancy_fnv1a64;
} WVCStats;
typedef struct { float x, y, z; } WVCPoint;

/* Fixed recovered 128^3 grid. side/corner use supplied calibration units. */
WVCContext *wvc_create(float side, float corner_x, float corner_y, float corner_z);
void wvc_destroy(WVCContext *context);
/* 0 on success; -1 on rejected input/failure. P is row-major 3x4 float32.
 * The supplied mask has width*height bytes, 0 background, nonzero foreground.
 * The original mutates a private copy; caller bytes are never changed.
 * Validity is checked before the original ACCURATE operation is invoked.
 */
int wvc_apply(WVCContext *context, const float *projection12,
              const uint8_t *mask, size_t mask_bytes, uint32_t width, uint32_t height);
int wvc_get_stats(const WVCContext *context, WVCStats *stats);
/* Exact native packed layout x-major/y/z, little bit order along z.
 * Returns required bytes (262144). Copies only when capacity is sufficient.
 */
size_t wvc_copy_occupancy(const WVCContext *context, uint8_t *output, size_t capacity);
/* New, explicitly labeled output filter: retain occupied cells whose projection
 * fell inside at least one supplied image. Six-neighbour boundary samples are
 * recomputed after filtering. Points are at corner+index*(side/128).
 * Returns required point count; copies only when capacity is sufficient.
 */
size_t wvc_copy_observed_boundary(const WVCContext *context, WVCPoint *output, size_t capacity);
/* Context-local diagnostic, valid until its next call. No exceptions cross C. */
const char *wvc_last_error(const WVCContext *context);
#ifdef __cplusplus
}
#endif
#endif
