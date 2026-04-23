# OCCT 七大模块速查

> Week 1 产出物 | 理解模块划分，建立整体认知框架

---

## 模块总览

OCCT 源码位于 `src/` 下，按功能划分为 **7 大模块**。解析器开发主要关注 **Modeling Data** 和 **Data Exchange**。

| 模块 | 英文 | 库前缀 | 职责 | 手写解析器是否需要 |
|:---|:---|:---|:---|:---|
| **基础类** | Foundation Classes | `TKernel`, `TKMath` | 基础类型、数学工具、内存管理、异常处理 | ✅ 参考实现 |
| **建模数据** | Modeling Data | `TKG2d`, `TKG3d`, `TKGeomBase`, `TKBRep` | **几何和拓扑数据结构**（核心）| 🔥 **核心对标对象** |
| **建模算法** | Modeling Algorithms | `TKTopAlgo`, `TKPrim`, `TKBool`, `TKFeat`, `TKFillet`, `TKOffset`, `TKMesh` | 布尔运算、倒角、网格化、体素化 | ❌ 了解即可 |
| **可视化** | Visualization | `TKService`, `TKV3d`, `TKOpenGl` | 3D 渲染、显示管线、交互 | ❌ |
| **应用框架** | Application Framework | `TKCDF`, `TKLCAF`, `TKCAF` | 文档对象模型、持久化、标签数据 | ❌ |
| **数据交换** | Data Exchange | `TKXSBase`, `TKDEIGES`, `TKDESTEP`, `TKDESTL`, `TKDEVRML` | **文件格式读写**（BREP/STEP/IGES/STL）| 🔥 **核心参考对象** |
| **Draw** | Draw Test Harness | `TKDraw` | 测试工具、脚本环境、演示 | ❌ |

---

## 核心模块详解

### 1. Foundation Classes（基础类）

**位置**：`src/FoundationClasses/`

| 子库 | 内容 | 关键类 |
|:---|:---|:---|
| `TKernel` | 基础类型、内存管理、字符串、集合 | `Standard_*`, `NCollection_*`, `OSD_*` |
| `TKMath` | 数学工具、几何基础、矩阵向量 | `gp_*`, `math_*`, `Bnd_*`, `BVH_*` |

**我的理解**：
- `gp_*`（geometric primitives）是最底层：点、向量、矩阵、变换
- `NCollection_*` 是 OCCT 自己的容器库（数组、列表、映射），类似 STL 但有自己的内存分配策略
- `Standard_*` 封装了平台差异（类型别名、异常、内存分配器）

---

### 2. Modeling Data（建模数据）⭐ 重点

**位置**：`src/ModelingData/` 和 `src/ModelingAlgorithms/`

这是手写解析器的**核心对标对象**。所有 CAD 文件最终被解析为这些内存数据结构。

#### 2.1 几何层（Geometry）— 定义"长什么样"

**库**：`TKG2d`, `TKG3d`, `TKGeomBase`

| 包名 | 内容 | 关键类 |
|:---|:---|:---|
| `Geom` | 3D 参数化几何（曲线/曲面）| `Geom_Surface`, `Geom_Curve`, `Geom_BSplineSurface` |
| `Geom2d` | 2D 参数化几何 | `Geom2d_Curve` |
| `gp` | 初等几何实体 | `gp_Pnt`, `gp_Vec`, `gp_Dir`, `gp_Ax3` |

**核心概念**：
- **参数化表示**：任何曲线有参数 `u`，任何曲面有参数 `(u, v)`
- **NURBS**：`Geom_BSplineSurface` / `Geom_BSplineCurve`，工业标准表示
- **初等曲面**：平面、圆柱、圆锥、球、圆环

#### 2.2 拓扑层（Topology）— 定义"怎么连"

**库**：`TKBRep`

| 类名 | 含义 | 包含什么 | 手写 IR 对应 |
|:---|:---|:---|:---|
| `TopoDS_Shape` | 抽象基类 | TShape + Location + Orientation | `Shape` |
| `TopoDS_Compound` | 复合体 | 多个 Shape 的无序集合 | — |
| `TopoDS_Solid` | 实体 | 封闭的体积 | `Body` |
| `TopoDS_Shell` | 壳 | 面的集合（可闭合）| `Shell` |
| `TopoDS_Face` | 面 | 有 Surface 几何 + 边界 | `Face` |
| `TopoDS_Wire` | 环 | 边的有序集合 | `Wire` |
| `TopoDS_Edge` | 边 | 有 Curve 几何 + 参数范围 | `Edge` |
| `TopoDS_Vertex` | 顶点 | 有 3D 点坐标 | `Vertex` |

**层级关系**：
```
Solid (1) → Shell (1+) → Face (1+) → Wire (1+) → Edge (1+) → Vertex (2+)
```

**我的理解**：
- 拓扑不关心"具体方程是什么"，只关心"谁包含谁、谁连接谁"
- 同一个几何曲面可以被多个 Face 引用（共享面）
- Orientation（FORWARD/REVERSED）决定面的法向朝内还是朝外

