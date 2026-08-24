# 第 22 章 Regions · 中卷：Features 区域测量（41 算子 · 7 主题簇）

> **HALCON 官方手册第 22 章 Regions** 全部 104 个算子中，**中卷 = Features 子章节**独占 **41 算子**，是 Regions 章最厚的一卷。  
> 上卷（35 算子）已经讲完「看 + 造 + 集合论」基础四件套；**本卷把每个区域『量得有多准』的全部 41 种测量工具一次给全**。  
> 它是机器视觉从「找到区域」到「判断好坏、分类筛选、定位定向」之间那座桥——**上接分割（Ch20 上 OCR/Segmentation 把目标从背景里抠出来），下启分类（Ch19 Morphology、Ch15 Classification 给区域打标签）**。  
> 一句话总结：**Features 章的本质 = 一台覆盖几何/拓扑/矩/空间/行程五大维度的"区域测量仪"**。

---

## 1. 全章结构：7 主题簇总览

| 主题簇 | 算子数 | 一句话功能 | 典型场景 |
|---|---|---|---|
| **① 基础测量** | 8 | 像素级标量（面积、质心、直径、轮廓长、欧拉数、连通数等） | 缺陷面积统计、目标质心跟踪 |
| **② 内接外接** | 5 | 最小/最大包围几何（圆、轴对齐/旋转矩形） | 零件尺寸测量、装箱排版 |
| **③ 形状因子** | 7 | 圆度、矩形度、紧凑度、凸度、椭圆近似等无量纲指标 | 颗粒分析、形状筛选 |
| **④ 矩与不变量** | 7 | 几何矩、中心矩、平移/旋转/缩放不变矩 | 字符识别、形状匹配归一化 |
| **⑤ 行程与厚度** | 4 | 行程长度分布、厚度直方图 | 骨架分析、裂纹测深 |
| **⑥ 距离与邻域** | 6 | 汉明距离、邻域搜索、点查询、空间关系 | 区域配准、相对位置判断 |
| **⑦ 特征选择器** | 4 | 批量算特征、按阈值筛选 | Blob 分析主流程 |

**总图**：本卷是 HALCON 视觉检测流水线的「**特征工程中心**」——分割之后（Ch20 上）、匹配之前（Ch17 上）的必经环节；select_shape 系列的批量特征计算是 `inspect_*` 系列工业检测算子（Ch16）的算力底座。

---

## 2. 7 主题簇分述（详细模式）

> 算子格式：**算子名 | 一句话功能 · HDevelop 关键签名**。  
> 每个算子附"**用途 / 重点参数 / 误区**"三段注。

### ① 基础测量（8 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **area_center** | 区域面积与质心 · `area_center(Regions : : : Area, Row, Column)` |
| **area_holes** | 所有孔洞的面积之和 · `area_holes(Regions : : : Area)` |
| **diameter_region** | 区域直径（边界两点最大距离）+ 两端坐标 · `diameter_region(Regions : : : Row1, Column1, Row2, Column2, Diameter)` |
| **height_width_ratio** | 轴对齐外接矩形高/宽比 · `height_width_ratio(Regions : : : Height, Width, Ratio)` |
| **contlength** | 边界总长（相邻像素按 √2 修正） · `contlength(Regions : : : ContLength)` |
| **connect_and_holes** | 连通分量数 + 孔洞数（一次算俩） · `connect_and_holes(Regions : : : NumConnected, NumHoles)` |
| **euler_number** | 欧拉数 = 连通分量数 − 孔洞数 · `euler_number(Regions : : : EulerNumber)` |
| **orientation_region** | 区域主轴方向（弧度） · `orientation_region(Regions : : : Phi)` |

**用途**：
- 8 个都是 O(像素) 级标量，**对单个 Region 数组返回 1×N 元组**（N = 区域数）。
- **面积是所有 Blob 分析的第一关**——`Area`=0 的区域直接淘汰（噪声），`Area`<阈值用 `select_shape` 一刀切。
- **欧拉数**是材料学/细胞学的核心指标：每个孔洞降 1，断裂降 1——可判连通性破坏。
- **orientation_region** 比 `elliptic_axis` 返回的 `Phi` 少一个 `+π/2` 校正，是工业上最常用的"目标朝向"。

