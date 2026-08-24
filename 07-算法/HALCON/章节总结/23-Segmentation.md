# 第 23 章 Segmentation：图像分割（53 算子 · 6 子族）

> **HALCON 官方手册第 23 章 Segmentation** 是 Ch20 OCR/Ch22 Regions 之外的"**图像级**"分割工具集——直接对**整张图**操作，把像素分成几类、找出边缘、定位目标边界。  
> 一句话总结：**第 23 章的本质 = "**把一张图里的目标"抠"出来**"的 6 套武器"**——① 像素级分类（深度学习/统计学习）、② 边缘检测（Sobel/Canny 风格）、③ 极值稳定区域（MSER 文字定位）、④ 区域生长（种子扩展）、⑤ 阈值分割（Otsu/局部/动态）、⑥ 地形学（分水岭/极值点）**。

---

## 1. 全章结构：6 子族总览

| 子族 | 算子数 | 一句话功能 | 典型场景 |
|---|---|---|---|
| **① 像素分类** | 13 | 用 GMM/KNN/MLP/SVM/LUT/2D 统计把每像素归类 | 缺陷检测分类、纹理分割 |
| **② 边缘检测** | 4 | 边缘幅值 + 方向非极大抑制 + 双滞后阈值 | Canny 风格边缘提取、缺陷边缘 |
| **③ 极值稳定区域** | 1 | MSER（最大稳定极值区域）——自然场景文字定位 | 自然场景文字 OCR 预定位 |
| **④ 区域生长** | 5 | 从种子点按灰度/距离/均值容差生长 | 粘连目标分离、肿瘤分割 |
| **⑤ 阈值分割** | 16 | 全局/局部/动态/方差/字符/双阈值 + 过零点 + 亚像素 | 工业最常用的二值化武器库 |
| **⑥ 地形学** | 14 | 分水岭 + 极值/鞍点/高原/盆地——把灰度图当"地形"处理 | 粘连物体分离、目标中心定位 |

**与第 22 章的分工**：
- **Ch22 Regions** = 操作"**二值掩膜**"（`Region` 数据结构）
- **Ch23 Segmentation** = 操作"**灰度图像**"，**生成**二值掩膜供 Ch22 处理
- 典型流水线：Ch23 `binary_threshold` → Ch22 `connection` + `select_shape_std` + `area_center` → Ch22中 `select_shape`

---

## 2. 6 子族分述（详细模式）

### ① 像素分类（Classification，13 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **add_samples_image_class_gmm** | 把标注好的区域喂给 GMM 训练集 · `add_samples_image_class_gmm(Image, ClassRegions : : GMMHandle, Randomize :)` |
| **add_samples_image_class_knn** | 把标注好的区域喂给 KNN 训练集 · `add_samples_image_class_knn(Image, ClassRegions : : KNNHandle :)` |
| **add_samples_image_class_mlp** | 把标注好的区域喂给 MLP 训练集 · `add_samples_image_class_mlp(Image, ClassRegions : : MLPHandle :)` |
| **add_samples_image_class_svm** | 把标注好的区域喂给 SVM 训练集 · `add_samples_image_class_svm(Image, ClassRegions : : SVMHandle :)` |
| **class_2dim_sup** | 2D 特征空间有监督分类 · `class_2dim_sup(ImageCol, ImageRow, FeatureSpace : RegionClass2Dim :)` |
| **class_2dim_unsup** | 2D 特征空间无监督聚类 · `class_2dim_unsup(Image1, Image2 : Classes : Threshold, NumClasses :)` |
| **class_ndim_norm** | n 维多通道图像的正态分布分类 · `class_ndim_norm(MultiChannelImage : Regions : Metric, SingleMultiple, Radius, Center :)` |
| **classify_image_class_gmm** | GMM 像素分类（推理） · `classify_image_class_gmm(Image : ClassRegions : GMMHandle, RejectionThreshold :)` |
| **classify_image_class_knn** | KNN 像素分类（推理，输出距离图） · `classify_image_class_knn(Image : ClassRegions, DistanceImage : KNNHandle, RejectionThreshold :)` |
| **classify_image_class_lut** | LUT（查表）像素分类 · `classify_image_class_lut(Image : ClassRegions : ClassLUTHandle :)` |
| **classify_image_class_mlp** | MLP 像素分类（推理） · `classify_image_class_mlp(Image : ClassRegions : MLPHandle, RejectionThreshold :)` |
| **classify_image_class_svm** | SVM 像素分类（推理） · `classify_image_class_svm(Image : ClassRegions : SVMHandle :)` |
| **learn_ndim_norm** | 训练 n 维正态分类器 · `learn_ndim_norm(Foreground, Background, Image : : Metric, Distance, MinNumberPercent :)` |

