# 第 22 章 Regions · 下卷：几何变换 + 区域变换（29 算子 · 6 主题簇）

> **HALCON 官方手册第 22 章 Regions** 全部 104 个算子的收官之卷：**Geometric Transformations 8 + Transformations 21 = 29 算子**。  
> 上卷讲完「看 + 造 + 集合论」（35），中卷讲完「测量」（41），**本卷把每个区域"换个姿势"的全部 29 件工具一次给全**。  
> 一句话总结：**每个区域都是可塑的几何泥——8 个算子换坐标系（仿射/射影/极坐标/镜像/平移/转置/缩放），21 个算子改形状（骨架/填孔/去噪/重塑/连通拆分/距离场/裁剪分区）**。

---

## 1. 全卷结构：6 主题簇总览

| 主题簇 | 族 | 算子数 | 一句话功能 | 典型场景 |
|---|---|---|---|---|
| **① 几何变换** | Geo | 8 | 换坐标系：仿射/射影/极坐标/镜像/平移/转置/缩放 | 标定后坐标修正、环形目标展开 |
| **② 骨架中轴** | Trans | 4 | 骨架化 + 交叉点检测 + 线段拆分 | 走线分析、血管/裂纹网络 |
| **③ 区域修复** | Trans | 4 | 填孔、按形状填孔、删短行程、去噪 | 掩膜修补、毛刺清理 |
| **④ 区域重塑** | Trans | 4 | 凸包/内圆/外接形状转换、区域扩张、排名滤波 | 形状归一化、边界平滑 |
| **⑤ 距离分割** | Trans | 3 | 连通分量拆分 + 距离场 + 最近点场 | Blob 分析、细线测量、骨架前置 |
| **⑥ 裁剪与拆分** | Trans | 6 | 矩形裁剪、特征排序、线扫描合并、动态/矩形分区 | ROI 裁剪、超大区域切页 |

**两族的本质分工**：**Geometric（8）= 刚体/非刚体坐标重映射，形状不变、位置变**；**Transformations（21）= 形状重塑，拓扑结构可能改变**（连通数、孔数、行程都会变）。

---

## 2. 6 主题簇分述（详细模式）

> 算子格式：**算子名 | 一句话功能 · HDevelop 关键签名**。  
> 每个算子附"**用途 / 重点参数 / 误区**"三段注。

### ① 几何变换（Geometric Transformations，8 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **affine_trans_region** | 仿射变换（平移+旋转+缩放+剪切+镜像，一次搞定） · `affine_trans_region(Region : RegionAffineTrans : HomMat2D, Interpolate :)` |
| **projective_trans_region** | 射影变换（3D 平面投影到 2D） · `projective_trans_region(Regions : TransRegions : HomMat2D, Interpolation :)` |
| **polar_trans_region** | 极坐标展开（环形→矩形条带） · `polar_trans_region(Region : PolarTransRegion : Row, Column, AngleStart, AngleEnd, RadiusStart, RadiusEnd, Width, Height, Interpolation :)` |
| **polar_trans_region_inv** | 极坐标逆变换（矩形条带→环形） · `polar_trans_region_inv(PolarRegion : XYTransRegion : Row, Column, AngleStart, AngleEnd, RadiusStart, RadiusEnd, WidthIn, HeightIn, Width, Height, Interpolation :)` |
| **mirror_region** | 镜像翻转 · `mirror_region(Region : RegionMirror : Mode, WidthHeight :)` |
| **move_region** | 平移（整数像素） · `move_region(Region : RegionMoved : Row, Column :)` |
| **transpose_region** | 转置（行列互换，主对角线镜像） · `transpose_region(Region : Transposed : Row, Column :)` |
| **zoom_region** | 缩放（ScaleWidth/ScaleHeight 独立） · `zoom_region(Region : RegionZoom : ScaleWidth, ScaleHeight :)` |