**重点参数**：
- 所有 8 个都"无控制参数"——直接喂区域、拿标量。
- `Row, Column` 是图像坐标 `(y, x)`，**不是 `(x, y)`**！与 `gen_circle` 等保持一致。

**误区**：
- ⚠️ `area_center` 返回的 `Row, Column` 是**实数（带亚像素）**，不是整数质心——若需整数化用 `tuple_round`。
- ⚠️ `contlength` 对斜向边缘按 `√2` 修正（而非 1.0），与 `gen_rectangle1` 的几何周长**不完全相等**，差 0.4142 像素/斜边。
- ⚠️ `orientation_region` 是**主轴方向**（最长对称轴），并非"目标朝向"（可能差 90°）——若需目标指向头尾，请用 `moments_region_2nd` 算 `Phi` 再加 `if Phi>0: Phi+π/2` 转换。
- ⚠️ `area_holes` 计算的是**所有孔的面积之和**，不是每个孔单独面积——若要"每个孔"，得 `connection + fill_up` 拆分。

### ② 内接外接（5 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **smallest_circle** | 最小外接圆（Welzl 算法） · `smallest_circle(Regions : : : Row, Column, Radius)` |
| **smallest_rectangle1** | 最小外接轴对齐矩形 · `smallest_rectangle1(Regions : : : Row1, Column1, Row2, Column2)` |
| **smallest_rectangle2** | 最小外接旋转矩形（带角度与半轴长） · `smallest_rectangle2(Regions : : : Row, Column, Phi, Length1, Length2)` |
| **inner_circle** | 最大内接圆 · `inner_circle(Regions : : : Row, Column, Radius)` |
| **inner_rectangle1** | 最大内接轴对齐矩形 · `inner_rectangle1(Regions : : : Row1, Column1, Row2, Column2)` |

**用途**：
- **最小外接圆/矩形**是装配检测、装箱规划的标准前置——比如"这个零件能塞进 R=12mm 的圆孔吗？"。
- **最小旋转矩形** `smallest_rectangle2` 返回的 `Phi, Length1, Length2` 三件套是工业测量黄金参数——直接喂给 `gen_rectangle2` 画辅助线，或喂给 `vector_to_pose` 做抓取位姿估计。
- **内接圆/矩形**用于"最薄处"/"最窄处"测量（如瓶口内径、缝隙最小宽度）。

**重点参数**：
- `smallest_rectangle2` 的 `Phi` 是**旋转角，弧度**，约定 `Length1 ≥ Length2`（HALCON 内部会归一化），相当于"先沿主轴量 Length1、再垂直量 Length2"。
- `smallest_circle` 用 Welzl 随机化算法，**对凹区域可能不是紧贴的圆**——需要更精确请用 `shape_trans` 转凸包再算。

**误区**：
- ⚠️ `smallest_rectangle1` 是**外接**（包围整个区域），与 `inner_rectangle1`（内接）容易混——`inner_rectangle1` 在区域内，**Row2-Row1+1, Column2-Column1+1** 是"能塞进的最大矩形"。
- ⚠️ `smallest_rectangle2` 返回的 `Row, Column` 是**矩形中心**，不是区域质心——两者一般差几像素。
- ⚠️ 三个 smallest/inner 在 HALCON 里**没有控制参数**，纯算法；想"轴对齐到 5 度"这类约束需要 `gen_rectangle2` 手动试角度。

### ③ 形状因子（7 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **circularity** | 圆度 = 周长²/(4π·面积)，1 为完美圆 · `circularity(Regions : : : Circularity)` |
| **rectangularity** | 矩形度 = 区域面积 / 外接矩形面积，1 为完美矩形 · `rectangularity(Regions : : : Rectangularity)` |
| **compactness** | 紧凑度 = 周长²/(16π·面积)，1 为圆，0.785 为正方形 · `compactness(Regions : : : Compactness)` |
| **convexity** | 凸度 = 凸包周长 / 区域周长，1 为凸 · `convexity(Regions : : : Convexity)` |
| **roundness** | 圆润度 = 内接圆半径 / 外接圆半径，1 为圆 · `roundness(Regions : : : Distance, Sigma, Roundness, Sides)` |
| **eccentricity** | 离心率三件套（各向异性、块度、结构因子） · `eccentricity(Regions : : : Anisometry, Bulkiness, StructureFactor)` |
| **elliptic_axis** | 等效椭圆半轴长 Ra, Rb 与方向 Phi · `elliptic_axis(Regions : : : Ra, Rb, Phi)` |

