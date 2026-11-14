#!/usr/bin/env python3
"""Generate a new native replay Xcode project in an external build directory.

Original projects/source are never edited. Inputs are copied into a fixture
resource directory; the app computes reconstruction from these inputs at runtime.
"""
from pathlib import Path
import argparse,hashlib,plistlib,shutil,subprocess,sys
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--dataset',type=Path,required=True)
p.add_argument('--calibration',type=Path,required=True)
p.add_argument('--opencv-framework',type=Path)
a=p.parse_args();root=Path(__file__).resolve().parents[2];freehand=root.name=='freehand-voxel-carving';name='FreehandUpdated' if freehand else 'VolumeCarvingUpdated';out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
resources=out/'Resources/dinosaur';resources.mkdir(parents=True,exist_ok=True)
for folder in ['pictures','silhouettes']:
 shutil.copytree(a.dataset/folder,resources/folder,dirs_exist_ok=True)
shutil.copyfile(a.calibration,resources/'calibration.json')
shutil.copyfile(root/'updated/ios/App/NativeController.mm',out/'NativeController.mm')
shutil.copyfile(root/'updated/ios/App/DisplayColors.h',out/'DisplayColors.h')
if freehand:
 core=out/'original-core';subprocess.run([sys.executable,str(root/'updated/prepare_sources.py'),str(core)],check=True)
 sourcefiles=[str(root/'updated/native/freehand.cpp')]+[str(x) for x in sorted(core.glob('*.cpp'))]
 headers=[str(root/'updated/native'),str(core)]
 flags='-include '+str(root/'updated/compat.h')
else:
 core=root/'source/Sculptor';sourcefiles=[str(root/'updated/native/volume_carving.cpp')]+[str(core/n) for n in ['Vector2D.cpp','Vector3D.cpp','Vector3DEx.cpp','Triangle.cpp','Mesh.cpp']]
 headers=[str(root/'updated/native'),str(root/'updated/harness/compat'),str(core),str(root/'source/Drop Shadows')]
 flags='-Dnil=nullptr -ffp-contract=off -Wno-c++11-narrowing'
objects={}
def ident(s):return hashlib.sha1(s.encode()).hexdigest()[:24].upper()
def obj(key,isa,**kw):
 n=ident(key);objects[n]={'isa':isa,**kw};return n
def file(path,kind,tree='<group>'):return obj('file:'+path,'PBXFileReference',path=path,lastKnownFileType=kind,sourceTree=tree)
def build(ref,flags=None):
 d={'fileRef':ref}
 if flags:d['settings']={'COMPILER_FLAGS':flags}
 return obj('build:'+ref,'PBXBuildFile',**d)
sourceRefs=[];sourceBuilds=[]
for path in ['NativeController.mm']+sourcefiles:
 ref=file(path,'sourcecode.cpp.objcpp' if path.endswith('.mm') else 'sourcecode.cpp.cpp','<absolute>' if path.startswith('/') else '<group>');sourceRefs.append(ref);sourceBuilds.append(build(ref,None if path.endswith('.mm') else flags))
res=file('Resources/dinosaur','folder');frameworks=[];frameworkBuilds=[]
for fw in ['UIKit','SceneKit','Foundation','CoreGraphics','QuartzCore','Accelerate','CoreMedia','CoreVideo','AVFoundation','ImageIO']:
 ref=file('System/Library/Frameworks/'+fw+'.framework','wrapper.framework','SDKROOT');frameworks.append(ref);frameworkBuilds.append(build(ref))