**用途**：
- **4 个 `add_samples_*`** 是"**数据准备**"——把人工标注的 ClassRegions（按颜色编码类别的 Region 集合）喂给分类器，得到 Handle。
- **4 个 `classify_image_class_*`** 是"**推理**"——喂入整张图，输出 ClassRegions（每个连通区一类）。
- **4 个分类器对比**：
  - **GMM**（高斯混合）= 概率密度模型，**软分类**，可输出拒绝阈值
  - **KNN**（K 近邻）= 距离最近投票，**对噪声敏感**，KNN 多输出一个 DistanceImage
  - **MLP**（多层感知机）= 神经网络，**对非线性最有效**
  - **SVM**（支持向量机）= 几何间隔最大，**小样本首选**
  - **LUT**（查表）= 速度最快，**只支持单特征**，需提前用 `create_class_lut` 建表
- **3 个 `class_*`** 是"**轻量版**"——无需训练，直接用 2 个特征图像做 2D 直方图阈值或聚类。
- **`learn_ndim_norm`** 是"**无 Handle 训练**"——直接对前景/背景 Region 学习正态分布。

**重点参数**：
- 4 个 `add_samples_*` 的 `ClassRegions` **必须按颜色索引**（class 1 = 灰度值 1，class 2 = 灰度值 2...）——`set_class_box` 不适用此处。
- 4 个 `classify_*` 的 `RejectionThreshold` ∈ [0, 1]——`0` 表示"强制分类"（无拒绝区），越大拒绝越多。
- `class_ndim_norm` 的 `Metric` ∈ {'euclidean', 'city-block', 'mahalanobis'}；`Radius` 是局部窗口半径。

**误区**：
- ⚠️ **4 个 `add_samples_*` 与 Ch20 下的 `add_samples_image_class_*` 是同一族**——名字相同，行为相同；先 `create_*` 建分类器（Ch20 下），再 `add_samples_*` 喂数据（Ch23），再 `train_*` 训练（Ch20 下），再 `classify_image_class_*` 推理（Ch23）。
- ⚠️ `class_2dim_sup` 是"**无训练**"的 2D 阈值——只接受**两个特征图**（如原图 + 边缘强度图），对 2D 散点图做矩形/任意形状分割。
- ⚠️ `classify_image_class_lut` 的 LUT **不抗噪声**——要求特征明显分离；若重叠严重用 SVM/MLP。
- ⚠️ `learn_ndim_norm` 的 `MinNumberPercent` ∈ [1, 100]——百分比过小过拟合，过大欠拟合。

### ② 边缘检测（Edges，4 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **detect_edge_segments** | 边缘段检测（边缘图 → 边缘线段） · `detect_edge_segments(Image : : SobelSize, MinAmplitude, MaxDistance, MinLength : BeginRow, BeginCol, EndRow, EndCol)` |
| **hysteresis_threshold** | 双滞后阈值（Canny 高/低阈值） · `hysteresis_threshold(Image : RegionHysteresis : Low, High, MaxLength :)` |
| **nonmax_suppression_amp** | 非极大幅值抑制（仅按幅值） · `nonmax_suppression_amp(ImgAmp : ImageResult : Mode :)` |
| **nonmax_suppression_dir** | 非极大方向抑制（按幅值+方向） · `nonmax_suppression_dir(ImgAmp, ImgDir : ImageResult : Mode :)` |

