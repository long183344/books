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
| [章节总结/16-Inspection](./HALCON/章节总结/16-Inspection.md) | HALCON 官方手册第 16 章 **检测** 53 个算子（5 族：Bead Inspection 胶路检测 5 + OCV 光学字符校验 8 + Structured Light 结构光 11 + Texture Inspection 纹理检测 15 + Variation Model 差异模型 14），工业质检"五朵金花"——胶路宽窄/字符对错/结构光解码/纹理瑕疵/与金标准图逐像素比对，全部"训练→检测→出结果"三段式（附五瓣金花美学思维导图） |
| [章节总结/17-Matching(上)](./HALCON/章节总结/17-Matching(上).md) | HALCON 官方手册第 17 章 Matching **上卷** 65 个算子（3 族：Correlation-Based NCC 14 + Shape-Based 28 + Deformable 23），**经典模板匹配**——"图像本身就是模板，像素或轮廓是匹配依据"；`create_*_model` → `find_*_model` → `clear_*_model` 三件套共享；Shape 抗旋转+缩放、Deformable 还抗局部形变（附三角辐射思维导图） |
| [章节总结/18-Matrix](./HALCON/章节总结/18-Matrix.md) | HALCON 官方手册第 18 章 Matrix **矩阵运算** 57 个算子（7 族：Access 8 + Arithmetic 27 + Creation 4 + Decomposition 3 + Eigenvalues 4 + Features 7 + File 4），HALCON 内部"线性代数底座"——`create_matrix` 起步、`get/set_*_matrix` 读写、`mult/add/sub/pow_*_matrix[_mod]` 算 + 12 对原地版省内存 50%、`solve_matrix`/`svd_matrix`/`invert_matrix`/`eigenvalues_*` 四大线性代数引擎，是相机标定/位姿估计/PCA 的数学根基（附七星连珠美学思维导图） |
| [章节总结/19-Morphology](./HALCON/章节总结/19-Morphology.md) | HALCON 官方手册第 19 章 **形态学** 43 个算子（2 族：Gray Values 灰度形态学 18 + Region 区域形态学 25），HALCON 一切"提取骨架、去毛刺、补孔、分离连通"的数学基础——同一套 SE 数学切两个输入域：GrayValues 是图像灰度的 min/max 卷积（开闭滤波/TopHat 提前景/Range 边缘），Region 是二值集合的 SE 探测（hit-or-miss 找角点/minkowski 求凸包）；`gen_disc_se`+`gray_opening_rect`+`opening_circle`+`hit_or_miss` 是四大件（附七瓣辐射思维导图） |
| [章节总结/20-OCR(上)](./HALCON/章节总结/20-OCR(上).md) | HALCON 官方手册第 20 章 OCR **上卷 33 算子**（4 族：Deep OCR 端到端 6 + Segmentation 文本检测与字符切分 12 + Lexica 词典与拼写纠错 6 + CNN Classifier 字符分类器 9），「从图到字」的识别核心——Deep OCR 一键通用场景、传统四步走（`create_text_model_reader`→`find_text`→`segment_characters`→`do_ocr_*_class_cnn`）精控专业场景、`lookup_lexicon`/`suggest_lexicon` 词典后处理永远加分（附四方辐射美学思维导图） |
| [章节总结/21-Object](./HALCON/章节总结/21-Object.md) | HALCON 官方手册第 21 章 **Object** 16 个算子（2 族：Information 信息查询 5 + Manipulation 操作管理 11），Iconic Object 元组管家用具箱——5 个只读看（`count_obj`/`get_obj_class`/`compare_obj`/`test_equal_obj`/`get_channel_info`）+ 11 个结构化改（`select_obj`/`concat_obj`/`copy_obj`/`insert_obj`/`remove_obj`/`replace_obj`/`obj_diff`/`clear_obj`/`gen_empty_obj`/`obj_to_integer`/`integer_to_obj`），所有操作严格遵循集合论语义（附双子星辐射思维导图） |
| [章节总结/22-Regions(上)](./HALCON/章节总结/22-Regions(上).md) | HALCON 官方手册第 22 章 Regions **上卷 35 算子**（4 族：Access 查询 5 + Creation 创建 21 + Sets 集合论 6 + Tests 断言 3），二值掩模「看、造、算、判」基础四件套——`get_region_points/runs/polygon/convex/contour` 解码 + `gen_circle/ellipse/rectangle1/rectangle2/_polygon_filled/_random_/...` 造几何 + `union1/union2/intersection/difference/symm_difference/complement` 集合论 + `test_equal_region/test_subset_region/test_region_point` 断言；是中卷 Features（测量）与下卷 Transformations（变换）的脚手架（附四角辐射思维导图） |
| [章节总结/22-Regions(中)](./HALCON/章节总结/22-Regions(中).md) | HALCON 官方手册第 22 章 Regions **中卷 41 算子**（1 族 7 主题：Features 区域测量 41 — 基础测量 8 + 内接外接 5 + 形状因子 7 + 矩与不变量 7 + 行程与厚度 4 + 距离与邻域 6 + 特征选择器 4），区域「测得有多准」全 41 件套——基础测标量（area_center/smallest_*）、形状因子（circularity/convexity）、不变矩（Hu 7 维指纹）、行程厚度、汉明距离、select_shape 系列批量筛选；**HALCON 视觉流水线的"特征工程中心"**——分割之后、匹配之前、Ch16 工业检测的算力底座（附七瓣辐射美学思维导图） |
| [章节总结/22-Regions(下)](./HALCON/章节总结/22-Regions(下).md) | HALCON 官方手册第 22 章 Regions **下卷 29 算子收官**（2 族 6 主题：Geometric 几何变换 8 — 仿射/射影/极坐标/镜像/平移/转置/缩放 + Transformations 区域变换 21 — 骨架中轴 4 + 区域修复 4 + 区域重塑 4 + 距离分割 3 + 裁剪拆分 6），「把区域换个姿势」——`affine_trans_region` 万能瑞士军刀、`polar_trans_region` 环形展开神器、`connection` 使用频率 Top3、`skeleton+junctions_skeleton` 线网络分析、`sort_region('character')` OCR 排队、`distance_transform` 距离场引擎；全章 35+41+29=**104 算子**一次讲完（附六角辐射美学思维导图） |
| [章节总结/23-Segmentation](./HALCON/章节总结/23-Segmentation.md) | HALCON 官方手册第 23 章 **Segmentation 图像分割** 53 个算子（6 子族：像素分类 13 + 边缘检测 4 + 极值稳定区域 1 + 区域生长 5 + 阈值分割 16 + 地形学 14），「把图里目标"抠"出来」的 6 套武器——`binary_threshold`(Otsu)/`dyn_threshold`(不均匀光照)/`local_threshold`(Sauvola)/`var_threshold`(金属纹理)/`watersheds_marker`(粘连分离)/`segment_image_mser`(自然场景文字)/`regiongrowing`(种子扩散)/`local_max_sub_pix`(亚像素特征点)；Ch20下管训练 Ch23管推理的 HALCON 经典设计（附六角辐射美学思维导图） |
| [章节总结/24-System(上)](./HALCON/章节总结/24-System(上).md) | HALCON 官方手册第 24 章 System **上卷 47 算子**（5 子族：计算设备 11 + 数据库 3 + 错误处理 7 + I/O 设备 15 + 元信息 11），「本地系统资源管理」——`activate_compute_device` GPU 加速 4 步套路（query→open→init→activate）/ `set_check('none'/'input'/'all')` 三档检查模式 / `get_extended_error_info` HDevelop catch 块主战武器 / `read_io_channel` + `write_io_channel` PLC 5 步触发拍照 / `get_operator_name` + `search_operator` + `get_param_info` 反射元数据（IDE/代码生成/ML 选算子底座）；全章 12 子族 133 算子，本卷 + 下卷（多线程/并行/网络 86 ops）（附五角辐射美学思维导图） |
| [章节总结/24-System(中)](./HALCON/章节总结/24-System(中).md) | HALCON 官方手册第 24 章 System **中卷 52 算子**（4 子族：Multithreading 多线程同步 38 + Operating System 操作系统 4 + Parallelization 自动算子并行化 AOP 6 + Parameters 算子超时控制 4），「让 HALCON 用满 CPU 跑完不超时」——`lock_mutex`/`signal_condition`/`enqueue_message` 多线程三大原语 + `wait_condition` 释放 mutex+阻塞+重锁三步原子 + `set_aop_info` + `set_system('parallelize_operators','true')` 双开关 AOP 部署 + `set_operator_timeout` 算子熔断器 + `barrier` 三方同步 + `optimize_aop` 离线算力评测（附四角辐射美学思维导图） |
| [章节总结/24-System(下)](./HALCON/章节总结/24-System(下).md) | HALCON 官方手册第 24 章 System **下卷 36 算子**（4 子族：Parameters 算子超时控制 4 + Serial RS-232 串口 7 + SerializedItem 序列化项 5 + Sockets TCP/UDP 套接字 20），「分布式系统篇」——`socket_accept_connect('accept','IP',PORT,'TCP',30)` 3 合 1 超级 socket 算子（取代 `open_socket_accept/connect` 两个的合并版） + `set_socket_param('TCP_NODELAY','true')` 关 Nagle 解决粘包 + `send_image/receive_image` 图像联网同步 + `send_serialized_item/fwrite_serialized_item` 模型跨机持久化传送 + `create_serialized_item_ptr` C/C++ 互操作（外部 byte[] 转 HALCON 句柄） + `set_serial_param(SH, 115200, 8, 'none', 'none', 1, 1000, 50)` 工业 RS-232 串口 7 参数（波特率/数据位/流控/奇偶/停止位/超时/字符间超时） + `set_operator_timeout('*', 3, 'cancel')` 全局算子熔断器（生产产线网络抖动救星） + `get_serialized_item_ptr` 拿底层指针接入 OpenCV；全章 12 子族 133 算子全部收官（47 + 52 + 36）（附四角非平衡美学思维导图，右下大卡 Sockets 网络套接字） |
| [章节总结/25-Tools(上)](./HALCON/章节总结/25-Tools(上).md) | HALCON 官方手册第 25 章 Tools **上卷 32 算子**（2 子族：Background Estimator 背景估计 7 + Function 1D 一维函数 25），「HALCON 的数学小工具箱——视频流建模 + 1D 信号处理」——`create_bg_esti`(10参初始化)+`run_bg_esti`(Kalman 自适应输出前景)+`update_bg_esti`(半监督注入永久背景) + `compose_funct_1d`(嵌套 f(g(x)))+`invert_funct_1d`(反函数沿 y=x 对折)+`smooth_funct_1d_gauss`(高斯 σ 端点镜像)+`distance_funct_1d`(L2 距离积分)+`match_funct_1d_trans`(平移对齐找位移)+`write/read_funct_1d`(.fun 二进制持久化)+`local_min_max_funct_1d`(严格/平台/全极值 6 模式)；全章 8 子族 103 算子，本卷 = 视频流 + 1D 信号（最'数学'的两族）（附双子星辐射美学思维导图） |
| [章节总结/25-Tools(中)](./HALCON/章节总结/25-Tools(中).md) | HALCON 官方手册第 25 章 Tools **中卷 42 算子**（5 主题：Distance Transform 距离变换 10 + Distance 测距 17 + Angle/Projection 角度·投影 4 + Intersection 求交 10 + Area Measure 面积 1），「HALCON 的几何决策算子库——从点-点距离到 2D 多边形碰撞」——`create_distance_transform_xld`（Mode 3 选 1）+`apply_distance_transform_xld`（Levels 正负偏移）+`get_distance_transform_xld_contour`（等距线提取） + `distance_pp/pl/pr/ps/lr/pc/lc/cc` 17 种二元测距 + `distance_cc_min_points`（最近点对坐标同时返回）+ `distance_rr_min_dil`（先膨胀 1px 融合细缝）+ `angle_ll`（同时也是 distance_ll 的别名）+ `projection_pl`（点沿直线垂直落点） + `intersection_segments/lines/line_circle/circles` 10 种求交 + `intersection_contours_xld`（多边形布尔求交）+ `area_intersection_rectangle2`（两旋转矩形 IOU 计算极简）；本章 = 视觉'几何决策'层（零件位姿匹配/夹具避让/路径规划/OCR 字符间距/抓取点投影）（附五角辐射美学思维导图） |

---

## 这个分类的约定

- **算子文档统一格式**：签名 → 是什么 → 关键参数 → 怎么用 → 坑 → 官方文档链接。
- **签名以官方 Operator Reference 为准**：HALCON 版本差异会改参数，每篇标注"数据基准"版本。
- **示例用 HDevelop 语法**：可直接粘到 HDevelop 运行，注释用中文。