product=file(name+'.app','wrapper.application','BUILT_PRODUCTS_DIR')
sources=obj('sources','PBXSourcesBuildPhase',buildActionMask=2147483647,files=sourceBuilds,runOnlyForDeploymentPostprocessing=0)
resphase=obj('resources','PBXResourcesBuildPhase',buildActionMask=2147483647,files=[build(res)],runOnlyForDeploymentPostprocessing=0)
fwphase=obj('frameworks','PBXFrameworksBuildPhase',buildActionMask=2147483647,files=frameworkBuilds,runOnlyForDeploymentPostprocessing=0)
settings={'SDKROOT':'iphoneos','IPHONEOS_DEPLOYMENT_TARGET':'16.0','TARGETED_DEVICE_FAMILY':'1,2','CLANG_ENABLE_MODULES':'YES','CLANG_ENABLE_OBJC_ARC':'YES','CLANG_CXX_LANGUAGE_STANDARD':'c++14','CLANG_CXX_LIBRARY':'libc++','CODE_SIGN_STYLE':'Automatic','DEVELOPMENT_TEAM':'','PRODUCT_BUNDLE_IDENTIFIER':'org.awetzler.freehand.updated' if freehand else 'org.awetzler.volumecarving.updated','PRODUCT_NAME':name,'INFOPLIST_FILE':'Info.plist','HEADER_SEARCH_PATHS':['$(inherited)']+['"'+x+'"' for x in headers],'GCC_PREPROCESSOR_DEFINITIONS':['$(inherited)','PROJECT_FREEHAND='+('1' if freehand else '0')],'COMPRESS_PNG_FILES':'NO','STRIP_PNG_TEXT':'NO','ENABLE_BITCODE':'NO','SUPPORTED_PLATFORMS':'iphoneos iphonesimulator','GCC_OPTIMIZATION_LEVEL':'3','DEBUG_INFORMATION_FORMAT':'dwarf-with-dsym','OTHER_LDFLAGS':['$(inherited)','-lc++','-lz']}
if freehand:
 if not a.opencv_framework:p.error('--opencv-framework required for Freehand')
 settings['FRAMEWORK_SEARCH_PATHS']=['$(inherited)',str(a.opencv_framework.resolve().parent)]
 settings['OTHER_LDFLAGS']+=['-framework','opencv2']
configs=[obj('cfg:'+n,'XCBuildConfiguration',name=n,buildSettings=settings) for n in ['Debug','Release']]
configList=obj('config-list','XCConfigurationList',buildConfigurations=configs,defaultConfigurationIsVisible=0,defaultConfigurationName='Release')
target=obj('app','PBXNativeTarget',name=name,productName=name,productReference=product,productType='com.apple.product-type.application',buildConfigurationList=configList,buildPhases=[sources,fwphase,resphase],dependencies=[],buildRules=[])
products=obj('products','PBXGroup',name='Products',children=[product],sourceTree='<group>')
main=obj('main','PBXGroup',children=sourceRefs+[res]+frameworks+[products],sourceTree='<group>')
project=obj('project','PBXProject',attributes={'LastUpgradeCheck':'1610'},buildConfigurationList=configList,compatibilityVersion='Xcode 14.0',developmentRegion='en',knownRegions=['en','Base'],mainGroup=main,productRefGroup=products,projectDirPath='',projectRoot='',targets=[target])
proj=out/(name+'.xcodeproj');(proj/'xcshareddata/xcschemes').mkdir(parents=True,exist_ok=True)
(proj/'project.pbxproj').write_bytes(plistlib.dumps({'archiveVersion':'1','classes':{},'objectVersion':'56','objects':objects,'rootObject':project},sort_keys=False))
ref=f'<BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="{name}.app" BlueprintName="{name}" ReferencedContainer="container:{name}.xcodeproj"/>'
(proj/f'xcshareddata/xcschemes/{name}.xcscheme').write_text(f'<?xml version="1.0"?><Scheme LastUpgradeVersion="1610" version="1.3"><BuildAction parallelizeBuildables="NO" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="NO" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES">{ref}</BuildActionEntry></BuildActionEntries></BuildAction><LaunchAction buildConfiguration="Release" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES"><BuildableProductRunnable runnableDebuggingMode="0">{ref}</BuildableProductRunnable></LaunchAction><AnalyzeAction buildConfiguration="Release"/><ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/></Scheme>\n')
info={'CFBundleDevelopmentRegion':'en','CFBundleExecutable':'$(EXECUTABLE_NAME)','CFBundleIdentifier':'$(PRODUCT_BUNDLE_IDENTIFIER)','CFBundleName':name,'CFBundlePackageType':'APPL','CFBundleShortVersionString':'2026.11','CFBundleVersion':'1','LSRequiresIPhoneOS':True,'UILaunchScreen':{},'UISupportedInterfaceOrientations':['UIInterfaceOrientationPortrait'],'UIRequiresFullScreen':True}
(out/'Info.plist').write_bytes(plistlib.dumps(info))
print(proj)
