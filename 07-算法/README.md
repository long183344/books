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

---

## 这个分类的约定

- **算子文档统一格式**：签名 → 是什么 → 关键参数 → 怎么用 → 坑 → 官方文档链接。
- **签名以官方 Operator Reference 为准**：HALCON 版本差异会改参数，每篇标注"数据基准"版本。
- **示例用 HDevelop 语法**：可直接粘到 HDevelop 运行，注释用中文。