**用途**：
- **affine_trans_region 是几何变换的"瑞士军刀"**——`hom_mat2d_identity` → `hom_mat2d_translate/rotate/scale` → `affine_trans_region` 三步组合，覆盖 move/mirror/zoom 的全部能力（但专用算子更快）。
- **polar_trans_region 是环形检测神器**——瓶盖密封圈、圆形码盘、轮胎字符等环形目标，展开成矩形后即可用常规 `find_text`/模板匹配。
- **projective_trans_region** 用于相机倾斜拍摄的场景——标定后用 `HomMat2D` 把梯形畸变拉回矩形。

**重点参数**：
- `affine_trans_region` 的 `Interpolate` ∈ {'nearest_neighbor', 'bilinear'}——区域默认整数像素，bilinear 无意义（区域无灰度），**永远传 'nearest_neighbor'**。
- `mirror_region` 的 `Mode` ∈ {'row','column','diagonal'}——'row' 是上下翻（沿水平轴），'column' 是左右翻（沿垂直轴）。
- `zoom_region` 的 `Scale` < 1 会**丢像素**（亚采样），区域可能碎裂——配合 `union1` 或 `connection` 使用。

**误区**：
- ⚠️ `move_region` 只接受**整数** Row/Column——亚像素平移请用 `affine_trans_region`（但它输出也是整数像素，真正的亚像素在 XLD/图像层）。
- ⚠️ 极坐标变换 `AngleStart/AngleEnd` 用**弧度**，且扫描方向是**逆时针**（数学约定），与图像 Row 向下的坐标系方向相反。
- ⚠️ `zoom_region` 缩放以**图像原点 (0,0)** 为锚点，不是区域中心——若要围绕中心缩放，需先 `move_region` 移到原点、缩放、再移回。
- ⚠️ 8 个几何算子输出的都是**整数像素区域**（HALCON Region 本质是像素集合，无亚像素）——要亚像素精度请转 XLD（`gen_contour_region_xld`）再 `affine_trans_contour_xld`。

### ② 骨架中轴（Transformations，4 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **skeleton** | 骨架化（细化到单像素中轴线） · `skeleton(Region : Skeleton : : )` |
| **junctions_skeleton** | 找骨架的端点 + 交叉点 · `junctions_skeleton(Region : EndPoints, JuncPoints : : )` |
| **split_skeleton_lines** | 按交叉点把骨架拆成独立线段（返回端点坐标） · `split_skeleton_lines(SkeletonRegion : : MaxDistance : BeginRow, BeginCol, EndRow, EndCol)` |
| **split_skeleton_region** | 按交叉点把骨架拆成独立线段（返回区域） · `split_skeleton_region(SkeletonRegion : RegionLines : MaxDistance :)` |

**用途**：
- **skeleton 是"线网络分析"的第一步**——印刷电路走线、血管网络、裂纹网络、道路提取，全靠骨架化把"面条状区域"压缩成单像素线。
- **junctions_skeleton** 一次输出**两类特征点**：`EndPoints`（线头，度为 1）+ `JuncPoints`（交叉，度 ≥ 3）——拓扑分析的基础。
- **split_skeleton_*** 是"分而治之"——把网络拆成独立线段后，每段可单独测长（`contlength`）、测向（`orientation_region`）。

**重点参数**：
- `split_skeleton_lines` 的 `MaxDistance` 是**短段合并阈值**——短于此的碎段会被并入邻段（防噪声）。
- `split_skeleton_lines` 返回**坐标元组**（无区域），`split_skeleton_region` 返回**区域元组**——前者适合直接喂 `gen_region_line` 重建，后者适合后续 `select_shape`。

**误区**：
- ⚠️ `skeleton` 的输出**可能不是严格 8 连通单像素线**——交叉点处可能有 2 像素宽，需 `junctions_skeleton` 或形态学 `thin` 再处理。
- ⚠️ **骨架对边界噪声极度敏感**——一个毛刺就是一个新端点 + 新分支！工业上骨架化前必须 `opening_circle` / `remove_noise_region` 预处理。
- ⚠️ `split_skeleton_*` 要求输入**必须是 skeleton 输出**（或手造的细线区域）——粗区域直接喂会得到未定义行为。

