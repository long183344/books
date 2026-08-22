# 第 13 章 Graphics（下卷）· 窗口系统 + 输出

> HALCON 20.11.1.0 Operator Reference — Graphics 章节下半部分
> 上卷 = 主动绘图 + 交互（3D Scene / Drawing / LUT / Mouse / Object，78 ops）
> **本卷 = 窗口系统 + 输出（Output / Parameters / Text / Window，87 ops）**

---

## 0. 本卷定位

上卷解决"画什么、怎么画、怎么交互"，本卷解决"画在哪里、以什么样式画、文字怎么写、窗口怎么管"。

- **Output（16）**：把图形原语（`disp_*`）直接画到窗口——圆、线、矩形、箭头、XLD、3D 模型等。这是最底层的"显示动作"。
- **Parameters（38）**：控制"怎么画"的样式与状态——颜色、线宽、填充、绘制模式、坐标映射（`set_*` / `get_*` / `query_*`），以及图像↔窗口坐标换算。
- **Text（12）**：文本绘制与度量——`disp_text` 推荐新接口，`write_string`/`read_string` 为经典光标式接口。
- **Window（21）**：窗口全生命周期——`open_window` / `close_window` / 属性查询 / 导出 / 3D 姿态。

> 一句话记忆：**Output 是笔，Parameters 是笔的样式，Text 是另一种笔，Window 是纸。**

---

## 1. 四族速览

| 族 | 算子数 | 一句话定位 | 代表算子 |
|---|---|---|---|
| **Output** | 16 | 把图形原语画到窗口 | `disp_image` `disp_region` `disp_obj` `disp_xld` `disp_object_model_3d` |
| **Parameters** | 38 | 控制绘制样式与坐标映射 | `set_color` `set_draw` `set_part` `set_line_width` `convert_coordinates_*` |
| **Text** | 12 | 文本绘制与度量 | `disp_text` `set_font` `write_string` `read_string` |
| **Window** | 21 | 窗口管理与导出 | `open_window` `close_window` `dump_window` `update_window_pose` |
| **合计** | **87** | | |

---

## 2. Output 族（16 算子）— 图形显示原语

**用途**：将图像、区域、XLD、3D 对象模型等"画"到指定窗口。`WindowHandle` 是几乎所有 `disp_*` 的必填输入。

### 2.1 显示原语一览

| 算子 | 一句话功能 | 核心参数 |
|---|---|---|
| `disp_image` | 显示图像（最基础） | `Image`, `WindowHandle` |
| `disp_color` | 彩色显示多通道图像 | `ColorImage` |
| `disp_channel` | 显示单通道 | `MultichannelImage`, `Channel` |
| `disp_region` | 显示区域（按 color/draw 着色） | `DispRegions` |
| `disp_obj` | 通用显示图标对象（分派到图像/区域/XLD） | `Object` |
| `disp_xld` | 显示 XLD 轮廓/多边形 | `XLDObject` |
| `disp_object_model_3d` | 显示 3D 对象模型 | `ObjectModel3D`, `CamParam`, `Pose` |
| `disp_arc` | 绘制圆弧 | `CenterRow/Col`, `Angle`, `BeginRow/Col` |
| `disp_arrow` | 带箭头线段 | `Row1/Col1 → Row2/Col2`, `Size` |
| `disp_circle` | 绘制圆 | `Row`, `Column`, `Radius` |
| `disp_cross` | 十字标记 | `Row`, `Column`, `Size`, `Angle` |
| `disp_ellipse` | 绘制椭圆 | `CenterRow/Col`, `Phi`, `Radius1/2` |
| `disp_line` | 直线段 | `Row1/Col1 → Row2/Col2` |
| `disp_polygon` | 多边形（顶点序列） | `Row[]`, `Column[]` |
| `disp_rectangle1` | 平行矩形 | `Row1/Col1/Row2/Col2` |
| `disp_rectangle2` | 旋转矩形 | `CenterRow/Col`, `Phi`, `Length1/2` |

### 2.2 重点算子

**`disp_image ( Image : : WindowHandle : )`**
最基础的显示算子。显示样式由 `set_part`（缩放映射）、`set_color`/`set_draw` 等控制。通常流程：`read_image` → `dev_open_window`（或 `open_window`）→ `disp_image`。

