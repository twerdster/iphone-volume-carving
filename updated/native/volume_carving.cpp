// New platform interface. All carving is the unchanged original Sculptor<128>.
#include "volume_carving.h"
#include <cmath>
#include <cstring>
#include <limits>
#include <memory>
#include <string>
#include <vector>
#include "Sculptor.h"

namespace {
constexpr unsigned kSize=128;
constexpr size_t kCells=size_t(kSize)*kSize*kSize;
constexpr size_t kBytes=kCells/8;
struct Probe final : Sculptor<kSize> {
    Probe(float side,float x,float y,float z):Sculptor<kSize>(side,Vector3D(x,y,z)){}
    bool on(unsigned x,unsigned y,unsigned z) const {
        return (sculpture[x][y][z>>3] & (1u<<(z&7)))!=0;
    }
    const unsigned char *packed() const {return &sculpture[0][0][0];}
};
size_t index(unsigned x,unsigned y,unsigned z){return (size_t(x)*kSize+y)*kSize+z;}
}
struct WVCContext {
    std::unique_ptr<Probe> core;
    float side,corner[3];
    uint32_t views=0;
    std::vector<uint8_t> observed;
    std::string error;
    WVCContext(float s,float x,float y,float z):core(new Probe(s,x,y,z)),side(s),corner{x,y,z},observed(kCells,0){}
    bool filtered(unsigned x,unsigned y,unsigned z) const {return core->on(x,y,z)&&observed[index(x,y,z)];}
    bool boundary(unsigned x,unsigned y,unsigned z) const {
        return filtered(x,y,z)&&(x==0||y==0||z==0||x==kSize-1||y==kSize-1||z==kSize-1||
            !filtered(x-1,y,z)||!filtered(x+1,y,z)||!filtered(x,y-1,z)||!filtered(x,y+1,z)||!filtered(x,y,z-1)||!filtered(x,y,z+1));
    }
};
extern "C" {
WVCContext *wvc_create(float side,float x,float y,float z){
    if(!std::isfinite(side)||side<=0||!std::isfinite(x)||!std::isfinite(y)||!std::isfinite(z))return nullptr;
    try{return new WVCContext(side,x,y,z);}catch(...){return nullptr;}
}
void wvc_destroy(WVCContext *c){delete c;}
int wvc_apply(WVCContext *c,const float *p,const uint8_t *mask,size_t bytes,uint32_t width,uint32_t height){
    if(!c)return -1;
    c->error.clear();
    if(!p||!mask||width==0||height==0||width>4096||height>4096||bytes!=size_t(width)*height){c->error="invalid projection, dimensions or exact mask byte count";return -1;}
    for(unsigned i=0;i<12;++i)if(!std::isfinite(p[i])){c->error="nonfinite camera coefficient";return -1;}
    try{
        std::vector<uint8_t> seen(kCells,0);
        const float step=c->side/kSize;
        // Match the original float32 multiply/add order and truncating pixel
        // conversion. Also reject undefined original conversions before carving.
        for(unsigned x=0;x<kSize;++x)for(unsigned y=0;y<kSize;++y)for(unsigned z=0;z<kSize;++z){
            const float wx=x*step+c->corner[0],wy=y*step+c->corner[1],wz=z*step+c->corner[2];
            const float denominator=((wx*p[8]+wy*p[9])+wz*p[10])+p[11];
            const float u=(((wx*p[0]+wy*p[1])+wz*p[2])+p[3])/denominator;
            const float v=(((wx*p[4]+wy*p[5])+wz*p[6])+p[7])/denominator;
            if(!std::isfinite(u)||!std::isfinite(v)||double(u)<std::numeric_limits<int>::min()||double(u)>std::numeric_limits<int>::max()||double(v)<std::numeric_limits<int>::min()||double(v)>std::numeric_limits<int>::max()){
                c->error="projection yields nonfinite or out-of-int-range pixel coordinates";return -1;
            }
            int px=int(u),py=int(v);seen[index(x,y,z)]=px>=0&&py>=0&&uint32_t(px)<width&&uint32_t(py)<height;
        }
        std::unique_ptr<unsigned char[]> privateMask(new unsigned char[bytes]);
        for(size_t i=0;i<bytes;++i)privateMask[i]=mask[i]?255:0;
        SculptData data;std::memcpy(data.projection,p,12*sizeof(float));data.sizeXmap=width;data.sizeYmap=height;data.map=privateMask.get();
        c->core->Sculp(&data,ACCURATE);
        for(size_t i=0;i<kCells;++i)c->observed[i]|=seen[i];
        ++c->views;return 0;
    }catch(const std::exception &e){c->error=e.what();return -1;}catch(...){c->error="native adapter failed";return -1;}
}
int wvc_get_stats(const WVCContext *c,WVCStats *stats){
    if(!c||!stats)return -1;
    WVCStats result{};result.views=c->views;result.occupancy_fnv1a64=UINT64_C(14695981039346656037);
    for(size_t i=0;i<kBytes;++i){result.occupancy_fnv1a64^=c->core->packed()[i];result.occupancy_fnv1a64*=UINT64_C(1099511628211);}
    for(unsigned x=0;x<kSize;++x)for(unsigned y=0;y<kSize;++y)for(unsigned z=0;z<kSize;++z){result.raw_voxels+=c->core->on(x,y,z);result.observed_voxels+=c->filtered(x,y,z);result.observed_boundary_points+=c->boundary(x,y,z);}
    *stats=result;return 0;
}
size_t wvc_copy_occupancy(const WVCContext *c,uint8_t *output,size_t capacity){
    if(!c)return 0;if(output&&capacity>=kBytes)std::memcpy(output,c->core->packed(),kBytes);return kBytes;
}
size_t wvc_copy_observed_boundary(const WVCContext *c,WVCPoint *output,size_t capacity){
    if(!c)return 0;size_t count=0;
    for(unsigned x=0;x<kSize;++x)for(unsigned y=0;y<kSize;++y)for(unsigned z=0;z<kSize;++z)count+=c->boundary(x,y,z);
    if(!output||capacity<count)return count;
    size_t at=0;const float step=c->side/kSize;
    for(unsigned x=0;x<kSize;++x)for(unsigned y=0;y<kSize;++y)for(unsigned z=0;z<kSize;++z)if(c->boundary(x,y,z))output[at++]={x*step+c->corner[0],y*step+c->corner[1],z*step+c->corner[2]};
    return count;
}
const char *wvc_last_error(const WVCContext *c){return c?c->error.c_str():"null native carving context";}
}
