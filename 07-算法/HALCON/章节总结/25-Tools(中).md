# 第 25 章 Tools · 中卷：几何度量与空间求解（42 算子 · 5 主题）

> HALCON '几何度量与空间求解' 全套 — 距离变换 / 测距 / 角度 / 求交 / 面积测量 5 大主题。从 '点-点距离' 到 '2D 多边形碰撞面积',从 '欧氏距离场' 到 'XLD 等距线' —— 这是机器视觉中'几何决策'的算子库,广泛应用于: 零件位姿匹配、夹具避让、路径规划、缺陷定位、OCR 字符间距、机器人抓取点投影等。

---

## 1. 全卷结构：5 主题总览

| 主题 | 算子数 | 一句话功能 | 典型场景 |
|---|---|---|---|
| **① Distance Transform** | 10 | XLD 距离场创建/应用/等距线提取 | 工件公差带、形状偏移、避让路径 |
| **② Distance 测距** | 17 | 点/线/区域/XLD 之间的距离（17 种组合） | 测距、碰撞检测、位姿匹配 |
| **③ Angle / Projection** | 4 | 夹角/方向角/椭圆采样 | 旋转对齐、方向判定、椭圆特征 |
| **④ Intersection 求交** | 10 | 直线/线段/圆/XLD 两两求交 | 交点检测、几何反推、夹具碰撞 |
| **⑤ Area Measure** | 1 | 两旋转矩形相交面积 | IOU 重叠度、零件干涉判定 |

**与上卷的分工**：
- **上卷** = HALCON 的'数学小工具'（背景估计 7 + 1D 函数 25 = 32 算子）
- **中卷（本卷）** = HALCON 的'几何度量与空间求解'（42 算子）—— 距离变换 + 测距 + 角度 + 求交 + 面积
- **下卷**（待做） = Grid Rectification 5 + Hough 7 + Interpolation 5 + Lines 2 + Mosaicking 10 = 29 算子

---

## 2. 5 主题分述（详细模式）

### ① Distance Transform (距离变换，10 算子)

**核心思想**：以 XLD 轮廓为'参考点',生成一个标量场,场内每点的值 = 该点到参考轮廓的最短欧氏距离。
**典型用途**：
- **公差带可视化** —— 距离场可视化,看工件边缘±0.5mm 的'安全带'
- **形状偏移** —— create 后 apply 到另一轮廓,得到等距收缩/膨胀
- **路径规划** —— 用 get_contour 取 Level=X 的等距线作为避让路径

**算法族**：
- `create_/apply_/get_contour_/set_param_/get_param` —— 距离场核心 5 步
- `serialize_/deserialize_/read_/write_/clear` —— 距离场持久化 5 步

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **apply_distance_transform_xld** | 把距离变换结果应用到 XLD 轮廓 → 离散等距线 · `apply_distance_transform_xld( Contour : ContourOut : DistanceTransformID : )` |
| **clear_distance_transform_xld** | 清除距离变换模型（释放句柄 + 内存） · `clear_distance_transform_xld( : : DistanceTransformID : )` |
| **create_distance_transform_xld** | 创建 XLD 距离变换模型（Mode 3 选 1） · `create_distance_transform_xld( Contour : : Mode , MaxDistance : DistanceTransformID )` |
| **get_distance_transform_xld_contour** | 提取等距线轮廓（指定 Level 偏移量） · `get_distance_transform_xld_contour( : Contour : DistanceTransformID : )` |
| **get_distance_transform_xld_param** | 查询距离变换参数（Mode/MaxDistance 等） · `get_distance_transform_xld_param( : : DistanceTransformID , GenParamName : GenParamValue )` |
| **read_distance_transform_xld** | 从 .dtxd 文件读取距离变换 · `read_distance_transform_xld( : : FileName : DistanceTransformID )` |
| **serialize_distance_transform_xld** | 序列化为二进制流（用于传输/存储） · `serialize_distance_transform_xld( : : DistanceTransformID : SerializedItemHandle )` |
| **set_distance_transform_xld_param** | 热更新参数（重建前可改 Mode） · `set_distance_transform_xld_param( : : DistanceTransformID , GenParamName , GenParamValue : )` |
| **write_distance_transform_xld** | 写入 .dtxd 文件 · `write_distance_transform_xld( : : DistanceTransformID , FileName : )` |
| **deserialize_distance_transform_xld** | 反序列化距离变换（来自二进制流） · `deserialize_distance_transform_xld( : : SerializedItemHandle : DistanceTransformID )` |

#### ★ apply_distance_transform_xld — 把距离变换结果应用到 XLD 轮廓 → 离散等距线
- **用途**：距离场的应用阶段 —— 把 DistanceTransform 应用到目标 XLD 上,得到一组等距偏移线。
- **参数**：Levels: 偏移距离列表（正负值都支持,负值=向内偏移）
- **误区**：必须在 create + set_param 之后调用,且同一 DistanceTransform 可重复 apply 不同 XLD