**用途**：
- **Canny 边缘检测器**的 HALCON 实现四件套：
  1. `sobel_amp` / `sobel_dir` 算幅值/方向（Ch11）
  2. `nonmax_suppression_dir` 沿梯度方向细化为 1 像素宽
  3. `hysteresis_threshold` 双阈值（`High` 强边缘 + `Low` 弱边缘）连接成闭合边缘
  4. `detect_edge_segments` 把边缘拆成线段（端点坐标元组）
- **`hysteresis_threshold` 也可独立用于任何梯度图**（如 `edges_image` 的输出）——双阈值连接是"边缘去断"通用技巧。
- **`nonmax_suppression_amp` 比 `nonmax_suppression_dir` 简单**——只按局部极大抑制，无需方向图；适合对称结构（如圆）。

**重点参数**：
- `hysteresis_threshold` 的 `High` ≥ `Low`——典型比值 2:1 或 3:1；`MaxLength` 是断点间最大桥接距离（消除短断点）。
- `nonmax_suppression_*` 的 `Mode` ∈ {'nms', 'inms', 'rnms', 'gradient'}——`'nms'` 严格 1 像素宽；`'gradient'` 保持原宽度。
- `detect_edge_segments` 的 `MaxDistance` 是**多边形逼近**的最大偏差（亚像素精度）；`MinLength` 是线段最小长度（去短噪声）。

**误区**：
- ⚠️ `nonmax_suppression_*` **不内置梯度计算**——需先用 `sobel_amp`/`sobel_dir` 或 `edges_image` 算梯度，再喂入。
- ⚠️ `hysteresis_threshold` 输出的是 **Region**（像素集合），不是 XLD 轮廓——要 XLD 用 `gen_contours_xld` 转换。
- ⚠️ `detect_edge_segments` **依赖连通**——若边缘断成碎段，输出也碎；可先 `close_edges` 闭边。

### ③ 极值稳定区域（MSER，1 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **segment_image_mser** | MSER 极值稳定区域（自然场景文字定位神器） · `segment_image_mser(Image : MSERDark, MSERLight : Polarity, MinArea, MaxArea, Delta, MaxAreaVariation, MinDiversity :)` |

**用途**：
- **MSER 是自然场景文字定位的"算法之王"**——Matas 2004 的开创性算法，对**尺度、旋转、仿射都鲁棒**。
- **HALCON 一次返回两类区域**：`MSERDark`（深色背景亮文字）+ `MSERLight`（亮色背景深文字）——通过 `Polarity` 切换。
- **典型用法链**：`segment_image_mser` → `select_shape_std(MSER, 'area', 80)` → `select_shape(..., 'circularity', 'and', 0.5, 1.0)` → `dilation_circle` 合并碎片 → `connection` → 喂给 Ch20 OCR `do_ocr_*_class_cnn`。

**重点参数**：
- `MinArea` / `MaxArea` 是 MSER 区域像素面积范围（太小的噪声、太大的背景都要滤）。
- `Delta` 是**稳定性阈值**——5~10 较稳；越大输出越少。
- `MaxAreaVariation` 是区域在阈值扫描中的**最大面积变化率**——越大越宽松。
- `MinDiversity` 是**父子区域不重叠阈值**——避免嵌套冗余。