### ③ 区域修复（Transformations，4 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **fill_up** | 填满所有孔洞 · `fill_up(Region : RegionFillUp : : )` |
| **fill_up_shape** | 只填满足形状条件的孔 · `fill_up_shape(Region : RegionFillUp : Feature, Min, Max :)` |
| **eliminate_runs** | 删除过短/过长行程 · `eliminate_runs(Region : RegionClipped : ElimShorter, ElimLonger :)` |
| **remove_noise_region** | 去噪（按连通分量大小/形状） · `remove_noise_region(InputRegion : OutputRegion : Type :)` |

**用途**：
- **fill_up 是 OCR/字符识别的预处理必做**——字符 'o'/'e'/'a' 中心的孔若不填，会误判为多连通，干扰 `connection` 和特征计算。
- **fill_up_shape** 是"选择性填孔"——比如"只填面积 < 100 的噪声孔，保留中央大孔"：`fill_up_shape(Region, Filled, 'area', 1, 100)`。
- **eliminate_runs** 直接在**行程编码层**操作（比形态学更快）——去水平方向毛刺。
- **remove_noise_region** 按 `Type` 一参去噪，比 `connection + select_shape` 两步快。

**重点参数**：
- `fill_up_shape` 的 `Feature` 与 `select_shape` 一致（'area', 'width', 'height', 'circularity' 等）——**判断的是"孔的特征"**，不是整个区域。
- `remove_noise_region` 的 `Type` ∈ {'small_dilation', 'small_erosion', 'big_dilation', 'big_erosion'}——`small_*` 删小噪声，`big_*` 删大块。

**误区**：
- ⚠️ `fill_up` **会填掉所有孔**——若目标是"环形零件中间的孔要保留"，千万别用 fill_up（用 `fill_up_shape` 或形态学 `closing`）。
- ⚠️ `eliminate_runs` 的阈值 `ElimShorter/ElimLonger` 是**像素数**（1 表示删所有 1 像素行程）——设 0 表示"不删"。
- ⚠️ `remove_noise_region` 的 `small_dilation` 模式**可能把目标边界也吃掉 1 像素**——精度敏感场景慎用。

### ④ 区域重塑（Transformations，4 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **shape_trans** | 形状变换（凸包/内圆/外接圆/内矩形/外接矩形） · `shape_trans(Region : RegionTrans : Type :)` |
| **expand_region** | 区域扩张（避开禁区） · `expand_region(Regions, ForbiddenArea : RegionExpanded : Iterations, Mode :)` |
| **rank_region** | 排名滤波（矩形窗口内计数阈值化） · `rank_region(Region : RegionCount : Width, Height, Number :)` |
| **background_seg** | 背景分割（前景取补 + 连通拆分） · `background_seg(Foreground : BackgroundRegions : : )` |

**用途**：
- **shape_trans 是形状归一化的"6 选 1"**——`Type` ∈ {'convex'（凸包）, 'ellipse'（等效椭圆）, 'outer_circle'（最小外接圆）, 'inner_circle'（最大内接圆）, 'rectangle1'（外接轴对齐矩形）, 'rectangle2'（外接旋转矩形）}。匹配前把目标统一转凸包，抗形变能力暴涨。
- **expand_region** 是"带障碍物的膨胀"——比如道路网扩张但避开湖泊禁区；比 `dilation1` 多了 ForbiddenArea 约束。
- **rank_region** 等价于图像形态学 `rank_image` 的区域版——窗口内前景像素数 ≥ Number 才保留（同时抗噪 + 保边界）。
- **background_seg** 一次拿到"每个封闭背景区域"——瓶内液面检测、腔体分割。

**重点参数**：
- `expand_region` 的 `Mode` ∈ {'image'（限制在图像域内）, 'region'（限制在原区域内）} + `Iterations`（-1 表示无限迭代直到收敛）。
- `rank_region` 的 `Number` 阈值——窗口 `Width×Height` 内前景数 ≥ Number 才输出；`Number = W*H` 等价 erosion，`Number = 1` 等价 dilation。

