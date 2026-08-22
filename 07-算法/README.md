# 07 · 算法

> 机器视觉、图像处理、数值方法、数据结构等算法专题。先从 HALCON 算子体系起步。

## 阅读路线

**如果你做视觉检测** → 先看 [HALCON/01-圆形椭圆与圆弧算子解析](./HALCON/01-圆形椭圆与圆弧算子解析.md)，把圆/椭圆/圆弧这条最常用的几何测量线打通。

```
HALCON 圆/椭圆/圆弧算子   ← 圆形测量的事实主力
   ↓
HALCON 直线/矩形算子       ← 待补
   ↓
HALCON 模板匹配 / 亚像素   ← 待补
   ↓
数值方法 / 数据结构         ← 待补
```

## 目录

### [HALCON/](./HALCON/)
| 文件 | 讲什么 |
| --- | --- |
| [01-圆形椭圆与圆弧算子解析](./HALCON/01-圆形椭圆与圆弧算子解析.md) | Region/XLD/几何三层、gen_circle 到 fit_*_contour_xld、gen_measure_arc 圆弧测量、实战与坑 |
| [02-窗口显示与绘图显示算子解析](./HALCON/02-窗口显示与绘图显示算子解析.md) | 显示/交互/绘图三线区分、window 管理、dev_set_* 环境、dev_disp_text 文本方框、draw_* 取 ROI、paint_* 固化进图 |
| [章节总结/01-1D测量](./HALCON/章节总结/01-1D测量.md) | HALCON 官方手册第 1 章 18 个算子分成 6 大族（生成/提取/模糊/配置/平移/持久化）、measure_* vs fuzzy_measure_* 选型、典型闭环、量产 PCB 焊盘宽实战 |
| [章节总结/02-2D测量](./HALCON/章节总结/02-2D测量.md) | HALCON 官方手册第 2 章 30 个算子（MetrologyHandle = "测量图纸"），5 种 add_object、对齐/求解、取结果、参数三层、桥接 1D 章、BGA 100 实例实战 |
| [章节总结/03-3D匹配](./HALCON/章节总结/03-3D匹配.md) | HALCON 官方手册第 3 章 40 个算子（4 大族：3D Box / Deformable Surface / Shape-Based / Surface-Based），从 2D 跃进 3D，返回 6D 位姿，机器人抓取/Bin-Picking 主流族 |
| [章节总结/04-3D对象模型](./HALCON/章节总结/04-3D对象模型.md) | HALCON 官方手册第 4 章 52 个算子（4 大族：Creation / Features / Segmentation / Transformations），核心抽象 ObjectModel3D 句柄，造→量→拆→变 4 步流水线（附思维导图） |
| [章节总结/05-3D重建](./HALCON/章节总结/05-3D重建.md) | HALCON 官方手册第 5 章 65 个算子（5 大族：Binocular Stereo / Depth From Focus / Multi-View / Photometric / Sheet Of Light），五种物理路径互补，从 2D 图像反推 3D 几何（附五角形思维导图） |
| [章节总结/06-标定](./HALCON/章节总结/06-标定.md) | HALCON 官方手册第 6 章 64 个算子（10 子族：Binocular / Calibration Object / Camera Parameters / Hand-Eye / Inverse Projection / Monocular / Multi-View / Projection / Rectification / Self-Calibration），三套 API 老 flat → 新 CalibData → 自标定，世界↔相机↔像素几何管的焊死步骤（附思维导图） |
| [章节总结/07-分类](./HALCON/章节总结/07-分类.md) | HALCON 官方手册第 7 章 101 个算子（6 族：GMM / KNN / MLP / SVM / LUT / Misc），核心 4 分类器共享 5 件套模板（create → 样本 → train → classify → IO），LUT 烧成极速查表、ClassTrainData 跨族样本袋（附思维导图） |
| [章节总结/08-控制](./HALCON/章节总结/08-控制.md) | HALCON 官方手册第 8 章 35 个 HDevelop 关键字（7 族：赋值/条件/循环/异常/过程·并行/元组↔向量/杂项），不是图像算子而是脚本语言级关键字，导出 C++/Python 后被翻译成目标语言原生控制流（附七边形思维导图） |
| [章节总结/10-开发](./HALCON/章节总结/10-开发.md) | HALCON 官方手册第 10 章 42 个 `dev_*` 算子（8 族：窗口/绘图/文本·对话框/变量·内存/错误/更新/工具/系统·偏好），**只在 HDevelop IDE 或 HDevEngine 内部有效**——导出 C++/Python/.NET 后 17 失效、6 仅 HDevEngine、19 可移植（附八边形思维导图） |
| [章节总结/11-文件](./HALCON/章节总结/11-文件.md) | HALCON 官方手册第 11 章 51 个 File I/O 算子（7 子族：Access/Images/Misc/Object/Region/Tuple/XLD），本章是**导出可移植性最高**的一章——51 个全部可在 C++/Python/.NET 外部调用；每对象都有"读写+序列化"四件套；DXF/ARC/INFO 是 CAD-GIS 桥梁（附七边形思维导图） |
| [章节总结/12-滤波(上)](./HALCON/章节总结/12-滤波(上).md) | HALCON 官方手册第 12 章 **上卷** 41 个算子（3 族：Arithmetic 算术代数 / Bitwise 位运算 / Color 颜色空间），像素级独立计算——流水线最便宜的环节；三角函数 / Mult-Add / LUT / PCA 全部要点（附思维导图） |
| [章节总结/12-滤波(中)](./HALCON/章节总结/12-滤波(中).md) | HALCON 官方手册第 12 章 **中卷** 87 个算子（7 族：Edges 边缘 23 + Enhancement 增强 7 + Inpainting 修补 6 + Geometric Transforms 几何变换 12 + FFT 频域 31 + Lines 直线 4 + Match 模板匹配 4），从像素级迈入邻域 + 空间重采样 + 频域滤波 + 直线 + 模板匹配；Canny/Sobel/DoG + 各扩散 + 各修补 + 各投影 + FFT + 模板匹配（附思维导图） |
| [章节总结/12-滤波(下)](./HALCON/章节总结/12-滤波(下).md) | HALCON 官方手册第 12 章 **下卷** 59 个算子（8 族：Misc 杂项 8 + Smoothing 平滑 24 + Noise 噪声 5 + Wiener 复原 6 + Points 兴趣点 7 + OpticalFlow 光流 4 + SceneFlow 场景流 2 + Texture 纹理 3），空域平滑/保边去噪/数据增噪/Wiener 去卷积/Harris-Foerstner-Sojka/多网格光流/纹理度量（附思维导图） |
| [章节总结/13-Graphics(上)](./HALCON/章节总结/13-Graphics(上).md) | HALCON 官方手册第 13 章 Graphics **上卷** 78 个算子（5 族：3D Scene 三维场景 20 + Drawing 鼠标绘图 23 + LUT 颜色查找表 3 + Mouse 鼠标输入 11 + Object 绘图对象 21），主动绘图与交互——画什么 + 怎么画 + 鼠标按键 + 可绑定窗口的可复用交互控件（附五边形思维导图） |
| [章节总结/13-Graphics(下)](./HALCON/章节总结/13-Graphics(下).md) | HALCON 官方手册第 13 章 Graphics **下卷** 87 个算子（4 族：Output 图形显示 16 + Parameters 绘制参数 38 + Text 文本绘制 12 + Window 窗口管理 21），窗口系统 + 输出——`open_window`+`set_*` 样式 + `disp_*`/`disp_text` 绘制 + `convert_coordinates_*` 坐标换算 + `dump_window` 导出 + 3D 窗口姿态（附四边形思维导图） |
| [章节总结/14-Identification](./HALCON/章节总结/14-Identification.md) | HALCON 官方手册第 14 章 **识别** 44 个算子（3 族：Bar Code 一维条码 15 + Data Code 二维码 12 + Sample-Based 样本学习 17），把图像读成字符串或类别——条码 (EAN/UPC/Code 128) / 二维码 (DM/QR/Aztec/PDF417) / 工业样本识别 (零件型号/缺陷等级)，全部遵循"建模型→找→取"三段式（附三族辐射思维导图） |
| [章节总结/15-Image(上)](./HALCON/章节总结/15-Image(上).md) | HALCON 官方手册第 15 章 Image **上卷** 62 个算子（5 族：Access 像素访问 9 + Acquisition 相机采集 14 + Channel 通道拆分合并 17 + Creation 造图 16 + Domain 域操作 6），图像的"输入与组织"五件套——看图/取图/拼通道/造图/设 ROI；`reduce_domain` 是 HALCON 的 ROI 工具，`compose/decompose2..7` 处理彩色图通道（附五边形思维导图） |
| [章节总结/15-Image(下)](./HALCON/章节总结/15-Image(下).md) | HALCON 官方手册第 15 章 Image **下卷** 44 个算子（4 族：Features 特征/统计/熵 24 + Format 裁剪拼接 9 + Manipulation 像素改写 6 + Type Conversion 类型互换 5），图像的"分析与变换"四件套——`area_center_gray/intensity/entropy_gray/gen_cooc_matrix` 算特征 + `crop_part/crop_rectangle2/tile_images` 裁拼 + `paint_region/xld`/`overpaint_*`/`set_grayval` 改写 + `convert_image_type/complex_to_real/real_to_vector_field` 换类型（附四边形思维导图） |

---

## 这个分类的约定

- **算子文档统一格式**：签名 → 是什么 → 关键参数 → 怎么用 → 坑 → 官方文档链接。
- **签名以官方 Operator Reference 为准**：HALCON 版本差异会改参数，每篇标注"数据基准"版本。
- **示例用 HDevelop 语法**：可直接粘到 HDevelop 运行，注释用中文。
