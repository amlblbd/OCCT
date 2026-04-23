# OCCT 编译过程记录

> Week 1 产出物 | 记录编译环境、步骤、问题和解决方案

---

## 环境信息

| 项目 | 版本/信息 |
|:---|:---|
| OS | Ubuntu 22.04 LTS |
| GCC | 11.4.0 |
| G++ | 11.4.0 |
| CMake | 3.31.4 |
| CPU 核心 | 12 核 |

---

## 系统依赖（已预装）

OCCT 编译前需要安装第三方库，本系统已预装：

| 依赖 | 用途 | 状态 |
|:---|:---|:---|
| FreeType 2.11.1 | 可视化文本渲染 | ✅ 已装 |
| Tcl/Tk 8.6 | DRAW 测试工具 | ✅ 已装 |
| OpenGL / Mesa | 3D 显示 | ✅ 已装 |
| TBB 2021.5 | 并行计算 | ✅ 已装 |
| FreeImage 3.18 | 图片格式支持 | ✅ 已装 |
| X11 | 窗口系统 | ✅ 已装 |

---

## 编译步骤

### 1. CMake 配置

```bash
cd /home/cz/OCCT
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
```

配置结果：
- 自动检测到 FreeType、Tcl/Tk、Xlib
- 生成 Makefile 到 `build/`

### 2. 编译

```bash
cmake --build . -j$(nproc)   # -j12
```

**问题**：后台编译任务 30 分钟超时中断（`timed_out`）。

**实际情况**：超时前已编译 **66 个动态库**（`.so` 文件），`build/src` 目录达 219MB。说明编译本身没问题，只是 OCCT 代码量太大，完整编译需要更长时间。

### 3. 安装

**第一次尝试**：
```bash
invoke install
# 或
cmake --build . --target install
```

**失败**：默认安装前缀 `/usr/local`，需要 root 权限：
```
CMake Error: file cannot create directory: /usr/local/share/doc/opencascade
```

**解决方案**：修改安装前缀为项目目录下的 `install/`：

```bash
cd /home/cz/OCCT/build
cmake -DCMAKE_INSTALL_PREFIX=/home/cz/OCCT/install .
cmake --install .
```

**安装结果**：
| 项目 | 数据 |
|:---|:---|
| 安装目录 | `/home/cz/OCCT/install` |
| 总大小 | 189 MB |
| 动态库 (.so) | 198 个 |
| 可执行文件 | 5 个（含 DRAWEXE）|
| 头文件 | `include/opencascade/` 下全部 OCCT 头 |

---

## 遇到的问题和解决

### 问题 1：安装权限不足

**现象**：`invoke install` 报错 `/usr/local` 无写入权限。

**原因**：CMake 默认 `CMAKE_INSTALL_PREFIX=/usr/local`。

**解决**：重新 configure 指定 `--prefix`：
```bash
cmake -DCMAKE_INSTALL_PREFIX=/home/cz/OCCT/install .
cmake --install .
```

后续在 `tasks.py` 中将默认前缀改为 `os.path.join(OCCT_ROOT, "install")`。

---

### 问题 2：.gitignore 过于严格

**现象**：新建的文件（`tasks.py`、`GIT_WORKFLOW.md`、`exercises/`）被 `git status` 忽略，显示 "nothing to commit, working tree clean"。

**原因**：OCCT 的 `.gitignore` 第 7 行是 `/*`，会忽略根目录下所有未明确豁免的文件。这是 OCCT 官方为了防止编译产物被误提交的设计。

**解决**：在 `.gitignore` 中添加例外：
```gitignore
!/.github/
!/tasks.py
!/GIT_WORKFLOW.md
!/exercises/
/exercises/**/build/   # 但忽略练习目录下的编译产物
```

---

### 问题 3：DRAWEXE 启动时 bgerror

**现象**：`invoke draw` 启动 DRAWEXE 时，命令行出现多次 `bgerror`：
```
Original error: no files matched glob pattern "*.tcl"
```

**原因**：
1. `CSF_DrawPluginDefaults` 环境变量指向的路径下缺少某些 `.tcl` 脚本
2. 系统没有安装浏览器，Help 菜单触发 `xdg-open` 失败

**影响**：不影响核心功能。Draw 窗口正常弹出，`box` / `whatis` 等命令可正常执行。

**状态**：未深入解决，非阻塞问题。

---

## invoke 编译脚本

为简化后续操作，编写了 `tasks.py`（基于 Python invoke 库）：

```bash
invoke build      # 增量编译 OCCT
invoke clean      # 清空 build/
invoke rebuild    # 重新编译
invoke install    # 安装（默认到 ~/OCCT/install）
invoke status     # 查看编译状态
invoke draw       # 启动 DRAWEXE（自动设环境变量）
```

**设计要点**：
- 自动检测 OCCT Linux 输出布局（`build/lin64/gcc/lib/`）
- `draw` 任务自动导出 `CASROOT`、`CSF_OCCTResourcePath`、`LD_LIBRARY_PATH`
- 默认 12 核并行编译

---

## VS Code 调试配置

为 `exercises/week1/first_occ.cpp` 配置了 GDB 调试：

| 文件 | 作用 |
|:---|:---|
| `.vscode/launch.json` | 调试配置（程序路径、环境变量、GDB）|
| `.vscode/tasks.json` | 预构建任务（F5 前自动编译）|

**使用方式**：在 `first_occ.cpp` 打断点 → 按 `F5` → GDB 自动启动。

**注意**：调试必须用 **Debug 模式**编译。Release 的 `-O3` 优化会导致断点乱跳、变量值错乱。

```bash
cd exercises/week1/build
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build .
```

---

## 关键路径速查

| 路径 | 内容 |
|:---|:---|
| `/home/cz/OCCT` | 源码根目录 |
| `/home/cz/OCCT/build` | 编译目录（722MB）|
| `/home/cz/OCCT/build/lin64/gcc/lib/` | 编译产物 .so |
| `/home/cz/OCCT/build/lin64/gcc/bin/DRAWEXE` | 测试工具 |
| `/home/cz/OCCT/install` | 安装目录（189MB）|
| `/home/cz/OCCT/install/include/opencascade/` | 头文件 |
| `/home/cz/OCCT/install/lib/` | 安装后的库 |
| `/home/cz/OCCT/install/bin/DRAWEXE` | 安装后的测试工具 |

---

## 参考资料

- [OCCT 官方编译文档](https://dev.opencascade.org/doc/overview/html/build_upgrade__building_occt.html)
- [CMake 安装前缀说明](https://cmake.org/cmake/help/latest/variable/CMAKE_INSTALL_PREFIX.html)