**误区**：
- ⚠️ MSER 对**光滑渐变**图像效果差（如金属表面）——对**高对比度文字**（黑字白底）效果最佳。
- ⚠️ **输出是 Region 集合**（多连通），需 `connection` 拆开再 `select_shape`——否则 `select_shape` 不工作。
- ⚠️ MSER **计算量 O(n log log n)**——千万像素图可能 1~3 秒；实时性要求场景慎用。
- ⚠️ **Ch24 章 `segment_image_mser_gray`** 与本算子**功能基本一致**，仅对灰度图优化；多通道图仍用本算子。

### ④ 区域生长（Region Growing，5 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **expand_gray** | 灰度区域扩张（种子按灰度容差 + 几何） · `expand_gray(Regions, Image, ForbiddenArea : RegionExpand : Iterations, Mode, Threshold :)` |
| **expand_gray_ref** | 参考灰度区域扩张（种子按参考值容差） · `expand_gray_ref(Regions, Image, ForbiddenArea : RegionExpand : Iterations, Mode, RefGray, Tolerance :)` |
| **regiongrowing** | 经典区域生长（按灰度差 + 最小尺寸） · `regiongrowing(Image : Regions : RasterHeight, RasterWidth, Tolerance, MinSize :)` |
| **regiongrowing_mean** | 均值区域生长（按窗口均值差） · `regiongrowing_mean(Image : Regions : StartRows, StartColumns, Tolerance, MinSize :)` |
| **regiongrowing_n** | n 邻域通道区域生长（多通道） · `regiongrowing_n(MultiChannelImage : Regions : Metric, MinTolerance, MaxTolerance, MinSize :)` |

**用途**：
- **5 个算子都是"**种子向外扩散**"思想**——区别在于"扩散规则"：
  - `expand_gray` = 单点/区域向外膨胀，邻域像素灰度差 ≤ `Threshold` 接纳
  - `expand_gray_ref` = 扩展到指定参考灰度 ± 容差
  - `regiongrowing` = 矩形网格扫描，相邻块灰度差 ≤ `Tolerance` 合并
  - `regiongrowing_mean` = 局部均值作种子，自适应阈值
  - `regiongrowing_n` = 多通道图（彩色），多维距离
- **`expand_gray` + `ForbiddenArea`** 是"**避障生长**"——如血管扩张但避开骨骼；与 Ch22 `expand_region` 一脉相承。
- **`regiongrowing` 是 Ch23 的"扫一遍出全图"经典版**——输入整图直接出全部分割；适合噪声小、对比度高的图。

**重点参数**：
- `expand_gray` 的 `Mode` ∈ {'image', 'region'}——是否限制在图像域/原区域内。
- `regiongrowing` 的 `RasterWidth/RasterHeight` 是**网格尺寸**——越大块越粗（"过分割"风险降），细节差。
- `regiongrowing_n` 的 `MinTolerance/MaxTolerance` 是**双阈值**——min 控制"分多细"，max 控制"是否合并"。

**误区**：
- ⚠️ `regiongrowing` 的**网格扫描是串行的**——结果依赖扫描起点；如需确定结果用 `regiongrowing_mean` + 固定 `StartRows/Columns`。
- ⚠️ `expand_gray` 只能接受**小种子**（<100 像素）——大种子会"长爆"。
- ⚠️ `regiongrowing_n` 接受**多通道**图像——但要传 `MultiChannelImage`（不是普通 Image），用 `image_to_channels` 转。

