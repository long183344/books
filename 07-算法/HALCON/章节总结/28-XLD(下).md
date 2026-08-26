# 第 28 章 XLD(下)

## 序言

HALCON 操作员手册第 28 章 **XLD**(eXtended Line Descriptions)的下半段聚焦于 XLD 数据结构上的'变形与重组'——把已有 XLD 改造为更适于下游的几何对象。本卷三子族合计 **34 个算子**。

全章共 **6 个子族 95 个算子**(Access 4 + Creation 12 + Features 45 + Sets 8 + Transformations 20 + Geometric Transformations 6)。上卷交代了 XLD 的'数据模型'(存取/构造/量度),本卷交代 XLD 的'操作方程'(集合运算/局部变换/几何变换)。**Sets** 用布尔代数的四个基本操作(并/交/差/对称差)处理闭合轮廓或多边形所围区域;**Transformations** 处理 XLD 自身的点列形状(平滑/裁剪/分段/重排/合并);**Geometric Transformations** 处理 XLD 与坐标系之间的映射(仿射/极坐标/平行偏移/透视)。

一句话定位:**XLD 上的三大类操作方程——'区域化'(Sets)、'重塑化'(Transformations)、'坐标系变化'(Geometric Transformations)**——任何下游几何任务都依赖这三组工具。

## 1. 全卷结构表

| 子族 | 算子数 | 核心功能 | 典型场景 |
| ---- | ------ | -------- | -------- |
| **Sets(集合运算)** | 8 | XLD 闭合轮廓/多边形所围区域的并/交/差/对称差 | 区域布尔代数、配准后差分检测、目标分割 |
| **Transformations(局部变换)** | 20 | 平滑、裁剪、分段、重排、合并等 XLD 自身点列形状的变形 | edges_image 后处理、road 拼接、blob split/merge |
| **Geometric Transformations(几何变换)** | 6 | XLD 在不同坐标系间的映射(仿射/极坐标/平行/透视) | 姿态归一、圆环展开、PCB 平行尺规、相机校正 |
| **合计(本卷)** | **34** | — | — |

## 2. 子族分述

### 2.1 Sets(8 ops)

Sets 家族是两套对称算子:每种布尔运算(差/交/对称差/并)各有两个版本——`closed_contours_xld` 处理**闭合轮廓**(HXLDCont)所围区域;`closed_polygons_xld` 处理**闭合多边形**(HXLDPoly)所围区域。所有 4 种运算共 8 算子:

- **差集**:`difference_*`(A − B, 左操作数 − 右操作数)
- **交集**:`intersection_*`(A ∩ B)
- **对称差**:`symm_difference_*`((A ∪ B) − (A ∩ B),等价 A ⊕ B)
- **并集**:`union2_*`(A ∪ B, 命名 2 防止与 SetType 的 union tuple 重名)

| 算子 | 一句话功能 | 详细签名 |
| ---- | -------- | -------- |
| `difference_closed_contours_xld` | 计算两个闭合轮廓所围区域的差集(Contours - Sub),返回差集边界轮廓。 | `difference_closed_contours_xld (Contours, Sub : ContoursDifference : : )` |
| `difference_closed_polygons_xld` | 计算两个闭合多边形所围区域的差集,返回差集边界多边形。 | `difference_closed_polygons_xld (Polygons, Sub : PolygonsDifference : : )` |
| `intersection_closed_contours_xld` | 计算两个闭合轮廓所围区域的交集,返回交集边界轮廓。 | `intersection_closed_contours_xld (Contours1, Contours2 : ContoursIntersection : : )` |
| `intersection_closed_polygons_xld` | 计算两个闭合多边形所围区域的交集,返回交集边界多边形。 | `intersection_closed_polygons_xld (Polygons1, Polygons2 : PolygonsIntersection : : )` |
| `symm_difference_closed_contours_xld` | 计算两个闭合轮廓所围区域的对称差(并 - 交),返回边界轮廓。 | `symm_difference_closed_contours_xld (Contours1, Contours2 : ContoursDifference : : )` |
| `symm_difference_closed_polygons_xld` | 计算两个闭合多边形所围区域的对称差,返回边界多边形。 | `symm_difference_closed_polygons_xld (Polygons1, Polygons2 : PolygonsDifference : : )` |
| `union2_closed_contours_xld` | 把两个闭合轮廓所围区域合并成一个轮廓集合(集合并)。 | `union2_closed_contours_xld (Contours1, Contours2 : ContoursUnion : : )` |
| `union2_closed_polygons_xld` | 把两个闭合多边形所围区域合并成一个多边形集合。 | `union2_closed_polygons_xld (Polygons1, Polygons2 : PolygonsUnion : : )` |