#### 2.3 BRep 工具

**库**：`TKBRep` 中的 `BRep` 包

| 类/函数 | 用途 |
|:---|:---|
| `BRep_Tool::Surface(Face)` | 提取 Face 的底层 Surface |
| `BRep_Tool::Curve(Edge)` | 提取 Edge 的底层 Curve + 参数范围 |
| `BRep_Tool::Pnt(Vertex)` | 提取 Vertex 的 3D 坐标 |
| `BRep_Builder` | 从零构建拓扑结构 |
| `BRepTools::Read/Write` | BREP 文件读写 |

---

### 3. Data Exchange（数据交换）⭐ 重点

**位置**：`src/DataExchange/`

| 格式 | 库 | 关键类 | 说明 |
|:---|:---|:---|:---|
| **BREP** | `TKBRep` | `BRepTools::Read/Write` | OCCT 原生文本格式 |
| **STEP** | `TKDESTEP`, `TKXSBase` | `STEPControl_Reader`, `STEPControl_Writer` | AP214/AP242 标准 |
| **IGES** | `TKDEIGES`, `TKXSBase` | `IGESControl_Reader`, `IGESControl_Writer` | 老式标准 |
| **STL** | `TKDESTL` | `StlAPI::Read/Write` | 三角网格 |
| **OBJ** | `TKDEOBJ` | `RWObj_CafReader` | 简单网格 |
| **VRML** | `TKDEVRML` | — | 网页 3D |

**解析流程**（以 STEP 为例）：
```
STEP 文件 → STEPControl_Reader::ReadFile()
         → TransferRoots()     [把 STEP 实体转为 OCCT 内部对象]
         → OneShape()          [获取最终的 TopoDS_Shape]
```

**我的理解**：
- 手写解析器的目标是**替代**这些 Reader，直接从文件解析出自己的 IR
- 但必须先读懂这些 Reader 的源码，才能知道文件格式怎么映射到数据结构
- Week 5 的核心任务就是读这些源码

---

### 4. Modeling Algorithms（建模算法）

**位置**：`src/ModelingAlgorithms/`

了解即可，手写解析器不需要实现这些。

| 库 | 功能 |
|:---|:---|
| `TKPrim` | 基本体素（立方体、圆柱、球、圆锥）|
| `TKBool` | 布尔运算（交、并、差）|
| `TKFillet` | 倒圆角 |
| `TKFeat` | 特征（孔、槽、凸台）|
| `TKMesh` | 表面网格化（用于 STL/显示）|
| `TKTopAlgo` | 拓扑算法（剖分、切片、投影）|

---

### 5. Visualization（可视化）

**位置**：`src/Visualization/`

| 库 | 功能 |
|:---|:---|
| `TKService` | 底层显示服务 |
| `TKV3d` | 3D 视图、相机、光照 |
| `TKOpenGl` | OpenGL 渲染驱动 |

了解即可。解析器不需要显示功能。

---

## 类层次关系图

```
文件格式 (STEP/IGES/BREP)
    ↓
DataExchange Reader (Week 5 研读)
    ↓
TopoDS_Shape 拓扑树
    ├── TopoDS_Face ──→ BRep_Tool::Surface() → Geom_Surface
    │                                    ├── Geom_Plane
    │                                    ├── Geom_CylindricalSurface
    │                                    └── Geom_BSplineSurface  ← NURBS
    ├── TopoDS_Edge ──→ BRep_Tool::Curve()   → Geom_Curve
    │                                    ├── Geom_Line
    │                                    ├── Geom_Circle
    │                                    └── Geom_BSplineCurve
    └── TopoDS_Vertex → BRep_Tool::Pnt()     → gp_Pnt (x, y, z)
```

---

## 学习路线建议

| 优先级 | 内容 | 周次 |
|:---|:---|:---|
| P0 | TopoDS 拓扑遍历 | W2 |
| P0 | NURBS 参数提取 | W3 |
| P1 | BRepTools/STEPControl/IGESControl 源码 | W5 |
| P2 | Foundation Classes 容器和数学工具 | 穿插 |
| P3 | 建模算法和可视化 | 暂不深入 |

---

## 速查命令

```bash
# 查看某个包有哪些类
grep -r "class " src/ModelingData/TKBRep/BRep/ | head -20

# 查找某个类的定义位置
grep -rn "class TopoDS_Face" src/

# 查看模块划分（CMake 定义）
cat src/MODULES.cmake
```

---

## 参考资料

- [OCCT User Guide - Modeling Data](https://dev.opencascade.org/doc/overview/html/occt_user_guides__modeling_data.html)
- [OCCT User Guide - Data Exchange](https://dev.opencascade.org/doc/overview/html/occt_user_guides__exchange.html)
- TopoDS 包文档：`dox/user_guides/modeling_data/modeling_data.md`（源码内）
