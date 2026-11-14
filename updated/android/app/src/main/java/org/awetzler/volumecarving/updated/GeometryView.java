package org.awetzler.volumecarving.updated;
import android.content.Context;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;
import android.opengl.Matrix;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/** GLES20 renders the computed native arrays; no stored geometry is loaded. */
final class GeometryView extends GLSurfaceView {
 private final Viewer renderer=new Viewer();
 private final ScaleGestureDetector scale;
 private float lastX,lastY;
 GeometryView(Context context){super(context);setEGLContextClientVersion(2);setRenderer(renderer);
  scale=new ScaleGestureDetector(context,new ScaleGestureDetector.SimpleOnScaleGestureListener(){
   @Override public boolean onScale(ScaleGestureDetector d){renderer.zoom=Math.max(.45f,Math.min(3f,renderer.zoom*d.getScaleFactor()));return true;}
  });setContentDescription("Computed native geometry. Drag to rotate, pinch to zoom.");}
 void setGeometry(NativeBridge.Geometry geometry){queueEvent(()->renderer.setGeometry(geometry));}
 void resetView(){renderer.yaw=20;renderer.pitch=-17;renderer.zoom=1;}
 void setAutoRotate(boolean enabled){renderer.auto=enabled;}
 @Override public boolean onTouchEvent(MotionEvent event){scale.onTouchEvent(event);
  if(event.getActionMasked()==MotionEvent.ACTION_DOWN){lastX=event.getX();lastY=event.getY();getParent().requestDisallowInterceptTouchEvent(true);return true;}
  if(event.getActionMasked()==MotionEvent.ACTION_MOVE){if(!scale.isInProgress()&&event.getPointerCount()==1){renderer.yaw+=(event.getX()-lastX)*.45f;renderer.pitch+=(event.getY()-lastY)*.45f;}lastX=event.getX();lastY=event.getY();return true;}
  if(event.getActionMasked()==MotionEvent.ACTION_UP||event.getActionMasked()==MotionEvent.ACTION_CANCEL){getParent().requestDisallowInterceptTouchEvent(false);performClick();return true;}return true;}
 @Override public boolean performClick(){super.performClick();return true;}
 private static final class Viewer implements Renderer {
  volatile float yaw=20,pitch=-17,zoom=1;volatile boolean auto=false;
  private FloatBuffer positions,colors,normals;private int count,program;private boolean triangles;
  private float aspect=1;private long lastTime;
  private final float[] projection=new float[16],view=new float[16],model=new float[16],mv=new float[16],mvp=new float[16];
  private NativeBridge.Geometry current;
  private FloatBuffer buffer(float[] values){FloatBuffer b=ByteBuffer.allocateDirect(values.length*4).order(ByteOrder.nativeOrder()).asFloatBuffer();b.put(values).position(0);return b;}
  void setGeometry(NativeBridge.Geometry g){current=g;count=g.positions.length/3;triangles=g.triangles;
   if(count==0){positions=colors=normals=null;return;}
   // Native grid Z is height. Freehand mesh vertices already negate grid Z.
   // Only display arrays change here; persisted native arrays remain untouched.
   float[] oriented=new float[g.positions.length];
   for(int i=0;i<count;i++){oriented[i*3]=g.positions[i*3+1];oriented[i*3+1]=(triangles?-1:1)*g.positions[i*3+2];oriented[i*3+2]=-g.positions[i*3];}
   float[] low={Float.POSITIVE_INFINITY,Float.POSITIVE_INFINITY,Float.POSITIVE_INFINITY},high={Float.NEGATIVE_INFINITY,Float.NEGATIVE_INFINITY,Float.NEGATIVE_INFINITY};
   for(int i=0;i<oriented.length;i++){int a=i%3;low[a]=Math.min(low[a],oriented[i]);high[a]=Math.max(high[a],oriented[i]);}
   float extent=Math.max(high[0]-low[0],Math.max(high[1]-low[1],high[2]-low[2]));if(!(extent>0))extent=1;
   float[] p=new float[g.positions.length],c=new float[count*4],n=new float[g.positions.length];
   for(int i=0;i<p.length;i++){int a=i%3;p[i]=(oriented[i]-(low[a]+high[a])*.5f)*1.8f/extent;}
   for(int i=0;i<count;i++){
    if(g.colors.length==count*4){for(int k=0;k<4;k++)c[i*4+k]=(g.colors[i*4+k]&255)/255f;}
    else{float t=(oriented[i*3+1]-low[1])/Math.max(1e-9f,high[1]-low[1]);c[i*4]=.15f+.3f*t;c[i*4+1]=.62f+.25f*t;c[i*4+2]=.78f;c[i*4+3]=1;}
   }
   // Derive lighting normals from displayed faces. Recovered normals are exported unchanged.
   if(triangles){for(int i=0;i+8<p.length;i+=9){float ax=p[i+3]-p[i],ay=p[i+4]-p[i+1],az=p[i+5]-p[i+2],bx=p[i+6]-p[i],by=p[i+7]-p[i+1],bz=p[i+8]-p[i+2];float nx=ay*bz-az*by,ny=az*bx-ax*bz,nz=ax*by-ay*bx;float len=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);if(len>0){nx/=len;ny/=len;nz/=len;}for(int j=0;j<3;j++){n[i+j*3]=nx;n[i+j*3+1]=ny;n[i+j*3+2]=nz;}}}
   positions=buffer(p);colors=buffer(c);normals=buffer(n);
  }
  private int shader(int kind,String source){int s=GLES20.glCreateShader(kind);GLES20.glShaderSource(s,source);GLES20.glCompileShader(s);int[] status=new int[1];GLES20.glGetShaderiv(s,GLES20.GL_COMPILE_STATUS,status,0);if(status[0]==0)throw new IllegalStateException(GLES20.glGetShaderInfoLog(s));return s;}
  @Override public void onSurfaceCreated(GL10 gl,EGLConfig config){
   int v=shader(GLES20.GL_VERTEX_SHADER,"attribute vec3 aPosition;attribute vec4 aColor;attribute vec3 aNormal;uniform mat4 uMVP;uniform mat4 uModel;uniform float uLit;varying vec4 vColor;void main(){gl_Position=uMVP*vec4(aPosition,1.0);gl_PointSize=3.5;vec3 n=normalize(mat3(uModel)*aNormal+vec3(0.00001));float light=0.45+0.55*abs(dot(n,normalize(vec3(0.3,0.7,1.0))));vColor=vec4(aColor.rgb*mix(1.0,light,uLit),1.0);}");
   int f=shader(GLES20.GL_FRAGMENT_SHADER,"precision mediump float;varying vec4 vColor;void main(){gl_FragColor=vColor;}");program=GLES20.glCreateProgram();GLES20.glAttachShader(program,v);GLES20.glAttachShader(program,f);GLES20.glLinkProgram(program);int[] linked=new int[1];GLES20.glGetProgramiv(program,GLES20.GL_LINK_STATUS,linked,0);if(linked[0]==0)throw new IllegalStateException(GLES20.glGetProgramInfoLog(program));
   GLES20.glEnable(GLES20.GL_DEPTH_TEST);GLES20.glDisable(GLES20.GL_CULL_FACE);GLES20.glClearColor(.055f,.10f,.14f,1);lastTime=System.nanoTime();if(current!=null)setGeometry(current);
  }
  @Override public void onSurfaceChanged(GL10 gl,int width,int height){GLES20.glViewport(0,0,width,height);aspect=(float)width/Math.max(1,height);}
  @Override public void onDrawFrame(GL10 gl){GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT|GLES20.GL_DEPTH_BUFFER_BIT);long now=System.nanoTime();if(auto)yaw+=(now-lastTime)*1e-9f*15;lastTime=now;if(positions==null||count==0)return;
   Matrix.perspectiveM(projection,0,45,aspect,.1f,20);Matrix.setLookAtM(view,0,0,0,3.2f/zoom,0,0,0,0,1,0);Matrix.setIdentityM(model,0);Matrix.rotateM(model,0,pitch,1,0,0);Matrix.rotateM(model,0,yaw,0,1,0);Matrix.multiplyMM(mv,0,view,0,model,0);Matrix.multiplyMM(mvp,0,projection,0,mv,0);GLES20.glUseProgram(program);
   GLES20.glUniformMatrix4fv(GLES20.glGetUniformLocation(program,"uMVP"),1,false,mvp,0);GLES20.glUniformMatrix4fv(GLES20.glGetUniformLocation(program,"uModel"),1,false,model,0);GLES20.glUniform1f(GLES20.glGetUniformLocation(program,"uLit"),triangles?1:0);
   int a=GLES20.glGetAttribLocation(program,"aPosition"),c=GLES20.glGetAttribLocation(program,"aColor"),n=GLES20.glGetAttribLocation(program,"aNormal");
   GLES20.glEnableVertexAttribArray(a);GLES20.glEnableVertexAttribArray(c);GLES20.glEnableVertexAttribArray(n);GLES20.glVertexAttribPointer(a,3,GLES20.GL_FLOAT,false,0,positions);GLES20.glVertexAttribPointer(c,4,GLES20.GL_FLOAT,false,0,colors);GLES20.glVertexAttribPointer(n,3,GLES20.GL_FLOAT,false,0,normals);GLES20.glDrawArrays(triangles?GLES20.GL_TRIANGLES:GLES20.GL_POINTS,0,count);GLES20.glDisableVertexAttribArray(a);GLES20.glDisableVertexAttribArray(c);GLES20.glDisableVertexAttribArray(n);
  }
 }
}
