# 个人笔记库 · Personal Knowledge Base

> 一个用纯 Markdown 维护、按学科分类、可被 Git 追踪的个人知识仓库。
> 原则：**能查到的不抄，抄了要能用；每篇笔记至少有一张对比表和一个结论。**

---

## 分类导航

| 编号 | 分类 | 收录内容 | 当前状态 |
| --- | --- | --- | --- |
| [01](./01-计算机硬件/) | 计算机硬件 | CPU、主板、总线、插槽接口、装机选型、故障排查 | ✅ 已成体系（14 篇） |
| [02](./02-操作系统与底层/) | 操作系统与底层 | 内核、内存管理、进程调度、文件系统 | 🌱 待填充 |
| [03](./03-编程与开发/) | 编程与开发 | 语言特性、工程实践、架构设计 | 🌱 待填充 |
| [04](./04-网络与安全/) | 网络与安全 | 协议栈、加密、攻防、运维 | 🌱 待填充 |
| [05](./05-数据与AI/) | 数据与 AI | 数据工程、模型原理、推理部署 | 🌱 待填充 |
| [06](./06-工具与效率/) | 工具与效率 | 命令行、编辑器、自动化流程 | 🌱 待填充 |
| [07](./07-算法/) | 算法 | HALCON 算子、机器视觉、数值方法 | ✅ 已起步（HALCON 2 篇 + 章节总结 22 篇） |
| [99](./99-速记与灵感/) | 速记与灵感 | 未成型的碎片，定期归档到上面的分类 | 🌱 待填充 |
| [_模板](./_模板/) | 模板 | 新建笔记时复制这个 | ✅ |

---

## 重点专题：计算机硬件

第一批完整成文的主题。四条主线 + 一条汇总线：

```
CPU ──── 算什么、怎么算得快
 │
主板 ──── 谁把这些零件焊在一起、谁决定你能插什么
 │
总线 ──── 数据在零件之间怎么跑、跑多快
 │
插槽 ──── 物理上怎么连、连错了会怎样
 │
综合 ──── 上面四件事凑一起，钱该怎么花
```

### CPU
- [01 · 架构与工作原理](./01-计算机硬件/CPU/01-CPU架构与工作原理.md) — 流水线、乱序执行、缓存层级、分支预测
- [02 · 参数详解与分类对比](./01-计算机硬件/CPU/02-CPU参数详解与分类对比.md) — 主频/核心/缓存/TDP 到底看哪个，桌面 vs 移动 vs 服务器
- [03 · 前沿技术](./01-计算机硬件/CPU/03-CPU前沿技术.md) — GAA、背面供电、Chiplet、3D V-Cache、NPU 异构

### 主板
- [01 · 结构与芯片组](./01-计算机硬件/主板/01-主板结构与芯片组.md) — 供电、南北桥演进、PCH/FCH、板型
- [02 · 分级对比与选购](./01-计算机硬件/主板/02-主板分级对比与选购.md) — Intel/AMD 全系芯片组分级表与踩坑清单

### 总线
- [01 · 原理与分类](./01-计算机硬件/总线/01-总线原理与分类.md) — 并行 vs 串行、拓扑、带宽/延迟/一致性
- [02 · PCIe 演进与代际对比](./01-计算机硬件/总线/02-PCIe演进与代际对比.md) — Gen1→Gen7 全代际，编码、拆分、通道分配
- [03 · 前沿互连](./01-计算机硬件/总线/03-前沿互连-CXL-UCIe-NVLink.md) — CXL 内存池化、UCIe 芯粒互连、NVLink

### 插槽与接口
- [01 · CPU 插槽](./01-计算机硬件/插槽与接口/01-CPU插槽-LGA-PGA-BGA.md) — LGA/PGA/BGA、AM5/LGA1851 及历代对照
- [02 · 内存插槽](./01-计算机硬件/插槽与接口/02-内存插槽-DIMM与CAMM2.md) — DDR 代际、通道、CAMM2/LPCAMM2/SOCAMM
- [03 · 扩展与存储接口](./01-计算机硬件/插槽与接口/03-扩展与存储接口.md) — M.2 键位、SATA、USB4、雷电、供电接口