#### ★ create_distance_transform_xld — 创建 XLD 距离变换模型（Mode 3 选 1）
- **用途**：HALCON 的'欧氏距离场'生成器 —— 把 XLD 轮廓作为参考,生成一个标量场,每个点的值是它到参考轮廓的最短欧氏距离。
- **参数**：Mode 选 'point_to_point'（点到点） / 'point_to_segment'（点到线段） / 'fast_point_to_segment'（加速版）
- **误区**：不是 Region 距离变换！要算 Region 的距离变换需用 Ch18 的 distance_transform 算子族

#### ★ get_distance_transform_xld_contour — 提取等距线轮廓（指定 Level 偏移量）
- **用途**：提取等距线 —— 把标量距离场可视化为轮廓(等高线),返回 XLD。
- **参数**：Level: 偏移量(标量或列表),返回的 XLD 即为该 Level 对应的等距线


---

### ② Distance 测距 (点/线/区域，17 算子)

**算子命名规则**：
- 第 1 字符: 第一个被测对象(p=point, l=line, s=segment, r=region, c=XLD contour)
- 第 2 字符: 第二个被测对象(同上)
- 后缀 `_min`: 返回最小距离(单值最快); `_min_points`: 同时返回最近点对坐标

**典型用途**：
- **零件匹配** —— 测目标轮廓到模板轮廓的最小距离,作为匹配分数
- **碰撞检测** —— distance_ss(线段-线段) / distance_rr_min(区域-区域)
- **避让路径** —— distance_pr(点到区域边界) 实时判断路径点是否安全

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **distance_pp** | 两点间欧氏距离（最常用） · `distance_pp( : : Row1 , Column1 , Row2 , Column2 : Distance )` |
| **distance_pl** | 点到直线距离 · `distance_pl( : : Row , Column , Row1 , Column1 , Row2 , Column2 : Distance )` |
| **distance_pr** | 点到区域边界距离（Region 点云 → 区域外距） · `distance_pr( Region : : Row , Column : DistanceMin , DistanceMax )` |
| **distance_ps** | 点到线段距离（区别于 distance_pl: 端点截断） · `distance_ps( : : Row , Column , Row1 , Column1 , Row2 , Column2 : DistanceMin , DistanceMax )` |
| **distance_lr** | 直线到区域距离 · `distance_lr( Region : : Row1 , Column1 , Row2 , Column2 : DistanceMin , DistanceMax )` |
| **distance_pc** | 点到 XLD 轮廓距离 · `distance_pc( Contour : : Row , Column : DistanceMin , DistanceMax )` |
| **distance_lc** | 直线到 XLD 轮廓距离 · `distance_lc( Contour : : Row1 , Column1 , Row2 , Column2 : DistanceMin , DistanceMax )` |
| **distance_cc** | 两个 XLD 轮廓最小距离 · `distance_cc( Contour1 , Contour2 : : Mode : DistanceMin , DistanceMax )` |
| **distance_cc_min** | 两轮廓最小距离点对（单值最快） · `distance_cc_min( Contour1 , Contour2 : : Mode : DistanceMin )` |
| **distance_cc_min_points** | 两轮廓最小距离点对（含两端坐标） · `distance_cc_min_points( Contour1 , Contour2 : : Mode : DistanceMin , Row1 , Column1 , Row2 , Column2 )` |
| **distance_contours_xld** | 通用轮廓-轮廓距离函数（输入是 xld 数组） · `distance_contours_xld( ContourFrom , ContourTo : ContourOut : Mode : )` |
| **distance_sc** | 线段到 XLD 轮廓距离 · `distance_sc( Contour : : Row1 , Column1 , Row2 , Column2 : DistanceMin , DistanceMax )` |
| **distance_sl** | 线段到直线距离 · `distance_sl( : : RowA1 , ColumnA1 , RowA2 , ColumnA2 , RowB1 , ColumnB1 , RowB2 , ColumnB2 : DistanceMin , DistanceMax )` |
| **distance_sr** | 线段到区域距离 · `distance_sr( Region : : Row1 , Column1 , Row2 , Column2 : DistanceMin , DistanceMax )` |
| **distance_ss** | 两线段最小距离（工业零件碰撞检测） · `distance_ss( : : RowA1 , ColumnA1 , RowA2 , ColumnA2 , RowB1 , ColumnB1 , RowB2 , ColumnB2 : DistanceMin , DistanceMax )` |
| **distance_rr_min** | 两区域最小距离（Region 边界最近点距离） · `distance_rr_min( Regions1 , Regions2 : : : MinDistance , Row1 , Column1 , Row2 , Column2 )` |
| **distance_rr_min_dil** | 两区域最小距离（先膨胀，融合细缝） · `distance_rr_min_dil( Regions1 , Regions2 : : : MinDistance )` |

#### ★ distance_pp — 两点间欧氏距离（最常用）
- **用途**：几何最基础算子 —— 两 2D 点的欧氏距离。
- **参数**：输入支持批量：Row1/Column1/Row2/Column2 都是 tuple，输出 Distance 数组逐对计算
- **误区**：是 sqrt(ΔR² + ΔC²) 浮点；如需像素整数,用 round + 后处理

