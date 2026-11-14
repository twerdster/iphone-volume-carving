package org.awetzler.volumecarving.updated;
final class NativeBridge {
 static {System.loadLibrary("carving_android");}
 static native long create(float side,float x,float y,float z);
 static native void destroy(long handle);
 static native long[] apply(long handle,double[] projection,int[] rgba,int[] silhouette,int width,int height);
 static native long[] finish(long handle);
 static native Geometry geometry(long handle);
 static native byte[] occupancy(long handle);
 static final class Geometry {
  final float[] positions,normals;final byte[] colors;final boolean triangles;
  Geometry(float[] p,float[] n,byte[] c,boolean t){positions=p;normals=n;colors=c;triangles=t;}
 }
}
