// Updated Android JNI adapter; reconstruction remains in the recovered C++ operators.
#include <jni.h>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef WFC_FREEHAND
#include "freehand.h"
using Context=WFCContext;
#else
#include "volume_carving.h"
using Context=WVCContext;
#endif
namespace {
Context *context(jlong h){if(!h)throw std::runtime_error("closed native context");return reinterpret_cast<Context*>(h);}
void error(JNIEnv *e,const char *message){if(!e->ExceptionCheck()){auto t=e->FindClass("java/lang/IllegalStateException");if(t)e->ThrowNew(t,message);}}
jlongArray stats(JNIEnv *e,Context *c){
#ifdef WFC_FREEHAND
 WFCStats s{};if(wfc_get_stats(c,&s))throw std::runtime_error(wfc_last_error(c));
 jlong out[]={jlong(s.views),jlong(s.occupied_voxels),jlong(s.triangles),jlong(s.vertices),jlong(s.occupancy_fnv1a64)};
#else
 WVCStats s{};if(wvc_get_stats(c,&s))throw std::runtime_error(wvc_last_error(c));
 jlong out[]={jlong(s.views),jlong(s.raw_voxels),jlong(s.observed_voxels),jlong(s.observed_boundary_points),jlong(s.occupancy_fnv1a64)};
#endif
 auto a=e->NewLongArray(5);if(a)e->SetLongArrayRegion(a,0,5,out);return a;
}
}
#define METHOD(n) Java_org_awetzler_volumecarving_updated_NativeBridge_##n
#define NULL_CATCH catch(const std::exception &x){error(e,x.what());return nullptr;}catch(...){error(e,"unknown native failure");return nullptr;}
extern "C" JNIEXPORT jlong JNICALL METHOD(create)(JNIEnv *e,jclass,jfloat side,jfloat x,jfloat y,jfloat z){try{
#ifdef WFC_FREEHAND
 auto *c=wfc_create(side,x,y,z);
#else
 auto *c=wvc_create(side,x,y,z);
#endif
 if(!c)throw std::runtime_error("native context creation failed");return reinterpret_cast<jlong>(c);
}catch(const std::exception &x){error(e,x.what());return 0;}catch(...){error(e,"unknown native failure");return 0;}}
extern "C" JNIEXPORT void JNICALL METHOD(destroy)(JNIEnv *,jclass,jlong h){
#ifdef WFC_FREEHAND
 wfc_destroy(reinterpret_cast<Context*>(h));
#else
 wvc_destroy(reinterpret_cast<Context*>(h));
#endif
}
extern "C" JNIEXPORT jlongArray JNICALL METHOD(apply)(JNIEnv *e,jclass,jlong h,jdoubleArray projection,jintArray image,jintArray mask,jint width,jint height){try{
 if(width<=0||height<=0||width>4096||height>4096||!projection||!image||!mask||e->GetArrayLength(projection)!=12||e->GetArrayLength(image)!=width*height||e->GetArrayLength(mask)!=width*height)throw std::invalid_argument("exact camera/image/mask dimensions required");
 auto *c=context(h);double p[12];e->GetDoubleArrayRegion(projection,0,12,p);
 std::vector<jint> argb(size_t(width)*height),silhouette(argb.size());e->GetIntArrayRegion(image,0,argb.size(),argb.data());e->GetIntArrayRegion(mask,0,silhouette.size(),silhouette.data());
 if(e->ExceptionCheck())return nullptr;
 std::vector<uint8_t> rgba(argb.size()*4),bits(argb.size());
 for(size_t i=0;i<argb.size();++i){uint32_t a=argb[i],m=silhouette[i];rgba[4*i]=a>>16;rgba[4*i+1]=a>>8;rgba[4*i+2]=a;rgba[4*i+3]=a>>24;unsigned r=(m>>16)&255,g=(m>>8)&255,b=m&255;bits[i]=((299*r+587*g+114*b+500)/1000)?255:0;}
#ifdef WFC_FREEHAND
 float rt[12];if(wfc_dinosaur_rt(p,rt)||wfc_apply(c,p,rt,rgba.data(),rgba.size(),bits.data(),bits.size(),width,height))throw std::runtime_error(wfc_last_error(c));
#else
 float pf[12];for(int i=0;i<12;++i)pf[i]=float(p[i]);if(wvc_apply(c,pf,bits.data(),bits.size(),width,height))throw std::runtime_error(wvc_last_error(c));
#endif
 return stats(e,c);
}NULL_CATCH}
extern "C" JNIEXPORT jlongArray JNICALL METHOD(finish)(JNIEnv *e,jclass,jlong h){try{auto *c=context(h);
#ifdef WFC_FREEHAND
 if(wfc_make_mesh(c))throw std::runtime_error(wfc_last_error(c));
#endif
 return stats(e,c);
}NULL_CATCH}
extern "C" JNIEXPORT jobject JNICALL METHOD(geometry)(JNIEnv *e,jclass,jlong h){try{
 auto *c=context(h);std::vector<float> pos,normals;std::vector<uint8_t> colors;bool triangles=false;
#ifdef WFC_FREEHAND
 triangles=true;pos.resize(wfc_copy_positions(c,nullptr,0));normals.resize(wfc_copy_normals(c,nullptr,0));colors.resize(wfc_copy_colors(c,nullptr,0));
 wfc_copy_positions(c,pos.data(),pos.size());wfc_copy_normals(c,normals.data(),normals.size());wfc_copy_colors(c,colors.data(),colors.size());
#else
 std::vector<WVCPoint> points(wvc_copy_observed_boundary(c,nullptr,0));wvc_copy_observed_boundary(c,points.data(),points.size());pos.reserve(points.size()*3);for(auto &p:points){pos.push_back(p.x);pos.push_back(p.y);pos.push_back(p.z);}
#endif
 auto p=e->NewFloatArray(pos.size()),n=e->NewFloatArray(normals.size());auto color=e->NewByteArray(colors.size());if(!p||!n||!color)return nullptr;
 e->SetFloatArrayRegion(p,0,pos.size(),pos.data());e->SetFloatArrayRegion(n,0,normals.size(),normals.data());e->SetByteArrayRegion(color,0,colors.size(),reinterpret_cast<const jbyte*>(colors.data()));
 auto type=e->FindClass("org/awetzler/volumecarving/updated/NativeBridge$Geometry");if(!type)return nullptr;auto ctor=e->GetMethodID(type,"<init>","([F[F[BZ)V");if(!ctor)return nullptr;return e->NewObject(type,ctor,p,n,color,jboolean(triangles));
}NULL_CATCH}
extern "C" JNIEXPORT jbyteArray JNICALL METHOD(occupancy)(JNIEnv *e,jclass,jlong h){try{
#ifdef WFC_FREEHAND
 return e->NewByteArray(0);
#else
 auto *c=context(h);std::vector<uint8_t> bytes(wvc_copy_occupancy(c,nullptr,0));wvc_copy_occupancy(c,bytes.data(),bytes.size());auto a=e->NewByteArray(bytes.size());if(a)e->SetByteArrayRegion(a,0,bytes.size(),reinterpret_cast<const jbyte*>(bytes.data()));return a;
#endif
}NULL_CATCH}