#### ★ distance_cc_min_points — 两轮廓最小距离点对（含两端坐标）
- **用途**：两 XLD 轮廓最小距离点对 —— 返回最近距离 + 各自对应点。
- **参数**：返回 4 个 tuple: MinDistance + 轮廓A 的 (RowA1,ColA1) + 轮廓B 的 (RowB2,ColB2)
- **误区**：对于闭合轮廓,O(N²) 复杂度,长轮廓前先采样

#### ★ distance_rr_min_dil — 两区域最小距离（先膨胀，融合细缝）
- **用途**：两 Region 最小距离(膨胀版) —— 先把 Region 膨胀一个像素,再算最小距离。
- **参数**：可避免细缝(<1px)导致的'虚假接触';用于工件缝隙检测


---

### ③ Angle / Projection (角度·投影，4 算子)

**核心算子**：
- `angle_ll`: 两直线夹角(无方向 0~π),同时也是 distance_ll 的实现
- `angle_lx`: 直线与世界 X 轴夹角(用于方向对齐)
- `projection_pl`: 点到直线垂直投影(机器视觉'逆几何')
- `get_points_ellipse`: 椭圆参数化采样(用于椭圆拟合后取特征点)

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **angle_ll** | 两直线夹角（同时也是 distance_ll 的别名,线-线距离） · `angle_ll( : : RowA1 , ColumnA1 , RowA2 , ColumnA2 , RowB1 , ColumnB1 , RowB2 , ColumnB2 : Angle )` |
| **angle_lx** | 直线与世界 X 轴夹角（与水平线方向角） · `angle_lx( : : Row1 , Column1 , Row2 , Column2 : Angle )` |
| **projection_pl** | 点到直线投影（点沿直线垂直落点） · `projection_pl( : : Row , Column , Row1 , Column1 , Row2 , Column2 : RowProj , ColProj )` |
| **get_points_ellipse** | 椭圆上按角度取点（参数化椭圆采样） · `get_points_ellipse( : : Angle , Row , Column , Phi , Radius1 , Radius2 : RowPoint , ColPoint )` |

#### ★ angle_ll — 两直线夹角（同时也是 distance_ll 的别名,线-线距离）
- **用途**：两直线夹角 —— 返回弧度值（0 到 π）。同时也是 distance_ll 的实现。
- **参数**：8 参数 (RowA1,ColA1,RowA2,ColA2,RowB1,ColB1,RowB2,ColB2)
- **误区**：返回的是无符号夹角(0~π),如需方向角用 line_orientation

#### ★ projection_pl — 点到直线投影（点沿直线垂直落点）
- **用途**：点的直线投影 —— 给定点 P 和直线 (R1,C1)-(R2,C2),返回 P 在直线上的垂直落点。
- **参数**：返回 (RowProj,ColProj),对于'线外点',返回最近垂足;在线外时返回无穷远点（NaN）


---

### ④ Intersection (求交，10 算子)

**算法族（4 对二元几何对象）**：
- **Line-Lines**：intersection_lines / intersection_segments / intersection_line_circle / intersection_segment_circle / intersection_segment_line
- **Circles**：intersection_circles
- **Contour-X**：intersection_line_contour_xld / intersection_segment_contour_xld / intersection_circle_contour_xld / intersection_contours_xld

**返回值约定**：
- `IsOverlapping`: 'true'/'false'（'false' = 无交点,Row/Column 为空）
- `Row/Column`: 交点 tuple,可能 0、1、2 或 N 个值

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **intersection_lines** | 两直线交点（直线求交） · `intersection_lines( : : Line1Row1 , Line1Column1 , Line1Row2 , Line1Column2 , Line2Row1 , Line2Column1 , Line2Row2 , Line2Column2 : Row , Column , IsOverlapping )` |
| **intersection_line_circle** | 直线与圆交点（最多 2 个） · `intersection_line_circle( : : LineRow1 , LineColumn1 , LineRow2 , LineColumn2 , CircleRow , CircleColumn , CircleRadius , CircleStartPhi , CircleEndPhi , CirclePointOrder : Row , Column )` |
| **intersection_segments** | 两线段交点（无交点返回 IsOverlapping） · `intersection_segments( : : Segment1Row1 , Segment1Column1 , Segment1Row2 , Segment1Column2 , Segment2Row1 , Segment2Column1 , Segment2Row2 , Segment2Column2 : Row , Column , IsOverlapping )` |
| **intersection_segment_line** | 线段与直线交点（线段裁剪到直线上） · `intersection_segment_line( : : SegmentRow1 , SegmentColumn1 , SegmentRow2 , SegmentColumn2 , LineRow1 , LineColumn1 , LineRow2 , LineColumn2 : Row , Column , IsOverlapping )` |
| **intersection_segment_circle** | 线段与圆交点（端点若在圆外则裁剪） · `intersection_segment_circle( : : SegmentRow1 , SegmentColumn1 , SegmentRow2 , SegmentColumn2 , CircleRow , CircleColumn , CircleRadius , CircleStartPhi , CircleEndPhi , CirclePointOrder : Row , Column )` |
| **intersection_circles** | 两圆交点（最多 2 个交点 + IsOverlapping） · `intersection_circles( : : Circle1Row , Circle1Column , Circle1Radius , Circle1StartPhi , Circle1EndPhi , Circle1PointOrder , Circle2Row , Circle2Column , Circle2Radius , Circle2StartPhi , Circle2EndPhi , Circle2PointOrder : Row , Column , IsOverlapping )` |
| **intersection_segment_contour_xld** | 线段与 XLD 轮廓交点（多交点数组） · `intersection_segment_contour_xld( Contour : : SegmentRow1 , SegmentColumn1 , SegmentRow2 , SegmentColumn2 : Row , Column , IsOverlapping )` |
| **intersection_line_contour_xld** | 直线与 XLD 轮廓交点（多交点数组） · `intersection_line_contour_xld( Contour : : LineRow1 , LineColumn1 , LineRow2 , LineColumn2 : Row , Column , IsOverlapping )` |
| **intersection_circle_contour_xld** | 圆与 XLD 轮廓交点（多交点数组） · `intersection_circle_contour_xld( Contour : : CircleRow , CircleColumn , CircleRadius , CircleStartPhi , CircleEndPhi , CirclePointOrder : Row , Column )` |
| **intersection_contours_xld** | 两 XLD 轮廓交点（多边形布尔求交） · `intersection_contours_xld( Contour1 , Contour2 : : IntersectionType : Row , Column , IsOverlapping )` |