**误区**：
- ⚠️ `shape_trans` 的 6 种 `Type` 输出**都还是区域**（像素集合），不是 XLD 轮廓——要轮廓用 `gen_contour_region_xld`。
- ⚠️ `background_seg` 的输入是**前景**，输出是**背景的连通分量**——`complement + connection` 的快捷方式，但**不含被前景完全包围的孔**（孔需 `connection` 于 `difference`）。
- ⚠️ `expand_region` `Iterations = -1` 在无 ForbiddenArea 时**可能 OOM**（一直膨胀到图像边界）。

### ⑤ 距离分割（Transformations，3 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **connection** | 按连通性拆分为独立区域分量 · `connection(Region : ConnectedRegions : : )` |
| **distance_transform** | 距离变换（每像素到区域边界的距离场） · `distance_transform(Region : DistanceImage : Metric, Foreground, Width, Height :)` |
| **closest_point_transform** | 最近点变换（每像素到边界的最近点坐标 + 距离） · `closest_point_transform(Region : Distances, ClosestPoints : Metric, Foreground, ClosestPointMetric :)` |

**用途**：
- **connection 是 HALCON 使用频率 Top3 算子**——分割后必做，把多连通区域拆成单连通元组，后续 `select_shape`/`area_center` 才能逐个处理。
- **distance_transform** 输出**图像**（不是区域！）——是测厚（`tuple_max`）、骨架（配合 `skeleton`）、分水岭（`watersheds`）的底层引擎。
- **closest_point_transform** 是"最近邻导航"——每个像素都知道自己最近的边界点在哪，用于路径规划、边界投影。

**重点参数**：
- `connection` 无控制参数，**默认 8 连通**——要 4 连通得用 `connection` 前先形态学处理（或 HALCON 内部设置）。
- `distance_transform` 的 `Metric` ∈ {'city-block'（L1，快）, 'chessboard'（L∞，快）, 'octagonal'（L1/L∞ 混合，准）, 'euclidean'（L2，最准最慢）}；`Foreground` ∈ {'true'（算区域内部到边界）, 'false'（算区域外部到边界）}。
- `closest_point_transform` 的 `ClosestPointMetric` 与 `Metric` 独立——距离度量用 L2、最近点匹配用 L1 也行。

**误区**：
- ⚠️ `distance_transform` 输出的是 **real 图像**，且**值与像素距离成 1:1**（欧氏度量下）——不是归一化 0~1，直方图分析前别忘 `scale_image`。
- ⚠️ `connection` 的输出顺序**与行程扫描顺序相关**（大致从上到下）——需要确定顺序请接 `sort_region`。
- ⚠️ **connection 内存陷阱**：极大噪声图像 connection 可能产生 10⁵+ 个分量——先 `remove_noise_region` 或 `select_shape_std` 预筛。

### ⑥ 裁剪与拆分（Transformations，6 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **clip_region** | 按绝对矩形裁剪 · `clip_region(Region : RegionClipped : Row1, Column1, Row2, Column2 :)` |
| **clip_region_rel** | 按四边相对量裁剪 · `clip_region_rel(Region : RegionClipped : Top, Bottom, Left, Right :)` |
| **sort_region** | 按特征排序（首/末/列/行） · `sort_region(Regions : SortedRegions : SortMode, Order, RowOrCol :)` |
| **merge_regions_line_scan** | 线扫描图像的多帧区域合并 · `merge_regions_line_scan(CurrRegions, PrevRegions : CurrMergedRegions, PrevMergedRegions : : )` |
| **partition_dynamic** | 按距离动态分区（近似等宽切块） · `partition_dynamic(Region : Partitioned : Distance, Percent :)` |
| **partition_rectangle** | 按固定矩形网格分区 · `partition_rectangle(Region : Partitioned : Width, Height :)` |

