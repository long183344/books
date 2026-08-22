# HALCON 第 13 章 Graphics · 上卷（主动绘图与交互）

> **覆盖范围**：HALCON Operator Reference 中 Graphics 章节的 **5 个子族**——`3D Scene` / `Drawing` / `LUT` / `Mouse` / `Object`，合计 **78 个算子**。
> **下卷预告**：Graphics · 下卷将覆盖剩余 4 个子族 —— `Output` (16) / `Parameters` (38) / `Text` (12) / `Window` (21)，合计 87 算子（窗口系统与输出）。
> **作者目标**：按用户要求（章节切片 + 双语思维导图 + 完整签名速查含简洁功能介绍）做精细化整理。所有签名直接从 HALCON 20.11.1.0 官方 HTML 抽取，未做臆造；中文功能简介为浓缩理解、一句话讲清算子"做啥"。

---

## 0. 本卷定位与适用读者

| 维度 | 说明 |
|---|---|
| **章节归类** | Graphics（绘图与用户界面交互） |
| **核心问题域** | 怎么在 HALCON 窗口里 ① **画**几何（Drawing）② **渲染**三维物体（3D Scene）③ **变换**显示颜色（LUT）④ **读取**鼠标事件（Mouse） ⑤ **抽象**可复用的交互控件（Object） |
| **下游衔接** | 上接 Ch11（第 11 章 Regions / XLD，几何表示）；下接 Graphics · 下卷（窗口显示系统、文本显示、参数控制、图像输出） |
| **典型读者** | ① HALCON GUI 工具开发； ② 标定/测量前手动取点； ③ 三维体可视化与分析； ④ 跨语言工程化（move ROI、bot-style 注入事件） |
| **不覆盖** | HALCON 窗口本身的生命周期（dev_open_window / dev_close_window 等在第 13 章 Window 子族，留给 Graphics · 下卷） |

---

## 1. 全卷五族速览

| 子族 | 算子数 | 一句话定性 | 关键算子样例 |
|---|---|---|---|
| **3D Scene** | 20 | 在 HALCON 窗口里 **栅格化/采集** 一个由相机 + 光源 + 实例 + 标签组成的三维场景 | `create_scene_3d` / `render_scene_3d` / `add_scene_3d_camera` |
| **Drawing** | 23 | **同步阻塞**或**叠加可调**的交互式鼠标绘制，从点→线→圆→椭圆→NURBS 一应俱全 | `draw_circle` / `draw_rectangle2` / `draw_nurbs` |
| **LUT** | 3 | **伪彩色查找表**的设/查操作，给单通道图着色（热图 / 等高线伪彩等） | `set_lut` / `get_lut` / `query_lut` |
| **Mouse** | 11 | 直接读 **鼠标键位/位置/光标**或 **编程注入**鼠标事件（自动化/无头测试） | `get_mposition` / `set_mshape` / `send_mouse_*` |
| **Object** | 21 | 把"画什么"封装为 **可绑定窗口、可回调、可查询**的对象句柄，是 Drawing 的工程化替代 | `create_drawing_object_*` / `attach_drawing_object_to_window` / `set_drawing_object_callback` |

> **数量合计 78**，全章 165 算子的 ≈ 47%；Graphics · 下卷拿 87 个窗口/输出/文本/参数算子。

---

## 2. 子族 1 · 3D Scene（20 ops · 三维场景渲染）

### 2.1 设计目的

让 **没有 OpenGL 上下文** 的 HALCON 程序也能快速 **栅格化渲染**一个虚拟 3D 场景——典型用途：

- **测量仿真**：把相机内参、3D 物体、点光源都装进 Scene3D，调用 `display_scene_3d` 在窗口里 **看着摆位**；
- **离线出图**：用 `render_scene_3d` 把渲染结果写回图像数组，下游做 OCR / 视觉定位（避免 GL 依赖）；
- **可视调试**：给 `set_scene_3d_label` 打文字，给 `set_scene_3d_light_param` 调光照，无需重启就重画。

### 2.2 Scene3D 的对象模型（mental model）

```
Scene3D（场景）
├── Camera(s)  —— 若干个虚拟相机，每个有内参（CamParam）+ 外参（Pose）
├── Light(s)   —— 若干光源（环境光 / 方向光 / 点光源）
├── Instance(s)—— 已经 read_object_model_3d 读好的 3D 实例 + Pose
└── Label(s)   —— 2D/3D 文本标注，绑定一个 ReferencePoint
```

每个对象都有 **增 / 删 / 改** 三件套：

