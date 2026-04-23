// first_occ.cpp
// Week 1 第一个 OCCT C++ 程序：创建立方体，遍历拓扑，输出信息

#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepTools.hxx>
#include <BRep_Tool.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Edge.hxx>
#include <TopoDS_Vertex.hxx>
#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>
#include <gp_Pnt.hxx>
#include <iostream>
#include <map>
#include <string>

// 将 TopAbs_ShapeEnum 转换为可读字符串
std::string ShapeTypeToString(TopAbs_ShapeEnum type) {
    switch (type) {
        case TopAbs_COMPOUND:  return "Compound";
        case TopAbs_COMPSOLID: return "CompSolid";
        case TopAbs_SOLID:     return "Solid";
        case TopAbs_SHELL:     return "Shell";
        case TopAbs_FACE:      return "Face";
        case TopAbs_WIRE:      return "Wire";
        case TopAbs_EDGE:      return "Edge";
        case TopAbs_VERTEX:    return "Vertex";
        case TopAbs_SHAPE:     return "Shape";
        default:               return "Unknown";
    }
}

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "OCCT Week 1: First C++ Program" << std::endl;
    std::cout << "========================================" << std::endl;

    // 1. 创建一个立方体 (长=10, 宽=20, 高=30)
    std::cout << "\n[1] Creating a box (10 x 20 x 30) ..." << std::endl;
    BRepPrimAPI_MakeBox boxMaker(10.0, 20.0, 30.0);
    TopoDS_Shape box = boxMaker.Shape();
    std::cout << "    Box created. Shape type: " << ShapeTypeToString(box.ShapeType()) << std::endl;

    // 2. 用 TopExp_Explorer 统计各类拓扑元素数量
    std::cout << "\n[2] Topology exploration (using TopExp_Explorer):" << std::endl;

    std::map<std::string, int> counts;
    TopAbs_ShapeEnum types[] = {
        TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE,
        TopAbs_WIRE,  TopAbs_EDGE,  TopAbs_VERTEX
    };

    for (auto t : types) {
        int count = 0;
        for (TopExp_Explorer exp(box, t); exp.More(); exp.Next()) {
            ++count;
        }
        counts[ShapeTypeToString(t)] = count;
        std::cout << "    " << ShapeTypeToString(t) << ": " << count << std::endl;
    }

    // 3. 计算总体积和表面积
    std::cout << "\n[3] Geometric properties (using BRepGProp):" << std::endl;

    GProp_GProps volumeProps;
    BRepGProp::VolumeProperties(box, volumeProps);
    std::cout << "    Volume:  " << volumeProps.Mass() << " (expected: 6000)" << std::endl;

    GProp_GProps surfaceProps;
    BRepGProp::SurfaceProperties(box, surfaceProps);
    std::cout << "    Surface Area: " << surfaceProps.Mass() << " (expected: 2200)" << std::endl;

    // 4. 遍历 Face，打印每个面的面积
    std::cout << "\n[4] Face details:" << std::endl;
    int faceIndex = 1;
    for (TopExp_Explorer exp(box, TopAbs_FACE); exp.More(); exp.Next(), ++faceIndex) {
        TopoDS_Face face = TopoDS::Face(exp.Current());
        GProp_GProps faceProps;
        BRepGProp::SurfaceProperties(face, faceProps);
        std::cout << "    Face #" << faceIndex << " area = " << faceProps.Mass() << std::endl;
    }

    // 5. 遍历 Edge，打印第一条边的长度
    std::cout << "\n[5] Edge details:" << std::endl;
    int edgeIndex = 1;
    for (TopExp_Explorer exp(box, TopAbs_EDGE); exp.More(); exp.Next(), ++edgeIndex) {
        TopoDS_Edge edge = TopoDS::Edge(exp.Current());
        GProp_GProps edgeProps;
        BRepGProp::LinearProperties(edge, edgeProps);
        if (edgeIndex <= 4) {
            std::cout << "    Edge #" << edgeIndex << " length = " << edgeProps.Mass() << std::endl;
        }
    }
    std::cout << "    ... (total " << counts["Edge"] << " edges)" << std::endl;

    // 6. 遍历 Vertex，打印第一个顶点的坐标
    std::cout << "\n[6] Vertex details:" << std::endl;
    int vtxIndex = 1;
    for (TopExp_Explorer exp(box, TopAbs_VERTEX); exp.More(); exp.Next(), ++vtxIndex) {
        TopoDS_Vertex vtx = TopoDS::Vertex(exp.Current());
        gp_Pnt p = BRep_Tool::Pnt(vtx);
        if (vtxIndex <= 4) {
            std::cout << "    Vertex #" << vtxIndex << " = ("
                      << p.X() << ", " << p.Y() << ", " << p.Z() << ")" << std::endl;
        }
    }
    std::cout << "    ... (total " << counts["Vertex"] << " vertices)" << std::endl;

    // 7. 将形状保存为 BREP 文件
    std::string filename = "box_10x20x30.brep";
    std::cout << "\n[7] Saving shape to: " << filename << std::endl;
    if (BRepTools::Write(box, filename.c_str())) {
        std::cout << "    Save OK." << std::endl;
    } else {
        std::cout << "    Save FAILED." << std::endl;
        return 1;
    }

    std::cout << "\n========================================" << std::endl;
    std::cout << "Done!" << std::endl;
    std::cout << "========================================" << std::endl;

    return 0;
}