#### ★ intersection_line_circle — 直线与圆交点（最多 2 个）
- **用途**：直线与圆交点 —— 最多 2 个交点,相切时返回 1 个,无交点返回空 tuple。
- **参数**：相切时 IsOverlapping=true

#### ★ intersection_segments — 两线段交点（无交点返回 IsOverlapping）
- **用途**：两线段交点 —— 严格判断'相交于线段内部'还是'端点相接'。
- **参数**：返回 IsOverlapping = 'true'/'false',若 'true' 则 Row/Column 为交点
- **误区**：两线段共线时返回 false（用 intersection_lines 处理共线情形）

#### ★ intersection_contours_xld — 两 XLD 轮廓交点（多边形布尔求交）
- **用途**：两 XLD 轮廓的求交 —— 通用多边形布尔求交,返回所有交点。
- **参数**：多交点数组,按轮廓 A 上的顺序返回
- **误区**：对于'自相交'轮廓可能产生几何矛盾,先用 union/intersection 闭合 XLD


---

### ⑤ Area Measure (面积测量，1 算子)

**核心算子**：`area_intersection_rectangle2` — HALCON 中'两矩形相交面积'的极简实现,用于 IOU 计算。

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **area_intersection_rectangle2** | 两旋转矩形（rectangle2）的相交面积（快速重叠度） · `area_intersection_rectangle2( : : Rect1Row , Rect1Column , Rect1Phi , Rect1Length1 , Rect1Length2 , Rect2Row , Rect2Column , Rect2Phi , Rect2Length1 , Rect2Length2 : AreaIntersection )` |

#### ★ area_intersection_rectangle2 — 两旋转矩形（rectangle2）的相交面积（快速重叠度）
- **用途**：两旋转矩形相交面积 — 用于 IOU（Intersection over Union）计算的极简实现。
- **参数**：输入 13 参数 (2× rectangle2 + 1 overlap mode)
- **误区**：返回的是相交面积,如需 IOU 再用 (area_intersection) / (area_R1 + area_R2 - area_intersection)


---

## 3. 附录：42 算子完整描述

**apply_distance_transform_xld** — 把距离变换结果应用到 XLD 轮廓 → 离散等距线

> The operator apply_distance_transform_xld determines for each point in Contour the minimal distance to the reference contour using its XLD distance transform DistanceTransformID . The returned contour ContourOut consists of Contour with the attribute 'distance' containing the calculated distances. They can be accessed by querying the attribute 'distance' with get_contour_attrib_xld . See the operator reference of get_contour_attrib_xld for further information about contour attributes. Note that the distances depend on the parameters of create_distance_transform_xld : The distances are clipped to the maximum distance specified by the parameter MaxDistance. The parameter Mode determines whether the distances are calculated 'point_to_point' or 'point_to_segment' . For further details please refer to the documentation of create_distance_transform_xld .

**clear_distance_transform_xld** — 清除距离变换模型（释放句柄 + 内存）

> clear_distance_transform_xld clears the XLD distance transform DistanceTransformID that was previously created by create_distance_transform_xld .

**create_distance_transform_xld** — 创建 XLD 距离变换模型（Mode 3 选 1）

> create_distance_transform_xld creates the XLD distance transform of the reference contour Contour and returns the resulting handle in DistanceTransformID . Once the XLD distance transform has been created, the operator apply_distance_transform_xld calculates pointwise distances from test contours to the reference contour Contour . More precisely, for each point of a test contour its minimal distance to the contours in Contour is calculated.