| 增 | 删 | 改 |
|---|---|---|
| `add_scene_3d_camera` | `remove_scene_3d_camera` | `set_scene_3d_camera_pose` |
| `add_scene_3d_light` | `remove_scene_3d_light` | `set_scene_3d_light_param` |
| `add_scene_3d_instance` | `remove_scene_3d_instance` | `set_scene_3d_instance_pose` / `set_scene_3d_instance_param` |
| `add_scene_3d_label` | `remove_scene_3d_label` | `set_scene_3d_label_param` |
| `create_scene_3d`（创建句柄） | `clear_scene_3d`（整场清空） | `set_scene_3d_param`（全局属性） |

### 2.3 三个 "Render 出口"

| 函数 | 用途 | 备注 |
|---|---|---|
| `display_scene_3d` | 直接绘制到 **现成 HALCON 窗口**（由 WindowHandle 指定）| 需要先 `dev_open_window` 才能显示 |
| `render_scene_3d` | 渲染到 **图像变量**（Image），不调用窗口 | 用于离线流水线、保存截图 |
| `get_display_scene_3d_info` | 从已显示窗口 **拾取**（hit-test）某 (Row, Col) 处是哪一对象 | 给交互功能提供数据支撑 |

### 2.4 典型 GenParamName 速查

通过 `set_scene_3d_param` / `set_scene_3d_*_param` 传入：

- `'background_color'`：背景色（RGB 三元组，0–1）
- `'depth_map'`：`'enable'` 启用深度图渲染（`render_scene_3d` 时拿到深度）
- `'lighting'`：`'default'` / `'none'` / `'ambient'` 等开关
- `'shadow'`：`'enable'` 启用阴影仿真
- `'disp_background'`：`'true'` 在 display 时是否画背景
- `'object_color_persistence'`：实例颜色是否被 set_instance_param 永久改写

### 2.5 关键签名（一行版）

```
create_scene_3d  ( : : : Scene3D )                                       ← 句柄
render_scene_3d  ( : Image : Scene3D , CameraIndex : )                  ← 出图
display_scene_3d ( : : WindowHandle , Scene3D , CameraIndex : )         ← 显屏
add_scene_3d_camera ( : : Scene3D , CameraParam : CameraIndex )         ← 加相机
add_scene_3d_light  ( : : Scene3D , LightPosition , LightKind : LightIndex )
add_scene_3d_instance ( : : Scene3D , ObjectModel3D , Pose : InstanceIndex )
set_scene_3d_camera_pose  ( : : Scene3D , CameraIndex , Pose : )
set_scene_3d_to_world_pose ( : : Scene3D , ToWorldPose : )
```

---

## 3. 子族 2 · Drawing（23 ops · 鼠标交互式绘制）

### 3.1 设计目的

给 **标定 / 测量 / 手动取点** 一个统一入口：用户 **画什么** → 程序 **立即拿到** Region / XLD / Row-Column 几何参数。

- 23 个算子分为两条轴：
  - **几何类型**轴：点 / 线 / 圆 / 椭圆 / 矩形 / 多边形 / NURBS / Region / XLD
  - **交互模式**轴：阻塞式 `draw_*` / 叠加式 `draw_*_mod` / 拖拽式 `drag_region*`

### 3.2 三种交互模式横向对比

| 模式 | 同步？ | 可叠加已有显示？ | 旋/移/缩？ | 输出 |
|---|---|---|---|---|
| `draw_*`（如 `draw_circle`） | 是（阻塞等用户放开右键） | 否（窗口会先帮你清一下） | 否 | 基本几何参数 |
| `draw_*_mod`（如 `draw_rectangle2_mod`） | 是 | 是（叠加在原图上） | 是（`Rotate`/`Move`/`Scale`/`KeepRatio`） | 同上 |
| `drag_region*`（如 `drag_region2`） | 是 | 是 | 是 | 新 Region（仿射变换后的形状） |

### 3.3 几何类型分布

| 几何 | 同步版 | 叠加版 | 备注 |
|---|---|---|---|
| 点 | `draw_point` | `draw_point_mod` | `mod` 版接受 `RowIn/ColumnIn` 初值 |
| 线 | `draw_line` | `draw_line_mod` | 输出两个端点 |
| 矩形（轴对齐） | `draw_rectangle1` | `draw_rectangle1_mod` | 左上 + 右下角 |
| 矩形（带角度） | `draw_rectangle2` | `draw_rectangle2_mod` | 输出 (Row, Col, Phi, Length1, Length2) |
| 圆 | `draw_circle` | `draw_circle_mod` | 输出 3 元 |
| 椭圆 | `draw_ellipse` | `draw_ellipse_mod` | 输出 5 元 |
| 折线 | `draw_polygon` | —— | 不带 mod 版（折线自带撤销/重启能力） |
| NURBS（控制） | `draw_nurbs` | `draw_nurbs_mod` | 输出控制点 + 权重 |
| NURBS（插值） | `draw_nurbs_interp` | `draw_nurbs_interp_mod` | 输出节点序列（Knots） |
| Region | `draw_region` | —— | 程序绘 Region，需先 `gen_region_*` |
| XLD | `draw_xld` | `draw_xld_mod` | 自由曲线轮廓 |