**重点算子注**:`union2_closed_contours_xld` 是配准后差分检测中的'容器'——把目标区域和 mask 合并为单一轮廓,后续 set_difference 系列直接做 A−B,得到精确的'目标去掉 mask'部分;与 contour_point_num_xld 联用可量化目标尺寸变化。

### 2.2 Transformations(20 ops)

Transformations 家族按对 XLD 几何改动的'类型'分为 5 个分组:

- **平滑 / 回归 / 加噪**(3 个):`smooth_contours_xld`、`regress_contours_xld`、`add_noise_white_contour_xld`
- **闭合 / 裁剪 / 端点裁剪**(3 个):`close_contours_xld`、`clip_contours_xld`、`clip_end_points_contours_xld`、`crop_contours_xld`(实际 4 个归此处,合并其它子组合)
- **分段 / 拆分 / 排序**(3 个):`segment_contours_xld`、`segment_contour_attrib_xld`、`split_contours_xld`、`sort_contours_xld`
- **合并 / 拼接**(9 个):`merge_cont_line_scan_xld`、`union_adjacent_contours_xld`、`union_cocircular_contours_xld`、`union_cotangential_contours_xld`、`union_collinear_contours_xld`、`union_collinear_contours_ext_xld`、`union_straight_contours_xld`、`combine_roads_xld` + `shape_trans_xld`(形态转换)

| 算子 | 一句话功能 | 详细签名 |
| ---- | -------- | -------- |
| `add_noise_white_contour_xld` | 给 XLD 多边形/轮廓点加白噪声,用于鲁棒性测试或仿真。 | `add_noise_white_contour_xld (Contours : NoisyContours : NumRegrPoints, Amp : )` |
| `clip_contours_xld` | 裁剪 XLD 轮廓/多边形至矩形 ROI(超出部分截掉)。 | `clip_contours_xld (Contours : ClippedContours : Row1, Column1, Row2, Column2 : )` |
| `clip_end_points_contours_xld` | 只裁剪 XLD 轮廓首尾端点(中间不动),用于去除悬线段。 | `clip_end_points_contours_xld (Contours : ClippedContours : Mode, Length : )` |
| `close_contours_xld` | 把开放 XLD 轮廓首尾连接为闭合(用直线段或桥接)。 | `close_contours_xld (Contours : ClosedContours : : )` |
| `combine_roads_xld` | 把道路线段几何合并(典型为车道线/路网图形)为更平滑的统一 XLD。 | `combine_roads_xld (EdgePolygons, ModParallels, ExtParallels, CenterLines : RoadSides : MaxAngleParallel, MaxAngleColinear, MaxDistanceParallel, MaxDistanceColinear : )` |
| `crop_contours_xld` | 按矩形 ROI 坐标裁剪 XLD(只保留 ROI 内部段)。 | `crop_contours_xld (Contours : CroppedContours : Row1, Col1, Row2, Col2, CloseContours : )` |
| `merge_cont_line_scan_xld` | 合并 line scan 数据中相同扫描行之间的相邻 XLD 片段。 | `merge_cont_line_scan_xld (CurrConts, PrevConts : CurrMergedConts, PrevMergedConts : ImageHeight, Margin, MergeBorder, MaxImagesCont : )` |
| `regress_contours_xld` | 对 XLD 点列做高阶多项式回归,得到一条更平滑的拟合曲线。 | `regress_contours_xld (Contours : RegressContours : Mode, Iterations : )` |
| `segment_contour_attrib_xld` | 按 XLD 局部属性(如 'gray' 边缘响应)分段,把断点切开。 | `segment_contour_attrib_xld (Contour : ContourPart : Attribute, Operation, Min, Max : )` |
| `segment_contours_xld` | 通用按位分段(可自定义规则),把 XLD 拆成多个子轮廓。 | `segment_contours_xld (Contours : ContoursSplit : Mode, SmoothCont, MaxLineDist1, MaxLineDist2 : )` |
| `shape_trans_xld` | 把 XLD 轮廓转换为多边形/凸包/圆环等不同表达形式(此函数跨章节通用)。 | `shape_trans_xld (XLD : XLDTrans : Type : )` |
| `smooth_contours_xld` | 对 XLD 点列做高斯/样条平滑,减少噪声引起的锯齿(配 edges_image 的高频边)。 | `smooth_contours_xld (Contours : SmoothedContours : NumRegrPoints : )` |
| `sort_contours_xld` | 按几何特征(长度/方向/列位置)对 XLD 轮廓排序,便于下游有序处理。 | `sort_contours_xld (Contours : SortedContours : SortMode, Order, RowOrCol : )` |
| `split_contours_xld` | 按固定像素步长把 XLD 多边形拆成多段,长边变短边便于匹配。 | `split_contours_xld (Polygons : Contours : Mode, Weight, Smooth : )` |
| `union_adjacent_contours_xld` | 合并空间相邻(端点距离近)的 XLD 轮廓为一条连续轮廓。 | `union_adjacent_contours_xld (Contours : UnionContours : MaxDistAbs, MaxDistRel, Mode : )` |
| `union_cocircular_contours_xld` | 按共圆关系合并 XLD 弧段(从多段断弧拼成完整圆,带共圆判定)。 | `union_cocircular_contours_xld (Contours : UnionContours : MaxArcAngleDiff, MaxArcOverlap, MaxTangentAngle, MaxDist, MaxRadiusDiff, MaxCenterDist, MergeSmallContours, Iterations : )` |
| `union_collinear_contours_ext_xld` | 合并共线 XLD 直线段为一条长线段(扩展模式,允许容差+方向)。 | `union_collinear_contours_ext_xld (Contours : UnionContours : MaxDistAbs, MaxDistRel, MaxShift, MaxAngle, MaxOverlap, MaxRegrError, MaxCosts, WeightDist, WeightShift, WeightAngle, WeightLink, WeightRegr, Mode : )` |
| `union_collinear_contours_xld` | 合并共线 XLD 直线段为一条长线段(标准模式)。 | `union_collinear_contours_xld (Contours : UnionContours : MaxDistAbs, MaxDistRel, MaxShift, MaxAngle, Mode : )` |
| `union_cotangential_contours_xld` | 按切点连续性合并 XLD 弧段(形成 G2 连续平滑弧),适合曲面边缘。 | `union_cotangential_contours_xld (Contours : UnionContours : FitClippingLength, FitLength, MaxTangAngle, MaxDist, MaxDistPerp, MaxOverlap, Mode : )` |
| `union_straight_contours_xld` | 把折线中所有'共线小段'合并为单一长直线(直线 edge extraction 后处理)。 | `union_straight_contours_xld (Contours : UnionContours : MaxDist, MaxDiff, Percent, Mode, Iterations : )` |

