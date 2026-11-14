cmake_minimum_required(VERSION 3.16)
project(VolumeCarvingNative LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(RECOVERED "${CMAKE_CURRENT_LIST_DIR}/../../source/Sculptor")
add_library(volume_carving_native STATIC volume_carving.cpp
  "${RECOVERED}/Vector2D.cpp" "${RECOVERED}/Vector3D.cpp"
  "${RECOVERED}/Vector3DEx.cpp" "${RECOVERED}/Triangle.cpp" "${RECOVERED}/Mesh.cpp")
set_target_properties(volume_carving_native PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_include_directories(volume_carving_native PUBLIC "${CMAKE_CURRENT_LIST_DIR}" PRIVATE
  "${CMAKE_CURRENT_LIST_DIR}/../harness/compat" "${RECOVERED}"
  "${CMAKE_CURRENT_LIST_DIR}/../../source/Drop Shadows")
target_compile_definitions(volume_carving_native PRIVATE nil=nullptr)
target_compile_options(volume_carving_native PRIVATE -ffp-contract=off -Wno-c++11-narrowing)
# A native C ABI can be imported by Swift/Objective-C++ or an Android JNI shim.
# No host Python, UIKit, OpenCV, camera SDK, PNG decoder or meshing implementation.
option(WVC_BUILD_TESTS "Build host C-ABI regression" ON)
if(WVC_BUILD_TESTS)
 add_executable(volume_carving_regression regression.cpp)
 target_link_libraries(volume_carving_regression PRIVATE volume_carving_native)
 enable_testing()
 add_test(NAME c_abi_prism COMMAND volume_carving_regression)
endif()
option(WVC_BUILD_REPLAY "Build host PNG C-ABI replay" OFF)
if(WVC_BUILD_REPLAY)
 find_package(PNG REQUIRED)
 add_executable(volume_native_replay replay.cpp)
 target_compile_definitions(volume_native_replay PRIVATE PROJECT_FREEHAND=0)
 target_link_libraries(volume_native_replay PRIVATE volume_carving_native PNG::PNG)
endif()