**用途**：
- **clip_region** 是"硬裁"——把区域裁剪到 ROI 矩形内，图像域之外的垃圾像素一键清除。
- **clip_region_rel** 是"软裁"——四边各缩进 N 像素，去除边界伪影（镜头暗角、拼接缝）。
- **sort_region** 是流水线的"排队员"——OCR 从左到右读字符前必须 `sort_region(..., 'first_point', 'true', 'column')`。
- **partition_*** 是"切块机"——超大区域切页处理；`partition_dynamic` 按**区域内容**自适应切块（等宽近似），`partition_rectangle` 按**固定网格**切。

**重点参数**：
- `sort_region` 的 `SortMode` ∈ {'character'（字符阅读顺序）, 'first_point'（首个像素点）, 'last_point'（末像素点）, 'upper_left'（左上角）, 'lower_right'（右下角）}；`Order` ∈ {'true'（升序）, 'false'（降序）}；`RowOrCol` ∈ {'row', 'column'}。
- `partition_dynamic` 的 `Percent` 是重叠率——0 表示无重叠，10 表示相邻块重叠 10%（防边界截断目标）。
- `merge_regions_line_scan` 专用于**线扫描相机**——相邻帧的区域按时间一致性合并，处理"同一物体跨帧"。

**误区**：
- ⚠️ `clip_region` 与 `intersection` + `gen_rectangle1` 等价但**更快**（内联优化）——能用 clip_region 就别组合。
- ⚠️ `sort_region` 的 `'character'` 模式按"字符阅读方向"排序（从上到下、从左到右），**仅适合 OCR 场景**——通用排序用 'first_point'。
- ⚠️ `partition_dynamic` 的 `Distance` 是**目标块宽**，但实际块宽受区域形状影响（±Percent% 浮动）——精确等宽请用 `partition_rectangle`。

---

## 3. 关键技术要点

### 3.1 几何变换的"层次"选择

| 需求 | 用什么 | 精度 |
|---|---|---|
| 整数平移 | `move_region` | 像素 |
| 任意刚体+缩放 | `affine_trans_region` | 像素 |
| 倾斜拍摄修正 | `projective_trans_region` | 像素 |
| 环形展开 | `polar_trans_region` | 像素 |
| **亚像素变换** | 转 XLD：`gen_contour_region_xld` + `affine_trans_contour_xld` | 亚像素 |

**核心事实**：HALCON Region 是**整数像素集合**，所有几何变换输出都无亚像素——要亚像素精度必须升维到 XLD 或 Image。

### 3.2 仿射矩阵的"三步组合拳"

```
hom_mat2d_identity(::HomMat2D)                      → 单位阵
hom_mat2d_translate(::HomMat2D, Tx, Ty : HomMat2DTranslate)  → 平移
hom_mat2d_rotate(::HomMat2D, Phi, Px, Py : HomMat2DRotate)   → 绕 (Px,Py) 旋转
hom_mat2d_scale(::HomMat2D, Sx, Sy, Px, Py : HomMat2DScale)  → 绕 (Px,Py) 缩放
affine_trans_region(Region : R2 : HomMat2D, 'nearest_neighbor')
```

**注意**：矩阵乘法**不满足交换律**——先 rotate 再 translate 与先 translate 再 rotate 结果不同！HALCON 的 `hom_mat2d_*` 是**右乘**（新变换在局部坐标系执行）。

### 3.3 极坐标变换的"环形展开"套路

```
* 1. 找圆心（用中卷的 smallest_circle / area_center）
area_center(Ring, Row, Column, ...)
* 2. 极坐标展开成矩形条带
polar_trans_region(Ring, PolarRegion, Row, Column, 0, rad(360), R_in, R_out, W, H, 'nearest_neighbor')
* 3. 条带上做常规处理（OCR / 模板匹配 / 1D 测量）
* 4. 需要时逆变换回环形
polar_trans_region_inv(PolarRegion, BackRegion, ...)
```

**应用**：瓶盖字符、密封圈缺陷、圆形码盘、轮胎侧壁——全部"圆变方"后一马平川。

### 3.4 connection 的性能优化

