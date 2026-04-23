
```markdown
# 阶段 0：OCC + FreeCAD 基础（6 周）

> 理解 OCC 内核架构、B-Rep 数据结构，为手写解析器建立认知基础。  
> 调整：先学 OCC 底层，再学 FreeCAD 上层；拓扑遍历用 C++ 实现。

**时间**：2026-04-23 起，共 6 周  
**投入**：每周 10-15 小时  
**前置要求**：Linux 开发环境、C++ 基础、CMake 基础、Git 基础

---

## 总体目标

| 目标 | 说明 |
|:---|:---|
| 编译 OCC 源码并运行示例 | 理解构建系统，能修改和调试 |
| 掌握 TopoDS 拓扑层级 | 能用 C++ 遍历 Shape → Solid → Shell → Face → Wire → Edge → Vertex |
| 理解 NURBS 参数化表示 | 能用 C++ 提取控制点、节点向量、权重 |
| 读懂 BRepTools/STEPControl/IGESControl 源码 | 知道文件如何被解析为内存对象 |
| 理解 FreeCAD 如何封装 OCC | 知道上层封装与底层内核的映射关系 |

---

## 周计划总览

| 周 | 主题 | 核心技能 | 产出物 |
|:---|:---|:---|:---|
| W1 | OCC 环境搭建与架构 | 编译 OCC、模块图、类层次 | 可运行的 OCC 示例程序 |
| W2 | TopoDS 拓扑结构 | 拓扑类、迭代器、父子关系、Orientation | C++ 拓扑遍历程序 |
| W3 | Geom 几何与 NURBS | 曲面/曲线类型、BSpline 参数 | C++ NURBS 提取程序 |
| W4 | C++ 拓扑遍历实战 | 综合遍历、属性提取、输出 JSON | 完整分析工具 |
| W5 | DataExchange 源码 | BRepTools、STEPControl、IGESControl | 源码阅读笔记 + IR 初稿 |
| W6 | FreeCAD 上层封装 | FreeCAD 如何使用 OCC、Python 绑定、文档对象模型 | FreeCAD 插件/宏脚本 |

---

## 第 1 周：OCC 环境搭建与架构概览

### 目标
编译 OCC 源码，运行示例程序，理解模块划分。

### 每日任务

| 天 | 任务 | 具体内容 | 时间 |
|:---|:---|:---|:---|
| D1 | 下载与依赖 | 克隆 OCCT 源码，安装依赖（tcl/tk、freetype、freeimage、openvr 等） | 2h |
| D2 | CMake 配置 | 配置编译选项，理解各模块的 CMake 开关 | 2h |
| D3 | 编译与安装 | 编译 TKKernel、TKMath、TKG3d、TKBRep 等核心库 | 2h |
| D4 | 运行 Draw 测试 | 启动 `draw.sh`，执行基本命令（`box b 1 2 3`、`whatis b`） | 2h |
| D5 | 模块图研读 | 七大模块：Foundation、Modeling Data、Modeling Algorithms、Visualization、Application Framework、Data Exchange、Draw | 2h |
| D6 | 类层次概览 | 浏览 `inc/` 目录，理解 Geom、TopoDS、BRep、BRepTools 的类关系 | 3h |
| D7 | 写第一个 C++ 程序 | 用 OCC API 创建一个立方体，遍历其拓扑，打印信息 | 3h |

### OCC 核心模块速查

| 模块 | 库名 | 职责 | 解析器是否需要 |
|:---|:---|:---|:---|
| Foundation Classes | TKernel, TKMath | 基础类型、数学工具 | 是（参考实现）|
| Modeling Data | TKG2d, TKG3d, TKGeomBase, TKBRep | 几何和拓扑数据结构 | **核心对标对象** |
| Modeling Algorithms | TKTopAlgo, TKPrim, TKBool, TKFeat, TKFillet, TKOffset, TKMesh | 建模算法（布尔、倒角、网格化）| 否（了解即可）|
| Visualization | TKService, TKV3d | 3D 显示 | 否 |
| Application Framework | TKCDF, TKLCAF | 文档框架、标签数据 | 否 |
| Data Exchange | TKXSBase, TKSTEP, TKIGES, TKSTL, TKVRML | 文件格式读写 | **核心参考对象** |
| Draw | TKDraw | 测试和演示工具 | 否 |

### 产出物

| 产出 | 说明 |
|:---|:---|
| `~/occt-install/` | 编译好的 OCC 库 |
| `exercises/week1/first_occ.cpp` | 第一个 OCC C++ 程序 |
| `exercises/week1/CMakeLists.txt` | 构建配置 |
| `notes/occ_build.md` | 编译过程记录，遇到的问题和解决 |
| `notes/occ_modules.md` | 七大模块笔记 |

### 验收标准

> 能独立编译 OCC 源码，运行 C++ 程序创建立方体并遍历拓扑，输出与 Draw 测试一致。

### 参考资料

| 资源 | 链接 |
|:---|:---|
| OpenCASCADE 官方文档 | https://dev.opencascade.org/doc/overview/html/index.html |
| OpenCASCADE 源码 | https://github.com/Open-Cascade-SAS/OCCT |
| OCC 编译指南 | https://dev.opencascade.org/doc/overview/html/occt_dev_guides__building.html |

---

## 第 2 周：TopoDS 拓扑结构

### 目标
深入理解 TopoDS_Shape 的层级关系、迭代器、父子关系、Orientation。

### 每日任务

| 天 | 任务 | 具体内容 | 时间 |
|:---|:---|:---|:---|
| D1 | TopoDS_Shape 基础 | `ShapeType()`、`Orientation()`、`Nullify()`、`IsNull()`、`Location()` | 2h |
| D2 | 拓扑迭代器 | `TopoDS_Iterator`（父子遍历）vs `TopExp_Explorer`（全局搜索） | 2h |
| D3 | 父子关系构建 | `BRep_Builder`、`BRepPrimAPI` 如何构建拓扑关系 | 2h |
| D4 | 拓扑属性 | `BRep_Tool::Surface()`、`BRep_Tool::Curve()`、`BRep_Tool::Pnt()`、`BRep_Tool::Triangulation()` | 2h |
| D5 | 遍历算法 | `TopExp::MapShapes()`、`TopTools_IndexedMapOfShape`、`TopTools_IndexedDataMapOfShapeListOfShape` | 3h |
| D6 | Orientation 与闭合性 | `TopAbs_FORWARD`、`REVERSED`、`INTERNAL`、`EXTERNAL`；`BRep_Tool::IsClosed()` | 3h |
| D7 | 综合练习 | 写一个 C++ 程序，完整遍历复杂模型，统计各类数量，验证闭合性 | 3h |

### TopoDS 类层次

```
TopoDS_Shape (抽象基类，含 TShape + Location + Orientation)
├── TopoDS_Compound      (复合体，无几何)
├── TopoDS_CompSolid     (复合实体，无几何)
├── TopoDS_Solid         (实体，有体积)
│   └── TopoDS_Shell     (壳，面的集合)
│       └── TopoDS_Face  (面，有 Surface 几何)
│           └── TopoDS_Wire (环，边的有序集合)
│               └── TopoDS_Edge (边，有 Curve 几何 + 参数范围)
│                   └── TopoDS_Vertex (顶点，有 Point 几何)
```

### 核心类对照表

| TopoDS 类 | 几何关联 | 你的 IR 对应 | 关键方法 |
|:---|:---|:---|:---|
| `TopoDS_Vertex` | `gp_Pnt` (3D 点) | `Vertex` | `BRep_Tool::Pnt()` |
| `TopoDS_Edge` | `Geom_Curve` + 参数范围 | `Edge` | `BRep_Tool::Curve()` |
| `TopoDS_Wire` | Edge 的有序集合 | `Wire` | `TopoDS_Iterator` |
| `TopoDS_Face` | `Geom_Surface` + 裁剪线 | `Face` | `BRep_Tool::Surface()` |
| `TopoDS_Shell` | Face 的集合（闭合） | `Shell` | `TopoDS_Iterator` |
| `TopoDS_Solid` | Shell 的集合（封闭体） | `Body` | `TopoDS_Iterator` |

### 产出物

| 产出 | 说明 |
|:---|:---|
| `exercises/week2/topology_explorer.cpp` | 完整拓扑遍历 C++ 程序 |
| `exercises/week2/closure_checker.cpp` | 闭合性检查工具（Shell 是否封闭）|
| `notes/topods_hierarchy.md` | TopoDS 类层次详细笔记 |
| `notes/topods_orientation.md` | Orientation 四种状态的含义和应用场景 |
| `design/ir_topology_v1.md` | 统一 IR 拓扑部分初稿 |

### 验收标准

> C++ 程序能读取 BREP 文件，完整遍历拓扑树，统计各类型数量，验证 Shell 闭合性。

### 参考资料

| 资源 | 链接 |
|:---|:---|
| OCC Modeling Data 文档 | https://dev.opencascade.org/doc/overview/html/occt_user_guides__modeling_data.html |
| TopoDS 包文档 | https://dev.opencascade.org/doc/refman/html/package_topods.html |
| BRep_Tool 文档 | https://dev.opencascade.org/doc/refman/html/class_b_rep___tool.html |

---

## 第 3 周：Geom 几何与 NURBS

### 目标
理解 Geom/Geom2d 包的曲面/曲线类型，掌握 NURBS 的参数化表示，用 C++ 提取参数。

### 每日任务

| 天 | 任务 | 具体内容 | 时间 |
|:---|:---|:---|:---|
| D1 | Geom 包概览 | `Geom_Surface`、`Geom_Curve` 的子类体系，RTTI 识别 | 2h |
| D2 | 初等曲面 | `Geom_Plane`、`Geom_CylindricalSurface`、`Geom_ConicalSurface`、`Geom_SphericalSurface`、`Geom_ToroidalSurface` | 2h |
| D3 | 初等曲线 | `Geom_Line`、`Geom_Circle`、`Geom_Ellipse` | 2h |
| D4 | NURBS 曲面 | `Geom_BSplineSurface`：U/V 阶数、控制点、节点向量、权重 | 3h |
| D5 | NURBS 曲线 | `Geom_BSplineCurve`：阶数、控制点、节点向量、权重 | 3h |
| D6 | 参数化与求值 | `Value(u, v)`、`D1`、`D2` 的含义，参数域与 3D 点的映射 | 3h |
| D7 | 综合 C++ 程序 | 提取任意模型的所有几何参数，输出 JSON | 3h |

### NURBS 核心参数对照

| 参数 | 含义 | C++ 获取方法 |
|:---|:---|:---|
| Degree (U/V) | 多项式阶数 | `UDegree()`, `VDegree()` |
| Control Points (Poles) | 控制顶点网格 | `Poles()` |
| Knots (U/V) | 节点向量 | `UKnots()`, `VKnots()` |
| Weights | 权重（有理 NURBS）| `Weights()` |
| Multiplicities | 节点重数 | `UMultiplicities()`, `VMultiplicities()` |
| Periodic | 是否周期 | `IsUPeriodic()`, `IsVPeriodic()` |
| Rational | 是否有理 | `IsURational()`, `IsVRational()` |

### 产出物

| 产出 | 说明 |
|:---|:---|
| `exercises/week3/nurbs_extractor.cpp` | NURBS 参数提取 C++ 程序 |
| `exercises/week3/geometry_types.cpp` | 所有几何类型的识别和参数提取 |
| `notes/geom_surfaces.md` | 所有 Surface 类型的参数说明 |
| `notes/geom_curves.md` | 所有 Curve 类型的参数说明 |
| `notes/nurbs_math.md` | NURBS 数学原理笔记 |
| `data/nurbs_samples/` | 各模型的 NURBS 参数 JSON 文件 |

### 验收标准

> C++ 程序能读取 BREP 文件，提取所有 NURBS 曲面和曲线的完整参数，输出为 JSON，与 FreeCAD Python 结果一致。

### 参考资料

| 资源 | 链接 |
|:---|:---|
| OCC Modeling Data 文档 | https://dev.opencascade.org/doc/overview/html/occt_user_guides__modeling_data.html |
| Geom 包文档 | https://dev.opencascade.org/doc/refman/html/package_geom.html |
| NURBS 数学基础 | 《The NURBS Book》(书籍) |

---

## 第 4 周：C++ 拓扑遍历实战

### 目标
综合前两周内容，写一个完整的 C++ 分析工具，支持 BREP/STEP/IGES 读取。

### 每日任务

| 天 | 任务 | 具体内容 | 时间 |
|:---|:---|:---|:---|
| D1 | 统一分析类设计 | 设计 `CADAnalyzer` 类，整合拓扑遍历 + 几何提取 | 2h |
| D2 | BREP 读取集成 | 用 `BRepTools::Read()` 读取，完整分析 | 2h |
| D3 | STEP 读取集成 | 用 `STEPControl_Reader` 读取，完整分析 | 3h |
| D4 | IGES 读取集成 | 用 `IGESControl_Reader` 读取，完整分析 | 3h |
| D5 | JSON 输出格式化 | 用 nlohmann/json 输出结构化报告 | 2h |
| D6 | 性能基准测试 | 统计解析时间、内存使用 | 3h |
| D7 | 与 FreeCAD 对比 | 同一文件，C++ 结果 vs FreeCAD Python 结果 | 3h |

### 产出物

| 产出 | 说明 |
|:---|:---|
| `exercises/week4/cad_analyzer.cpp` | 完整分析工具 |
| `exercises/week4/CMakeLists.txt` | 构建配置（链接 STEP/IGES 库）|
| `reports/week4/` | 多个模型的分析报告 JSON |
| `notes/performance_baseline.md` | 性能基准数据（解析时间、内存）|

### 验收标准

> 命令行工具 `cad_analyzer file.step` 能输出完整的 JSON 报告，与 FreeCAD Python 结果一致。

### 参考资料

| 资源 | 链接 |
|:---|:---|
| BRepTools 文档 | https://dev.opencascade.org/doc/refman/html/class_b_rep_tools.html |
| STEPControl 文档 | https://dev.opencascade.org/doc/refman/html/class_s_t_e_p_control___reader.html |
| IGESControl 文档 | https://dev.opencascade.org/doc/refman/html/class_i_g_e_s_control___reader.html |
| nlohmann/json | https://github.com/nlohmann/json |

---

## 第 5 周：DataExchange 源码研读

### 目标
读懂 BRepTools、STEPControl、IGESControl 的源码主线，理解文件解析流程。

### 每日任务

| 天 | 任务 | 具体内容 | 时间 |
|:---|:---|:---|:---|
| D1 | BRepTools::Read() 主线 | 跟踪完整调用链，理解 BREP 文本格式解析 | 3h |
| D2 | BRep 文本格式细节 | 分析段落结构（版本、类型、几何、拓扑、位置） | 3h |
| D3 | STEPControl_Reader 主线 | `ReadFile()` → `TransferRoots()` → `OneShape()` | 3h |
| D4 | STEP 解析细节 | `STEPControl_ActorRead`、`Transfer` 机制、Entity 映射 | 3h |
| D5 | IGESControl_Reader 主线 | `ReadFile()` → `TransferRoots()` | 3h |
| D6 | IGES 解析细节 | DE/PD 解析、`IGESToBRep` 转换器 | 3h |
| D7 | 对比总结 + IR 设计 | 三种格式解析流程对比，完成统一 IR 初稿 | 4h |

### 源码阅读重点文件

| 格式 | 文件路径 | 关键函数 |
|:---|:---|:---|
| BREP | `src/BRepTools/BRepTools.cxx` | `Read()` |
| BREP | `src/BRepTools/BRepTools_Reader.cxx` | 内部读取实现 |
| STEP | `src/STEPControl/STEPControl_Reader.cxx` | `ReadFile()`, `TransferRoots()` |
| STEP | `src/STEPControl/STEPControl_ActorRead.cxx` | `Transfer()` |
| IGES | `src/IGESControl/IGESControl_Reader.cxx` | `ReadFile()`, `TransferRoots()` |
| IGES | `src/IGESToBRep/IGESToBRep_Actor.cxx` | `Transfer()` |

### 产出物

| 产出 | 说明 |
|:---|:---|
| `notes/source_breptools.md` | BRepTools 源码笔记 |
| `notes/source_stepcontrol.md` | STEPControl 源码笔记 |
| `notes/source_igescontrol.md` | IGESControl 源码笔记 |
| `notes/format_comparison.md` | 三种格式解析流程对比 |
| `design/ir_v1.md` | 统一 IR 完整初稿 |
| `design/parser_architecture_v1.md` | 解析器架构初稿 |

### 验收标准

> 能向他人清晰解释三种格式的解析流程差异，完成统一 IR 设计初稿。

### 参考资料

| 资源 | 链接 |
|:---|:---|
| OCC Data Exchange 文档 | https://dev.opencascade.org/doc/overview/html/occt_user_guides__exchange.html |
| STEP 交换文档 | https://dev.opencascade.org/doc/overview/html/occt_user_guides__step.html |
| IGES 交换文档 | https://dev.opencascade.org/doc/overview/html/occt_user_guides__iges.html |

---

## 第 6 周：FreeCAD 上层封装

### 目标
理解 FreeCAD 如何封装 OCC，掌握文档对象模型，能用 Python 脚本和 C++ 扩展。

### 每日任务

| 天 | 任务 | 具体内容 | 时间 |
|:---|:---|:---|:---|
| D1 | FreeCAD 安装与界面 | 安装 FreeCAD，对比 OCC Draw 和 FreeCAD GUI 的异同 | 2h |
| D2 | 文档对象模型 | `App.Document`、`App.Part`、`App.Body`、`Part.Feature` | 2h |
| D3 | Python 脚本基础 | 宏录制、Python 控制台、遍历文档对象 | 2h |
| D4 | FreeCAD vs OCC 映射 | FreeCAD 的 `Part.Shape` 如何封装 `TopoDS_Shape` | 3h |
| D5 | Import/Export 模块 | 阅读 `src/Mod/Part/App/ImportStep.cpp` 等 | 3h |
| D6 | C++ 扩展开发 | 写一个 FreeCAD C++ 模块，调用自定义 OCC 代码 | 3h |
| D7 | 综合对比 | 同一操作在 OCC C++、FreeCAD Python、FreeCAD GUI 中的对比 | 3h |

### FreeCAD 与 OCC 的映射关系

| FreeCAD 对象 | OCC 对象 | 说明 |
|:---|:---|:---|
| `Part.Feature` | `TopoDS_Shape` | 几何特征 |
| `Part.Shape` | `TopoDS_Shape` | 形状封装 |
| `Part.Face` | `TopoDS_Face` | 面 |
| `Part.Edge` | `TopoDS_Edge` | 边 |
| `Part.Vertex` | `TopoDS_Vertex` | 顶点 |
| `Part.Surface` | `Geom_Surface` | 曲面几何 |
| `Part.Curve` | `Geom_Curve` | 曲线几何 |
| `App.Document` | `TDocStd_Document` | 文档 |
| `App.Part` | `TDF_Label` | 部件容器 |

### 产出物

| 产出 | 说明 |
|:---|:---|
| `exercises/week6/freecad_macros/` | FreeCAD Python 宏脚本 |
| `exercises/week6/freecad_module/` | 简单的 FreeCAD C++ 扩展模块 |
| `notes/freecad_vs_occ.md` | FreeCAD 与 OCC 的映射关系表 |
| `notes/freecad_import_export.md` | Import/Export 模块源码笔记 |

### 验收标准

> 能写 FreeCAD Python 宏脚本自动化操作，理解 FreeCAD C++ 模块的编译和加载。

### 参考资料

| 资源 | 链接 |
|:---|:---|
| FreeCAD Wiki | https://wiki.freecad.org |
| FreeCAD Python 脚本 | https://wiki.freecad.org/Power_users_hub |
| FreeCAD C++ 开发 | https://wiki.freecad.org/Developer_hub |
| FreeCAD 论坛 | https://forum.freecad.org |

---

## 关键产出清单

| 周 | 必须产出 | 存放位置 |
|:---|:---|:---|
| W1 | 编译好的 OCC 库 + 第一个 C++ 程序 | `~/occt-install/`, `exercises/week1/` |
| W2 | C++ 拓扑遍历程序 + 闭合性检查 | `exercises/week2/` |
| W3 | C++ NURBS 提取程序 + JSON 输出 | `exercises/week3/`, `data/nurbs_samples/` |
| W4 | 完整 CAD 分析工具（BREP/STEP/IGES） | `exercises/week4/`, `reports/week4/` |
| W5 | 三份源码笔记 + IR 初稿 | `notes/source_*.md`, `design/ir_v1.md` |
| W6 | FreeCAD 宏脚本 + C++ 扩展 | `exercises/week6/` |

---

## 每日时间分配建议

| 时间段 | 工作日 | 周末 |
|:---|:---|:---|
| 理论学习 | 30-40 min | 1h |
| 动手操作/编码 | 40-50 min | 2h |
| 笔记整理 | 10-20 min | 1h |
| **日总计** | **1-1.5h** | **4h** |

---

## 常见问题与应对

| 问题 | 应对 |
|:---|:---|
| OCC 编译失败 | 检查依赖版本，参考官方编译指南，或尝试 Docker 编译环境 |
| 源码看不懂 | 先抓主线（函数入口→关键调用→返回），细节后续补 |
| NURBS 数学看不懂 | 先看直观效果（改控制点观察形状变化），再补数学 |
| FreeCAD 模块编译失败 | 检查 FreeCAD 版本与 OCC 版本兼容性 |
| 进度落后 | 优先保证 W2-W4 的核心程序，W5-W6 可压缩 |

---

## 资源汇总

### 官方文档

| 资源 | 链接 |
|:---|:---|
| OpenCASCADE 官方文档 | https://dev.opencascade.org/doc/overview/html/index.html |
| OpenCASCADE 源码 | https://github.com/Open-Cascade-SAS/OCCT |
| FreeCAD Wiki | https://wiki.freecad.org |
| FreeCAD 源码 | https://github.com/FreeCAD/FreeCAD |
| FreeCAD 论坛 | https://forum.freecad.org |

### 书籍

| 书名 | 用途 |
|:---|:---|
| 《OpenCASCADE 技术指南》| 中文，OCC 架构和 API |
| 《CAD/CAM 原理与应用》| B-Rep 理论基础 |
| 《The NURBS Book》| NURBS 数学原理 |

### 工具

| 工具 | 用途 |
|:---|:---|
| `draw.sh` | OCC 自带测试工具 |
| `FreeCAD -c` | FreeCAD 命令行模式 |
| `grep -r` | 源码搜索 |

---

*阶段 0 结束标志：能独立用 C++ 程序分析任意 CAD 文件的拓扑和几何，能向他人解释 OCC 解析流程，完成统一 IR 初稿，理解 FreeCAD 如何封装 OCC。*

---

*文档版本: 3.0*  
*创建日期: 2026-04-22*  
*更新日期: 2026-04-23*  
```