**get_distance_transform_xld_contour** — 提取等距线轮廓（指定 Level 偏移量）

> get_distance_transform_xld_contour returns the reference contour Contour that was used to build the XLD distance transform DistanceTransformID . This can be used for visualization purposes while comparing a given contour against the reference contour using apply_distance_transform_xld .

**get_distance_transform_xld_param** — 查询距离变换参数（Mode/MaxDistance 等）

> get_distance_transform_xld_param returns the parameters used to build the XLD distance transform DistanceTransformID . The names of the parameters are passed in GenParamName and their values are returned in GenParamValue . GenParamName can contain the names of parameters 'mode' and 'max_distance' .

**read_distance_transform_xld** — 从 .dtxd 文件读取距离变换

> read_distance_transform_xld reads an XLD distance transform which previously has been stored with write_distance_transform_xld from the file given by FileName and returns the handle DistanceTransformID . The default HALCON extension for the XLD distance transform is 'hdtc'. get_distance_transform_xld_contour can be used to get the reference contour that was used to build the XLD distance transform DistanceTransformID .

**serialize_distance_transform_xld** — 序列化为二进制流（用于传输/存储）

> serialize_distance_transform_xld serializes the XLD distance transform DistanceTransformID . The serialized XLD distance transform is returned in the handle SerializedItemHandle and can be deserialized with deserialize_distance_transform_xld .

**set_distance_transform_xld_param** — 热更新参数（重建前可改 Mode）

> set_distance_transform_xld_param sets new parameters for the XLD distance transform DistanceTransformID . The names and values of the parameters are passed in GenParamName and GenParamValue , respectively. GenParamName can contain the names of parameters 'mode' and 'max_distance' . The XLD distance transform of the original reference contour is then rebuilt with updated values of parameters.

**write_distance_transform_xld** — 写入 .dtxd 文件

> write_distance_transform_xld writes the XLD distance transform DistanceTransformID into the file given by FileName . The default HALCON extension for the XLD distance transform is 'hdtc'. The stored XLD distance transform can be read in with read_distance_transform_xld .

**deserialize_distance_transform_xld** — 反序列化距离变换（来自二进制流）

> deserialize_distance_transform_xld deserializes an XLD distance transform. The serialized XLD distance transform is defined by the handle SerializedItemHandle . The deserialized XLD distance transform is returned in DistanceTransformID . Note that the previous values of DistanceTransformID are overwritten, if the handle already exists.

**distance_pp** — 两点间欧氏距离（最常用）

> The operator distance_pp calculates the distance between pairs of points according to the following formula: The result is returned in Distance .

**distance_pl** — 点到直线距离

> The operator distance_pl calculates the orthogonal distance between points ( Row , Column ) and lines, given by two arbitrary points on the line. The result is passed in Distance . distance_pl calculates the distances between a set of n points and one line as well as the distances between a set of n points and n lines.

**distance_pr** — 点到区域边界距离（Region 点云 → 区域外距）

> The operator distance_pr calculates the distance between a point and one region. As input the coordinates of the points ( Row , Column ) and one region are expected. If a point is inside of the region, its minimum distance is zero. The parameters DistanceMin and DistanceMax return the result of the calculation.

**distance_ps** — 点到线段距离（区别于 distance_pl: 端点截断）

> The operator distance_ps calculates the minimum and maximum distance between a point ( Row , Column ) and a line segment which is represented by the start point ( Row1 , Column1 ) and the end point ( Row2 , Column2 ). DistanceMax is the maximum distance between the point and the end points of the line segment. DistanceMin is identical to distance_pl in the case that the point is “between” the two endpoints. Otherwise, the minimum distance to one of the end points is used.

**distance_lr** — 直线到区域距离

> The operator distance_lr calculates the orthogonal distance between a line and one region. As input the coordinates of two points on a line ( Row1 , Column1 , Row2 , Column2 ) and one region are expected. The parameters DistanceMin and DistanceMax return the result of the calculation.

**distance_pc** — 点到 XLD 轮廓距离

> The operator distance_pc calculates the distance between one or several points and a single contour. As input the coordinates of the points ( Row , Column ) and the contour ( Contour ) are expected. The parameters DistanceMin and DistanceMax return the result of the calculation. Note that the result corresponds to the distances between the points and the segments of the contour and not the distances between the points and the base points of the contour (see also distance_contours_xld ).

**distance_lc** — 直线到 XLD 轮廓距离

> The operator distance_lc calculates the orthogonal distance between a line and the segments of one contour. As input the coordinates of two points on a line ( Row1 , Column1 , Row2 , Column2 ) and one contour ( Contour ) are expected. The parameters DistanceMin and DistanceMax return the result of the calculation.

**distance_cc** — 两个 XLD 轮廓最小距离

> The operator distance_cc calculates the minimum and maximum distance between the base points of two contours ( Contour1 and Contour2 ). The parameters DistanceMin and DistanceMax contain the resulting distance. The parameter Mode sets the type of computing the distance: 'point_to_point' only determines the minimum and maximum distance between the base points of the contours. This results in faster algorithm, but may lead to inaccurate minimum distances. In contrast, 'point_to_segment' determines the actual minimum distance between the contour segments.

