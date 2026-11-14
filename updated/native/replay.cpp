// New portable host replay of the C ABI; actual reconstruction stays in core.
#include <png.h>
#include <sys/stat.h>
#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>
#include <cstdlib>
#include <cmath>
#include <cctype>
#include <iomanip>
#if PROJECT_FREEHAND
#include "freehand.h"
#else
#include "volume_carving.h"
#endif
void require(bool condition,const std::string &message){if(!condition)throw std::runtime_error(message);}
std::vector<uint8_t> rgba(const std::string &path){png_image input{};input.version=PNG_IMAGE_VERSION;require(png_image_begin_read_from_file(&input,path.c_str()),"cannot read "+path);input.format=PNG_FORMAT_RGBA;require(input.width==720&&input.height==576,"expected720x576fixture");std::vector<uint8_t> pixels(PNG_IMAGE_SIZE(input));bool ok=png_image_finish_read(&input,nullptr,pixels.data(),0,nullptr);png_image_free(&input);require(ok,"PNG decode failed");return pixels;}
std::vector<double> matrices(const std::string &path){std::ifstream in(path);std::string text((std::istreambuf_iterator<char>(in)),{});auto key=text.find("\"projection_matrices\"");require(key!=std::string::npos,"missing calibration matrices");const char *cursor=text.c_str()+text.find('[',key);std::vector<double> result;for(unsigned i=0;i<432;++i){while(*cursor&&(*cursor=='['||*cursor==']'||*cursor==','||std::isspace(static_cast<unsigned char>(*cursor))))++cursor;char *end=nullptr;double value=std::strtod(cursor,&end);require(end!=cursor&&std::isfinite(value),"malformed calibration matrix");result.push_back(value);cursor=end;}return result;}
template<class T>void binary(const std::string &path,const std::vector<T>&values){std::ofstream f(path,std::ios::binary);f.write(reinterpret_cast<const char*>(values.data()),values.size()*sizeof(T));f.close();require(bool(f),"cannot write "+path);}
int main(int argc,char **argv){try{
 require(argc==4,"usage: native_replay DATASET CALIBRATION_JSON OUTPUT_DIRECTORY");const std::string data=argv[1],output=argv[3];mkdir(output.c_str(),0755);const auto cameras=matrices(argv[2]);std::vector<unsigned> counts;std::vector<float> positions;std::vector<uint8_t> colors;
#if PROJECT_FREEHAND
 WFCContext *context=wfc_create(.2463f,-.1307f,-.1307f,-.7483f);
#else
 WVCContext *context=wvc_create(.2463f,-.1307f,-.1307f,-.7483f);
#endif
 require(context,"cannot allocate native context");
 for(unsigned view=0;view<36;++view){auto image=rgba(data+"/pictures/viff."+std::to_string(view+1)+".png"),maskRGBA=rgba(data+"/silhouettes/sil_"+std::to_string(view+1)+".png");std::vector<uint8_t> mask(maskRGBA.size()/4);for(size_t i=0;i<mask.size();++i)mask[i]=maskRGBA[i*4+1];const double *p=cameras.data()+view*12;unsigned raw=0,observed=0;
#if PROJECT_FREEHAND
 float rt[12];require(wfc_dinosaur_rt(p,rt)==0,"fixture rt calculation failed");require(wfc_apply(context,p,rt,image.data(),image.size(),mask.data(),mask.size(),720,576)==0,wfc_last_error(context));WFCStats stats{};wfc_get_stats(context,&stats);raw=observed=stats.occupied_voxels;
#else
 float pf[12];for(unsigned i=0;i<12;++i)pf[i]=float(p[i]);require(wvc_apply(context,pf,mask.data(),mask.size(),720,576)==0,wvc_last_error(context));WVCStats stats{};wvc_get_stats(context,&stats);raw=stats.raw_voxels;observed=stats.observed_voxels;
#endif
 counts.push_back(raw);std::cout<<"VIEW "<<view+1<<' '<<raw<<' '<<observed<<std::endl;
 }
 unsigned raw=0,observed=0,triangles=0;uint64_t hash=0;
#if PROJECT_FREEHAND
 require(wfc_make_mesh(context)>0,wfc_last_error(context));WFCStats stats{};wfc_get_stats(context,&stats);raw=observed=stats.occupied_voxels;triangles=stats.triangles;hash=stats.occupancy_fnv1a64;positions.resize(wfc_copy_positions(context,nullptr,0));wfc_copy_positions(context,positions.data(),positions.size());for(float &v:positions)v/=64.f;colors.resize(wfc_copy_colors(context,nullptr,0));wfc_copy_colors(context,colors.data(),colors.size());wfc_destroy(context);require(raw==22377&&triangles==25200,"native C ABI result differs from historical-matrix reference counts");
#else
 WVCStats stats{};wvc_get_stats(context,&stats);raw=stats.raw_voxels;observed=stats.observed_voxels;hash=stats.occupancy_fnv1a64;std::vector<WVCPoint> points(wvc_copy_observed_boundary(context,nullptr,0));wvc_copy_observed_boundary(context,points.data(),points.size());for(const auto &p:points){positions.insert(positions.end(),{(p.x+.1307f)/.2463f*2-1,(p.y+.1307f)/.2463f*2-1,-((p.z+.7483f)/.2463f*2-1)});colors.insert(colors.end(),{50,215,206,255});}std::vector<uint8_t> packed(wvc_copy_occupancy(context,nullptr,0));wvc_copy_occupancy(context,packed.data(),packed.size());binary(output+"/occupancy.bin",packed);wvc_destroy(context);require(raw==27310&&observed==21480&&positions.size()/3==6415,"native C ABI result differs from reference counts");
#endif
 for(float coordinate:positions)require(std::isfinite(coordinate),"computed geometry is nonfinite");require(colors.size()==positions.size()/3*4,"geometry/color array lengths disagree");
#if PROJECT_FREEHAND
 require(hash==UINT64_C(0x803e245304c9b374),"Freehand occupancy hash differs from fixed-fixture baseline");
#else
 require(hash==UINT64_C(0xbc1847c8e8264d3f),"Volume occupancy hash differs from fixed-fixture baseline");
#endif
 binary(output+"/positions.f32",positions);binary(output+"/colors.rgba",colors);std::ofstream metrics(output+"/run-result.json");metrics<<"{\"completed\":true,\"native_views\":36,\"raw_voxels\":"<<raw<<",\"observed_voxels\":"<<observed<<",\"triangles\":"<<triangles<<",\"rendered_vertices\":"<<positions.size()/3<<",\"occupancy_fnv1a64\":\""<<std::hex<<std::setw(16)<<std::setfill('0')<<hash<<std::dec<<"\",\"occupancy_after_each_view\":[";for(size_t i=0;i<counts.size();++i){if(i)metrics<<',';metrics<<counts[i];}metrics<<"],\"input\":\"36 real dinosaur masks/photos; supplied rounded cameras\",\"camera_capture\":false,\"pose_tracking\":false}"<<std::endl;metrics.close();require(bool(metrics),"cannot write/close completion marker");std::cout<<"COMPLETE "<<raw<<' '<<observed<<' '<<triangles<<' '<<positions.size()/3<<std::endl;return 0;
}catch(const std::exception &e){std::cerr<<"ERROR "<<e.what()<<std::endl;return 1;}}