### ⑤ 阈值分割（Threshold，16 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **auto_threshold** | 自动直方图阈值（多区域分割） · `auto_threshold(Image : Regions : Sigma :)` |
| **binary_threshold** | Otsu 二值阈值（最常用） · `binary_threshold(Image : Region : Method, LightDark : UsedThreshold)` |
| **char_threshold** | 字符提取阈值（针对文字） · `char_threshold(Image, HistoRegion : Characters : Sigma, Percent : Threshold)` |
| **check_difference** | 差异检查（与模板对比） · `check_difference(Image, Pattern : Selected : Mode, DiffLowerBound, DiffUpperBound, GrayOffset, AddRow, AddCol :)` |
| **dual_threshold** | 双阈值（范围筛选） · `dual_threshold(Image : RegionCrossings : MinSize, MinGray, Threshold :)` |
| **dyn_threshold** | 动态阈值（局部均值对比） · `dyn_threshold(OrigImage, ThresholdImage : RegionDynThresh : Offset, LightDark :)` |
| **fast_threshold** | 快速阈值（MinMax 全局） · `fast_threshold(Image : Region : MinGray, MaxGray, MinSize :)` |
| **histo_to_thresh** | 直方图转阈值（人工分析工具） · `histo_to_thresh(: : Histogramm, Sigma : MinThresh, MaxThresh)` |
| **laplace_of_gauss** | 高斯拉普拉斯（边缘增强） · `laplace_of_gauss(Image : ImageLaplace : Sigma :)` |
| **local_threshold** | 局部阈值（Niblack/Sauvola 等） · `local_threshold(Image : Region : Method, LightDark, GenParamName, GenParamValue :)` |
| **sub_image** | 图像相减（预处理常备） · `sub_image(ImageMinuend, ImageSubtrahend : ImageSub : Mult, Add :)` |
| **threshold** | 全局阈值（最基础） · `threshold(Image : Region : MinGray, MaxGray :)` |
| **threshold_sub_pix** | 亚像素阈值（边缘精度） · `threshold_sub_pix(Image : Border : Threshold :)` |
| **var_threshold** | 方差阈值（局部标准差） · `var_threshold(Image : Region : MaskWidth, MaskHeight, StdDevScale, AbsThreshold, LightDark :)` |
| **zero_crossing** | 过零点（二阶导数边缘） · `zero_crossing(Image : RegionCrossing :)` |
| **zero_crossing_sub_pix** | 亚像素过零点 · `zero_crossing_sub_pix(Image : ZeroCrossings :)` |

**用途**：
- **16 算子是"工业分割全家福"**——按场景选择：
  - **均匀光照** → `binary_threshold`（Otsu）或 `threshold`（手动）
  - **不均匀光照** → `dyn_threshold`（先 `mean_image`/`gauss_image` 做平滑图，再与原图比）
  - **印刷字符** → `char_threshold`（针对字符直方图特殊优化）
  - **细节丰富**（金属表面/纤维） → `local_threshold`（Sauvola）或 `var_threshold`（按局部方差）
  - **背景相近**（血管/裂纹） → `check_difference` 与模板对比
  - **大区域分割** → `auto_threshold` 一次出多类
- **3 个 sub_pix 算子**（`threshold_sub_pix`/`zero_crossing_sub_pix`/`critical_points_sub_pix`）输出**亚像素精度**——边缘定位精度 0.1 像素级，远胜于普通 `threshold`。
- **`sub_image` 在 Threshold 族**是因为它与 `dyn_threshold` 配套——先 `mean_image` 再 `sub_image` 得到高通图。

**重点参数**：
- `binary_threshold` 的 `Method` ∈ {'max_separability'（Otsu 默认）, 'smooth_histo'（直方图平滑）, 'min_residual'（最小残差）}。
- `local_threshold` 的 `Method` ∈ {'adapted_std_dev', 'background_mean', 'otsu', 'niblack', 'sauvola', 'sauvola_modified', 'sort', 'interpolate'}。
- `dyn_threshold` 的 `Offset` ∈ [0, 255]——越大越严（少分）；`LightDark` ∈ {'light', 'dark', 'equal', 'not_equal'}。
- `var_threshold` 的 `MaskWidth/Height` 是**局部窗口**——太小时噪声敏感，太大时边缘模糊。