**用途**：
- 这 7 个**无量纲指标**是工业筛检的核心武器——同样的两个齿轮，靠 `compactness` 差 0.02 就能挑出。
- `eccentricity` 一次性返回 3 个独立指标：Anisometry（Ra/Rb，>1 椭）、Bulkiness（π·Ra·Rb/area，填充比）、StructureFactor（Anisometry·Bulkiness 复合）。
- `roundness` 与 `circularity` 都用于"圆度"，但定义不同：roundness **0~1 严格**（不依赖面积），circularity **理论上 0~∞**（对非圆 > 1）。

**重点参数**：
- `circularity`、`compactness` 都是"周长² 形式"——对噪声区域**极度敏感**，低阈值时容易把"毛刺"误判为圆度差。
- `convexity` 需要先 `shape_trans(Region, ConvexRegion, 'convex')` 算凸包内嵌——HALCON 内部自动，不需用户调。

**误区**：
- ⚠️ `circularity = 1.0` **不是 100% 等于圆**——一个五边形圆度也只有 ~0.7；要更精确请用 `roundness`（内/外接圆半径比，区分五边形/七边形 vs 圆）。
- ⚠️ `rectangularity` 在 L 形、T 形零件上会很低（~0.5）——这是"形状匹配成功"的反面指标。
- ⚠️ `eccentricity` 在像素离散化下，**对扁长区域** Anisometry 会比理论值偏小——建议先 `dilation_circle` 做亚像素平滑再算。
- ⚠️ `elliptic_axis` 的 `Phi` **约定方向为 0~π**，与 `orientation_region` 的 `Phi`（-π/2~π/2）**范围不同**。

### ④ 矩与不变量（7 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **moments_region_2nd** | 二阶几何矩（M11, M20, M02）+ 主轴 Ia, Ib · `moments_region_2nd(Regions : : : M11, M20, M02, Ia, Ib)` |
| **moments_region_2nd_invar** | 二阶平移/缩放不变矩 · `moments_region_2nd_invar(Regions : : : M11, M20, M02)` |
| **moments_region_2nd_rel_invar** | 二阶旋转/缩放/平移完全不变矩 PHI1, PHI2 · `moments_region_2nd_rel_invar(Regions : : : PHI1, PHI2)` |
| **moments_region_3rd** | 三阶几何矩（M21, M12, M03, M30） · `moments_region_3rd(Regions : : : M21, M12, M03, M30)` |
| **moments_region_3rd_invar** | 三阶平移/缩放不变矩 · `moments_region_3rd_invar(Regions : : : M21, M12, M03, M30)` |
| **moments_region_central** | 中心矩（相对质心） · `moments_region_central(Regions : : : I1, I2, I3, I4)` |
| **moments_region_central_invar** | 中心不变矩 PSI1~4 · `moments_region_central_invar(Regions : : : PSI1, PSI2, PSI3, PSI4)` |

**用途**：
- **不变矩是模式识别的"指纹"**——同样形状无论位置/大小/方向，矩值不变，用于：字符识别（OCR 特征向量）、形状匹配归一化、零件分类。
- `moments_region_2nd_rel_invar`（PHI1, PHI2）和 `moments_region_central_invar`（PSI1~4）是 **Hu 矩的两种实现**——前者来自二阶、后者含三阶信息。
- **区域指纹**计算标准三步：① `moments_region_2nd_invar` 算 PHI1, PHI2；② `moments_region_3rd_invar` 算三阶；③ 拼接成 7 维特征向量喂给 MLP/SVM（Ch20 下）。

**重点参数**：
- `moments_region_2nd` 的 `Ia, Ib` 是**等效椭圆的半轴长**——比 `elliptic_axis` 算得更快，**与 `elliptic_axis` 在数值上略有差异**（用 4 倍缩放系数）。
- `moments_region_central` 的 `I1~I4` 是**归一化的中心矩**（除以零阶矩的 2/3、5/3 等幂次），天然具有平移不变性。