**`disp_obj ( Object : : WindowHandle : )`**
通用显示入口：传入图像、区域或 XLD 都能正确渲染（内部按对象类型分派）。在写通用可视化工具时优先用它，避免对类型做分支判断。注意它与 `dev_display` 的区别：`dev_display` 作用于"活动窗口"，`disp_obj` 显式指定 `WindowHandle`。

**`disp_object_model_3d ( : : WindowHandle, ObjectModel3D, CamParam, Pose, GenParamName, GenParamValue : )`**
在窗口中渲染 3D 对象模型。需要相机内参 `CamParam` 与姿态 `Pose`，并可经 `GenParamName/GenParamValue` 调点大小、着色模式等。与"上卷"的 3D Scene 不同：`disp_object_model_3d` 是"一次性显示单个模型"，而 `Scene3D` 是"构建一个可交互、多对象的场景"。

> 样式控制提示：圆的填充/边缘取决于 `set_draw`（'fill' 实心 / 'margin' 描边）；颜色取决于 `set_color` / `set_colored`。

---

## 3. Parameters 族（38 算子）— 绘制样式与坐标映射

**用途**：决定"怎么画"。分成 4 类：
1. **样式设置** `set_*`：颜色、线宽、绘制模式、填充、图标、形状、轮廓样式、窗口参数。
2. **样式查询** `get_*`：读回当前设置。
3. **能力查询** `query_*`：枚举该窗口支持的选项（颜色名、线宽范围、形状集合等）。
4. **坐标换算** `convert_coordinates_*`：图像坐标 ↔ 窗口坐标（含 `set_part` 缩放）。

### 3.1 样式设置/查询对照表

| 设置 `set_*` | 查询 `get_*` | 控制什么 |
|---|---|---|
| `set_color` | — | 单色（'red'/'#ff0000'...） |
| `set_colored` | — | 多色循环（N 色自动分配） |
| `set_rgb` | `get_rgb` | RGB 三元组 |
| `set_rgba` | `get_rgba` | RGBA（含 alpha 透明） |
| `set_hsi` | `get_hsi` | HSI 颜色空间 |
| `set_gray` | — | 灰度值 |
| `set_draw` | `get_draw` | 'fill' / 'margin' |
| `set_line_width` | `get_line_width` | 线宽 |
| `set_line_style` | `get_line_style` | 点划线定义 |
| `set_contour_style` | `get_contour_style` | XLD 轮廓样式 |
| `set_paint` | `get_paint` | 区域填充方式 |
| `set_shape` | `get_shape` | 区域形状（original/rectangle1/ellipse...） |
| `set_icon` | `get_icon` | 区域图标 |
| `set_part` | `get_part` | 图像→窗口的缩放映射矩形 |
| `set_part_style` | `get_part_style` | 部分图像样式 |
| `set_window_param` | `get_window_param` | 窗口级参数（抗锯齿/背景等） |

### 3.2 能力查询 `query_*`

| 算子 | 返回 |
|---|---|
| `query_all_colors` | 全部可用颜色名 |
| `query_color` | 支持的颜色 |
| `query_colored` | 'colored' 模式支持的颜色数（无 WindowHandle） |
| `query_gray` | 灰度值范围 |
| `query_line_width` | 线宽范围 `Min, Max` |
| `query_paint` | 可用填充方式 |
| `query_shape` | 可用区域形状 |
| `query_window_type` / `query_font` | 窗口类型 / 字体列表 |

> 注意 `query_colored` / `query_line_width` / `query_shape` 的签名**没有 WindowHandle**（全局能力），而 `query_color` / `query_paint` 等需要 `WindowHandle`。

### 3.3 坐标换算（重点）

**`convert_coordinates_image_to_window ( : : WindowHandle, RowImage, ColumnImage : RowWindow, ColumnWindow )`**
把图像坐标（行列）换算成窗口像素坐标。内部考虑了 `set_part` 设定的缩放与平移（即"图像哪一块映射到窗口哪一块"）。做交互拾取（鼠标坐标 → 图像坐标）时必用其反向版本。

**`convert_coordinates_window_to_image ( : : WindowHandle, RowWindow, ColumnWindow : RowImage, ColumnImage )`**
反向换算。典型用途：鼠标点击得到窗口坐标 → 换算成图像坐标 → 在该位置取灰度/区域。

> 关键坑：如果没调用 `set_part`，窗口坐标默认等于图像坐标（1:1）；一旦 `set_part` 做了缩放（例如把大图缩放到窗口），必须用这两个换算算子，否则拾取位置错位。