**误区**：
- ⚠️ `threshold` 输出**整数像素**的 Region，`threshold_sub_pix` 输出 **XLD 亚像素轮廓**——**两者完全不是同一类结果**！
- ⚠️ `dyn_threshold` 的 `Offset` 是**绝对灰度差**（不是相对百分比）——对深色目标设小 Offset（如 5~10）。
- ⚠️ `local_threshold` 的 `niblack/sauvola` **对白底黑字**字符效果极佳，**黑底白字**要传 `'dark'` LightDark。
- ⚠️ `laplace_of_gauss` 是**二阶导算子**，输出有正有负（用 `zero_crossing` 提取边缘），不是直方图阈值可处理的。
- ⚠️ `sub_image` 的 `Mult/Add` 是**仿射变换参数**：`result = (a - b) * Mult + Add`——典型用 `Mult = 1, Add = 0`（直接相减）；若要归一化到 0~255 设 `Mult = 1/2, Add = 128`（要先 `scale_image` 收范围）。

### ⑥ 地形学（Topography，14 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **critical_points_sub_pix** | 亚像素临界点（一阶/二阶导数=0 的位置） · `critical_points_sub_pix(Image : : Filter, Sigma, Threshold : RowMin, ColumnMin, RowMax, ColumnMax)` |
| **local_max** | 局部极大值（像素级） · `local_max(Image : LocalMaxima :)` |
| **local_max_sub_pix** | 亚像素局部极大值 · `local_max_sub_pix(Image : : Filter, Sigma, Threshold : Row, Column)` |
| **local_min** | 局部极小值（像素级） · `local_min(Image : LocalMinima :)` |
| **local_min_sub_pix** | 亚像素局部极小值 · `local_min_sub_pix(Image : : Filter, Sigma, Threshold : Row, Column)` |
| **lowlands** | 低地（连通极小区域） · `lowlands(Image : Lowlands :)` |
| **lowlands_center** | 低地中心（低地质心） · `lowlands_center(Image : Lowlands :)` |
| **plateaus** | 高地（连通极大区域） · `plateaus(Image : Plateaus :)` |
| **plateaus_center** | 高地中心（高地质心） · `plateaus_center(Image : Plateaus :)` |
| **pouring** | 注水（模拟水从低地倒流到高原） · `pouring(Image : Regions : Mode, MinGray, MaxGray :)` |
| **saddle_points_sub_pix** | 亚像素鞍点 · `saddle_points_sub_pix(Image : : Filter, Sigma, Threshold : Row, Column)` |
| **watersheds** | 分水岭（无标记版） · `watersheds(Image : Basins, Watersheds :)` |
| **watersheds_marker** | 标记分水岭（可控合并） · `watersheds_marker(Image, Markers : Basins :)` |
| **watersheds_threshold** | 阈值分水岭（先阈值再分水岭） · `watersheds_threshold(Image : Basins : Threshold :)` |

**用途**：
- **14 算子把"灰度图"当"地形"看**——灰度 = 海拔，灰度峰 = 山峰，灰度谷 = 山谷。
- **3 个分水岭算子**是 HALCON 的"**粘连物体分离**"杀手锏：
  - `watersheds` = 默认分水岭，过分割严重（每个山头一个区域），但稳定
  - `watersheds_marker` = **用 Marker Region 控制**——指定种子在哪、背景在哪，分割可控
  - `watersheds_threshold` = **先阈值再分水岭**——先去掉不明显的谷，再分剩余
- **6 个极值算子**（`local_max/min` × 普通/sub_pix + `critical_points_sub_pix`）找"**关键定位点**"——如星点定位、特征点检测、棋盘格角点。
- **`pouring` 是分水岭的"反义"**——不是从低往高爬，而是"倒水"模拟——能找流域盆地（适合找"每个洞属于哪个山头"）。

**重点参数**：
- 4 个 `*_sub_pix` 算子的 `Filter` ∈ {'facet', 'gauss'}——`'facet'` 用多项式拟合，最快；`'gauss'` 用高斯卷积，最准。
- `watersheds_marker` 的 `Markers` **必须包含背景标记**（如区域边框）——否则会"全部分给前景"。
- `watersheds_threshold` 的 `Threshold` 是**分水岭的最小谷深**——越大分得越粗。
- `pouring` 的 `Mode` ∈ {'all', 'centers', 'image'}——`'centers'` 只输出注水中心点（Region 中心）。