**重点算子注**

**`smooth_contours_xld` 详解**

- **参数核心**:Contours (in/out) ∈ HXLDCont; NumRegress 控制邻域点数,典型 5~20,越大越平滑但越粗;ClipLineEndpoints ('auto'/'true'/'false'),'auto' 时自动避开端点; 输出 smoothedContours 与输入等长度的点列。
- **误区警示**:1)NumRegress 不能比轮廓点总数还大,否则抛错;2)对带尖角的多边形(如拐角),过大的 NumRegress 会把尖角圆化;3)ClipLineEndpoints='auto' 在某些 HALCON 版本里默认 false,本节专点 XLD 上需要手动设 'auto' 来保两端长度;4)smooth 后 arc length 一般不变(插值节点保持),但如果同时段分裂(split_contours_xld)再用,顺序重要。
- **场景适用**:光滑前级处理:edges_image(scharr) → smooth_contours_xld → 后续 fit_line/fit_circle,得到的高质量无锯齿输入。配合 split_contours_xld/union 系列前后衔接,可以拉直长边。

**`union_collinear_contours_ext_xld` 详解**

- **参数核心**:Contours (in/out) ∈ HXLDCont; MaxCoLLinDist 最大共线距离(像素),MaxCoLLinDeviation 最大直线偏差(像素); MergeType='auto'/'all','auto' 时只合并共端点的; 注意 IO 合并回原图(不是另存)。
- **误区警示**:1)MaxCoLLinDeviation 给的是像素阈值,对 edges_image(scharr)后的细线给 1.5~3 像素;2)输入 XLD 必须按 line scan 收集的 _parallel_ 直边,不然会把斜线误判为'line' 再合并;3)它不会处理**保留断开**, 输出是合并过的 contour(可能在 IO 中原地替换);4)和 union_collinear_contours_xld 区别是 _ext 支持'共线但不相邻'的多段合并,而标准版只合并共端点的。
- **场景适用**:路网扫描线合并、PCB 长直走线测量、道路边缘拼接的标准后处理。用法:edges_image → split_contours → union_collinear_contours_ext_xld 一次完成'分段直线→最长直线'转换。