---

## 4. Text 族（12 算子）— 文本绘制与度量

**用途**：在窗口上写文字、量字体、读交互输入。

### 4.1 两类文本接口

| 类型 | 算子 | 说明 |
|---|---|---|
| **推荐新接口** | `disp_text` | 一次调用在指定位置显示文本，支持坐标系/颜色/通用参数，无需先 `set_tposition` |
| **经典光标接口** | `set_tposition` → `write_string` → `new_line` | 先定位文本光标，再写、换行 |
| 字体 | `set_font` / `get_font` / `query_font` | 设置/查询/枚举字体（含大小，如 'mono 14'） |
| 度量 | `get_font_extents` / `get_string_extents` | 字体整体度量 / 单字符串像素尺寸 |
| 光标查询 | `get_tposition` | 读取当前文本光标位置 |
| 交互输入 | `read_char` / `read_string` | 从窗口阻塞读取用户输入（字符/字符串） |

### 4.2 重点算子

**`disp_text ( : : WindowHandle, String, CoordSystem, Row, Column, Color, GenParamName, GenParamValue : )`**
HALCON 推荐的文本显示方式。亮点：
- `CoordSystem` 可设 `'window'`（窗口坐标）或 `'image'`（图像坐标，自动随 `set_part` 缩放）。
- `Row`/`Column` 支持 `'left'`/`'top'`/`'right'`/`'bottom'` 等字符串做自动对齐。
- `GenParamName/Value` 可传 `'box'`、`'shadow'` 等做背景框/阴影。

**`write_string ( : : WindowHandle, String : )` + `set_tposition` / `new_line`**
经典光标式写法：`set_tposition` 定位 → `write_string` 输出 → `new_line` 下移。适合逐行打印日志式文本。注意光标位置以窗口坐标为准。

**`read_string ( : : WindowHandle, InString, Length : OutString )`**
阻塞等待用户在窗口输入字符串，`InString` 为默认回显值，`Length` 限制最大长度。用于简单的图形界面交互（不推荐做复杂 UI，复杂交互用 HDevelop 的 GUI 或外部程序）。

---

## 5. Window 族（21 算子）— 窗口管理

**用途**：窗口的创建、销毁、属性、像素访问、内容导出，以及 3D 窗口姿态。

### 5.1 生命周期与导出

| 算子 | 一句话功能 |
|---|---|
| `open_window` | 打开窗口，返回 `WindowHandle` |
| `close_window` | 关闭窗口、释放句柄 |
| `clear_window` | 清空（填背景色） |
| `copy_rectangle` | 窗口间复制矩形像素 |
| `dump_window` | 导出窗口到图像文件（bmp/png...） |
| `dump_window_image` | 窗口当前内容 → `Image` 对象 |
| `flush_buffer` | 刷新双缓冲（双缓冲模式下令绘制生效） |
| `new_extern_window` | 绑定外部（第三方 GUI）窗口句柄 → `WindowHandle` |

### 5.2 属性查询与设置

| 算子 | 功能 |
|---|---|
| `get_window_attr` / `set_window_attr` | 窗口属性（创建前用 `set_`） |
| `get_window_extents` / `set_window_extents` | 尺寸与位置 |
| `get_window_type` / `set_window_type` / `query_window_type` | 窗口类型 |
| `get_window_pointer3` | 取像素内存指针（红/绿/蓝三通道，直接读写） |
| `get_os_window_handle` | 取 OS 原生窗口句柄（嵌入第三方 UI） |
| `set_window_dc` | 设置设备上下文 |
| `get_window_param` / `set_window_param` | 窗口级参数（见 Parameters 族） |

### 5.3 3D 窗口相关

| 算子 | 功能 |
|---|---|
| `disp_object_model_3d` | （见 Output 族）渲染 3D 模型 |
| `get_disp_object_model_3d_info` | 查询 3D 对象在窗口中的显示信息（点拾取） |
| `update_window_pose` | 更新 3D 窗口的相机/物体姿态（鼠标拖拽旋转） |
| `unproject_coordinates` | 窗口坐标反投影到 3D 世界坐标（配合 `CamParam`/`Pose`） |

### 5.4 重点算子