**误区**：
- ⚠️ `watersheds` **过分割是常态**——100 个粘连目标可能出 1000 个 Basin。务必用 `watersheds_marker` 显式控制。
- ⚠️ `local_max` 输出**像素坐标的 Region**，`local_max_sub_pix` 输出**实数坐标的元组**——前者喂 Ch22，后者喂 Ch18 矩阵或 Ch25 calibration。
- ⚠️ `critical_points_sub_pix` 同时找**极小 + 极大**——输出是两套元组（`RowMin, ColumnMin` 极小点 + `RowMax, ColumnMax` 极大点）。
- ⚠️ `pouring` 与 `watersheds` **互为对偶**——前者从下往上倒水，后者从上往下漫水。
- ⚠️ `lowlands` 与 `lowlands_center` 区别：前者返回整个低地区域（像素集合），后者返回低地的**中心**（一个点/区域）。

---

## 3. 关键技术要点

### 3.1 阈值分割的"6 步选择法"

| 场景 | 首选算子 | 备选 |
|---|---|---|
| 均匀光照单峰 | `binary_threshold`（Otsu 默认） | `threshold`（手动） |
| 不均匀光照 | `dyn_threshold`（需先 `mean_image`） | `local_threshold`（Sauvola） |
| 印刷字符 | `char_threshold` | `binary_threshold` + 形态学 |
| 金属/纹理表面 | `var_threshold`（按局部方差） | `local_threshold`（adapted_std_dev） |
| 多区域分割 | `auto_threshold` | `class_ndim_norm` |
| 边缘定位（亚像素） | `threshold_sub_pix` | `zero_crossing_sub_pix` |

### 3.2 动态阈值的"差图"三件套

```
mean_image(Image, Mean, 51, 51)    * 计算局部均值
dyn_threshold(Image, Mean, DynRegion, 5, 'light')   * 局部高光区
```

**原理**：原图 - 均值图 = 高频残差图，残差 > 阈值即为前景。**Offset 控制敏感度**。

### 3.3 分水岭的"标记控制"（粘连分离标准套路）

```
* 1. 找确信的种子（用 binary_threshold + select_shape）
binary_threshold(Image, Bin, 'max_separability', 'dark', UsedThreshold)
opening_circle(Bin, Opening, 5)  * 抗噪
connection(Opening, Conn)
select_shape_std(Conn, Seeds, 'area', 80)  * 保留大头
* 2. 加背景标记
boundary(Conn, Border, 'inner')
concat_obj(Seeds, Border, Markers)
* 3. 标记分水岭
watersheds_marker(Image, Markers, Basins)
```

**核心**：种子是"目标中心"，边界是"背景外圈"——`watersheds_marker` 在两者之间铺水。

### 3.4 像素分类的"3 步训练流水线"

```
1. create_class_* (Ch20 下)            → 创建分类器 Handle
2. add_samples_image_class_* (Ch23)    → 喂标注好的区域
3. train_class_* (Ch20 下)             → 训练
4. classify_image_class_* (Ch23)       → 推理
5. clear_class_* (Ch20 下)             → 释放
```

**Ch20 下（OCV）管训练，Ch23（Segmentation）管推理**——这种"训练/推理分两章"的 HALCON 设计是因为 GPU/CPU 算力优化分离。

### 3.5 MSER 的"自然场景文字定位"标准流水线

```
segment_image_mser(Image, MSERDark, MSERLight, 'dark_on_light', ...)
select_shape_std(MSERLight, Selected, 'area', 70)   * 过滤小碎片
connection(Selected, Connected)
select_shape(Connected, Filtered, 'circularity', 'and', 0.3, 1.0, 'max_area')  
* OCR 喂入
dilation_circle(Filtered, Dilated, 1.5)
connection(Dilated, Words)
sort_region(Words, SortedWords, 'character', 'true', 'column')
* do_ocr_word_knn(SortedWords, Image, OCRHandle, 'auto', RecWords, Conf)
```