### 3.4 一定要会的参数：`Rotate` / `Move` / `Scale` / `KeepRatio`

`draw_*_mod` 与 `draw_nurbs*` 系列都有：

```
draw_rectangle2_mod ( : : WindowHandle , RowIn , ColumnIn , PhiIn , Length1In , Length2In
                          : Row , Column , Phi , Length1 , Length2 )
```

| 参数 | 含义 | 典型取值 |
|---|---|---|
| `Rotate` | 用户能否用 **右拖** 旋转 | `'true'` / `'false'` |
| `Move` | 用户能否 **左拖** 平移 | `'true'` / `'false'` |
| `Scale` | 用户能否按住 Shift 等改变大小 | `'true'` / `'false'` |
| `KeepRatio` | 矩形缩放是否保持宽高比 | `'true'` / `'false'` |
| `Edit` | NURBS 是否允许鼠标右键调节点 | `'true'` / `'false'` |

经验：**几乎永远全开**（都 `'true'`），体验与商业 OCR/标定工具一致。

### 3.5 `drag_region*` 三件套

| 函数 | 输入 Region 的位置轴 | 输出 |
|---|---|---|
| `drag_region1` | 仅 Row/Column | 仿射后 Region |
| `drag_region2` | + Phi | 同样，但带一个旋转自由度 |
| `drag_region3` | 完整 6 自由度 | 投影变换 |

用于**测量编辑**：让用户**手动拽**程序生成的 Region 到正确位置，再喂给后续算法。

### 3.6 关键签名（一行版）

```
draw_circle (WindowHandle, Row, Column, Radius)
draw_rectangle2 ( : : WindowHandle : Row , Column , Phi , Length1 , Length2 )
draw_nurbs_interp ( : ContOut : WindowHandle , Rotate , Move , Scale , KeepRatio , Degree
                       : ControlRows , ControlCols , Knots , Rows , Cols , Tangents )
drag_region2 ( SourceRegion : DestinationRegion : WindowHandle , Row , Column : )
draw_xld_mod ( ContIn : ContOut : WindowHandle , Rotate , Move , Scale , KeepRatio , Edit : )
```

---

## 4. 子族 3 · LUT（3 ops · 颜色查找表）

### 4.1 设计目的

**单通道灰度图**（如深度图、热力图、显著性图）→ **彩色显示**的廉价映射方法。HALCON 的窗口支持把每个灰度值通过 256 长的 LUT 映射到 RGB：
- **热图**（黑→红→黄→白）；
- **彩虹**（蓝→青→绿→黄→红）；
- **等高线伪彩**（连续色带）。

### 4.2 三件套

| 函数 | 作用 | 备注 |
|---|---|---|
| `set_lut` | 设置当前窗口 LUT | 单参数 `LookUpTable` 是一组 H 字节长度 256*3（RGB 共 256 级） |
| `get_lut` | 取当前窗口 LUT | 用于保存/拷贝当前显示风格 |
| `query_lut` | 查询系统可用 LUT 名列表 | 返回字符串元组，每个对应一种内置色带 |

### 4.3 关键签名

```
set_lut ( : : WindowHandle , LookUpTable : )
get_lut ( : : WindowHandle : LookUpTable )
query_lut ( : : WindowHandle : LookUpTable )
```

### 4.4 常见用法

```hdevelop
query_lut (WindowHandle, LUTNames)        * 查所有 LUT 名
* 选 'sqrt'（常用伪彩）→ 查询索引
get_lut (WindowHandle, CurrentLUT)        * 备份当前
set_lut (WindowHandle, LUTNames[0])       * 应用某个内置 LUT
```

---

## 5. 子族 4 · Mouse（11 ops · 鼠标输入与事件注入）

### 5.1 设计目的

两条主线：

1. **读鼠标** —— `get_m*` 函数：阻塞/非阻塞地获取鼠标 **按键、位置、光标形状**；
2. **写鼠标** —— `send_mouse_*` 函数：**程序模拟**鼠标事件，给无头/自动化场景用。

### 5.2 读 vs 写 速查

| 类别 | 算子 |
|---|---|
| 阻塞读键位 | `get_mbutton` / `get_mbutton_sub_pix` |
| 非阻塞读坐标 | `get_mposition` / `get_mposition_sub_pix` |
| 读光标形状 | `get_mshape` / `query_mshape` |
| 写光标形状 | `set_mshape` |
| 注入鼠标事件 | `send_mouse_down_event` / `send_mouse_up_event` / `send_mouse_drag_event` / `send_mouse_double_click_event` |

### 5.3 `sub_pix` 与非 `sub_pix` 的差别

