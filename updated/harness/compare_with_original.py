"""Compare safe bounded synthetic inputs with the original C++ carving core.

This harness exercises only carving, not missing mesh extraction or the iOS
application. New harness/compat declarations are documented separately.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

UPDATED = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UPDATED))
sys.path.insert(0, str(UPDATED/'harness'))
from build_original import build
from volume_carving_port import ACCURATE, FAST, SculptData, Sculptor


def compare(views, size=16, mode=ACCURATE, exes=None):
    exes = exes or build('strict')
    views = list(views)
    lines = [f'{size} {size} 0 0 0 {len(views)}']
    for view in views:
        lines += [f'{int(mode == FAST)} {view.size_x} {view.size_y}',
                  ' '.join(repr(x) for x in view.projection), view.map.hex()]
    model = Sculptor(size, float(size), (0,0,0))
    counts, maps = [], []
    for view in views:
        local = SculptData(list(view.projection), bytearray(view.map), view.size_x, view.size_y)
        model.sculp(local, mode)
        counts.append(model.count_on())
        maps.append(local.map.hex())
    with tempfile.TemporaryDirectory(prefix='volume-reference-') as td:
        src, dst = Path(td)/'input.txt', Path(td)/'output.txt'
        src.write_text('\n'.join(lines)+'\n')
        subprocess.run([str(exes['carve']),str(src),str(dst)], check=True, timeout=30)
        original = dst.read_text().splitlines()
    for i, (count, pixels) in enumerate(zip(counts,maps)):
        if original[2*i] != f'view {i} on={count}' or original[2*i+1] != pixels:
            raise AssertionError(f'view {i}: original/updated count or mask differs')
    if original[2*len(views)] != model.bits_hex():
        raise AssertionError('original/updated final occupancy bits differ')
    return {'views':len(views),'mode':mode,'counts':counts,'occupancy_bytes':len(model.sculpture),'exact':True}


if __name__ == '__main__':
    from demo import disk_views
    executables = build('strict')
    for mode in (ACCURATE,FAST):
        print(compare(disk_views(16,5),mode=mode,exes=executables))
