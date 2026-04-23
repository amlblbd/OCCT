cmake_minimum_required(VERSION 3.10)
project(Week1_FirstOCC)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 指定 OpenCASCADE 安装路径
set(OpenCASCADE_DIR "/home/cz/OCCT/install/lib/cmake/opencascade")

find_package(OpenCASCADE REQUIRED)

add_executable(first_occ first_occ.cpp)

target_include_directories(first_occ PRIVATE ${OpenCASCADE_INCLUDE_DIR})

target_link_libraries(first_occ
    ${OpenCASCADE_FoundationClasses_LIBRARIES}
    ${OpenCASCADE_ModelingData_LIBRARIES}
    ${OpenCASCADE_ModelingAlgorithms_LIBRARIES}
)

# 或者更简单地直接链接所有库：
# target_link_libraries(first_occ ${OpenCASCADE_LIBRARIES})