### 2.3 Geometric Transformations(6 ops)

Geometric Transformations 家族是'XLD 坐标系映射的最小集',覆盖 3 类标准变换:

- **2D 仿射**:`affine_trans_contour_xld`、`affine_trans_polygon_xld`(同 hom_mat2d, 前者适用 HXLDCont, 后者适用 HXLDPoly)
- **极坐标 ↔ 直角**:`polar_trans_contour_xld`、`polar_trans_contour_xld_inv`(中心作为像素原点,半径/角度作为新坐标;逆变换互为对立)
- **方向偏移**:`gen_parallel_contour_xld`(沿轮廓法向等距偏移,生成平行尺规)
- **透视**:`projective_trans_contour_xld`(hom_mat2d 升级到 3x3, 模拟相机透视 / 倾斜相机校正)

| 算子 | 一句话功能 | 详细签名 |
| ---- | -------- | -------- |
| `affine_trans_contour_xld` | 对 XLD 轮廓施加 2D 仿射变换(旋转+平移+缩放+错切,输入为 HomMat2D)。 | `affine_trans_contour_xld (Contours : ContoursAffineTrans : HomMat2D : )` |
| `affine_trans_polygon_xld` | 对 XLD 多边形施加 2D 仿射变换(同 affine_trans_contour_xld 但多边形版)。 | `affine_trans_polygon_xld (Polygons : PolygonsAffineTrans : HomMat2D : )` |
| `gen_parallel_contour_xld` | 把 XLD 轮廓按法向等距偏移生成 parallel contour(配合变换)。 | `gen_parallel_contour_xld (Contours : ParallelContours : Mode, Distance : )` |
| `polar_trans_contour_xld` | 把 XLD 轮廓从直角坐标变换到极坐标(中心+半径/角度)。 | `polar_trans_contour_xld (Contour : PolarTransContour : Row, Column, AngleStart, AngleEnd, RadiusStart, RadiusEnd, Width, Height : )` |
| `polar_trans_contour_xld_inv` | 极坐标 XLD 反变换回直角坐标(对应 polar_trans_contour_xld 的逆向)。 | `polar_trans_contour_xld_inv (PolarContour : XYTransContour : Row, Column, AngleStart, AngleEnd, RadiusStart, RadiusEnd, WidthIn, HeightIn, Width, Height : )` |
| `projective_trans_contour_xld` | 对 XLD 轮廓施加透视投影变换(HomMat3D 形式),用于相机校正/取景变换。 | `projective_trans_contour_xld (Contours : ContoursProjTrans : HomMat2D : )` |

**重点算子注**

**`gen_parallel_contour_xld` 详解**

- **参数核心**:Parallel (out) ∈ HXLDPolyList; Contour (in) XLD 轮廓; Mode ('gradient' / 'fixed' 必选其一),fixed 需要 Distance 与数值;GenParamName='distance' 控偏移距离;'normalize_direction'='true' 把方向归一到 0~2π。
- **误区警示**:1)Mode='gradient' 必须先对原图做 edges_image,然后 contours 上有灰度属性才能正确偏移;2)Distance=0 时会生成一条与原轮廓重合的平行线,无意义;3)对于自相交轮廓,parallel 可能产生多段接续,需要 union 系列兜底;4)与 gen_parallels_xld(本节上卷)不同,本算子是单条 contour 的方向偏移,而后者是基于灰度的两条平行边缘提取。
- **场景适用**:经典用途:PCB 走线生成'上限'与'下限'两条参考线,再与实际边缘做宽度测量;也用于亚像素尺规的微调零点。

**`affine_trans_contour_xld` 详解**

