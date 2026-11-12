"""Updated2026 synthetic silhouette-to-voxel demonstration; no phone/SDK required.

Run from updated/: python3 demo.py --size 24 --radius 8 --out build
The views are ideal orthographic disks. Their visual hull is not an original
capture, marching-cubes mesh, or measured reconstruction benchmark.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from volume_carving_port import ACCURATE, SculptData, Sculptor


def disk_views(size: int = 24, radius: float = 8):
    center = (size - 1) / 2
    pixels = bytearray(255 if (x-center)**2 + (y-center)**2 <= radius**2 else 0
                       for y in range(size) for x in range(size))
    projections = ([1,0,0,0, 0,1,0,0, 0,0,0,1],
                   [1,0,0,0, 0,0,1,0, 0,0,0,1],
                   [0,1,0,0, 0,0,1,0, 0,0,0,1])
    return [SculptData(p, bytearray(pixels), size, size) for p in projections]


def carve_demo(size: int = 24, radius: float = 8, mode: str = ACCURATE):
    model = Sculptor(size, float(size), (0, 0, 0))
    counts = [model.count_on()]
    for view in disk_views(size, radius):
        model.sculp(view, mode)
        counts.append(model.count_on())
    return model, counts


def point_cloud_svg(model: Sculptor) -> str:
    points = sorted(model.occupied(), key=lambda p: sum(p))
    # New display-only isometric projection of the actual occupied voxels.
    scale = 300 / model.size
    circles = []
    for x, y, z in points:
        u = 400 + (x-y)*0.85*scale
        v = 400 + ((x+y)*0.35-z)*scale
        light = int(55 + 135*z/max(1,model.size-1))
        circles.append(f'<circle cx="{u:.2f}" cy="{v:.2f}" r="{max(1,scale*.17):.2f}" fill="rgb(30,{light},160)"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 650">'
            '<rect width="800" height="650" fill="white"/>'
            '<text x="30" y="30" font-family="sans-serif" font-size="20">SYNTHETIC visual hull from three disk silhouettes</text>'
            + ''.join(circles) +
            f'<text x="30" y="625" font-family="sans-serif">{len(points)} occupied voxels; new point-cloud display, no mesh extraction</text></svg>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size', type=int, choices=(16,24,32,64), default=24)
    parser.add_argument('--radius', type=float, default=8)
    parser.add_argument('--out', type=Path, default=Path('build'))
    args = parser.parse_args()
    if not math.isfinite(args.radius) or args.radius <= 0:
        parser.error('radius must be finite and positive')
    model, counts = carve_demo(args.size, args.radius)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'synthetic-hull.ply').write_text(model.to_ply())
    (args.out/'synthetic-hull.svg').write_text(point_cloud_svg(model))
    print('SYNTHETIC occupied voxels before/after each view:', counts)
    print('Wrote point cloud and illustration to', args.out)


if __name__ == '__main__':
    main()
