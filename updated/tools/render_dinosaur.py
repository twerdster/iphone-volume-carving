#!/usr/bin/env python3
"""Render original-core voxel samples beside their real input photographs.

The uniform teal color is a display aid. This carver does not recover texture
or triangles. Views use the dataset's actual camera matrices.
"""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image,ImageDraw,ImageFont


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=Path('assets'))
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    frames=args.results/'frames';frames.mkdir(exist_ok=True)
    metrics=json.loads((args.results/'metrics.json').read_text());points=np.load(args.results/'dinosaur.npz')['points']
    fontfile='/System/Library/Fonts/Supplemental/Arial.ttf'
    if not Path(fontfile).exists():fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    fonts={n:ImageFont.truetype(fontfile,n) for n in [12,14,16,18,22,28]}
    for i,P in enumerate(metrics['calibration']['projection_matrices']):
        image=Image.new('RGB',(1000,600),'#f1f6f9');d=ImageDraw.Draw(image)
        d.text((35,24),'Volume carving · calibrated image replay',font=fonts[28],fill='#12324b')
        d.text((35,65),f"Recovered C++ Sculptor · 36 real views · {metrics['grid_size']}³ voxel grid",font=fonts[18],fill='#49657a')
        d.text((35,105),'INPUT PHOTOGRAPH',font=fonts[14],fill='#49657a')
        photo=Image.open(args.dataset/'pictures'/f'viff.{i+1}.png').convert('RGB').resize((390,312))
        image.paste(photo,(35,135))
        mask=Image.open(args.dataset/'silhouettes'/f'sil_{i+1}.png').convert('RGB').resize((130,104))
        image.paste(mask,(35,465));d=ImageDraw.Draw(image)
        d.text((180,477),f'View {i+1:02d} / 36',font=fonts[22],fill='#12324b')
        d.text((180,510),'Supplied foreground mask',font=fonts[14],fill='#49657a')
        d.text((480,105),'OBSERVED VOXEL SURFACE · SAME CAMERA',font=fonts[14],fill='#49657a')
        d.rounded_rectangle((470,135,965,535),radius=10,fill='#10283b')
        P=np.array(P).reshape(3,4);uvw=points@P[:,:3].T+P[:,3];xy=uvw[:,:2]/uvw[:,2:3]
        # Actual input-camera projection; the depth tint is visualization only.
        order=np.argsort(uvw[:,2])[::-1];depth=uvw[:,2];depth=(depth-depth.min())/(np.ptp(depth)+1e-12)
        for index in order:
            x,y=xy[index];x=480+x*(480/720);y=143+y*(384/576)
            if 473<x<962 and 138<y<532:
                shade=1-depth[index]*.48;c=(int(54*shade),int(218*shade),int(209*shade))
                d.ellipse((x-2,y-2,x+2,y+2),fill=c)
        d.text((485,545),f"{metrics['observed_voxels']:,} observed / {metrics['occupied_voxels']:,} raw voxels",font=fonts[18],fill='#12324b')
        d.text((35,577),'Input: VGG / W. Niem · Never-observed voxels excluded from display; raw export retained · Saved playback',font=fonts[12],fill='#49657a')
        image.save(frames/f'{i:04d}.png')
    Image.open(frames/'0000.png').save(args.out/'dinosaur-carving.png')
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','6','-i',str(frames/'%04d.png'),'-c:v','libx264','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(args.out/'dinosaur-carving.mp4')],check=True)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(args.out/'dinosaur-carving.mp4'),'-filter_complex','fps=4,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64[p];[b][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0',str(args.out/'dinosaur-carving.gif')],check=True)
    # Standalone, local browser viewer; no data upload or external libraries.
    cloud=(points-points.mean(axis=0));cloud/=np.max(np.ptp(cloud,axis=0))
    values=json.dumps(np.round(cloud,5).tolist(),separators=(',',':'))
    html='''<!doctype html><meta charset="utf-8"><title>Dinosaur voxel boundary samples</title>
<style>body{margin:0;background:#10283b;color:#dcf2f4;font:16px system-ui}header{padding:20px}h1{margin:0;font-size:24px}p{margin:8px 0}canvas{width:100vw;height:75vh;touch-action:none}</style>
<header><h1>Dinosaur · occupied voxel boundary samples</h1><p>Recovered C++ Sculptor, 36 calibrated silhouettes, GRID_SIZE³ grid. Display excludes never-observed voxels; raw PLY retained. Drag to rotate; scroll to zoom.</p><p>Display color only; no recovered texture or mesh. See the validation record for scope and provenance.</p></header><canvas></canvas><script>
const points=POINTS,canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');let yaw=0,pitch=-.3,zoom=1,drag=null;
function draw(){canvas.width=innerWidth*devicePixelRatio;canvas.height=innerHeight*.75*devicePixelRatio;let w=canvas.width,h=canvas.height,s=Math.min(w,h)*.8*zoom;ctx.fillStyle='#10283b';ctx.fillRect(0,0,w,h);let a=Math.cos(yaw),b=Math.sin(yaw),c=Math.cos(pitch),d=Math.sin(pitch);let q=points.map(([x,y,z])=>{let X=a*x-b*z,Z=b*x+a*z;return[X,c*y-d*Z,d*y+c*Z]}).sort((p,q)=>p[2]-q[2]);for(let [x,y,z] of q){ctx.fillStyle=`hsl(177 62% ${55+z*22}%)`;ctx.beginPath();ctx.arc(w/2+x*s,h/2-y*s,2*devicePixelRatio,0,Math.PI*2);ctx.fill()}}
canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)};canvas.onpointermove=e=>{if(drag){yaw+=(e.clientX-drag[0])*.01;pitch+=(e.clientY-drag[1])*.01;drag=[e.clientX,e.clientY];draw()}};canvas.onpointerup=()=>drag=null;canvas.onwheel=e=>{e.preventDefault();zoom=Math.max(.25,Math.min(4,zoom*Math.exp(-e.deltaY*.001)));draw()};onresize=draw;draw();</script>'''.replace('POINTS',values).replace('GRID_SIZE',str(metrics['grid_size']))
    (args.out/'dinosaur-viewer.html').write_text(html)


if __name__=='__main__':main()