- **参数核心**:Contours (in/out) ∈ HXLDCont; HomMat2D 是 vector_angle_to_rigid / hom_mat2d_identity / hom_mat2d_scale 等构造的 2D 齐次矩阵; 注意 HaloContour('omit_alignment' 选 'true'/'false')控制是否补偿像素错位。
- **误区警示**:1)HomMat2D 必须用 'ry'/'rx' 形式传入(不是 angle/rad);用 vector_angle_to_rigid(Row, Col, Phi, ...) 里变量名虽叫 Row/Col,但实际对 2D 坐标系(x,y)生效;2)做放大缩小时,fit_line/fit_circle 输出的 Length/Radius 单位不变,而 affine_trans 后端的 contour 几何已缩放,可能与原始像素尺度不一致;3)对多段轮廓,变换保持段序,但 zorder 不变(本算子不重叠合并);4)'omit_alignment'='false' 时会给所有像素加 0.5 偏移(为了 0/1 索引像素对齐)。
- **场景适用**:对 XLD 做姿态归一化(把目标摆正)、坐标到画布的转换(在 templated match 后)、或对参考模板做旋转/平移后入库。是 Ch26 齐次矩阵在 XLD 上的具体应用入口。

## 3. 全卷算子速查表(34 算子)

> 按子族分组;子族内按字母序。下表含一句话中文功能。

### 3.1 Sets(8 ops)

| # | 算子 | 一句话功能 | HDevelop 关键签名 |
| - | ---- | -------- | ---------------- |
| 1 | `difference_closed_contours_xld` | 计算两个闭合轮廓所围区域的差集(Contours - Sub),返回差集边界轮廓。 | `difference_closed_contours_xld (Contours, Sub : ContoursDifference : : )` |
| 2 | `difference_closed_polygons_xld` | 计算两个闭合多边形所围区域的差集,返回差集边界多边形。 | `difference_closed_polygons_xld (Polygons, Sub : PolygonsDifference : : )` |
| 3 | `intersection_closed_contours_xld` | 计算两个闭合轮廓所围区域的交集,返回交集边界轮廓。 | `intersection_closed_contours_xld (Contours1, Contours2 : ContoursIntersection : : )` |
| 4 | `intersection_closed_polygons_xld` | 计算两个闭合多边形所围区域的交集,返回交集边界多边形。 | `intersection_closed_polygons_xld (Polygons1, Polygons2 : PolygonsIntersection : : )` |
| 5 | `symm_difference_closed_contours_xld` | 计算两个闭合轮廓所围区域的对称差(并 - 交),返回边界轮廓。 | `symm_difference_closed_contours_xld (Contours1, Contours2 : ContoursDifference : : )` |
| 6 | `symm_difference_closed_polygons_xld` | 计算两个闭合多边形所围区域的对称差,返回边界多边形。 | `symm_difference_closed_polygons_xld (Polygons1, Polygons2 : PolygonsDifference : : )` |
| 7 | `union2_closed_contours_xld` | 把两个闭合轮廓所围区域合并成一个轮廓集合(集合并)。 | `union2_closed_contours_xld (Contours1, Contours2 : ContoursUnion : : )` |
| 8 | `union2_closed_polygons_xld` | 把两个闭合多边形所围区域合并成一个多边形集合。 | `union2_closed_polygons_xld (Polygons1, Polygons2 : PolygonsUnion : : )` |

### 3.2 Transformations(20 ops)