| 场景 | 优化 |
|---|---|
| 噪声多（>10⁴ 分量） | 先 `remove_noise_region` 再 connection |
| 只关心大目标 | connection 后 `select_shape_std(..., 'area', 50)` |
| 只需连通数 | 用中卷 `connect_and_holes`（不拆分，更快） |
| 超大图像 | 先 `clip_region` 到 ROI 再 connection |

### 3.5 骨架化标准预处理流水线

```
原始区域 → opening_circle(去毛刺) → fill_up(填噪孔) → skeleton(骨架)
        → junctions_skeleton(交叉点) → split_skeleton_region(拆线段)
        → 每段 contlength 测长 / orientation_region 测向
```

**跳过 opening + fill_up 直接骨架 = 端点爆炸**（每个噪声毛刺都是一个新分支）。

### 3.6 distance_transform 的 Foreground 语义

| Foreground | 算的是 |
|---|---|
| `'true'` | **区域内部**每像素到边界的距离（骨架/测厚用） |
| `'false'` | **区域外部**每像素到边界的距离（分水岭/缓冲区用） |

输出是 **real 图像**，值 = 距离（非归一化）——`threshold` 距离 > d 的像素即可得"内缩 d 的核心区"（比 erosion 快且连续）。

---

## 4. 流水线定位

```
[分割 Ch20 上] → [上卷:看造算判] → [中卷:Features 测量] → 【本卷:几何与形状变换】
                                                            ↓
                        [匹配 Ch17 上]  ← 标定后 affine_trans_region 修正模板位姿
                        [OCR Ch20 上]   ← sort_region 'character' 排队 + fill_up 填字符孔
                        [形态学 Ch19]   ← skeleton/rank_region 与 Ch19 的 SE 数学互补
```

**本卷是 Regions 章的收官**——把"静态"的区域变成"可搬、可变、可拆"的动态对象，是匹配、OCR、测量三大下游的几何预处理中心。

---

## 5. 与其它章节的关联

- **Ch17 上 Matching**：`find_shape_model` 内部用 `affine_trans_region` 做位姿假设；`projective_trans_region` 是透视匹配的预处理。
- **Ch20 上 OCR**：`sort_region('character')` + `fill_up` 是字符区域预处理的黄金组合。
- **Ch19 Morphology**：`rank_region` ≈ 区域版 rank 滤波；`expand_region` 是带约束的 dilation；`skeleton` 与 Ch19 `thin/thick` 互补（thin 是 SE 迭代，skeleton 是中轴变换）。
- **Ch18 Matrix**：`affine_trans_region` 的 `HomMat2D` 由 Ch18 矩阵运算构造（`hom_mat2d_*` 系列本质是 2×3 仿射矩阵）。
- **Ch16 Inspection**：`partition_rectangle` 切块 + 逐块 `connection` 是超大图像检测的标准加速套路。
- **中卷 Features**：`distance_transform` + `gray_histo` 是"最薄处测量"的第二种实现（中卷 3.3 节）。

---

## 6. 6 主题簇算子速查表

| 簇 | 算子（按功能顺序） |
|---|---|
| ① 几何变换 | affine_trans_region、projective_trans_region、polar_trans_region、polar_trans_region_inv、mirror_region、move_region、transpose_region、zoom_region |
| ② 骨架中轴 | skeleton、junctions_skeleton、split_skeleton_lines、split_skeleton_region |
| ③ 区域修复 | fill_up、fill_up_shape、eliminate_runs、remove_noise_region |
| ④ 区域重塑 | shape_trans、expand_region、rank_region、background_seg |
| ⑤ 距离分割 | connection、distance_transform、closest_point_transform |
| ⑥ 裁剪与拆分 | clip_region、clip_region_rel、sort_region、merge_regions_line_scan、partition_dynamic、partition_rectangle |

> **第 22 章 Regions 全章收官**：上卷 35 + 中卷 41 + 下卷 29 = **104 算子**，HALCON 二值区域处理的完整体系（看造算判 → 测量 → 变换）一次讲完。  
> **下一章预告**：第 23 章 Segmentation（阈值分割/边缘检测/分水岭等），Regions 的"上游水源"。