**distance_cc_min** — 两轮廓最小距离点对（单值最快）

> distance_cc_min calculates the minimum distance between two contours Contour1 and Contour2 . The minimum distance is returned in DistanceMin . The parameter Mode sets the type of computing the distance. 'point_to_point' determines the distance between the closest contour points, 'fast_point_to_segment' calculates the distance between the line segments adjacent to these points, and 'point_to_segment' determines the actual minimum distance between the contour segments.

**distance_cc_min_points** — 两轮廓最小距离点对（含两端坐标）

> distance_cc_min_points calculates the minimum distance between Contour1 and Contour2 . The minimum distance is returned in DistanceMin . In comparison to distance_cc_min , this operator also returns the points on the contours that provide the minimum distance. The point on Contour1 is returned in Row1 and Column1 ; the point on Contour2 is returned in Row2 and Column2 . The parameter Mode sets the type of computing the distance. 'fast_point_to_segment' calculates the distance between the line segments adjacent to the closest contour points, and 'point_to_segment' determines the actual minimum distance between the contour segments.

**distance_contours_xld** — 通用轮廓-轮廓距离函数（输入是 xld 数组）

> The operator distance_contours_xld calculates for each point in ContourFrom the minimal distance to the contours in ContourTo . The operator returns the contour ContourOut which consists of ContourFrom containing the computed distances in the attribute 'distance' . The distances can be accessed by querying the attribute 'distance' with the operator get_contour_attrib_xld . See the operator reference of get_contour_attrib_xld for further information about contour attributes. The parameter Mode determines which distances are calculated for each point in ContourFrom : 'point_to_point' calculates the minimal distance to the base points of ContourTo . In contrast, 'point_to_segment' calculates the minimum distance to the contour segments in ContourTo (see the figure below).

**distance_sc** — 线段到 XLD 轮廓距离

> The operator distance_sc calculates the distance between a line segment and the line segments of one contour. Row1 , Column1 , Row2 , Column2 are the start and end coordinates of a line segment, Contour represents the input contour. The parameters DistanceMin and DistanceMax contain the resulting distances.

**distance_sl** — 线段到直线距离

> The operator distance_sl calculates the minimum and maximum orthogonal distance between a line segment and a line. As input the coordinates of two points on the line segment ( RowA1 , ColumnA1 , RowA2 , ColumnA2 ) and on the line ( RowB1 , ColumnB1 , RowB2 , ColumnB2 ) are expected. The parameters DistanceMin and DistanceMax return the result of the calculation. If the line segments are intersecting, DistanceMin returns zero.

**distance_sr** — 线段到区域距离

> The operator distance_sr calculates the distance between a line segment and one region. Row1 , Column1 , Row2 , Column2 are the start and end coordinates of a line segment. The parameters DistanceMin and DistanceMax contain the resulting distances.

**distance_ss** — 两线段最小距离（工业零件碰撞检测）

> The operator distance_ss calculates the minimum and maximum distance between two line segments. As input the coordinates of the start and end point of the first line segment ( RowA1 , ColumnA1 , RowA2 , ColumnA2 ) and of the second line segment ( RowB1 , ColumnB1 , RowB2 , ColumnB2 ) are used. The parameters DistanceMin and DistanceMax return the result of the calculation. If the line segments are intersecting, DistanceMin returns zero.

**distance_rr_min** — 两区域最小距离（Region 边界最近点距离）

> The operator distance_rr_min calculates the minimum distance of pairs of regions. If several regions are passed in Regions1 and Regions2 the distance between the contour pixels of each i-th element is calculated and then forms the i-th entry in the output parameter MinDistance . The Euclidean distance is used. The parameters ( Row1 , Column1 ) and ( Row2 , Column2 ) indicate the position on the contour of Regions1 and Regions2 , respectively, that have the minimum distance. The calculation is carried out by comparing all contour pixels (see get_region_contour ). This means in particular that holes in the regions are ignored. Furthermore, it is not checked whether one region lies completely within the other region. In this case, a minimum distance > 0 is returned. It is also not checked whether both regions contain a nonempty intersection. In the latter case, a minimum distance of 0 or > 0 can be returned, depending on whether the contours of the regions contain a common point or not.

**distance_rr_min_dil** — 两区域最小距离（先膨胀，融合细缝）

> The operator distance_rr_min_dil calculates the minimum distance between pairs of regions, by iteratively applying dilations on both regions until their intersection is non empty. If several regions are passed in Regions1 and Regions2 the distance between the i-th elements in each case is calculated. It then forms the i-th entry in the output parameter MinDistance . The calculation is carried out with the help of dilation with the Golay element 'h'. The result is: Number of iterations * 2 - 1. The mask 'h' has the effect that precisely the maximum metrics are calculated.

**angle_ll** — 两直线夹角（同时也是 distance_ll 的别名,线-线距离）