HALCON 内部窗口坐标系为浮点（sub-pixel），是否返回浮点影响后续算子的精度选择：

- `get_mposition` → `(Row, Column)` 整数；
- `get_mposition_sub_pix` → `(Row, Column)` 浮点；
- 同样适用于 `get_mbutton`。

> **经验**：做精密测量（如 subpixel 配准）就用 `sub_pix` 版本，否则像素整数即可。

### 5.4 `send_mouse_*_event` 的 Processed 含义

```
send_mouse_down_event ( : : WindowHandle , Row , Column , Button : Processed )
```

最后一参 `Processed` 表示 **HALCON 是否成功分发** 这个事件到窗口的回调（`Processed := 'true'`）。若仍为 `'false'`，通常说明：

- 窗口已被 `close_window` 或尚未 `open_window`；
- 回调列表里没有接受此事件的回调；
- 按钮编号在系统约定之外（如非 1/2/3）。

### 5.5 关键签名

```
get_mposition_sub_pix ( : : WindowHandle : Row , Column , Button )
set_mshape ( : : WindowHandle , Cursor : )
send_mouse_drag_event ( : : WindowHandle , Row , Column , Button : Processed )
query_mshape ( : : WindowHandle : ShapeNames )
```

---

## 6. 子族 5 · Object（21 ops · 绘图对象）

### 6.1 设计目的

`Object` 子族是 **Drawing 子族的工程化升级**：把"画什么"抽象成 **句柄** `DrawID`，可附加 **回调** / **修改参数** / **绑定窗口** / **跨语言导出**。

- Drawing 是同步阻塞式：**单次画 → 单次拿几何**；
- Object 是 **生命周期式**：可以长时间存在某个句柄上 **反复响应鼠标**。

### 6.2 五种绘制对象

| 工厂函数 | 几何 | 主要参数 |
|---|---|---|
| `create_drawing_object_circle` | 圆 | Row, Column, Radius |
| `create_drawing_object_circle_sector` | 圆扇形 | + StartAngle, EndAngle |
| `create_drawing_object_ellipse` | 椭圆 | + Phi, Radius1, Radius2 |
| `create_drawing_object_ellipse_sector` | 椭圆扇形 | + StartAngle, EndAngle |
| `create_drawing_object_line` | 线段 | 两个端点 |
| `create_drawing_object_rectangle1` | 轴对齐矩形 | 两个对角 |
| `create_drawing_object_rectangle2` | 带角度矩形 | (Row, Column, Phi, Length1, Length2) |
| `create_drawing_object_text` | 文本 | Row, Column, String |
| `create_drawing_object_xld` | XLD 自由轮廓 | 注入 XLD：`set_drawing_object_xld` |

### 6.3 生命周期：create → attach → callback → query → detach

```
  create_drawing_object_rectangle2 ( : : Row , Column , Phi , Length1 , Length2
                                     : DrawID )
                              │
                              ▼
  set_drawing_object_callback  ( : : DrawHandle , DrawObjectEvent ,
                                    CallbackFunction : )
                              │
                              ▼
  attach_drawing_object_to_window ( : : WindowHandle , DrawHandle : )
                              │
                              ▼
       [用户拖动 / 修改 → 回调触发]
                              │
                              ▼
  get_drawing_object_params  ( : : DrawID , GenParamName : GenParamValue )
                              │
                              ▼
  detach_drawing_object_from_window ( : : WindowHandle , DrawHandle : )
```

`set_drawing_object_callback` 接受以下事件名：

| 事件名 | 触发时机 |
|---|---|
| `'on_attach'` | 绑定窗口时 |
| `'on_detach'` | 解绑窗口时 |
| `'on_drag'` | 鼠标拖动对象时 |
| `'on_resize'` | 鼠标缩放对象时 |
| `'on_select'` | 鼠标点选对象时 |
| `'on_change'` | 任何几何/属性变化后 |

回调函数签名为 `(Row, Column, GenParamName, GenParamValue) → ([Result], ['stop'|'continue'])`。

### 6.4 `get_drawing_object_iconic` 的妙用

把绘图对象"翻译"为 Region/XLD：

```
get_drawing_object_iconic ( : Object : DrawID : )
```

然后可直接 `gen_contours_skeleton_from_xld` / `dilation_circle` 等等价 ROI 算子 —— **GUI 取点 → 几何对象 → 后处理** 一气呵成。

### 6.5 `set_content_update_callback`：`Object` 与 `Window` 子族的桥梁

`set_content_update_callback` 严格说属于 Graphics · 下卷的 Window 子族，但已在 **本卷 Object 文档**中提到——它用来注册 **窗口内容更新** 回调（区别于绘图对象回调）：

```
set_content_update_callback ( : : WindowHandle , CallbackFunction , CallbackContext : )
```