| # | 算子 | 一句话功能 | HDevelop 关键签名 |
| - | ---- | -------- | ---------------- |
| 1 | `add_noise_white_contour_xld` | 给 XLD 多边形/轮廓点加白噪声,用于鲁棒性测试或仿真。 | `add_noise_white_contour_xld (Contours : NoisyContours : NumRegrPoints, Amp : )` |
| 2 | `clip_contours_xld` | 裁剪 XLD 轮廓/多边形至矩形 ROI(超出部分截掉)。 | `clip_contours_xld (Contours : ClippedContours : Row1, Column1, Row2, Column2 : )` |
| 3 | `clip_end_points_contours_xld` | 只裁剪 XLD 轮廓首尾端点(中间不动),用于去除悬线段。 | `clip_end_points_contours_xld (Contours : ClippedContours : Mode, Length : )` |
| 4 | `close_contours_xld` | 把开放 XLD 轮廓首尾连接为闭合(用直线段或桥接)。 | `close_contours_xld (Contours : ClosedContours : : )` |
| 5 | `combine_roads_xld` | 把道路线段几何合并(典型为车道线/路网图形)为更平滑的统一 XLD。 | `combine_roads_xld (EdgePolygons, ModParallels, ExtParallels, CenterLines : RoadSides : MaxAngleParallel, MaxAngleColinear, MaxDistanceParallel, MaxDistanceColinear : )` |
| 6 | `crop_contours_xld` | 按矩形 ROI 坐标裁剪 XLD(只保留 ROI 内部段)。 | `crop_contours_xld (Contours : CroppedContours : Row1, Col1, Row2, Col2, CloseContours : )` |
| 7 | `merge_cont_line_scan_xld` | 合并 line scan 数据中相同扫描行之间的相邻 XLD 片段。 | `merge_cont_line_scan_xld (CurrConts, PrevConts : CurrMergedConts, PrevMergedConts : ImageHeight, Margin, MergeBorder, MaxImagesCont : )` |
| 8 | `regress_contours_xld` | 对 XLD 点列做高阶多项式回归,得到一条更平滑的拟合曲线。 | `regress_contours_xld (Contours : RegressContours : Mode, Iterations : )` |
| 9 | `segment_contour_attrib_xld` | 按 XLD 局部属性(如 'gray' 边缘响应)分段,把断点切开。 | `segment_contour_attrib_xld (Contour : ContourPart : Attribute, Operation, Min, Max : )` |
| 10 | `segment_contours_xld` | 通用按位分段(可自定义规则),把 XLD 拆成多个子轮廓。 | `segment_contours_xld (Contours : ContoursSplit : Mode, SmoothCont, MaxLineDist1, MaxLineDist2 : )` |
| 11 | `shape_trans_xld` | 把 XLD 轮廓转换为多边形/凸包/圆环等不同表达形式(此函数跨章节通用)。 | `shape_trans_xld (XLD : XLDTrans : Type : )` |
| 12 | `smooth_contours_xld` | 对 XLD 点列做高斯/样条平滑,减少噪声引起的锯齿(配 edges_image 的高频边)。 | `smooth_contours_xld (Contours : SmoothedContours : NumRegrPoints : )` |
| 13 | `sort_contours_xld` | 按几何特征(长度/方向/列位置)对 XLD 轮廓排序,便于下游有序处理。 | `sort_contours_xld (Contours : SortedContours : SortMode, Order, RowOrCol : )` |
| 14 | `split_contours_xld` | 按固定像素步长把 XLD 多边形拆成多段,长边变短边便于匹配。 | `split_contours_xld (Polygons : Contours : Mode, Weight, Smooth : )` |
| 15 | `union_adjacent_contours_xld` | 合并空间相邻(端点距离近)的 XLD 轮廓为一条连续轮廓。 | `union_adjacent_contours_xld (Contours : UnionContours : MaxDistAbs, MaxDistRel, Mode : )` |
| 16 | `union_cocircular_contours_xld` | 按共圆关系合并 XLD 弧段(从多段断弧拼成完整圆,带共圆判定)。 | `union_cocircular_contours_xld (Contours : UnionContours : MaxArcAngleDiff, MaxArcOverlap, MaxTangentAngle, MaxDist, MaxRadiusDiff, MaxCenterDist, MergeSmallContours, Iterations : )` |
| 17 | `union_collinear_contours_ext_xld` | 合并共线 XLD 直线段为一条长线段(扩展模式,允许容差+方向)。 | `union_collinear_contours_ext_xld (Contours : UnionContours : MaxDistAbs, MaxDistRel, MaxShift, MaxAngle, MaxOverlap, MaxRegrError, MaxCosts, WeightDist, WeightShift, WeightAngle, WeightLink, WeightRegr, Mode : )` |
| 18 | `union_collinear_contours_xld` | 合并共线 XLD 直线段为一条长线段(标准模式)。 | `union_collinear_contours_xld (Contours : UnionContours : MaxDistAbs, MaxDistRel, MaxShift, MaxAngle, Mode : )` |
| 19 | `union_cotangential_contours_xld` | 按切点连续性合并 XLD 弧段(形成 G2 连续平滑弧),适合曲面边缘。 | `union_cotangential_contours_xld (Contours : UnionContours : FitClippingLength, FitLength, MaxTangAngle, MaxDist, MaxDistPerp, MaxOverlap, Mode : )` |
| 20 | `union_straight_contours_xld` | 把折线中所有'共线小段'合并为单一长直线(直线 edge extraction 后处理)。 | `union_straight_contours_xld (Contours : UnionContours : MaxDist, MaxDiff, Percent, Mode, Iterations : )` |

### 3.3 Geometric Transformations(6 ops)