**`open_window ( : : Row, Column, Width, Height, FatherWindow, Mode, Machine : WindowHandle )`**
创建图形窗口。`FatherWindow` 为父窗口（0 表示独立窗口）；`Mode` 可为 'visible'/'' 等；`Machine` 用于远程显示（'' 表示本地）。返回句柄供后续 `disp_*` / `set_*` 使用。

> 与 `dev_open_window` 区别：`dev_open_window` 作用于"活动窗口"且受 HDevelop 环境管理；`open_window` 是编程态显式创建，适合部署到无 HDevelop 的运行环境。

**`dump_window ( : : WindowHandle, Device, FileName : )`**
把窗口内容导出为图片。`Device` 通常为 'bmp'/'png'/'jpeg' 等。`dump_window_image` 则是把内容转成 HALCON `Image` 对象留在内存，便于后续处理（无需落盘）。

**`update_window_pose ( : : WindowHandle, LastRow, LastCol, CurrentRow, CurrentCol, Mode : )`**
实现"鼠标拖拽旋转/平移 3D 场景"。传入上一帧与当前鼠标位置 + 模式（'x-z' 旋转等），自动更新场景姿态。配合 Output 族的 `disp_object_model_3d` / Scene3D 使用。

---

## 6. 四族关系图

```
                        open_window / close_window
                               │
                       ┌───────▼────────┐
                       │   Window 族 (21) │  ← 纸：窗口本身
                       │  句柄 / 属性 / 导出│
                       └───────┬─────────┘
                               │ 持有 WindowHandle
        ┌──────────────────────┼──────────────────────┐
        │                      │                       │
   ┌────▼─────┐        ┌───────▼────────┐      ┌───────▼──────┐
   │ Parameters│        │    Output 族    │      │   Text 族    │
   │   (38)    │        │     (16)        │      │    (12)      │
   │ 笔的样式  │───────▶│  把图原语画出来  │      │  写文字/读输入│
   │ 颜色/线宽 │ 决定    └────────────────┘      └──────────────┘
   │ 坐标映射  │ 外观
   └──────────┘
        │
        └─ convert_coordinates_* 串联 图像↔窗口 坐标（交互拾取关键）
```

**协作顺序**：`open_window` 拿到句柄 → `set_*` 配置样式 → `disp_*`/`disp_text` 绘制 → 交互时用 `convert_coordinates_*` 换算 → `dump_window` 导出成果。

---

## 7. 五语言对照速查（节选）

HALCON 同一算子支持 HDevelop / C / C++ / .NET / Python。以 `set_color` 与 `disp_image` 为例：

| HDevelop | C | C++ | .NET | Python |
|---|---|---|---|---|
| `set_color (WindowHandle, Color)` | `set_color(Hlong, const char*)` | `SetColor(Hlong, const HTuple&)` | `HWindow.SetColor(HTuple)` | `HWindow.set_color(color)` |
| `disp_image (Image, WindowHandle)` | `disp_image(Hobject, Hlong)` | `DispImage(Hobject, Hlong)` | `HWindow.DispImage(HImage)` | `HWindow.disp_image(image)` |

> 记忆口诀：**窗口类（`HWindow`）在 .NET/Python 中是对象方法，在 C/C++ 中是"句柄作第一参数"的普通函数。**

---

## 8. 误区与最佳实践（12 条）

1. **`disp_obj` vs `dev_display`**：前者显式传 `WindowHandle`（编程态安全），后者作用于"活动窗口"（仅 HDevelop 调试方便）。部署代码用 `disp_obj`。
2. **坐标换算必须配对 `set_part`**：一旦窗口做了缩放映射，鼠标拾取务必用 `convert_coordinates_window_to_image`，否则位置系统性偏移。
3. **`query_*` 是否需要句柄**：`query_colored`/`query_line_width`/`query_shape` 无 `WindowHandle`（查询全局能力），其余多数需要。调用前看签名。
4. **`set_draw('margin')` 才会描边**：默认常是 'fill'（实心）。画圆/矩形边框、看区域轮廓时记得切 'margin'。
5. **`set_colored(N)` 多色循环**：连续 `disp_region` 多个区域会自动分配不同颜色，适合可视化分类结果；单色用 `set_color`。
6. **`disp_text` 比 `write_string` 更省心**：新代码优先 `disp_text`（自带对齐/坐标系），旧光标式接口（`set_tposition`+`write_string`+`new_line`）仅维护老代码时用。
7. **`open_window` 在部署环境必用**：`dev_open_window` 依赖 HDevelop，编译后的程序里无效。
8. **双缓冲与 `flush_buffer`**：开启双缓冲后，绘制不会立即显示，需 `flush_buffer` 或在事件循环里刷新，否则画面"卡住不更新"。
9. **`dump_window` vs `dump_window_image`**：要落盘成图片文件用前者；要在内存里继续处理（OCR/保存前做标注）用后者返回 `Image`。
10. **3D 显示两种路线**：单模型一次性显示用 `disp_object_model_3d`；多对象、可交互旋转的场景用上卷的 `Scene3D`（`create_scene_3d` 等）。别混用。
11. **`get_window_pointer3` 直接写像素**：可绕过 `disp_*` 直接改窗口显存（做实时视频叠加），但需自己管理像素格式与尺寸，风险高、仅性能敏感场景用。
12. **`new_extern_window` 嵌第三方 GUI**：把 HALCON 窗口挂到 Qt/MFC 等父窗口，父窗口销毁前必须先 `close_window`，否则句柄泄漏。