> 提醒：可见 HALCON 把"对窗口的反应"分两层——
> ① **绘图对象**（Object 子族）针对单个 ROI；
> ② **窗口整体**（Window 子族，下卷）针对重绘/重渲染。

### 6.6 关键签名

```
create_drawing_object_rectangle2 ( : : Row , Column , Phi , Length1 , Length2 : DrawID )
attach_drawing_object_to_window ( : : WindowHandle , DrawHandle : )
set_drawing_object_callback     ( : : DrawHandle , DrawObjectEvent , CallbackFunction : )
get_drawing_object_iconic       ( : Object : DrawID : )
set_drawing_object_xld          ( Contour : : DrawID : )
get_drawing_object_params       ( : : DrawID , GenParamName : GenParamValue )
```

---

## 7. 五族关系图

```
        ┌────────────────────┐
        │   HALCON Window   │  ← Graphics · 下卷 Window 子族
        └─────────▲──────────┘
                  │ attaches/detaches
                  │
        ┌─────────┴──────────┐
        │   Drawing Object   │  ← Object 子族（21 ops）
        └─▲──────────────────┘
          │ callback
          │
   ┌──────┴────────┐         ┌────────────┐
   │  Drawing 系列 │         │  Mouse 系列│  ← Drawing（23）+ Mouse（11）
   └───────────────┘         └──────┬─────┘
                                   │ (读取鼠标事件)
                                   │
                          ┌────────▼────────┐
                          │    LUT / 3D     │  ← LUT（3）+ 3D Scene（20）
                          └─────────────────┘
```

- **Object** 是 Drawing 的 **句柄化升级** —— 同样画圆，一个 `draw_circle`（瞬时），一个 `create_drawing_object_circle`（长期绑定）。
- **Mouse** 是 **Drawing/Object 的事件源**。
- **3D Scene** 独立但需要 Window 容器（与 Window 子族协作）。
- **LUT** 作用于窗口的 **像素值→显示颜色** 通路。

---

## 8. 五语言对照速查（以 `draw_rectangle2` 为例）