**核心**：MSER 找文字候选 → 形状筛选 → 合并成词 → 排序 → OCR。

### 3.6 区域生长的"种子策略"

| 场景 | 种子来源 |
|---|---|
| 已知目标中心 | `area_center` + `gen_region_points` |
| 高亮/暗点 | `local_max` / `local_min` |
| 用户点击 | `draw_point` 交互 |
| 多个均匀目标 | `regiongrowing` 直接出全图 |

---

## 4. 流水线定位

```
[图像输入] → [预处理 (Ch11 image filters)] → 【本卷:6 套分割武器】
                                                ↓
                ┌──────────────────────────────┼──────────────────────────────┐
                ↓                              ↓                              ↓
        [Ch20 OCR 上 Deep OCR]           [Ch22 Regions 上卷]            [Ch20 OCR 下]
        segment_image_mser               connection + select_shape_std   classify_image_class_*
                ↓                              ↓                              ↓
        find_text + segment_characters    area_center + smallest_*       do_ocr_word_svm
```

**本卷是 HALCON 视觉流程的"**目标定位中心**"**——上游接原始图像，下游接 OCR/Ch22/Ch25 三条主分支。

---

## 5. 与其它章节的关联

- **Ch11 Image Filters**：`mean_image`/`gauss_image` 是 `dyn_threshold` 的前置；`laplace_of_gauss` 是 `zero_crossing` 的二阶导。
- **Ch20 上 OCR**：`segment_image_mser` → `find_text` → `segment_characters` 是自然场景 OCR 黄金链。
- **Ch20 下 OCV**：`add_samples_image_class_*`/`classify_image_class_*` 与 `create_class_*`/`train_class_*` 是训练/推理的"配对算子"。
- **Ch22 Regions**：`binary_threshold`/`watersheds_marker` 的输出直接喂 `connection + select_shape`。
- **Ch25 Calibration**：`local_max_sub_pix`/`critical_points_sub_pix` 是相机标定找特征点的主流方法。
- **Ch24 Calibration/Matching**：`regiongrowing` 与 Ch24 `shape_from_silhouette` 配合做 3D 重建。

---

## 6. 6 子族算子速查表

| 子族 | 算子（按功能顺序） |
|---|---|
| ① 像素分类 | add_samples_image_class_gmm/knn/mlp/svm、class_2dim_sup/unsup、class_ndim_norm、classify_image_class_gmm/knn/lut/mlp/svm、learn_ndim_norm |
| ② 边缘检测 | detect_edge_segments、hysteresis_threshold、nonmax_suppression_amp、nonmax_suppression_dir |
| ③ 极值稳定区域 | segment_image_mser |
| ④ 区域生长 | expand_gray、expand_gray_ref、regiongrowing、regiongrowing_mean、regiongrowing_n |
| ⑤ 阈值分割 | auto_threshold、binary_threshold、char_threshold、check_difference、dual_threshold、dyn_threshold、fast_threshold、histo_to_thresh、laplace_of_gauss、local_threshold、sub_image、threshold、threshold_sub_pix、var_threshold、zero_crossing、zero_crossing_sub_pix |
| ⑥ 地形学 | critical_points_sub_pix、local_max、local_max_sub_pix、local_min、local_min_sub_pix、lowlands、lowlands_center、plateaus、plateaus_center、pouring、saddle_points_sub_pix、watersheds、watersheds_marker、watersheds_threshold |

> **下一章预告**：第 24 章 Edge Filters（边缘算子深度版）/ 或第 25 章 System（相机/标定/图像采集）。HALCON 的"图像→世界"坐标打通在 System 章。