---

## 9. 完整签名速查

> 格式：`算子 | 一句话功能 | HDevelop 签名`。签名已精简为 `输入 : 输出` 标准形态。

### 9.1 Output 族（16）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `disp_arc` | 绘制圆弧 | `disp_arc ( : : WindowHandle, CenterRow, CenterCol, Angle, BeginRow, BeginCol : )` |
| `disp_arrow` | 带箭头线段 | `disp_arrow ( : : WindowHandle, Row1, Column1, Row2, Column2, Size : )` |
| `disp_channel` | 显示单通道 | `disp_channel ( MultichannelImage : : WindowHandle, Channel : )` |
| `disp_circle` | 绘制圆 | `disp_circle ( : : WindowHandle, Row, Column, Radius : )` |
| `disp_color` | 彩色显示图像 | `disp_color ( ColorImage : : WindowHandle : )` |
| `disp_cross` | 十字标记 | `disp_cross ( : : WindowHandle, Row, Column, Size, Angle : )` |
| `disp_ellipse` | 绘制椭圆 | `disp_ellipse ( : : WindowHandle, CenterRow, CenterCol, Phi, Radius1, Radius2 : )` |
| `disp_image` | 显示图像 | `disp_image ( Image : : WindowHandle : )` |
| `disp_line` | 直线段 | `disp_line ( : : WindowHandle, Row1, Column1, Row2, Column2 : )` |
| `disp_obj` | 通用显示对象 | `disp_obj ( Object : : WindowHandle : )` |
| `disp_object_model_3d` | 显示 3D 模型 | `disp_object_model_3d ( : : WindowHandle, ObjectModel3D, CamParam, Pose, GenParamName, GenParamValue : )` |
| `disp_polygon` | 多边形 | `disp_polygon ( : : WindowHandle, Row, Column : )` |
| `disp_rectangle1` | 平行矩形 | `disp_rectangle1 ( : : WindowHandle, Row1, Column1, Row2, Column2 : )` |
| `disp_rectangle2` | 旋转矩形 | `disp_rectangle2 ( : : WindowHandle, CenterRow, CenterCol, Phi, Length1, Length2 : )` |
| `disp_region` | 显示区域 | `disp_region ( DispRegions : : WindowHandle : )` |
| `disp_xld` | 显示 XLD | `disp_xld ( XLDObject : : WindowHandle : )` |

