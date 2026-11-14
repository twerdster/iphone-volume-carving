#include "DisplayColors.h"
// New 2026 UIKit/SceneKit frontend. Reconstructs from bundled inputs on-device.
#import <UIKit/UIKit.h>
#import <SceneKit/SceneKit.h>
#import <CommonCrypto/CommonDigest.h>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <cmath>
#if PROJECT_FREEHAND
#include "freehand.h"
#else
#include "volume_carving.h"
#endif
static std::vector<uint8_t> pixels(UIImage *image){
 if(!image.CGImage)throw std::runtime_error("Missing fixture image");
 size_t w=CGImageGetWidth(image.CGImage),h=CGImageGetHeight(image.CGImage);std::vector<uint8_t> data(w*h*4);
 CGColorSpaceRef space=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
 CGContextRef ctx=CGBitmapContextCreate(data.data(),w,h,8,w*4,space,kCGImageAlphaPremultipliedLast|kCGBitmapByteOrder32Big);CGColorSpaceRelease(space);
 if(!ctx)throw std::runtime_error("Cannot decode fixture RGBA");CGContextDrawImage(ctx,CGRectMake(0,0,w,h),image.CGImage);CGContextRelease(ctx);return data;
}
static NSString *sha256(NSData *data){unsigned char digest[CC_SHA256_DIGEST_LENGTH];CC_SHA256(data.bytes,(CC_LONG)data.length,digest);NSMutableString *text=[NSMutableString new];for(unsigned i=0;i<sizeof(digest);++i)[text appendFormat:@"%02x",digest[i]];return text;}
@interface NativeController:UIViewController
@property(nonatomic,strong)UILabel *status;
@property(nonatomic,strong)UILabel *scope;
@property(nonatomic,strong)UIImageView *input;
@property(nonatomic,strong)SCNView *sceneView;
@property(nonatomic,strong)UIProgressView *progress;
@property(nonatomic,strong)UIButton *runButton;
@property(nonatomic)BOOL running;
@end
@implementation NativeController
-(void)viewDidLoad{
 [super viewDidLoad];self.overrideUserInterfaceStyle=UIUserInterfaceStyleLight;self.view.backgroundColor=[UIColor colorWithRed:.94 green:.97 blue:.98 alpha:1];
 UIScrollView *scroll=[UIScrollView new];scroll.translatesAutoresizingMaskIntoConstraints=NO;[self.view addSubview:scroll];
 UIStackView *stack=[UIStackView new];stack.axis=UILayoutConstraintAxisVertical;stack.spacing=12;stack.translatesAutoresizingMaskIntoConstraints=NO;[scroll addSubview:stack];
 [NSLayoutConstraint activateConstraints:@[[scroll.topAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.topAnchor],[scroll.bottomAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.bottomAnchor],[scroll.leadingAnchor constraintEqualToAnchor:self.view.leadingAnchor],[scroll.trailingAnchor constraintEqualToAnchor:self.view.trailingAnchor],[stack.topAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.topAnchor constant:14],[stack.bottomAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.bottomAnchor constant:-20],[stack.leadingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.leadingAnchor constant:18],[stack.trailingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.trailingAnchor constant:-18],[stack.widthAnchor constraintEqualToAnchor:scroll.frameLayoutGuide.widthAnchor constant:-36]]];
 UILabel *title=[UILabel new];title.font=[UIFont boldSystemFontOfSize:26];title.numberOfLines=0;title.textColor=[UIColor colorWithRed:.08 green:.19 blue:.28 alpha:1];
#if PROJECT_FREEHAND
 title.text=@"Freehand · native replay";
#else
 title.text=@"Volume carving · native replay";
#endif
 [stack addArrangedSubview:title];self.scope=[UILabel new];self.scope.font=[UIFont systemFontOfSize:13];self.scope.numberOfLines=0;self.scope.textColor=[UIColor colorWithRed:.20 green:.32 blue:.40 alpha:1];self.scope.text=@"36 real dinosaur masks · supplied camera matrices · 128³ grid\nNew interface; no live camera or pose tracking. Actual C++ runs on this device.";[stack addArrangedSubview:self.scope];
 self.runButton=[UIButton buttonWithType:UIButtonTypeSystem];[self.runButton setTitle:@"Run 36 images on this device" forState:UIControlStateNormal];self.runButton.titleLabel.font=[UIFont boldSystemFontOfSize:18];[self.runButton addTarget:self action:@selector(run) forControlEvents:UIControlEventTouchUpInside];[stack addArrangedSubview:self.runButton];
 self.progress=[UIProgressView new];[stack addArrangedSubview:self.progress];
 self.status=[UILabel new];self.status.font=[UIFont monospacedDigitSystemFontOfSize:15 weight:UIFontWeightMedium];self.status.numberOfLines=0;self.status.textColor=[UIColor colorWithRed:.08 green:.19 blue:.28 alpha:1];self.status.text=@"Ready. Tap Run to reconstruct from inputs.";self.status.accessibilityIdentifier=@"native-status";[stack addArrangedSubview:self.status];
 self.input=[UIImageView new];self.input.contentMode=UIViewContentModeScaleAspectFit;[self.input.heightAnchor constraintEqualToConstant:120].active=YES;[stack addArrangedSubview:self.input];
 self.sceneView=[SCNView new];[self.sceneView.heightAnchor constraintEqualToConstant:330].active=YES;self.sceneView.backgroundColor=[UIColor colorWithRed:.035 green:.095 blue:.14 alpha:1];self.sceneView.allowsCameraControl=YES;self.sceneView.autoenablesDefaultLighting=NO;self.sceneView.scene=[SCNScene scene];[stack addArrangedSubview:self.sceneView];
 UILabel *credit=[UILabel new];credit.font=[UIFont systemFontOfSize:12];credit.numberOfLines=0;credit.textColor=[UIColor colorWithRed:.20 green:.32 blue:.40 alpha:1];
#if PROJECT_FREEHAND
 credit.text=@"Recovered C++ carving, marching cubes and vertex colors: Alex Fish; supervisors Aaron Wetzler, Yaron Honen, Ron Kimmel.\nInput: Wolfgang Niem / Hannover, Oxford VGG, bundled through Ben Tordoff. Drag the computed mesh to rotate.";
#else
 credit.text=@"Original C++ Sculptor: Sergey Kucher and Alex Povichuk; supervisor Aaron Wetzler.\nInput borrowed from Freehand: Wolfgang Niem / Hannover, Oxford VGG. Display filter excludes never-in-image cells; raw count retained. Teal boundary points, no mesh/texture. Drag to rotate.";
#endif
 [stack addArrangedSubview:credit];
 NSArray<NSString*> *arguments=[NSProcessInfo processInfo].arguments;
 if([arguments containsObject:@"--autorun"]){double delay=2;NSUInteger at=[arguments indexOfObject:@"--autorun-delay"];if(at!=NSNotFound&&at+1<arguments.count){double requested=[arguments[at+1] doubleValue];if(std::isfinite(requested)&&requested>=0&&requested<=60)delay=requested;}self.status.text=[NSString stringWithFormat:@"Auto-run will start in %.1f seconds. No computation yet.",delay];dispatch_after(dispatch_time(DISPATCH_TIME_NOW,(int64_t)(delay*NSEC_PER_SEC)),dispatch_get_main_queue(),^{[self run];});}
}
-(void)showGeometry:(std::vector<float>)positions colors:(std::vector<uint8_t>)colors triangles:(BOOL)triangles{
 NSUInteger count=positions.size()/3;std::vector<SCNVector3> vertices(count);std::vector<uint32_t> indices(count);
 float low[3]={INFINITY,INFINITY,INFINITY},high[3]={-INFINITY,-INFINITY,-INFINITY};for(size_t i=0;i<count;++i)for(int k=0;k<3;++k){low[k]=std::min(low[k],positions[i*3+k]);high[k]=std::max(high[k],positions[i*3+k]);}
 float center[3]={(low[0]+high[0])/2,(low[1]+high[1])/2,(low[2]+high[2])/2};float scale=1.7f/std::max(high[0]-low[0],std::max(high[1]-low[1],high[2]-low[2]));
 // Display only: world Z is up. Saved native output arrays remain unchanged.
 for(NSUInteger i=0;i<count;++i){vertices[i]=SCNVector3Make((positions[i*3+1]-center[1])*scale,-(positions[i*3+2]-center[2])*scale,-(positions[i*3]-center[0])*scale);indices[i]=(uint32_t)i;}
 SCNGeometrySource *v=[SCNGeometrySource geometrySourceWithVertices:vertices.data() count:count];
 const auto displayColors=updated_display::normalizedRGBA(colors);
 NSData *rgba=[NSData dataWithBytes:displayColors.data() length:displayColors.size()*sizeof(float)];
 SCNGeometrySource *c=[SCNGeometrySource geometrySourceWithData:rgba semantic:SCNGeometrySourceSemanticColor vectorCount:count floatComponents:YES componentsPerVector:4 bytesPerComponent:sizeof(float) dataOffset:0 dataStride:4*sizeof(float)];
 SCNGeometryElement *e=[SCNGeometryElement geometryElementWithData:[NSData dataWithBytes:indices.data() length:indices.size()*sizeof(uint32_t)] primitiveType:triangles?SCNGeometryPrimitiveTypeTriangles:SCNGeometryPrimitiveTypePoint primitiveCount:triangles?count/3:count bytesPerIndex:sizeof(uint32_t)];
 e.pointSize=3;e.minimumPointScreenSpaceRadius=1;e.maximumPointScreenSpaceRadius=4;
 SCNGeometry *geometry=[SCNGeometry geometryWithSources:@[v,c] elements:@[e]];SCNMaterial *m=[SCNMaterial material];m.lightingModelName=SCNLightingModelConstant;m.doubleSided=YES;geometry.materials=@[m];
 SCNScene *scene=[SCNScene scene];SCNNode *node=[SCNNode nodeWithGeometry:geometry];[scene.rootNode addChildNode:node];if([[NSProcessInfo processInfo].arguments containsObject:@"--orbit"]){[node runAction:[SCNAction repeatActionForever:[SCNAction rotateByX:0 y:M_PI*2 z:0 duration:18]]];self.sceneView.playing=YES;}
 SCNNode *camera=[SCNNode node];camera.camera=[SCNCamera camera];camera.camera.fieldOfView=50;camera.position=SCNVector3Make(0,0,2.8);[scene.rootNode addChildNode:camera];self.sceneView.scene=scene;self.sceneView.pointOfView=camera;
}
-(void)run{
 if(self.running)return;self.running=YES;self.runButton.enabled=NO;self.progress.progress=0;self.status.text=@"Starting native C++ reconstruction…";self.sceneView.scene=[SCNScene scene];
 NSString *docs=NSSearchPathForDirectoriesInDomains(NSDocumentDirectory,NSUserDomainMask,YES).firstObject;NSString *marker=[docs stringByAppendingPathComponent:@"run-result.json"];NSError *removeError=nil;if([[NSFileManager defaultManager]fileExistsAtPath:marker]&&![[NSFileManager defaultManager]removeItemAtPath:marker error:&removeError]){self.status.text=@"Cannot invalidate previous run marker; run not started.";self.running=NO;self.runButton.enabled=YES;return;}
 dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED,0),^{@autoreleasepool{
#if PROJECT_FREEHAND
 WFCContext *context=wfc_create(.2463f,-.1307f,-.1307f,-.7483f);
#else
 WVCContext *context=wvc_create(.2463f,-.1307f,-.1307f,-.7483f);
#endif
 try{
 if(!context)throw std::runtime_error("Native context allocation failed");
 NSString *folder=[[NSBundle mainBundle]pathForResource:@"dinosaur" ofType:nil];NSData *calibration=[NSData dataWithContentsOfFile:[folder stringByAppendingPathComponent:@"calibration.json"]];NSDictionary *metadata=[NSJSONSerialization JSONObjectWithData:calibration options:0 error:nil];NSArray *matrices=metadata[@"projection_matrices"];if(matrices.count!=36)throw std::runtime_error("Missing 36-view calibration fixture");
 NSMutableArray *history=[NSMutableArray new];double started=CACurrentMediaTime();
 for(int i=0;i<36;++i){@autoreleasepool{
 UIImage *photo=[UIImage imageWithContentsOfFile:[folder stringByAppendingPathComponent:[NSString stringWithFormat:@"pictures/viff.%d.png",i+1]]];UIImage *maskImage=[UIImage imageWithContentsOfFile:[folder stringByAppendingPathComponent:[NSString stringWithFormat:@"silhouettes/sil_%d.png",i+1]]];
 auto maskRGBA=pixels(maskImage);std::vector<uint8_t> mask(maskRGBA.size()/4);for(size_t j=0;j<mask.size();++j)mask[j]=maskRGBA[j*4+1];double p[12];for(int j=0;j<12;++j)p[j]=[matrices[i][j]doubleValue];uint32_t raw=0,observed=0;
#if PROJECT_FREEHAND
 auto rgba=pixels(photo);float rt[12];if(wfc_dinosaur_rt(p,rt)!=0||wfc_apply(context,p,rt,rgba.data(),rgba.size(),mask.data(),mask.size(),720,576)!=0)throw std::runtime_error(wfc_last_error(context));WFCStats stats{};wfc_get_stats(context,&stats);raw=stats.occupied_voxels;observed=raw;
#else
 float pf[12];for(int j=0;j<12;++j)pf[j]=float(p[j]);if(wvc_apply(context,pf,mask.data(),mask.size(),720,576)!=0)throw std::runtime_error(wvc_last_error(context));WVCStats stats{};wvc_get_stats(context,&stats);raw=stats.raw_voxels;observed=stats.observed_voxels;
#endif
 [history addObject:@(raw)];NSString *text=[NSString stringWithFormat:@"Computed view %d / 36\nRaw occupied: %u · displayed/observed: %u",i+1,raw,observed];dispatch_async(dispatch_get_main_queue(),^{self.progress.progress=(i+1)/36.f;self.input.image=photo;self.status.text=text;});
 }}
 std::vector<float> positions;std::vector<uint8_t> colors;uint32_t raw=0,observed=0,triangles=0;uint64_t hash=0;
#if PROJECT_FREEHAND
 int faces=wfc_make_mesh(context);if(faces<0)throw std::runtime_error(wfc_last_error(context));WFCStats stats{};wfc_get_stats(context,&stats);raw=observed=stats.occupied_voxels;triangles=stats.triangles;hash=stats.occupancy_fnv1a64;
 positions.resize(wfc_copy_positions(context,nullptr,0));wfc_copy_positions(context,positions.data(),positions.size());for(float &v:positions)v/=64.f;colors.resize(wfc_copy_colors(context,nullptr,0));wfc_copy_colors(context,colors.data(),colors.size());BOOL mesh=YES;
#else
 WVCStats stats{};wvc_get_stats(context,&stats);raw=stats.raw_voxels;observed=stats.observed_voxels;hash=stats.occupancy_fnv1a64;std::vector<WVCPoint> points(wvc_copy_observed_boundary(context,nullptr,0));wvc_copy_observed_boundary(context,points.data(),points.size());positions.reserve(points.size()*3);colors.reserve(points.size()*4);for(const auto &p:points){positions.push_back((p.x+.1307f)/.2463f*2-1);positions.push_back((p.y+.1307f)/.2463f*2-1);positions.push_back(-((p.z+.7483f)/.2463f*2-1));colors.insert(colors.end(),{50,215,206,255});}BOOL mesh=NO;
#endif
 NSLog(@"NATIVE_VALIDATION raw=%u observed=%u triangles=%u vertices=%lu occupancy=%016llx",raw,observed,triangles,(unsigned long)(positions.size()/3),(unsigned long long)hash);
#if PROJECT_FREEHAND
 if(raw!=22377||triangles!=25200||positions.size()!=25200u*9u||hash!=UINT64_C(0x803e245304c9b374))throw std::runtime_error("Bundled Freehand fixture differs from checked native baseline");
#else
 if(raw!=27310||observed!=21480||positions.size()!=6415u*3u||hash!=UINT64_C(0xbc1847c8e8264d3f))throw std::runtime_error("Bundled Volume fixture differs from checked native baseline");
#endif
 if(colors.size()!=positions.size()/3*4)throw std::runtime_error("Computed geometry/color lengths disagree");for(float coordinate:positions)if(!std::isfinite(coordinate))throw std::runtime_error("Computed geometry is nonfinite");
 NSData *positionData=[NSData dataWithBytes:positions.data() length:positions.size()*sizeof(float)],*colorData=[NSData dataWithBytes:colors.data() length:colors.size()];
 if(!positionData||!colorData)throw std::runtime_error("Cannot allocate saved geometry bytes");
 double elapsed=CACurrentMediaTime()-started;NSDictionary *result=@{@"completed":@YES,@"baseline_verified":@YES,@"positions_sha256":sha256(positionData),@"colors_sha256":sha256(colorData),@"calibration_sha256":sha256(calibration),@"saved_geometry_coordinates":@"Freehand grid-centered /64; Volume cube-normalized [-1,1] with Z flip; separate display centering/axis rotation is not saved",@"native_views":@36,@"raw_voxels":@(raw),@"observed_voxels":@(observed),@"triangles":@(triangles),@"rendered_vertices":@(positions.size()/3),@"occupancy_fnv1a64":[NSString stringWithFormat:@"%016llx",(unsigned long long)hash],@"occupancy_after_each_view":history,@"elapsed_seconds":@(elapsed),@"input":@"36 real dinosaur masks/photos; supplied rounded cameras",@"platform":@"native iOS C++ execution; new UIKit/SceneKit interface",@"camera_capture":@NO,@"pose_tracking":@NO};
 if(![positionData writeToFile:[docs stringByAppendingPathComponent:@"positions.f32"]atomically:YES])throw std::runtime_error("Cannot save computed positions");
 if(![colorData writeToFile:[docs stringByAppendingPathComponent:@"colors.rgba"]atomically:YES])throw std::runtime_error("Cannot save computed colors");
 NSData *json=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingPrettyPrinted error:nil];if(!json||![json writeToFile:marker atomically:YES])throw std::runtime_error("Cannot publish completion marker");NSLog(@"NATIVE_RECONSTRUCTION_RESULT %@",[[NSString alloc]initWithData:json encoding:NSUTF8StringEncoding]);
 NSString *done=[NSString stringWithFormat:@"Native computation complete · %.2f s\nRaw: %u · observed: %u\n%lu %@ · drag result to rotate",elapsed,raw,observed,(unsigned long)(mesh?triangles:positions.size()/3),mesh?@"triangles":@"boundary samples"];
 dispatch_async(dispatch_get_main_queue(),^{[self showGeometry:positions colors:colors triangles:mesh];self.status.text=done;self.running=NO;self.runButton.enabled=YES;});
 }catch(const std::exception &e){NSString *message=[NSString stringWithUTF8String:e.what()];dispatch_async(dispatch_get_main_queue(),^{self.status.text=[@"Native execution failed: " stringByAppendingString:message];self.running=NO;self.runButton.enabled=YES;});NSLog(@"NATIVE_RECONSTRUCTION_ERROR %@",message);}
#if PROJECT_FREEHAND
 wfc_destroy(context);
#else
 wvc_destroy(context);
#endif
 }});
}
@end
@interface RevivalDelegate:UIResponder<UIApplicationDelegate>
@property(nonatomic,strong)UIWindow *window;
@end
@implementation RevivalDelegate
-(BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)options{self.window=[[UIWindow alloc]initWithFrame:[UIScreen mainScreen].bounds];self.window.rootViewController=[NativeController new];[self.window makeKeyAndVisible];return YES;}
@end
int main(int argc,char **argv){@autoreleasepool{return UIApplicationMain(argc,argv,nil,NSStringFromClass([RevivalDelegate class]));}}
