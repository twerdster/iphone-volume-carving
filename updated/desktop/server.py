#!/usr/bin/env python3
"""New localhost UI that starts the actual C-ABI replay executable.
No stored result/video substitutes for a run. Inputs/outputs remain local.
"""
import argparse,hashlib,json,mimetypes,platform,subprocess,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--binary',type=Path,required=True)
p.add_argument('--dataset',type=Path,required=True)
p.add_argument('--calibration',type=Path,required=True)
p.add_argument('--work',type=Path,required=True)
p.add_argument('--port',type=int,default=8784)
p.add_argument('--project',choices=['freehand','volume'],required=True)
a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
freehand=a.project=='freehand'
lock=threading.Lock();state={'running':False,'view':0,'status':'Ready: press Compute to execute native C++.','complete':False};result=None
host='macOS' if platform.system()=='Darwin' else platform.system();title='Freehand Voxel Carving' if freehand else 'Volume Carving'
def compute(run_id):
 global result
 out=a.work/('run-'+time.strftime('%Y%m%d-%H%M%S')+'-'+str(time.time_ns()%1000000));started=time.monotonic();trace=[]
 try:
  out.mkdir()
  cmd=[str(a.binary.resolve()),str(a.dataset.resolve()),str(a.calibration.resolve()),str(out.resolve())]
  with (out/'native.log').open('w') as log:
   process=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
   for line in process.stdout:
    log.write(line);log.flush()
    if line.startswith('VIEW '):
     _,view,raw,observed=line.split();row={'view':int(view),'raw_voxels':int(raw),'observed_voxels':int(observed)};trace.append(row)
     with lock:state.update(row,status=f'Computed view {view} / 36 in native C++')
   code=process.wait()
  if code:raise RuntimeError(f'native replay exited {code}; see native.log')
  metrics=json.loads((out/'run-result.json').read_text())
  if metrics.get('completed') is not True or metrics.get('native_views')!=36:raise RuntimeError('native completion record failed validation')
  metrics.update(run_id=run_id,elapsed_seconds=time.monotonic()-started,platform=platform.platform(),native_binary_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),positions_sha256=hashlib.sha256((out/'positions.f32').read_bytes()).hexdigest(),colors_sha256=hashlib.sha256((out/'colors.rgba').read_bytes()).hexdigest(),new_frontend='localhost browser UI starts native C ABI replay',per_view_native_trace=trace)
  (out/'desktop-result.json').write_text(json.dumps(metrics,indent=2)+'\n')
  with lock:result=out;state.update(running=False,complete=True,status='Native computation complete; drag the computed result to rotate.',metrics=metrics)
 except Exception as error:
  with lock:state.update(running=False,complete=False,status='Native execution failed: '+str(error))
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,data,content='application/json',status=200):
  if isinstance(data,(dict,list)):data=json.dumps(data).encode()
  self.send_response(status);self.send_header('Content-Type',content);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
 def allowed(self):return self.headers.get('Host') in {f'127.0.0.1:{a.port}',f'localhost:{a.port}'}
 def do_GET(self):
  if not self.allowed():return self.send({'error':'local host required'},status=403)
  route=urlsplit(self.path).path
  if route=='/':return self.send(Path(__file__).with_name('index.html').read_bytes(),'text/html; charset=utf-8')
  if route=='/status':
   with lock:payload=dict(state)
   payload.update(project=title,freehand=freehand,platform=host)
   return self.send(payload)
  if route.startswith('/photo/'):
   try:
    view=int(route.split('/')[-1]);assert 1<=view<=36
    return self.send((a.dataset/'pictures'/f'viff.{view}.png').read_bytes(),'image/png')
   except (ValueError,AssertionError,FileNotFoundError):return self.send({'error':'unknown fixture view'},status=404)
  if route in ['/result/positions.f32','/result/colors.rgba','/result/run-result.json']:
   with lock:folder=result if state.get('complete') else None
   if folder:return self.send((folder/route.rsplit('/',1)[-1]).read_bytes(),'application/octet-stream' if not route.endswith('.json') else 'application/json')
  return self.send({'error':'not found'},status=404)
 def do_POST(self):
  global result
  if not self.allowed() or self.headers.get('Origin')!=f'http://{self.headers.get("Host")}':return self.send({'error':'same-origin local request required'},status=403)
  if self.path!='/run' or int(self.headers.get('Content-Length','0'))>64:return self.send({'error':'invalid request'},status=400)
  with lock:
   if state['running']:return self.send({'error':'run already active'},status=409)
   result=None;run_id=str(time.time_ns());state.clear();state.update(running=True,complete=False,view=0,run_id=run_id,status='Starting actual native C++ replay…')
  threading.Thread(target=compute,args=(run_id,),daemon=True).start();self.send({'started':True,'run_id':run_id})
print(f'{title}: http://127.0.0.1:{a.port}',flush=True)
ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