**误区**：
- ⚠️ **矩与不变矩的"不变性"是有限度的**——缩放不变依赖**面积归一化**，对**小区域（<10 像素）**离散化误差可能让 PHI1 偏移 >10%。
- ⚠️ `moments_region_2nd` 返回 `Ia, Ib`，**与 `elliptic_axis` 的 `Ra, Rb` 不相等**——`Ia = 2*Ra, Ib = 2*Rb`（直径 vs 半轴）。
- ⚠️ 7 个矩算子**都不抗噪声**——强烈建议先 `median_image` 或 `opening_circle` 降噪。
- ⚠️ `moments_region_3rd` 是**三阶几何矩**（非中心矩），对**位置敏感**——纯理论工具，工业上用 `*_invar` 版本更多。

### ⑤ 行程与厚度（4 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **runlength_distribution** | 行程编码分布（前/背景行/列长度直方图） · `runlength_distribution(Region : : : Foreground, Background)` |
| **runlength_features** | 行程统计特征（行程数、K/L 因子、均值、字节数） · `runlength_features(Regions : : : NumRuns, KFactor, LFactor, MeanLength, Bytes)` |
| **get_region_thickness** | 沿主轴方向厚度直方图 · `get_region_thickness(Region : : : Thickness, Histogramm)` |
| **get_region_index** | 查询某像素位于哪个行程 · `get_region_index(Regions : : Row, Column : Index)` |

**用途**：
- **行程编码**（runlength）是区域存储的底层格式——`runlength_features` 是 **HALCON 区域内存大小的快捷指标**（`Bytes` 直接报 Region 在内存里占多少字节）。
- `get_region_thickness` 是**测厚神器**——返回每个角度上从左边界到右边界的最长距离直方图，**自动找最薄处**（直方图最小值）。
- `get_region_index` 配 `paint_region` 做"标号重映射"——把多连通区域按行程索引重染。

**重点参数**：
- `runlength_distribution` 的 `Foreground, Background` 是**两组直方图**——分别按行（"水平行程"）和按列（"垂直行程"）统计。
- `get_region_thickness` 默认按**主轴方向**测厚度，可通过参数（HALCON 内部自动）调整。

**误区**：
- ⚠️ `runlength_features` 的 `Bytes` 字段是**理论压缩量**（假设 RLE 编码），不是"硬盘占用"——内存中 Region 对象本身有额外开销。
- ⚠️ `get_region_thickness` 是**直方图**，不是单一标量——最薄/最厚要自行 `tuple_min`/`tuple_max`。
- ⚠️ `get_region_index` 的 `Index` **从 0 开始**编号（对应 `runlength_distribution` 输出的索引），不是 1。

### ⑥ 距离与邻域（6 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **hamming_distance** | 两组区域逐像素异或差异 + 相似度 · `hamming_distance(Regions1, Regions2 : : : Distance, Similarity)` |
| **hamming_distance_norm** | 归一化汉明距离（按较长区域归一化） · `hamming_distance_norm(Regions1, Regions2 : : Norm : Distance, Similarity)` |
| **find_neighbors** | 在 MaxDistance 内找最近邻对 · `find_neighbors(Regions1, Regions2 : : MaxDistance : RegionIndex1, RegionIndex2)` |
| **select_region_point** | 筛选包含某像素点的区域 · `select_region_point(Regions : DestRegions : Row, Column :)` |
| **select_region_spatial** | 按空间方向关系筛选 · `select_region_spatial(Regions1, Regions2 : : Direction : RegionIndex1, RegionIndex2)` |
| **spatial_relation** | 区域对在 6 方向上的相对位置（百分数） · `spatial_relation(Regions1, Regions2 : : Percent : RegionIndex1, RegionIndex2, Relation)` |

**用途**：
- **汉明距离**是模板匹配的"粗糙版"——`Distance=0` 表示完全一致；`Distance/Norm` 越接近 0 越相似。常用于：①模板与样本的快速相似度评分；②掩膜精度评估。
- **find_neighbors** 是工业检测的灵魂——比如"找所有间距 < 5mm 的焊点对"，直接用。
- **spatial_relation** 输出 6 维特征（left/right/above/below/inside/overlap），是**关系学习**的特征源。

**重点参数**：
- `hamming_distance_norm` 的 `Norm` ∈ {'1','2','hamming','eulidean'}——`'hamming'` 最常用。
- `select_region_spatial` 的 `Direction` ∈ {'left','right','above','below'}——只能取 4 个基本方向。
- `spatial_relation` 返回 6×N×M 的 `Relation` 元组，每对区域 (i,j) 在 6 方向上各有一个百分数（0~1）= 该方向上像素占比。