### 9.2 Parameters 族（38）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `convert_coordinates_image_to_window` | 图像→窗口坐标 | `convert_coordinates_image_to_window ( : : WindowHandle, RowImage, ColumnImage : RowWindow, ColumnWindow )` |
| `convert_coordinates_window_to_image` | 窗口→图像坐标 | `convert_coordinates_window_to_image ( : : WindowHandle, RowWindow, ColumnWindow : RowImage, ColumnImage )` |
| `get_contour_style` | 查轮廓样式 | `get_contour_style ( : : WindowHandle : Style )` |
| `get_draw` | 查绘制模式 | `get_draw ( : : WindowHandle : Mode )` |
| `get_hsi` | 查 HSI 颜色 | `get_hsi ( : : WindowHandle : Hue, Saturation, Intensity )` |
| `get_icon` | 查区域图标 | `get_icon ( : Icon : WindowHandle : )` |
| `get_line_style` | 查线型 | `get_line_style ( : : WindowHandle : Style )` |
| `get_line_width` | 查线宽 | `get_line_width ( : : WindowHandle : Width )` |
| `get_paint` | 查填充方式 | `get_paint ( : : WindowHandle : Mode )` |
| `get_part` | 查显示部分 | `get_part ( : : WindowHandle : Row1, Column1, Row2, Column2 )` |
| `get_part_style` | 查部分样式 | `get_part_style ( : : WindowHandle : Style )` |
| `get_rgb` | 查 RGB | `get_rgb ( : : WindowHandle : Red, Green, Blue )` |
| `get_rgba` | 查 RGBA | `get_rgba ( : : WindowHandle : Red, Green, Blue, Alpha )` |
| `get_shape` | 查区域形状 | `get_shape ( : : WindowHandle : DisplayShape )` |
| `get_window_param` | 查窗口参数 | `get_window_param ( : : WindowHandle, Param : Value )` |
| `query_all_colors` | 查所有颜色 | `query_all_colors ( : : WindowHandle : Colors )` |
| `query_color` | 查可用颜色 | `query_color ( : : WindowHandle : Colors )` |
| `query_colored` | 查多色数 | `query_colored ( : : : PossibleNumberOfColors )` |
| `query_gray` | 查灰度范围 | `query_gray ( : : WindowHandle : Grayval )` |
| `query_line_width` | 查线宽范围 | `query_line_width ( : : : Min, Max )` |
| `query_paint` | 查填充方式 | `query_paint ( : : WindowHandle : Mode )` |
| `query_shape` | 查区域形状 | `query_shape ( : : : DisplayShape )` |
| `set_color` | 设颜色 | `set_color ( : : WindowHandle, Color : )` |
| `set_colored` | 设多色 | `set_colored ( : : WindowHandle, NumberOfColors : )` |
| `set_contour_style` | 设轮廓样式 | `set_contour_style ( : : WindowHandle, Style : )` |
| `set_draw` | 设绘制模式 | `set_draw ( : : WindowHandle, Mode : )` |
| `set_gray` | 设灰度 | `set_gray ( : : WindowHandle, GrayValues : )` |
| `set_hsi` | 设 HSI | `set_hsi ( : : WindowHandle, Hue, Saturation, Intensity : )` |
| `set_icon` | 设区域图标 | `set_icon ( Icon : : WindowHandle : )` |
| `set_line_style` | 设线型 | `set_line_style ( : : WindowHandle, Style : )` |
| `set_line_width` | 设线宽 | `set_line_width ( : : WindowHandle, Width : )` |
| `set_paint` | 设填充方式 | `set_paint ( : : WindowHandle, Mode : )` |
| `set_part` | 设显示部分 | `set_part ( : : WindowHandle, Row1, Column1, Row2, Column2 : )` |
| `set_part_style` | 设部分样式 | `set_part_style ( : : WindowHandle, Style : )` |
| `set_rgb` | 设 RGB | `set_rgb ( : : WindowHandle, Red, Green, Blue : )` |
| `set_rgba` | 设 RGBA | `set_rgba ( : : WindowHandle, Red, Green, Blue, Alpha : )` |
| `set_shape` | 设区域形状 | `set_shape ( : : WindowHandle, Shape : )` |
| `set_window_param` | 设窗口参数 | `set_window_param ( : : WindowHandle, Param, Value : )` |

### 9.3 Text 族（12）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `disp_text` | 显示文本（推荐） | `disp_text ( : : WindowHandle, String, CoordSystem, Row, Column, Color, GenParamName, GenParamValue : )` |
| `get_font` | 查字体 | `get_font ( : : WindowHandle : Font )` |
| `get_font_extents` | 查字体度量 | `get_font_extents ( : : WindowHandle : MaxAscent, MaxDescent, MaxWidth, MaxHeight )` |
| `get_string_extents` | 查字符串尺寸 | `get_string_extents ( : : WindowHandle, Values : Ascent, Descent, Width, Height )` |
| `get_tposition` | 查文本光标 | `get_tposition ( : : WindowHandle : Row, Column )` |
| `new_line` | 文本换行 | `new_line ( : : WindowHandle : )` |
| `query_font` | 查可用字体 | `query_font ( : : WindowHandle : Font )` |
| `read_char` | 读字符（交互） | `read_char ( : : WindowHandle : Char, Code )` |
| `read_string` | 读字符串（交互） | `read_string ( : : WindowHandle, InString, Length : OutString )` |
| `set_font` | 设字体 | `set_font ( : : WindowHandle, Font : )` |
| `set_tposition` | 设文本光标 | `set_tposition ( : : WindowHandle, Row, Column : )` |
| `write_string` | 写字符串 | `write_string ( : : WindowHandle, String : )` |