> The operator angle_ll calculates the angle between two lines. As input the coordinates of two points on the first line ( RowA1 , ColumnA1 , RowA2 , ColumnA2 ) and on the second line ( RowB1 , ColumnB1 , RowB2 , ColumnB2 ) are expected. The calculation is performed as follows: We interpret the lines as vectors with starting points RowA1 , ColumnA1 and RowB1 , ColumnB1 and end points RowA2 , ColumnA2 and RowB2 , ColumnB2 , respectively. Rotating the vector A counter clockwise onto the vector B (the center of rotation is the intersection point of the two lines) yields the angle. The result depends on the order of the points and on the order of the lines. The parameter Angle returns the angle in radians, ranging from -pi <= Angle <= pi.

**angle_lx** — 直线与世界 X 轴夹角（与水平线方向角）

> The operator angle_lx calculates the angle between one line and the horizontal axis. As input the coordinates of two points on the line ( Row1 , Column1 , Row2 , Column2 ) are expected. The calculation is performed as follows: We interpret the line as a vector with starting point Row1 , Column1 and end point Row2 , Column2 . The starting point is on the horizontal axis and defines the center of rotation in the following consideration. If the end point is above the horizontal axis, the angle (with positive sign) results from the rotation of the horizontal axis in counter clockwise direction onto the vector. If the end point is below the horizontal axis, the angle (with negative sign) results from the rotation of the horizontal axis in clockwise direction onto the vector. The result depends on the order of the two points defining the line. The parameter Angle returns the angle in radians, ranging from

**projection_pl** — 点到直线投影（点沿直线垂直落点）

> The operator projection_pl calculates the projection of a point ( Row , Column ) onto a line which is represented by the two points ( Row1 , Column1 ) and ( Row2 , Column2 ). The coordinates of the projected point are returned in RowProj and ColProj .

**get_points_ellipse** — 椭圆上按角度取点（参数化椭圆采样）

> get_points_ellipse returns the point ( RowPoint , ColPoint ) on the specified ellipse corresponding to the angle in Angle . With the parameter Angle you are setting the eccentric anomaly, which denotes the angle used for the parametric equation (see the figure below) and refers to the main axis of the ellipse. The ellipse itself is characterized by the center ( Row , Column ), the orientation of the main axis Phi relative to the horizontal axis, the length of the larger ( Radius1 ) and the smaller half axis ( Radius2 ). The angles are measured counter clockwise in radiant. image/svg+xml

**intersection_lines** — 两直线交点（直线求交）

> intersection_lines calculates the intersection point of two lines, which are defined by two of their points ( Line1Row1 , Line1Column1 ), ( Line1Row2 , Line1Column2 ), and ( Line2Row1 , Line2Column1 ), ( Line2Row2 , Line2Column2 ) respectively. The intersection point, if it exists, is returned in ( Row , Column ). If both lines are identical, IsOverlapping returns the value 1, otherwise 0 is returned. In this case no intersection point is returned in ( Row , Column ).

**intersection_line_circle** — 直线与圆交点（最多 2 个）

> intersection_line_circle calculates the intersection points of a line and a circle or circular arc. The line is defined by the points ( LineRow1 , LineColumn1 ) and ( LineRow2 , LineColumn2 ). The circle is defined by its center ( CircleRow , CircleColumn ) and its radius CircleRadius . In addition to that, a circular arc is characterized by the angle of the start point CircleStartPhi , the angle of the end point CircleEndPhi , and the point order CirclePointOrder along the boundary. If CirclePointOrder is set to 'positive' , the circular arc is defined counterclockwise. If CirclePointOrder is set to 'negative' , the circular arc is defined clockwise. The intersection points, if any, are returned in ( Row , Column ).

**intersection_segments** — 两线段交点（无交点返回 IsOverlapping）

> intersection_segments calculates the intersection point of two line segments, which are defined by their endpoints ( Segment1Row1 , Segment1Column1 ), ( Segment1Row2 , Segment1Column2 ), and ( Segment2Row1 , Segment2Column1 ), ( Segment2Row2 , Segment2Column2 ) respectively. The intersection point, if it exists, is returned in ( Row , Column ). If both segments have a part in common, IsOverlapping returns the value 1, otherwise 0 is returned. In this case the endpoints of the mutual segment are returned in ( Row , Column ).

**intersection_segment_line** — 线段与直线交点（线段裁剪到直线上）

> intersection_segment_line calculates the intersection point of a segment and a line. The segment is defined by its endpoints ( SegmentRow1 , SegmentColumn1 ) and ( SegmentRow2 , SegmentColumn2 ). The line is defined by the two points ( LineRow1 , LineColumn1 ) and ( LineRow2 , LineColumn2 ). The intersection point, if it exists, is returned in ( Row , Column ). If the segment and the line have a part in common, IsOverlapping returns the value 1, otherwise 0 is returned. In this case the endpoints of the mutual segment are returned in ( Row , Column ).

**intersection_segment_circle** — 线段与圆交点（端点若在圆外则裁剪）