**误区**：
- ⚠️ `hamming_distance` 与 `compare_obj`（Ch21）的差别：`compare_obj` 只输出**相等/不等**（严格像素级），`hamming_distance` 输出**差异量**（带相似度），前者布尔、后者标量。
- ⚠️ `find_neighbors` 的 `MaxDistance` 是**欧氏距离**，不是曼哈顿——对斜向最近邻要注意。
- ⚠️ `select_region_point` 是**包含语义**（点 ∈ 区域），不是"中心"语义——若中心包含得用 `area_center` 先算质心。
- ⚠️ `spatial_relation` 内部会先 `connection` 拆分，**不保留多连通原貌**——若需保持多连通，先 `connection` 外面。

### ⑦ 特征选择器（4 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **region_features** | 批量计算多个标量特征 · `region_features(Regions : : Features : Value)` |
| **select_shape** | 按标量特征阈值筛选（带 AND/OR 表达式） · `select_shape(Regions : SelectedRegions : Features, Operation, Min, Max :)` |
| **select_shape_proto** | 按与 Pattern 的相对特征筛选 · `select_shape_proto(Regions, Pattern : SelectedRegions : Feature, Min, Max :)` |
| **select_shape_std** | 按 HALCON 预设的标准形状筛选（最常用） · `select_shape_std(Regions : SelectedRegions : Shape, Percent :)` |

**用途**：
- **select_shape_std** 是 HALCON **最常用的筛选算子**——预设 12+ 个常见形状（'area', 'row', 'column', 'circularity', 'compactness', 'convexity', 'rectangularity', 'ra', 'rb', 'phi', 'anisometry', 'bulkiness'），一参搞定。
- **select_shape** 是"通用版"——支持 50+ 特征，且能写 `'area and (circularity > 0.8)'` 复合表达式。
- **select_shape_proto** 解决"按目标相对关系筛选"——比如"找所有大于模板 1.5 倍的孔"。

**重点参数**：
- `select_shape_std` 的 `Shape` ∈ {'area','row','column','width','height','circularity','compactness','convexity','rectangularity','ra','rb','phi','anisometry','bulkiness'}。
- `select_shape` 的 `Operation` 接受 `'and' / 'or'` 和复合表达式——`Min, Max` 是**元组**（每个特征一对阈值）。
- `region_features` 的 `Features` 是**字符串列表**（如 `'area','row','circularity'`），输出 `Value` 是 1×N 嵌套元组。

**误区**：
- ⚠️ `select_shape_std` 的 `Percent` ∈ [0, 100]——**50 表示"中位数"**（保留 50% 区域），不是 0.5。
- ⚠️ `select_shape` 的 `Min, Max` 是**逐特征对**——`Min = [100, 0.7]`、`Max = [10000, 1.0]` 对应两个特征的上下限。
- ⚠️ `select_shape_proto` 要求 Pattern **必须是单区域**——多区域 Pattern 会触发错误。
- ⚠️ `region_features` 返回**嵌套元组**（每个特征一列），不是 2D 数组——若需矩阵，用 `tuple_concat` 展平或 `gen_tuple_const` 重排。

---

## 3. 关键技术要点

### 3.1 形状因子的"全家福"

| 因子 | 范围 | 1.0 表示 | 主要应用 |
|---|---|---|---|
| `circularity` | 0~∞ | 完美圆 | 圆度筛选 |
| `compactness` | 0~∞ | 圆；0.785 = 正方形 | 整体形状 |
| `roundness` | 0~1 | 圆 | 圆度严格区分 |
| `rectangularity` | 0~1 | 矩形 | 矩形零件 |
| `convexity` | 0~1 | 凸 | 凸包完整性 |
| `eccentricity.Anisometry` | 1~∞ | 圆 | 长宽比 |
| `eccentricity.Bulkiness` | 0~1 | 圆 | 填充密度 |
| `eccentricity.StructureFactor` | 1~∞ | 圆 | 复合 |

### 3.2 不变矩的"指纹"选择

- **7 维 Hu 矩**（业界标准）：`PHI1, PHI2`（二阶） + `I1, I2, I3, I4`（中心矩）—— 拼接成 6~7 维向量喂给 MLP。
- **更高精度**可用 `moments_region_2nd_invar`（3 维）+ `moments_region_3rd_invar`（4 维）= 7 维。
- **对旋转鲁棒**必须用 `*_invar` 版本（不是 `moments_region_2nd`）。