### 9.4 Window 族（21）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `clear_window` | 清空窗口 | `clear_window ( : : WindowHandle : )` |
| `close_window` | 关闭窗口 | `close_window ( : : WindowHandle : )` |
| `copy_rectangle` | 窗口间复制 | `copy_rectangle ( : : WindowHandleSource, WindowHandleDestination, Row1, Column1, Row2, Column2, DestRow, DestColumn : )` |
| `dump_window` | 导出到文件 | `dump_window ( : : WindowHandle, Device, FileName : )` |
| `dump_window_image` | 窗口→图像 | `dump_window_image ( : Image : WindowHandle : )` |
| `flush_buffer` | 刷新缓冲 | `flush_buffer ( : : WindowHandle : )` |
| `get_disp_object_model_3d_info` | 查 3D 显示信息 | `get_disp_object_model_3d_info ( : : WindowHandle, Row, Column, Information : Value )` |
| `get_os_window_handle` | 取 OS 句柄 | `get_os_window_handle ( : : WindowHandle : OSWindowHandle, OSDisplayHandle )` |
| `get_window_attr` | 查窗口属性 | `get_window_attr ( : : AttributeName : AttributeValue )` |
| `get_window_extents` | 查尺寸位置 | `get_window_extents ( : : WindowHandle : Row, Column, Width, Height )` |
| `get_window_pointer3` | 取像素指针 | `get_window_pointer3 ( : : WindowHandle : ImageRed, ImageGreen, ImageBlue, Width, Height )` |
| `get_window_type` | 查窗口类型 | `get_window_type ( : : WindowHandle : WindowType )` |
| `new_extern_window` | 绑外部窗口 | `new_extern_window ( : : WINHWnd, Row, Column, Width, Height : WindowHandle )` |
| `open_window` | 打开窗口 | `open_window ( : : Row, Column, Width, Height, FatherWindow, Mode, Machine : WindowHandle )` |
| `query_window_type` | 查窗口类型 | `query_window_type ( : : : WindowTypes )` |
| `set_window_attr` | 设窗口属性 | `set_window_attr ( : : AttributeName, AttributeValue : )` |
| `set_window_dc` | 设设备上下文 | `set_window_dc ( : : WindowHandle, WINHDC : )` |
| `set_window_extents` | 设尺寸位置 | `set_window_extents ( : : WindowHandle, Row, Column, Width, Height : )` |
| `set_window_type` | 设窗口类型 | `set_window_type ( : : WindowType : )` |
| `unproject_coordinates` | 坐标反投影 | `unproject_coordinates ( Image : : WindowHandle, Row, Column : ImageRow, ImageColumn, Height )` |
| `update_window_pose` | 更新 3D 姿态 | `update_window_pose ( : : WindowHandle, LastRow, LastCol, CurrentRow, CurrentCol, Mode : )` |

---

## 10. 与 Graphics · 上卷衔接

- 上卷的 **Object 族**（`set_*_object` / `attach_drawing_object_to_window`）把"可交互绘图对象"挂到窗口——它依赖本卷 `open_window` 得到的 `WindowHandle`。
- 上卷的 **3D Scene 族**（`create_scene_3d` / `disp_scene_3d`）与本卷 `disp_object_model_3d` / `update_window_pose` / `unproject_coordinates` 共同构成 HALCON 的 3D 可视化栈。
- 上卷的 **Mouse 族**（`get_mposition` / `send_mouse_drag_event`）产生的窗口坐标，通常要用本卷 `convert_coordinates_window_to_image` 换算回图像坐标，才能完成交互拾取。

> 阅读建议：先读本卷 §3.3 与 §5.4，再回看上卷 Object / 3D Scene / Mouse 族，可形成"交互闭环"的完整认知。

---

*本卷覆盖 HALCON 第 13 章 Graphics 下半部分 87 个算子（Output 16 + Parameters 38 + Text 12 + Window 21）。签名取自官方 Operator Reference 20.11.1.0 的 HDevelop 列，已统一为 `输入 : 输出` 标准形态。*