> intersection_segment_circle calculates the intersection point of a segment and a circle or circular arc. The segment is defined by its endpoints ( SegmentRow1 , SegmentColumn1 ) and ( SegmentRow2 , SegmentColumn2 ). The circle is defined by its center ( CircleRow , CircleColumn ) and its radius CircleRadius . In addition to that, a circular arc is characterized by the angle of the start point CircleStartPhi , the angle of the end point CircleEndPhi , and the point order CirclePointOrder along the boundary. If CirclePointOrder is set to 'positive' , the circular arc is defined counterclockwise. If CirclePointOrder is set to 'negative' , the circular arc is defined clockwise. The intersection points, if any, are returned in ( Row , Column ).

**intersection_circles** — 两圆交点（最多 2 个交点 + IsOverlapping）

> intersection_circles calculates the intersection points of two circles or circular arcs. The points, if any, are returned in ( Row , Column ). The circles are defined by their center ( Circle1Row , Circle1Column ), and ( Circle2Row , Circle2Column ) respectively, and their radii Circle1Radius , and Circle2Radius respectively. In addition to that, a circular arc is characterized by the angle of the start point ( Circle1StartPhi , Circle2StartPhi ), the angle of the end point ( Circle1EndPhi , Circle2EndPhi ), and the point order ( Circle1PointOrder , Circle2PointOrder ) along the boundary. If Circle1PointOrder is set to 'positive' , the circular arc is defined counterclockwise. If Circle1PointOrder is set to 'negative' , the circular arc is defined clockwise. The same applies for Circle2PointOrder . If both circles or circular arcs have a part in common IsOverlapping returns the value 1, otherwise 0 is returned. In this case the endpoints of the mutual arc are returned in ( Row , Column ).

**intersection_segment_contour_xld** — 线段与 XLD 轮廓交点（多交点数组）

> intersection_segment_contour_xld calculates the intersection points of a segment and an XLD Contour . The segment is defined by its endpoints ( SegmentRow1 , SegmentColumn1 ) and ( SegmentRow2 , SegmentColumn2 ). The intersection points, if any, are returned in ( Row , Column ). If the segment and the XLD contour have a part in common IsOverlapping returns the value 1, otherwise 0 is returned. In this case the endpoints of the mutual segment are returned in ( Row , Column ).

**intersection_line_contour_xld** — 直线与 XLD 轮廓交点（多交点数组）

> intersection_line_contour_xld calculates the intersection points of a line and an XLD Contour . The line is defined by the points ( LineRow1 , LineColumn1 ) and ( LineRow2 , LineColumn2 ). The intersection points, if any, are returned in ( Row , Column ). If a part of the XLD contour lies on the line IsOverlapping returns the value 1, otherwise 0 is returned. In this case the endpoints of the XLD segment are returned in ( Row , Column ).

**intersection_circle_contour_xld** — 圆与 XLD 轮廓交点（多交点数组）

> intersection_circle_contour_xld calculates the intersection points of a circle or circular arc and the XLD Contour . The circle is defined by its center ( CircleRow , CircleColumn ) and its radius CircleRadius . In addition to that, a circular arc is characterized by the angle of the start point CircleStartPhi , the angle of the end point CircleEndPhi , and the point order CirclePointOrder along the boundary. If CirclePointOrder is set to 'positive' , the circular arc is defined counterclockwise. If CirclePointOrder is set to 'negative' , the circular arc is defined clockwise. The intersection points, if any, are returned in ( Row , Column ).

**intersection_contours_xld** — 两 XLD 轮廓交点（多边形布尔求交）

> intersection_contours_xld calculates the intersection points of the XLD Contour1 and XLD Contour2 which, if any, are returned in ( Row , Column ). The value in IntersectionType defines the way to calculate the intersections points. By setting IntersectionType = 'self' , only the self intersections within both contours are returned, i.e., the intersections within Contour1 and XLD Contour2 . For IntersectionType = 'mutual' , only the intersections between both contours are taken into account. The default value is IntersectionType = 'all' . In this case both, the self and the mutual intersections are returned in Row , Column ). If parts of the contours overlap in more than one point IsOverlapping returns the value 1, otherwise 0 is returned. IsOverlapping is set with regard to both the self and mutual overlap, regardless of the setting in IntersectionType . In case of a mutual overlap, the endpoints of the mutual segment are returned in ( Row , Column ).

**area_intersection_rectangle2** — 两旋转矩形（rectangle2）的相交面积（快速重叠度）

> area_intersection_rectangle2 calculates the intersection area of two oriented rectangles (i.e., of type rectangle2), which are defined by their parameters (center ( Rect1Row , Rect1Column ), orientation Rect1Phi , and the half edge lengths Rect1Length1 and Rect1Length2 ) and (center ( Rect2Row , Rect2Column ), orientation Rect2Phi , and the half edge lengths Rect2Length1 and Rect2Length2 ), respectively. The intersection area is returned in AreaIntersection . If multiple values are given for the parameters of the second rectangle, the output is a tuple with the intersection area of the first rectangle with each of the second rectangles. In case no parameters are given for the second rectangle, an empty tuple is returned in AreaIntersection .