| # | 算子 | 一句话功能 | HDevelop 关键签名 |
| - | ---- | -------- | ---------------- |
| 1 | `affine_trans_contour_xld` | 对 XLD 轮廓施加 2D 仿射变换(旋转+平移+缩放+错切,输入为 HomMat2D)。 | `affine_trans_contour_xld (Contours : ContoursAffineTrans : HomMat2D : )` |
| 2 | `affine_trans_polygon_xld` | 对 XLD 多边形施加 2D 仿射变换(同 affine_trans_contour_xld 但多边形版)。 | `affine_trans_polygon_xld (Polygons : PolygonsAffineTrans : HomMat2D : )` |
| 3 | `gen_parallel_contour_xld` | 把 XLD 轮廓按法向等距偏移生成 parallel contour(配合变换)。 | `gen_parallel_contour_xld (Contours : ParallelContours : Mode, Distance : )` |
| 4 | `polar_trans_contour_xld` | 把 XLD 轮廓从直角坐标变换到极坐标(中心+半径/角度)。 | `polar_trans_contour_xld (Contour : PolarTransContour : Row, Column, AngleStart, AngleEnd, RadiusStart, RadiusEnd, Width, Height : )` |
| 5 | `polar_trans_contour_xld_inv` | 极坐标 XLD 反变换回直角坐标(对应 polar_trans_contour_xld 的逆向)。 | `polar_trans_contour_xld_inv (PolarContour : XYTransContour : Row, Column, AngleStart, AngleEnd, RadiusStart, RadiusEnd, WidthIn, HeightIn, Width, Height : )` |
| 6 | `projective_trans_contour_xld` | 对 XLD 轮廓施加透视投影变换(HomMat3D 形式),用于相机校正/取景变换。 | `projective_trans_contour_xld (Contours : ContoursProjTrans : HomMat2D : )` |

## 4. 跨算子误区 & 调试提示

- **Sets 子族必须闭合**:`union2_closed_contours_xld` 等都强调 `closed` —— 输入 XLD 首尾必须重合(test_closed_xld 预检),否则布尔运算不收敛。
- **`difference_*` 是有向的**:`difference_closed_contours_xld(Contours, Sub, ...)` 计算 Contours−Sub,即 Contours 中去掉 Sub 的部分。要做相反方向请调换参数顺序,或用 `symm_difference_*`。
- **Transformations 子族大多是 in-place**:`smooth_contours_xld`、`split_contours_xld`、`union_*` 等许多会覆盖输入 XLD(同名变量重写),不是返回新对象。需要保留原始时先 `copy_obj` 或单独保存元组。
- **`smooth_contours_xld` 不要大 NumRegress**:5~15 通常就够,30+ 会把尖角变圆弧且计算变慢。要保留尖角请调小。
- **`union_collinear_contours_xld` 标准版 vs `_ext` 版**:标准版只合并共端点的,_ext 版合并'共线但不相邻'多段;PCB 长走线测量主要用 _ext。
- **`gen_parallel_contour_xld` 与 `gen_parallels_xld` 不同**:前者是**沿已知轮廓**做几何偏移(Mode='fixed'),后者是**对图像**追踪两条平行边缘(Mode='gradient')。混用导致出图失败。
- **`affine_trans_contour_xld` 的 HomMat2D 输入对齐**:用 `vector_angle_to_rigid(CRow,CCol,Phi, 0,0,0, HomMat)` 时,Row 对应 y 坐标,Col 对应 x 坐标,如果搞反相当于做了转置。
- **`polar_trans_contour_xld` 的中心点**:CenterRow/CenterColumn 必须**在图像外侧**指定一个参考点,通常取轮廓的几何中心;否则极坐标变换会出现退化。
- **`shape_trans_xld` 不是变形算子, 而是**:`shape_trans_xld(Contour, Output, 'convex' / 'circle_outer_circle' / 'rectangle1' / 'polygon' / 'ellipse')` 把 XLD 转为特定表达,不修改形状。

## 5. 调用链路与组合用法(3 段 HDevelop 伪代码)

### 5.1 配准后差分(检测配准误差):`gen_contour_region → union2_closed_contours → difference_closed_contours`