| 语言 | 函数（粗体为入口点） | 一次性 vs 句柄版 |
|---|---|---|
| HDevelop | `draw_rectangle2(...)`（直接调用） | 一次性 |
| C | `void draw_rectangle2(Hlong WindowHandle, double *Row, double *Column, double *Phi, double *Length1, double *Length2);` | 一次性 |
| C++ | `void DrawRectangle2(const HTuple& WindowHandle, HTuple* Row, HTuple* Column, HTuple* Phi, HTuple* Length1, HTuple* Length2);` | 一次性 |
| .NET (C# / VB) | `HDevEngine` 或 HALCON `.NET` 的 `HWindow.DrawRectangle2(...)` | 一次性 |
| Python | 同 `halcon.importang` 导出 `draw_rectangle2(...)` | 一次性 |
| HDevProcedure | `draw_rectangle2_mod(...)`（句柄版） | 句柄 + 回调 |

> HALCON 5 语言本身的命名约定：HDevelop 一律小写+下划线；C/C++ 是动词+名词；.NET 是 PascalCase；Python 同 HDevelop；HDevProc 是带 `_mod`/`create_*_object` 等 OO 化变体。

---

## 9. 常见误区与最佳实践

| # | 误区 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | **`draw_*` 接受键盘开始（如回车）** | 部分情况下不触发回调 | 显式提示用户 **单击左键完成** |
| 2 | **用 `get_mposition` 测亚像素** | 整数 → 测量误差大 | `get_mposition_sub_pix` |
| 3 | **`display_scene_3d` 未先 `open_window`** | 段错误 | `dev_open_window` 或 `open_window` 显式创建 |
| 4 | **LUT 应用后图像没更新** | set_lut 只对**后续 disp**有效 | `disp_image` 之后再 `set_lut`，或加 `disp_redraw` |
| 5 | **同一 DrawID attach 两次窗口** | 句柄状态错乱 | 先 `detach_drawing_object_from_window` |
| 6 | **`set_drawing_object_callback` 用错事件名** | 回调从不触发 | 严格 `'on_drag'` 等小写串，参考官方 Chapter 13.6 |
| 7 | **`draw_*_mod` 不传 `Rotate`/`Move`/`Scale`** | 默认 `'true'`，但有时会显式给 `'false'` 让用户锁死 | 不要传 `'false'` 强行限制（除非必要） |
| 8 | **`send_mouse_down_event` 在 headless 模式** | 无窗口导致 `Processed = false` | 检查 `dev_open_window` 是否真的开窗 |
| 9 | **Drawing + Object 混用** | 同步阻塞 `draw_*` 在 Object 回调里不工作 | 回调内仅做 **`get_drawing_object_params`** / 几何计算 |
| 10 | **未 `clear_drawing_object` 就调整** | 旧几何残留导致 `set_drawing_object_xld` 结果错乱 | 仅在构造后 OK，调几何用 `set_drawing_object_params` |

---

## 10. 完整签名速查（78 ops · 算子 | 一句话功能 | HDevelop 关键签名）

> 表头：算子 · 一句话功能 · HDevelop 签名（精简版，参数全展开可回原稿第 12 节）

### 10.1 3D Scene（20）

| 算子 | 一句话功能 | HDevelop 签名（核心节选） |
|---|---|---|
| `add_scene_3d_camera` | 向场景添加相机 | `add_scene_3d_camera ( : : Scene3D , CameraParam : CameraIndex )` |
| `add_scene_3d_instance` | 向场景添加 3D 实例 | `add_scene_3d_instance ( : : Scene3D , ObjectModel3D , Pose : InstanceIndex )` |
| `add_scene_3d_label` | 向场景添加文本标签 | `add_scene_3d_label ( : : Scene3D , Text , ReferencePoint , Position , RelatesTo : LabelIndex )` |
| `add_scene_3d_light` | 向场景添加光源 | `add_scene_3d_light ( : : Scene3D , LightPosition , LightKind : LightIndex )` |
| `clear_scene_3d` | 清空场景全部对象 | `clear_scene_3d ( : : Scene3D : )` |
| `create_scene_3d` | 新建 3D 场景句柄 | `create_scene_3d ( : : : Scene3D )` |
| `display_scene_3d` | 在窗口中显示 3D 场景 | `display_scene_3d ( : : WindowHandle , Scene3D , CameraIndex : )` |
| `get_display_scene_3d_info` | 从已显示场景拾取信息 | `get_display_scene_3d_info ( : : WindowHandle , Scene3D , Row , Column , Information : Value )` |
| `remove_scene_3d_camera` | 移除指定相机 | `remove_scene_3d_camera ( : : Scene3D , CameraIndex : )` |
| `remove_scene_3d_instance` | 移除指定实例 | `remove_scene_3d_instance ( : : Scene3D , InstanceIndex : )` |
| `remove_scene_3d_label` | 移除指定标签 | `remove_scene_3d_label ( : : Scene3D , LabelIndex : )` |
| `remove_scene_3d_light` | 移除指定光源 | `remove_scene_3d_light ( : : Scene3D , LightIndex : )` |
| `render_scene_3d` | 渲染 3D 到图像 | `render_scene_3d ( : Image : Scene3D , CameraIndex : )` |
| `set_scene_3d_camera_pose` | 设相机位姿 | `set_scene_3d_camera_pose ( : : Scene3D , CameraIndex , Pose : )` |
| `set_scene_3d_instance_param` | 设实例属性 | `set_scene_3d_instance_param ( : : Scene3D , InstanceIndex , GenParamName , GenParamValue : )` |
| `set_scene_3d_instance_pose` | 设实例位姿 | `set_scene_3d_instance_pose ( : : Scene3D , InstanceIndex , Pose : )` |
| `set_scene_3d_label_param` | 设标签属性 | `set_scene_3d_label_param ( : : Scene3D , LabelIndex , GenParamName , GenParamValue : )` |
| `set_scene_3d_light_param` | 设光源属性 | `set_scene_3d_light_param ( : : Scene3D , LightIndex , GenParamName , GenParamValue : )` |
| `set_scene_3d_param` | 设场景全局属性 | `set_scene_3d_param ( : : Scene3D , GenParamName , GenParamValue : )` |
| `set_scene_3d_to_world_pose` | 设场景到世界坐标 | `set_scene_3d_to_world_pose ( : : Scene3D , ToWorldPose : )` |

### 10.2 Drawing（23）

| 算子 | 一句话功能 | HDevelop 签名（核心节选） |
|---|---|---|
| `drag_region1` | 拖拽 Region（位置） | `drag_region1(Obj, New, WindowHandle)` |
| `drag_region2` | 拖拽 Region（+角度） | `drag_region2 ( SourceRegion : DestinationRegion : WindowHandle , Row , Column : )` |
| `drag_region3` | 拖拽 Region（+仿射） | `drag_region3 ( SourceRegion , MaskRegion : DestinationRegion : WindowHandle , Row , Column : )` |
| `draw_circle` | 画圆（同步） | `draw_circle(WindowHandle, Row, Column, Radius)` |
| `draw_circle_mod` | 画圆（叠加） | `draw_circle_mod(WindowHandle,20,20,15, Row, Column, Radius)` |
| `draw_ellipse` | 画椭圆（同步） | `draw_ellipse(WindowHandle, Row, Column, Phi, Radius1, Radius2)` |
| `draw_ellipse_mod` | 画椭圆（叠加） | `draw_ellipse_mod ( : : WindowHandle , RowIn , ColumnIn , PhiIn , Radius1In , Radius2In : Row , Column , Phi , Radius1 , Radius2 )` |
| `draw_line` | 画直线（同步） | `draw_line(WindowHandle, Row1, Column1, Row2, Column2)` |
| `draw_line_mod` | 画直线（叠加） | `draw_line_mod(WindowHandle,10,20,55,124, Row1, Column1, Row2, Column2)` |
| `draw_nurbs` | 画 NURBS（控制点） | `draw_nurbs ( : ContOut : WindowHandle , Rotate , Move , Scale , KeepRatio , Degree : Rows , Cols , Weights )` |
| `draw_nurbs_interp` | 画 NURBS（插值） | `draw_nurbs_interp ( : ContOut : WindowHandle , Rotate , Move , Scale , KeepRatio , Degree : ControlRows , ControlCols , Knots , Rows , Cols , Tangents )` |
| `draw_nurbs_interp_mod` | 画 NURBS（叠加插值） | `draw_nurbs_interp_mod ( : ContOut : WindowHandle , Rotate , Move , Scale , KeepRatio , Edit , Degree , RowsIn , ColsIn , TangentsIn : ControlRows , ControlCols , Knots , Rows , Cols , Tangents )` |
| `draw_nurbs_mod` | 画 NURBS（叠加） | `draw_nurbs_mod ( : ContOut : WindowHandle , Rotate , Move , Scale , KeepRatio , Edit , Degree , RowsIn , ColsIn , WeightsIn : Rows , Cols , Weights )` |
| `draw_point` | 画点（同步） | `draw_point(WindowHandle, Row, Column)` |
| `draw_point_mod` | 画点（叠加） | `draw_point_mod ( : : WindowHandle , RowIn , ColumnIn : Row , Column )` |
| `draw_polygon` | 画多边形行 | `draw_polygon(Polygon, WindowHandle)` |
| `draw_rectangle1` | 画轴对齐矩形 | `draw_rectangle1(WindowHandle, Row1, Column1, Row2, Column2)` |
| `draw_rectangle1_mod` | 画轴对齐矩形（叠加） | `draw_rectangle1_mod ( : : WindowHandle , Row1In , Column1In , Row2In , Column2In : Row1 , Column1 , Row2 , Column2 )` |
| `draw_rectangle2` | 画带角度矩形 | `draw_rectangle2 ( : : WindowHandle : Row , Column , Phi , Length1 , Length2 )` |
| `draw_rectangle2_mod` | 画带角度矩形（叠加） | `draw_rectangle2_mod ( : : WindowHandle , RowIn , ColumnIn , PhiIn , Length1In , Length2In : Row , Column , Phi , Length1 , Length2 )` |
| `draw_region` | 描 Region 轮廓 | `draw_region(Region, WindowHandle)` |
| `draw_xld` | 描 XLD 轮廓 | `draw_xld ( : ContOut : WindowHandle , Rotate , Move , Scale , KeepRatio : )` |
| `draw_xld_mod` | 描 XLD（叠加） | `draw_xld_mod ( ContIn : ContOut : WindowHandle , Rotate , Move , Scale , KeepRatio , Edit : )` |

### 10.3 LUT（3）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `get_lut` | 读当前 LUT | `get_lut ( : : WindowHandle : LookUpTable )` |
| `query_lut` | 列可用 LUT | `query_lut ( : : WindowHandle : LookUpTable )` |
| `set_lut` | 写 LUT | `set_lut(WindowHandle, LUTs[i])` |

### 10.4 Mouse（11）

| 算子 | 一句话功能 | HDevelop 签名（核心节选） |
|---|---|---|
| `get_mbutton` | 阻塞读鼠标键 | `get_mbutton ( : : WindowHandle : Row , Column , Button )` |
| `get_mbutton_sub_pix` | 阻塞读鼠标键（亚像素） | `get_mbutton_sub_pix ( : : WindowHandle : Row , Column , Button )` |
| `get_mposition` | 非阻塞读坐标 | `get_mposition ( : : WindowHandle : Row , Column , Button )` |
| `get_mposition_sub_pix` | 非阻塞读坐标（亚像素） | `get_mposition_sub_pix ( : : WindowHandle : Row , Column , Button )` |
| `get_mshape` | 读光标形状 | `get_mshape ( : : WindowHandle : Cursor )` |
| `query_mshape` | 列可用光标 | `query_mshape ( : : WindowHandle : ShapeNames )` |
| `send_mouse_double_click_event` | 注入双击 | `send_mouse_double_click_event ( : : WindowHandle , Row , Column , Button : Processed )` |
| `send_mouse_down_event` | 注入按下 | `send_mouse_down_event ( : : WindowHandle , Row , Column , Button : Processed )` |
| `send_mouse_drag_event` | 注入拖拽 | `send_mouse_drag_event ( : : WindowHandle , Row , Column , Button : Processed )` |
| `send_mouse_up_event` | 注入抬起 | `send_mouse_up_event ( : : WindowHandle , Row , Column , Button : Processed )` |
| `set_mshape` | 写光标形状 | `set_mshape ( : : WindowHandle , Cursor : )` |

### 10.5 Object（21）

| 算子 | 一句话功能 | HDevelop 签名（核心节选） |
|---|---|---|
| `attach_background_to_window` | 挂背景图像 | `attach_background_to_window ( Image : : WindowHandle : )` |
| `attach_drawing_object_to_window` | 绑绘图对象 | `attach_drawing_object_to_window ( : : WindowHandle , DrawHandle : )` |
| `clear_drawing_object` | 清空对象 | `clear_drawing_object ( : : DrawID : )` |
| `create_drawing_object_circle` | 建圆形对象 | `create_drawing_object_circle ( : : Row , Column , Radius : DrawID )` |
| `create_drawing_object_circle_sector` | 建扇形对象 | `create_drawing_object_circle_sector ( : : Row , Column , Radius , StartAngle , EndAngle : DrawID )` |
| `create_drawing_object_ellipse` | 建椭圆对象 | `create_drawing_object_ellipse ( : : Row , Column , Phi , Radius1 , Radius2 : DrawID )` |
| `create_drawing_object_ellipse_sector` | 建椭圆扇形对象 | `create_drawing_object_ellipse_sector ( : : Row , Column , Phi , Radius1 , Radius2 , StartAngle , EndAngle : DrawID )` |
| `create_drawing_object_line` | 建线段对象 | `create_drawing_object_line ( : : Row1 , Column1 , Row2 , Column2 : DrawID )` |
| `create_drawing_object_rectangle1` | 建轴对齐矩形对象 | `create_drawing_object_rectangle1 ( : : Row1 , Column1 , Row2 , Column2 : DrawID )` |
| `create_drawing_object_rectangle2` | 建带角度矩形对象 | `create_drawing_object_rectangle2 ( : : Row , Column , Phi , Length1 , Length2 : DrawID )` |
| `create_drawing_object_text` | 建文本对象 | `create_drawing_object_text ( : : Row , Column , String : DrawID )` |
| `create_drawing_object_xld` | 建 XLD 对象 | `create_drawing_object_xld ( : : Row , Column : DrawID )` |
| `detach_background_from_window` | 解挂背景 | `detach_background_from_window ( : : WindowHandle : )` |
| `detach_drawing_object_from_window` | 解绑对象 | `detach_drawing_object_from_window ( : : WindowHandle , DrawHandle : )` |
| `get_drawing_object_iconic` | 取对象几何 | `get_drawing_object_iconic ( : Object : DrawID : )` |
| `get_drawing_object_params` | 查对象属性 | `get_drawing_object_params ( : : DrawID , GenParamName : GenParamValue )` |
| `get_window_background_image` | 取窗口背景 | `get_window_background_image ( : BackgroundImage : WindowHandle : )` |
| `set_content_update_callback` | 设窗口刷新回调 | `set_content_update_callback ( : : WindowHandle , CallbackFunction , CallbackContext : )` |
| `set_drawing_object_callback` | 设对象回调 | `set_drawing_object_callback ( : : DrawHandle , DrawObjectEvent , CallbackFunction : )` |
| `set_drawing_object_params` | 改对象属性 | `set_drawing_object_params ( : : DrawID , GenParamName , GenParamValue : )` |
| `set_drawing_object_xld` | 注入 XLD | `set_drawing_object_xld ( Contour : : DrawID : )` |

---

## 11. 与 Graphics · 下卷的衔接

- 16 个 **Output 算子**（窗口内容 dump / save_image 系等）—— 下卷
- 38 个 **Parameters 算子**（全局显示参数查询与设置）—— 下卷
- 12 个 **Text 算子**（窗口文字渲染，覆盖 `set_tposition` / `write_string` 等）—— 下卷
- 21 个 **Window 算子**（窗口生命周期、`dev_open_window` 等）—— 下卷

下卷合计 87 ops，与本卷合起来正好是 HALCON Graphics 章节的 **165 算子总数**。

> **本卷的工作流尾巴**：把 Window 子族学到手后，可以完成 `dev_open_window` → `create_drawing_object_rectangle2` → `attach_drawing_object_to_window` → `set_drawing_object_callback` → 用户拖动 → `get_drawing_object_iconic` → `gen_region_polygon` → 测量 ROI 的 **完整闭环**，这是 Graphics 章节最常见的 HALCON GUI 模式。

---

> **文档版本**：HALCON 20.11.1.0。结构与索引随官方手册更新而变化。
> **编译日期**：2026-08-22。配套思维导图 PNG 见同目录 `12-滤波(中).png`（no — 见 `13-Graphics(上).png`）。