### 3.3 测厚的两种实现

- **直线测厚**（`get_region_thickness`）：沿主轴方向**所有**厚度的直方图——找最薄用 `tuple_min`。
- **局部测厚**（`distance_transform` + `gray_histo`）：每个像素的"到边界的距离"——最薄用 `tuple_min`。
- **选择建议**：机械零件大区域用 `get_region_thickness`；PCB 走线等细长区域用 `distance_transform`。

### 3.4 选择器的"快捷键"

| 算子 | 用法 | 速度 |
|---|---|---|
| `select_shape_std` | 一参选一特征 | 最快 |
| `select_shape` | 多特征组合筛选 | 中等 |
| `region_features` + `select_obj` | 完全自定义 | 慢但最灵活 |

### 3.5 测量"大数组"的性能优化

- 41 个算子中 `area_center`、`smallest_rectangle2`、`elliptic_axis` 对**大区域（>10⁶ 像素）**会慢——HALCON 用 SIMD 优化但仍 O(像素)。
- **多区域批处理**比**单区域循环**快 ~3x——尽量把 Regions 元组一次性喂进。
- 工业上若需 < 5ms/帧，**先 `zoom_image_factor` 降采样 2x** 再算，再用 `zoom_image_factor` 升回。

---

## 4. 流水线定位

```
[分割 Ch20 上]  →  [Regions 上卷：看造算判]  →  【本卷 Features：测得有多准】  →
[匹配 Ch17 上]  /  [分类 Ch20 下]  /  [控制测量 Ch16]
                  ↑                                    ↓
        select_shape 系列是 Ch16 工业检测算子（如 inspect_planar_calib）的"前置筛子"
```

**本卷是 HALCON 视觉流程的"特征工程中心"**——分割之后、匹配之前的必经环节；select_shape 系列批量特征计算是 Ch16 工业检测的算力底座。

---

## 5. 与其它章节的关联

- **Ch20 上 OCR**：`do_ocr_word_svm`（Ch20 下）的输入特征就是本卷的 `moments_region_2nd_invar` 等不变矩。
- **Ch16 Inspection**：`inspect_planar_calib` 等检测算子内部就是 `select_shape + region_features` 流水线。
- **Ch17 上 Matching**：`find_shape_model`（Ch17 上 Shape 族）用本卷 `moments_region_2nd` 的 `Ia, Ib` 算主轴做形状描述子。
- **Ch19 Morphology**：`area_center` 常被 `connection` 拆出的 blob 后调用，是经典的"形态学后处理 + 测量"组合。
- **Ch21 Object**：`count_obj` + `select_obj` + 本卷 `area_center` 是"对象管家的标准动作"。

---

## 6. 7 主题簇算子速查表

| 簇 | 算子（按功能顺序） |
|---|---|
| ① 基础测量 | area_center、area_holes、diameter_region、height_width_ratio、contlength、connect_and_holes、euler_number、orientation_region |
| ② 内接外接 | smallest_circle、smallest_rectangle1、smallest_rectangle2、inner_circle、inner_rectangle1 |
| ③ 形状因子 | circularity、rectangularity、compactness、convexity、roundness、eccentricity、elliptic_axis |
| ④ 矩与不变量 | moments_region_2nd、moments_region_2nd_invar、moments_region_2nd_rel_invar、moments_region_3rd、moments_region_3rd_invar、moments_region_central、moments_region_central_invar |
| ⑤ 行程与厚度 | runlength_distribution、runlength_features、get_region_thickness、get_region_index |
| ⑥ 距离与邻域 | hamming_distance、hamming_distance_norm、find_neighbors、select_region_point、select_region_spatial、spatial_relation |
| ⑦ 特征选择器 | region_features、select_shape、select_shape_proto、select_shape_std |

> **下卷预告**：第 22 章 Regions **下卷** = 几何变换 8 + 仿射变换 21 = 29 个算子。  
> 主题：**「把区域换个姿势」**——`move_region` 平移、`rotate_region` 旋转、`affine_trans_region` 仿射、`gen_region_polygon` 顶点还原、`minkowski_*` 集合运算…… 一句话："**每个区域都是可塑的几何泥**"。
