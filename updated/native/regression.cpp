// New C-ABI regression: analytical one-vote prism and rejected-input atomicity.
#include "volume_carving.h"
#include <cmath>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>
void require(bool condition,const char *message){if(!condition)throw std::runtime_error(message);}
int main(){try{
 require(wvc_create(0,0,0,0)==nullptr,"invalid side accepted");
 WVCContext *c=wvc_create(128,0,0,0);require(c,"create failed");WVCStats before{};require(wvc_get_stats(c,&before)==0,"stats failed");require(before.raw_voxels==128u*128u*128u&&before.views==0,"initial grid incorrect");
 std::vector<uint8_t> mask(128*128,0);for(int y=0;y<128;++y)for(int x=32;x<96;++x)mask[y*128+x]=255;auto saved=mask;
 float p[12]={1,0,0,0,0,1,0,0,0,0,0,1};
 require(wvc_apply(c,p,mask.data(),mask.size()-1,128,128)==-1,"truncated mask accepted");
 WVCStats rejected{};wvc_get_stats(c,&rejected);require(rejected.occupancy_fnv1a64==before.occupancy_fnv1a64&&rejected.views==0,"invalid input changed state");
 float zero[12]={};require(wvc_apply(c,zero,mask.data(),mask.size(),128,128)==-1,"zero denominator accepted");
 require(wvc_apply(c,p,mask.data(),mask.size(),128,128)==0,"prism apply failed");require(mask==saved,"caller mask changed");
 WVCStats stats{};wvc_get_stats(c,&stats);require(stats.views==1&&stats.raw_voxels==64u*128u*128u&&stats.observed_voxels==stats.raw_voxels,"wrong prism occupancy");
 std::vector<uint8_t> packed(wvc_copy_occupancy(c,nullptr,0));wvc_copy_occupancy(c,packed.data(),packed.size());
 for(unsigned x=0;x<128;++x)for(unsigned y=0;y<128;++y)for(unsigned z=0;z<128;++z){bool actual=(packed[(size_t(x)*128+y)*16+(z>>3)]>>(z&7))&1;require(actual==(x>=32&&x<96),"packed analytic prism differs");}
 require(stats.observed_boundary_points==64u*128u*128u-62u*126u*126u,"boundary count incorrect");
 std::vector<WVCPoint> points(wvc_copy_observed_boundary(c,nullptr,0));require(wvc_copy_observed_boundary(c,points.data(),points.size())==points.size(),"boundary export size differs");
 for(const auto &point:points)require(std::isfinite(point.x)&&point.x>=32&&point.x<=95&&point.y>=0&&point.y<=127&&point.z>=0&&point.z<=127,"boundary coordinate out of bounds");
 require(wvc_apply(c,p,mask.data(),mask.size(),128,128)==0,"repeat apply failed");WVCStats twice{};wvc_get_stats(c,&twice);require(stats.occupancy_fnv1a64==twice.occupancy_fnv1a64,"idempotence failed");wvc_destroy(c);
 std::cout<<"PASS C ABI analytic128^3 prism, full packed occupancy, boundary export, repeatability, caller-buffer preservation and invalid-input atomicity\n";return 0;
}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