### 综合
- [装机平台横向对比与选型决策](./01-计算机硬件/综合/装机平台横向对比与选型决策.md) — 按预算和用途给结论
- [硬件术语速查表](./01-计算机硬件/综合/硬件术语速查表.md) — 缩写地狱急救包
- [常见故障排查与维修实例](./01-计算机硬件/综合/常见故障排查与维修实例.md) — 真实案例归类、排查方法论、现代映射

---

## 重点专题：算法

### HALCON
- [01 · 圆形、椭圆与圆弧算子解析](./07-算法/HALCON/01-圆形椭圆与圆弧算子解析.md) — Region/XLD/1D 测量三层、gen_circle 到 fit_*_contour_xld、gen_measure_arc 圆弧测量、实战与坑
- [02 · 窗口显示与绘图显示算子解析](./07-算法/HALCON/02-窗口显示与绘图显示算子解析.md) — 显示/交互/绘图三线、window 管理、dev_set_*、dev_disp_text 文本方框、draw_* 取 ROI、paint_* 固化进图
- [章节总结 · 第 1 章 1D Measuring](./07-算法/HALCON/章节总结/01-1D测量.md) — 18 个算子拆成 6 大族、measure_* vs fuzzy_measure_* 选型、典型闭环、量产 PCB 焊盘宽实战
- [章节总结 · 第 2 章 2D Metrology](./07-算法/HALCON/章节总结/02-2D测量.md) — 30 个算子拆成 7 大族、MetrologyHandle 是"测量图纸"、5 种 add_object、align/apply 流程、BGA 100 实例实战
- [章节总结 · 第 3 章 3D Matching](./07-算法/HALCON/章节总结/03-3D匹配.md) — 40 个算子拆成 4 大族（3D Box / Deformable Surface / Shape-Based / Surface-Based）、从 2D 跃进 3D 返 6D 位姿、机器人抓取 / Bin-Picking 主流族
- [章节总结 · 第 4 章 3D Object Model](./07-算法/HALCON/章节总结/04-3D对象模型.md) — 52 个算子拆成 4 大族（Creation / Features / Segmentation / Transformations），ObjectModel3D 句柄抽象、造量拆变 4 步流水线（附思维导图 PNG）
- [章节总结 · 第 5 章 3D Reconstruction](./07-算法/HALCON/章节总结/05-3D重建.md) — 65 个算子拆成 5 大族（Binocular / Depth From Focus / Multi-View / Photometric / Sheet Of Light），5 种物理路径互补，从 2D 图像反推 3D 几何（附五角形思维导图 PNG）
- [章节总结 · 第 6 章 Calibration](./07-算法/HALCON/章节总结/06-标定.md) — 64 个算子拆成 10 子族（Binocular / Calibration Object / Camera Parameters / Hand-Eye / Inverse Projection / Monocular / Multi-View / Projection / Rectification / Self-Calibration），世界↔相机↔像素几何管焊死步骤，3 套 API 老 flat / 新 CalibData / 自标定（附思维导图 PNG）
- [章节总结 · 第 7 章 Classification](./07-算法/HALCON/章节总结/07-分类.md) — 101 个算子其实只 4 大分类器 + 4 套 LUT 烧表 + 11 个样本袋工具，**共享 5 件套模板** create→样本→train→classify→IO，拒识 / 离群检测 / 多模态特征全在内（附思维导图 PNG）
- [章节总结 · 第 8 章 Control](./07-算法/HALCON/章节总结/08-控制.md) — 35 个 HDevelop 脚本关键字（7 族：赋值/条件/循环/异常/过程·并行/元组↔向量/杂项），**不是图像算子**而是语言级关键字；导出 C++/Python 后被翻译为目标语言原生控制流（附七边形思维导图 PNG）
- [章节总结 · 第 10 章 Develop](./07-算法/HALCON/章节总结/10-开发.md) — 42 个 `dev_*` 算子分 8 族（窗口/绘图/文本/变量/错误/更新/工具/系统），**只在 HDevelop IDE 或 HDevEngine 内部生效**，导出后 17 失效、6 仅 HDevEngine、19 可移植（附八边形思维导图 PNG）
- [章节总结 · 第 11 章 File I/O](./07-算法/HALCON/章节总结/11-文件.md) — **51 个算子导出可移植性最高的章节**（7 子族：Access/Images/Misc/Object/Region/Tuple/XLD），每对象"读写+序列化"四件套；DXF/ARC 是 CAD-GIS 桥梁；`read_*_serialized_item`/`fwrite_*` 是跨进程流（附七边形思维导图 PNG）
- [章节总结 · 第 12 章 Filters · 上卷](./07-算法/HALCON/章节总结/12-滤波(上).md) — **像素级独立 41 算子**（Arithmetic 22 + Bit 8 + Color 11），三角函数 / Mult-Add / LUT / PCA 全部要点；流水线最便宜的环节（附思维导图 PNG）
- [章节总结 · 第 12 章 Filters · 中卷](./07-算法/HALCON/章节总结/12-滤波(中).md) — **邻域+空间+频域+直线+匹配 87 算子**（Edges 23 + Enhancement 7 + Inpainting 6 + Geometric 12 + FFT 31 + Lines 4 + Match 4），从像素级迈入邻域 + 空间重采样 + 频域滤波；Canny/Sobel/DoG + 各扩散 + 各修补 + 各投影 + FFT + 模板匹配（附思维导图 PNG）
- [章节总结 · 第 12 章 Filters · 下卷](./07-算法/HALCON/章节总结/12-滤波(下).md) — **空域+噪声+反卷积+特征+光流+纹理 59 算子**（Misc 8 + Smoothing 24 + Noise 5 + Wiener 6 + Points 7 + OpticalFlow 4 + SceneFlow 2 + Texture 3），Wiener 复原 + Harris/Foerstner/Lepetit + 多网格光流 + 场景流 + 纹理度量（附思维导图 PNG）
- [章节总结 · 第 13 章 Graphics · 上卷](./07-算法/HALCON/章节总结/13-Graphics(上).md) — **主动绘图+交互 78 算子**（3D Scene 20 + Drawing 23 + LUT 3 + Mouse 11 + Object 21），3D 场景栅格化渲染 + 同步/叠加交互绘点线圆椭圆矩形多边形NURBS + 伪彩色查找表 + 鼠标键位/光标/事件注入 + 可绑定窗口可回调的可复用绘图对象句柄（附五边形思维导图 PNG）
- [章节总结 · 第 13 章 Graphics · 下卷](./07-算法/HALCON/章节总结/13-Graphics(下).md) — **窗口系统+输出 87 算子**（Output 16 + Parameters 38 + Text 12 + Window 21），`open_window` 创建窗口 + `set_color/draw/line_width/part` 配置样式 + `disp_image/region/xld/object_model_3d` 显示原语 + `convert_coordinates_*` 图像↔窗口坐标换算 + `dump_window` 导出 + 3D 窗口姿态（附四边形思维导图 PNG）
- [章节总结 · 第 14 章 Identification](./07-算法/HALCON/章节总结/14-Identification.md) — **识别 44 算子**（Bar Code 一维条码 15 + Data Code 二维码 12 + Sample-Based 样本学习 17），图像→字符串/类别三范式：条码 (EAN/UPC/Code 128) / 二维码 (DM/QR/Aztec/PDF417) / 工业样本识别 (零件型号/缺陷等级)，全部"建模型→找→取"三段式（附三角辐射思维导图 PNG）
- [章节总结 · 第 15 章 Image · 上卷](./07-算法/HALCON/章节总结/15-Image(上).md) — **图像的输入与组织 62 算子**（Access 读像素 9 + Acquisition 相机采集 14 + Channel 通道拆分合并 17 + Creation 造图 16 + Domain 域操作 6），`get_grayval/image_pointer` / `open_framegrabber` / `grab_image_async` / `compose3` / `decompose3` / `gen_image_const` / `reduce_domain` ——HALCON 的 ROI 工具是 `reduce_domain`，彩色图就是多通道（附五边形思维导图 PNG）
- [章节总结 · 第 15 章 Image · 下卷](./07-算法/HALCON/章节总结/15-Image(下).md) — **图像的分析与变换 44 算子**（Features 特征统计熵 24 + Format 裁剪拼接 9 + Manipulation 像素改写 6 + Type Conversion 类型互换 5），`intensity/area_center_gray`/`entropy_gray`/`gen_cooc_matrix`/`fit_surface_*`/`select_gray`/`crop_part/rectangle2`/`tile_images`/`paint_region/xld`/`set_grayval`/`convert_image_type`/`complex_to_real`/`real_to_vector_field`（附四边形思维导图 PNG）
- [章节总结 · 第 16 章 Inspection](./07-算法/HALCON/章节总结/16-Inspection.md) — **工业检测五朵金花 53 算子**（Bead Inspection 胶路检测 5 + OCV 光学字符校验 8 + Structured Light 结构光 11 + Texture Inspection 纹理检测 15 + Variation Model 差异模型 14），胶路宽窄/字符对错/结构光解码/纹理瑕疵/与金标准图逐像素比对，全部"训练→检测→出结果"三段式；`create_variation_model`+`prepare_variation_model`+`compare_variation_model` 是零标注缺陷检测的利器（附五瓣金花美学思维导图 PNG）
- [章节总结 · 第 17 章 Matching · 上卷](./07-算法/HALCON/章节总结/17-Matching(上).md) — **经典模板匹配 65 算子**（Correlation-Based NCC 像素灰度块 14 + Shape-Based 轮廓金字塔 28 + Deformable 可形变网格 23），"图像本身就是模板，像素或轮廓是匹配依据"；`create_*_model → find_*_model → clear_*_model` 三件套共享；Shape 抗旋转+缩放，Deformable 还抗局部形变（calib 版返回 6D Pose 给机器人抓取）（附三角辐射思维导图 PNG）
- [章节总结 · 第 18 章 Matrix](./07-算法/HALCON/章节总结/18-Matrix.md) — **矩阵运算七色花 57 算子**（Access 取值赋值 8 + Arithmetic 算术运算 27 含 12 对 `_mod` 原地版 + Creation 矩阵构造 4 + Decomposition 矩阵分解 LU/QR/SVD 3 + Eigenvalues 特征值 4 + Features 行列式/均值/范数 7 + File 读写序列化 4），HALCON 高级算法（相机标定/位姿估计/PCA）的数学底座；`solve_matrix('LU')` 解线性方程组、`svd_matrix` 算伪逆、`invert_matrix` 求逆、`get_full/set_full_matrix` 是矩阵 ↔ tuple 互转的基座（附七星连珠美学思维导图 PNG）
- [章节总结 · 第 19 章 Morphology](./07-算法/HALCON/章节总结/19-Morphology.md) — **形态学 43 算子**（Gray Values 灰度形态学 18 + Region 区域形态学 25），HALCON 一切"提取骨架、去毛刺、补孔、分离连通"的数学基础——同一套 SE 数学切两个输入域：GrayValues 是图像灰度的 min/max 卷积（开闭滤波/TopHat 提前景/Range 边缘），Region 是二值集合的 SE 探测（hit-or-miss 找角点/minkowski 求凸包）；`gen_disc_se`+`gray_opening_rect`+`opening_circle`+`hit_or_miss` 是四大件（附七瓣辐射思维导图 PNG）
- [章节总结 · 第 20 章 OCR · 上卷](./07-算法/HALCON/章节总结/20-OCR(上).md) — **OCR 识别核心 33 算子**（Deep OCR 端到端深度引擎 6 + Segmentation 文本检测与字符切分 12 + Lexica 词典与拼写纠错 6 + CNN Classifier 字符分类器 9），「从图到字」的识别核心四件套——`create_deep_ocr`+`apply_deep_ocr` 一键搞定通用场景；传统四步走（`create_text_model_reader`→`find_text`→`segment_characters`→`do_ocr_*_class_cnn`）精控专业场景；`lookup_lexicon`+`suggest_lexicon` 词典后处理永远加分（附四方辐射美学思维导图 PNG）

---

## 使用约定

- **文件名**：`序号-主题.md`，序号决定阅读顺序，不代表重要性。
- **新建笔记**：复制 [`_模板/笔记模板.md`](./_模板/笔记模板.md)。
- **时效性**：涉及具体型号和价格的内容会过期。每篇笔记头部标注了"数据基准"日期，超过一年请重新核对。
- **交叉引用**：用相对路径链接，不要用绝对路径。
- **速记区**：`99-速记与灵感/` 里的东西随便写，但每月要清一次，要么升级成正式笔记，要么删掉。

## 提交规范

```
类型(范围): 摘要

feat  新增笔记 / 新增分类
docs  修订已有笔记内容
fix   订正错误、修链接
chore 结构调整、模板、配置
```
