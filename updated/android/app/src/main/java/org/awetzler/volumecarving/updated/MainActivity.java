package org.awetzler.volumecarving.updated;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/** A fresh reconstruction is performed by the native C ABI for each Run. */
public final class MainActivity extends Activity {
 private static final boolean FREEHAND=false;
 private static final String TITLE="Volume Carving";
 private final Handler main=new Handler(Looper.getMainLooper());
 // Activity recreation must not overlap native runs or shared output publication.
 private static final ExecutorService worker=Executors.newSingleThreadExecutor();
 private static final AtomicBoolean nativeRunOwned=new AtomicBoolean(false);
 private volatile boolean closed;
 private boolean running;
 private GeometryView geometry;
 private ImageView photo,mask;
 private ProgressBar progress;
 private TextView status,counts;
 private Button run;
 @Override public void onCreate(Bundle saved){super.onCreate(saved);
  ScrollView scroll=new ScrollView(this);LinearLayout column=new LinearLayout(this);column.setOrientation(LinearLayout.VERTICAL);column.setPadding(dp(14),dp(10),dp(14),dp(14));scroll.addView(column);
  column.addView(label(TITLE+" · updated",23));column.addView(label(FREEHAND?"Recovered carving → marching cubes → vertex colors":"Recovered Sculptor<128> → observed boundary samples",13));
  LinearLayout inputs=new LinearLayout(this);photo=new ImageView(this);photo.setId(R.id.photo);mask=new ImageView(this);mask.setId(R.id.mask);photo.setScaleType(ImageView.ScaleType.FIT_CENTER);mask.setScaleType(ImageView.ScaleType.FIT_CENTER);photo.setContentDescription("Current dinosaur photograph");mask.setContentDescription("Current supplied silhouette");inputs.addView(photo,new LinearLayout.LayoutParams(0,dp(112),1));inputs.addView(mask,new LinearLayout.LayoutParams(0,dp(112),1));column.addView(inputs);
  status=label("Ready · 36 calibrated dinosaur views",15);status.setId(R.id.status);column.addView(status);
  progress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);progress.setId(R.id.progress);progress.setMax(36);column.addView(progress,new LinearLayout.LayoutParams(-1,dp(16)));
  geometry=new GeometryView(this);geometry.setId(R.id.geometry);column.addView(geometry,new LinearLayout.LayoutParams(-1,dp(260)));
  column.addView(label(FREEHAND?"Computed colored triangles · drag to rotate, pinch to zoom":"Computed boundary points · display color by height · drag / pinch",12));
  counts=label("Native counts appear after each input view.\nComputed output appears after view 36.",14);counts.setId(R.id.counts);counts.setTypeface(android.graphics.Typeface.MONOSPACE);counts.setMinLines(4);column.addView(counts);
  LinearLayout buttons=new LinearLayout(this);run=new Button(this);run.setId(R.id.run);run.setText("Run 36 views");buttons.addView(run,new LinearLayout.LayoutParams(0,dp(50),1));Button reset=new Button(this);reset.setId(R.id.reset_view);reset.setText("Reset view");buttons.addView(reset,new LinearLayout.LayoutParams(0,dp(50),1));column.addView(buttons);reset.setOnClickListener(v->geometry.resetView());run.setOnClickListener(v->startRun());
  Switch rotate=new Switch(this);rotate.setId(R.id.auto_rotate);rotate.setText("Rotate computed output");rotate.setOnCheckedChangeListener((v,on)->geometry.setAutoRotate(on));column.addView(rotate,new LinearLayout.LayoutParams(-1,dp(44)));
  column.addView(label("Input: Wolfgang Niem / Hannover dinosaur, via Oxford VGG and Ben Tordoff’s example. "
   +"Rounded historical demoP calibration. Supplied masks; no camera or pose estimation. Input-view consistency is not independent 3D accuracy.",12));
  Button credits=new Button(this);credits.setId(R.id.credits);credits.setText("Credits, limits and notices");credits.setOnClickListener(v->showCredits());column.addView(credits);setContentView(scroll);
  if(getIntent().getBooleanExtra("autoRun",false))main.postDelayed(this::startRun,350);
 }
 private TextView label(String s,int size){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(android.graphics.Color.rgb(25,49,61));t.setPadding(0,dp(3),0,dp(3));return t;}
 private int dp(int value){return Math.round(value*getResources().getDisplayMetrics().density);}
 private void startRun(){if(running||closed)return;if(!nativeRunOwned.compareAndSet(false,true)){status.setText("Previous Activity is finishing native cleanup; retrying…");main.postDelayed(this::startRun,300);return;}running=true;run.setEnabled(false);status.setText("Starting fresh native reconstruction…");progress.setProgress(0);geometry.setGeometry(new NativeBridge.Geometry(new float[0],new float[0],new byte[0],FREEHAND));worker.execute(this::reconstruct);}
 private byte[] asset(String name)throws Exception{try(InputStream in=getAssets().open(name);ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] block=new byte[65536];int n;while((n=in.read(block))!=-1)out.write(block,0,n);return out.toByteArray();}}
 private Bitmap bitmap(String name)throws Exception{byte[] bytes=asset(name);BitmapFactory.Options opts=new BitmapFactory.Options();opts.inScaled=false;opts.inPreferredConfig=Bitmap.Config.ARGB_8888;Bitmap b=BitmapFactory.decodeByteArray(bytes,0,bytes.length,opts);if(b==null||b.getWidth()!=720||b.getHeight()!=576)throw new IllegalStateException("expected 720×576 PNG: "+name);return b;}
 private static String hex(byte[] bytes){StringBuilder out=new StringBuilder();for(byte b:bytes)out.append(String.format(Locale.US,"%02x",b&255));return out.toString();}
 private static String hash(byte[] bytes)throws Exception{return hex(MessageDigest.getInstance("SHA-256").digest(bytes));}
 private static byte[] rgba(int[] argb){byte[] out=new byte[argb.length*4];for(int i=0;i<argb.length;i++){out[4*i]=(byte)(argb[i]>>16);out[4*i+1]=(byte)(argb[i]>>8);out[4*i+2]=(byte)argb[i];out[4*i+3]=(byte)(argb[i]>>24);}return out;}
 private static byte[] binaryMask(int[] pixels){byte[] out=new byte[pixels.length];for(int i=0;i<pixels.length;i++){int a=pixels[i],r=(a>>16)&255,g=(a>>8)&255,b=a&255;out[i]=(byte)(((299*r+587*g+114*b+500)/1000)>0?255:0);}return out;}
 private static byte[] floats(float[] values){ByteBuffer b=ByteBuffer.allocate(values.length*4).order(ByteOrder.LITTLE_ENDIAN);for(float v:values)b.putFloat(v);return b.array();}
 private void atomic(File destination,byte[] bytes)throws Exception{File temp=File.createTempFile(destination.getName()+".",".tmp",destination.getParentFile());try(FileOutputStream out=new FileOutputStream(temp)){out.write(bytes);out.getFD().sync();}if(!temp.renameTo(destination))throw new IllegalStateException("cannot publish "+destination.getName());}
 private JSONObject save(File dir,String filename,byte[] bytes)throws Exception{atomic(new File(dir,filename),bytes);JSONObject j=new JSONObject();j.put("file",filename);j.put("bytes",bytes.length);j.put("sha256",hash(bytes));return j;}
 private JSONObject stats(long[] s)throws Exception{JSONObject j=new JSONObject();j.put("views",s[0]);j.put(FREEHAND?"occupied_voxels":"raw_voxels",s[1]);j.put(FREEHAND?"triangles":"observed_voxels",s[2]);j.put(FREEHAND?"vertices":"observed_boundary_points",s[3]);j.put("occupancy_fnv1a64",String.format(Locale.US,"%016x",s[4]));return j;}
 private void reconstruct(){long handle=0;File dir=new File(getFilesDir(),"reconstruction");try{
  if(!dir.isDirectory()&&!dir.mkdirs())throw new IllegalStateException("cannot create output directory");File completed=new File(dir,"run-result.json");if(completed.exists()&&!completed.delete())throw new IllegalStateException("cannot invalidate old completion record");
  byte[] calibrationBytes=asset("calibration.json"),manifestBytes=asset("input-manifest.json");JSONObject calibration=new JSONObject(new String(calibrationBytes,StandardCharsets.UTF_8));JSONArray corner=calibration.getJSONArray("cube_corner"),matrices=calibration.getJSONArray("projection_matrices");if(matrices.length()!=36)throw new IllegalStateException("36 calibrated views required");
  handle=NativeBridge.create((float)calibration.getDouble("cube_side"),(float)corner.getDouble(0),(float)corner.getDouble(1),(float)corner.getDouble(2));if(handle==0)throw new IllegalStateException("native create failed");
  JSONArray trace=new JSONArray();long start=SystemClock.elapsedRealtime();long[] current=null;
  for(int i=0;i<36;i++){
   if(closed)throw new InterruptedException("activity closed");final int view=i+1;
   Bitmap photograph=bitmap("pictures/viff."+view+".png"),silhouette=bitmap("silhouettes/sil_"+view+".png");int[] pixels=new int[720*576],masks=new int[pixels.length];photograph.getPixels(pixels,0,720,0,0,720,576);silhouette.getPixels(masks,0,720,0,0,720,576);
   double[] p=new double[12];JSONArray row=matrices.getJSONArray(i);for(int k=0;k<12;k++)p[k]=row.getDouble(k);
   long begin=SystemClock.elapsedRealtimeNanos();current=NativeBridge.apply(handle,p,pixels,masks,720,576);double millis=(SystemClock.elapsedRealtimeNanos()-begin)/1e6;
   if(current==null||current.length!=5||current[0]!=view)throw new IllegalStateException("native progress mismatch");JSONObject record=stats(current);record.put("native_apply_and_stats_ms",millis);record.put("decoded_rgba_sha256",hash(rgba(pixels)));record.put("decoded_binary_mask_sha256",hash(binaryMask(masks)));trace.put(record);atomic(new File(dir,"progress.json"),record.toString(2).getBytes(StandardCharsets.UTF_8));
   Log.i("CarvingRuntime",record.toString());final long[] display=current.clone();main.post(()->{if(closed)return;photo.setImageBitmap(photograph);mask.setImageBitmap(silhouette);progress.setProgress(view);status.setText("View "+view+" / 36 computed by recovered native core");showCounts(display,millis);});
  }
  main.post(()->{if(!closed)status.setText(FREEHAND?"Extracting recovered marching-cubes mesh and colors…":"Extracting observed boundary samples…");});
  if(closed)throw new InterruptedException("activity closed before extraction");
  current=NativeBridge.finish(handle);NativeBridge.Geometry result=NativeBridge.geometry(handle);validate(result,current);
  if(closed)throw new InterruptedException("activity closed before saving outputs");
  JSONObject outputs=new JSONObject();outputs.put("positions",save(dir,"positions.f32le",floats(result.positions)));outputs.put("normals",save(dir,"normals.f32le",floats(result.normals)));outputs.put("colors",save(dir,"colors.rgba8",result.colors));byte[] occupancy=NativeBridge.occupancy(handle);if(occupancy.length>0)outputs.put("raw_occupancy",save(dir,"occupancy.bin",occupancy));
  JSONObject done=stats(current);done.put("status","complete");done.put("implementation",FREEHAND?"recovered Sculpture carve + createMesh + recovered colors":"unchanged recovered Sculptor<128> ACCURATE + separate observed boundary output filter");done.put("geometry_type",FREEHAND?"colored triangles":"observed boundary points; height color is display only");done.put("grid_size",128);done.put("view_count",36);done.put("per_view",trace);done.put("outputs",outputs);done.put("calibration_asset_sha256",hash(calibrationBytes));done.put("input_manifest_sha256",hash(manifestBytes));done.put("elapsed_seconds",(SystemClock.elapsedRealtime()-start)/1000.0);done.put("elapsed_scope","PNG decode, native calls, statistics, extraction and output writes; not benchmark throughput");done.put("accuracy_scope","supplied historical data only; no independent 3D accuracy evaluation");
  // Completion is published last, after all output files and their hashes exist.
  if(closed)throw new InterruptedException("activity closed before completion publication");
  atomic(completed,done.toString(2).getBytes(StandardCharsets.UTF_8));Log.i("CarvingRuntime","COMPLETE "+done.toString());final long[] finalStats=current;
  main.post(()->{if(closed)return;geometry.setGeometry(result);status.setText("Complete · 36 views · computed "+(FREEHAND?"colored mesh":"boundary samples"));showCounts(finalStats,-1);running=false;run.setEnabled(true);run.setText("Recompute 36 views");});
 }catch(Throwable failure){Log.e("CarvingRuntime","reconstruction failed",failure);main.post(()->{if(closed)return;status.setText("Failed: "+failure.getClass().getSimpleName()+" · "+failure.getMessage());running=false;run.setEnabled(true);});}finally{try{if(handle!=0)NativeBridge.destroy(handle);}finally{nativeRunOwned.set(false);}}}
 private void validate(NativeBridge.Geometry g,long[] s){if(g==null||g.positions.length==0||g.positions.length%3!=0)throw new IllegalStateException("empty/invalid geometry");for(float v:g.positions)if(Float.isNaN(v)||Float.isInfinite(v))throw new IllegalStateException("nonfinite geometry");if(FREEHAND){if(!g.triangles||g.positions.length!=s[2]*9||g.normals.length!=g.positions.length||g.colors.length!=g.positions.length/3*4)throw new IllegalStateException("triangle/normal/color counts differ");}else if(g.triangles||g.positions.length!=s[3]*3)throw new IllegalStateException("boundary count differs");}
 private void showCounts(long[] s,double millis){counts.setText(String.format(Locale.US,FREEHAND?"Views %d / 36   occupied %,d\nTriangles %,d   vertices %,d\nOccupancy FNV %016x\n%s":"Views %d / 36   raw voxels %,d\nObserved %,d   boundary samples %,d\nOccupancy FNV %016x\n%s",s[0],s[1],s[2],s[3],s[4],millis<0?"Computed output: drag / pinch to inspect":String.format(Locale.US,"Native apply + stats %.1f ms",millis)));}
 private void showCredits(){String text=TITLE+" is an updated frontend for Aaron Wetzler. "+(FREEHAND?"Original project: Alex Fish, supervised by Aaron Wetzler, Yaron Honen and Ron Kimmel. The recovered carving, marching cubes and color routines run through prepared compatibility/repair copies. This is the historical demoP path, not live PointCloud capture.":"Original project: Sergey Kucher and Alex Povichuk, supervised by Aaron Wetzler. It calls the unchanged Sculptor<128> ACCURATE operator. The displayed boundary excludes cells whose projections never fall inside an input image; raw occupancy is retained. No triangle meshing or recovered texture is supplied.")+"\n\nDinosaur sequence: Wolfgang Niem, Hannover, via Oxford VGG (https://www.robots.ox.ac.uk/~vgg/data/mview/) and Ben Tordoff’s example in the Freehand archive. Existing terms/notices remain; no new blanket license is assigned.\n\n36 photographs, supplied silhouettes, rounded demoP cameras, 128³ grid. No camera or pose estimation. Supplied-view consistency does not establish independent 3D accuracy. The interactive geometry is computed during this run.\n\nOutputs and final completion record are under private files/reconstruction/. A partial run is not completion evidence.";new AlertDialog.Builder(this).setTitle("Credits and scope").setMessage(text).setPositiveButton("Close",null).setNeutralButton("Bundled notices",(d,w)->showNotices()).show();}
 private void showNotices(){try{ArrayList<String> files=new ArrayList<>();collect("licenses",files);new AlertDialog.Builder(this).setTitle("Notices").setItems(files.toArray(new String[0]),(d,which)->{try{TextView t=label(new String(asset(files.get(which)),StandardCharsets.UTF_8),12);t.setTextIsSelectable(true);ScrollView scroll=new ScrollView(this);scroll.addView(t);new AlertDialog.Builder(this).setTitle(files.get(which)).setView(scroll).setPositiveButton("Close",null).show();}catch(Exception e){Toast.makeText(this,e.toString(),Toast.LENGTH_LONG).show();}}).setPositiveButton("Close",null).show();}catch(Exception e){Toast.makeText(this,e.toString(),Toast.LENGTH_LONG).show();}}
 private void collect(String path,ArrayList<String> files)throws Exception{String[] names=getAssets().list(path);if(names==null||names.length==0){files.add(path);return;}for(String name:names)collect(path+"/"+name,files);}
 @Override protected void onNewIntent(Intent intent){super.onNewIntent(intent);setIntent(intent);if(intent.getBooleanExtra("autoRun",false))startRun();}
 @Override protected void onResume(){super.onResume();if(geometry!=null)geometry.onResume();}
 @Override protected void onPause(){if(geometry!=null)geometry.onPause();super.onPause();}
 @Override protected void onDestroy(){closed=true;main.removeCallbacksAndMessages(null);/* Process-wide FIFO remains alive for a replacement Activity. */super.onDestroy();}
}