```hdevelop
* 1. 读取参考图像 / 当前图像(略)
read_image(RefImage, 'reference.png')
read_image(TestImage, 'test.png')

* 2. 提取阈值区域
threshold(RefImage, RefReg, 128, 255)
threshold(TestImage, TestReg, 128, 255)

* 3. region -> XLD 闭合轮廓
gen_contour_region_xld(RefReg, RefContour, 'border_holes')
gen_contour_region_xld(TestReg, TestContour, 'border_holes')
close_contours_xld(TestContour, TestClosed)

* 4. 差集(检测增加/减少部分)
difference_closed_contours_xld(TestClosed, RefContour, DiffAdded)
intersection_closed_contours_xld(TestClosed, RefContour, Common)
symm_difference_closed_contours_xld(TestClosed, RefContour, OnlyChanged)
* OnlyChanged 是所有差异的边界
```

### 5.2 PCB 长直走线测量:`edges_image → split_contours → union_collinear_contours_ext → fit_line_contour`

```hdevelop
* 1. 边缘提取
edges_image(Image, ImaAmp, ImaDir, 'canny', 1, 'nms', 20, 40)

* 2. 提取 XLD 轮廓
edges_sub_pix(ImaAmp, Edges, 'sobel', 1, 20, 40)

* 3. 拆段(把长边断成短段,便于合并)
split_contours_xld(Edges, Split, 12, 5)

* 4. 平滑(去除阶梯锯齿)
smooth_contours_xld(Split, Smoothed, 9)

* 5. 合并共线段为最长直线
union_collinear_contours_ext_xld(Smoothed, Merged, 3.0, 1.5, 'auto')

* 6. 直线拟合(出 Length/Phi)
fit_line_contour_xld(Merged, 'regression', -1, 0, 5, 2, _, _, _, _, _, Lengths, Phis)
```

### 5.3 任意方向矩形归一化:`union_adjacent_contours → smallest_rectangle2 → affine_trans_contour`

```hdevelop
* 1. 候选轮廓相邻合并(去除短断)
union_adjacent_contours_xld(AllXLD, Merged, _, 3.0, 8.0)

* 2. 选主轮廓 + 取方向矩形
select_contours_xld(Merged, Tgt, 'contour_length', 60, 99999)
smallest_rectangle2_xld(Tgt, CRow, CCol, Phi, L1, L2)

* 3. 构造反向矩阵摆正
vector_angle_to_rigid(CRow, CCol, Phi, 0, 0, 0, HomMat2D)

* 4. 仿射变换(本卷核心算子)
affine_trans_contour_xld(Tgt, Aligned, HomMat2D)
* Aligned 是一个 0,0 为中心、水平朝上的标准 XLD

* 5. 输出阶段(可选)极坐标变换 —— 圆环展开为直线带
polar_trans_contour_xld(Aligned, Polar, 0, 0, 0, 6.28318, 0, 100)
polar_trans_contour_xld_inv(Polar, Back, 0, 0, 0, 6.28318, 0, 100)
```

## 6. 与其它章节的关联

- **第 12 章 Filtering**:`edges_image` 与 `edges_sub_pix` 是 Transformations 家族的上游;几个 edge 提取算子是 ch12 的子集展到 XLD。
- **第 22 章 Regions**:本卷 `gen_contour_region_xld` 与 `shape_trans_xld` 都是 Region ↔ XLD 双向桥;Sets 家族是 region 布尔代数(`difference` / `intersection` / `union1` / `union2`)在 XLD 上的对偶版。
- **第 25 章 Tools(Geometry)**:region 版本的 `difference` / `intersection` 隶属 ch25(Regions),XLD 版本在本章,但是同义。
- **第 26 章 Transformations(上)**:本卷 `affine_trans_contour_xld` / `projective_trans_contour_xld` 用的 HomMat2D/HomMat3D 都在 ch26 构造;`vector_angle_to_rigid` 是配套的便捷构造器。
- **第 17 章 Matching**:模板匹配通常返回 XLD 轮廓,与 minimum/maximum_rect1/rect2 配对可以用 affine_trans_contour_xld 做姿态归一。
- **第 16 章 Inspection**:差分/对称差算子(本卷 Sets)是工业界'缺陷检测'的便利法——目标区域减去参考区域。

## 7. 一句话核心要义

下卷为 XLD 装配了'三大类操作方程':**Sets** 把 XLD 当作区域做布尔运算,**Transformations** 把 XLD 当作曲线做局部变形,**Geometric Transformations** 把 XLD 在不同坐标系之间映射。三类数学上分别是代数、几何、坐标;在工业场景里则对应'区域识别差异'、'曲线拼接光滑'、'姿态归一'(配准与圆环展开)。
