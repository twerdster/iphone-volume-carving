#!/usr/bin/env python3
"""Replay real calibrated dinosaur masks through unchanged original Sculptor.

Requires a separate freehand-voxel-carving checkout with its source initialized.
Use the included historical rounded camera table in assets/dinosaur-calibration.json.
No missing MarchingCubes implementation is supplied or exercised.
"""
import argparse
from datetime import datetime
import hashlib
import json
import platform
import shutil
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from PIL import Image, __version__ as pillow_version

UPDATED=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UPDATED/'harness'))
from build_original import build


def unpack(path,size):
    raw=np.frombuffer(bytes.fromhex(path.read_text().strip()),dtype=np.uint8)
    return np.unpackbits(raw,bitorder='little').reshape(size,size,size).astype(bool)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--calibration',type=Path,required=True)
    ap.add_argument('--size',type=int,choices=[16,24,32,64,128],default=128)
    ap.add_argument('--out',type=Path,default=Path('build/dinosaur'))
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    snapshots=args.out/'snapshots';snapshots.mkdir(exist_ok=True)
    meta=json.loads(args.calibration.read_text());size=args.size
    paths=[args.dataset/'silhouettes'/f'sil_{i}.png' for i in range(1,37)]
    masks=[np.asarray(Image.open(p).convert('L'))>0 for p in paths]
    if any(m.shape!=(576,720) for m in masks):raise ValueError('expected 720x576 masks')
    lines=[f'{size} {meta["cube_side"]} '+ ' '.join(map(str,meta['cube_corner']))+' 36']
    for P,mask in zip(meta['projection_matrices'],masks):
        lines+=['0 720 576',' '.join(map(str,P)),(mask.astype(np.uint8)*255).tobytes().hex()]
    inp=args.out/'native-input.txt';inp.write_text('\n'.join(lines)+'\n')
    exe=build('strict')['carve'];start=time.perf_counter()
    subprocess.run([str(exe),str(inp),str(args.out/'native-output.txt'),str(snapshots)],check=True)
    seconds=time.perf_counter()-start
    actual=unpack(snapshots/'view-36.hex',size)
    # Independent array expression follows C++ float32 evaluation order, not
    # the Python port's implementation or the native occupancy bits.
    index=np.indices((size,size,size),dtype=np.float32).reshape(3,-1).T
    step=np.float32(np.float32(meta['cube_side'])/np.float32(size))
    world=index*step+np.array(meta['cube_corner'],dtype=np.float32)
    reference=np.ones(len(world),dtype=bool);ever_in_map=np.zeros(len(world),dtype=bool);counts=[];hashes={}
    for i,(P,mask,path) in enumerate(zip(meta['projection_matrices'],masks,paths),1):
        P=np.array(P,dtype=np.float32).reshape(3,4)
        uvw=np.stack([((world[:,0]*row[0]+world[:,1]*row[1])+world[:,2]*row[2])+row[3] for row in P],axis=1)
        xy=np.trunc(uvw[:,:2]/uvw[:,2:3]).astype(np.int32)
        valid=(xy[:,0]>=0)&(xy[:,0]<720)&(xy[:,1]>=0)&(xy[:,1]<576)
        ever_in_map|=valid
        keep=np.ones(len(world),dtype=bool);keep[valid]=mask[xy[valid,1],xy[valid,0]]
        reference&=keep
        native=unpack(snapshots/f'view-{i:02d}.hex',size)
        mismatches=int(np.count_nonzero(native.ravel()!=reference))
        if mismatches:raise AssertionError(f'view {i}: {mismatches} independent occupancy mismatches')
        counts.append(int(native.sum()));hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    observed=actual & ever_in_map.reshape(actual.shape)
    def boundary(grid):
        interior=np.zeros_like(grid)
        interior[1:-1,1:-1,1:-1]=grid[1:-1,1:-1,1:-1]&grid[:-2,1:-1,1:-1]&grid[2:,1:-1,1:-1]&grid[1:-1,:-2,1:-1]&grid[1:-1,2:,1:-1]&grid[1:-1,1:-1,:-2]&grid[1:-1,1:-1,2:]
        return np.argwhere(grid&~interior).astype(np.float32)*step+np.array(meta['cube_corner'],dtype=np.float32)
    raw_points=boundary(actual);points=boundary(observed)
    for name,cloud in [('dinosaur-voxels-raw.ply',raw_points),('dinosaur-voxels-observed.ply',points)]:
        with (args.out/name).open('w') as f:
            f.write(f'ply\nformat ascii 1.0\ncomment occupied voxel boundary samples; no mesh extraction\nelement vertex {len(cloud)}\nproperty float x\nproperty float y\nproperty float z\nend_header\n')
            np.savetxt(f,cloud,fmt='%.8g')
    np.savez_compressed(args.out/'dinosaur.npz',occupancy=actual,observed_occupancy=observed,points=points,raw_points=raw_points)
    result={'date':datetime.now().astimezone().date().isoformat(),'run_timestamp':datetime.now().astimezone().isoformat(),'input':'36 silhouettes and rounded historical camera matrices from Freehand dinosaur sample; different project from this code','grid_size':size,'voxel_count_initial':size**3,'voxel_counts_by_view':counts,'occupied_voxels':int(actual.sum()),'observed_voxels':int(observed.sum()),'observed_surface_voxel_samples':len(points),'raw_surface_voxel_samples':len(raw_points),'independent_mismatches_each_view':[0]*36,'native_carve_wall_seconds':seconds,'mode':'original ACCURATE, one background observation removes a voxel; out-of-map projections do not carve','source_changed':False,'mesh_extraction':False,'occupied_never_in_any_image':int(np.count_nonzero(actual.ravel()&~ever_in_map)),'environment':{'platform':platform.platform(),'python':platform.python_version(),'numpy':np.__version__,'pillow':pillow_version,'compiler':subprocess.check_output([shutil.which('clang++') or shutil.which('g++'),'--version'],text=True).splitlines()[0]},'photograph_sha256':{f'viff.{i}.png':hashlib.sha256((args.dataset/'pictures'/f'viff.{i}.png').read_bytes()).hexdigest() for i in range(1,37)},'mask_decode':'PIL convert L, nonzero luminance; supplied masks are white on black','output_filter':'separately labeled adapter excludes voxels never projected into any of the 36 images; raw native occupancy/export also retained','calibration':meta,'mask_sha256':hashes,'limitations':'input-view replay only; no held-out geometry or physical camera test; original mesh implementation absent'}
    (args.out/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['occupied_voxels','observed_voxels','observed_surface_voxel_samples','native_carve_wall_seconds','independent_mismatches_each_view']},indent=2))


if __name__=='__main__':main()
