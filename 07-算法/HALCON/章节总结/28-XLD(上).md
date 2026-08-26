# 第 28 章 XLD(上)

## 序言

HALCON 操作员手册第 28 章 **XLD**(eXtended Line Descriptions)是亚像素级轮廓/多边形数据结构的官方定义:把图像中'曲线/直线段/边缘对/属性键值对'抽象成一个统一对象族 `HXLD...`(HXLDCont / HXLDPoly / HXLDPara),是 1D 测量、边缘宽度、形状识别、亚像素配准的事实底层。

全章共 **6 个子族 94 个算子**(Access 4 + Creation 12 + Features 45 + Sets 8 + Transformations 20 + Geometric Transformations 5)。本章分为上、中、下三卷进行总结——**上卷涵盖前三个子族:Access(4)+Creation(12)+Features(45)= 61 个算子**。中卷涵盖 Sets(并集/交集/差集等共 8 个集合运算)和 Transformations(平滑/裁剪/合并等共 20 个局部变换),下卷涵盖 Geometric Transformations(5 个 2D 仿射/极坐标/投影变换)。

一句话定位:**把'像素'提升为'带属性 + 带方向的曲线'**,并在 XLD 上构建几何测量、形状描述、亚像素配准三大支柱。

## 1. 全卷结构表

| 子族 | 算子数 | 核心功能 | 典型场景 |
| ---- | ------ | -------- | -------- |
| **Access(访问)** | 4 | 从 XLD 对象中抽取原始坐标/属性 | 数据导出、几何重计算、第三方桥接 |
| **Creation(构造)** | 12 | 从图像/区域/参数生成 XLD | 模板制作、标定标记、平行边缘构造 |
| **Features(特征)** | 45 | XLD 的几何/形状/属性特征计算 | 测量筛选、形状分类、配准前数据 |
| **合计(本卷)** | **61** | — | — |

## 2. 子族分述

### 2.1 Access(4 ops)

本子族是 XLD → 通用元组的桥梁:返回对象内嵌的数值/参数,不重建新对象。常用于:把 XLD 拿到 HDevelop 外面做归一化、按列查询/排序、把数据塞进 HTuple 容器传到 GUI 或调用第三方算法。

| 算子 | 一句话功能 |
| ---- | -------- |
| `get_contour_xld` | 从 XLD 轮廓中取出每个点的 (Row, Col) 坐标序列。 |
| `get_lines_xld` | 把 XLD 多边形解构为多条直线段,得到起止点+长度+方向。 |
| `get_parallels_xld` | 取出 XLD parallels 的首组端点几何信息(用于边缘对分析)。 |
| `get_polygon_xld` | 取出 XLD 多边形的几何参数,每点附 (Row, Col, Length, Phi)。 |

**重点算子注**:`get_contour_xld` 与 `get_lines_xld` 是导出外部坐标的两种粒度;前者给**整条曲线上每个点**(离散与连续皆有),后者把多边形拆成**多条直线段**(便于和 Hough 直线混合计算)。

### 2.2 Creation(12 ops)

构造家族按'输入数据'分为 4 条路径:

- **几何参数 → XLD**:`gen_circle_contour_xld`、`gen_ellipse_contour_xld`、`gen_rectangle2_contour_xld`、`gen_cross_contour_xld`(参数化绘制)
- **顶点列表 → XLD**:`gen_contour_polygon_xld`、`gen_polygons_xld`(批量)、`gen_contour_polygon_rounded_xld`(带圆角)
- **控制点 → XLD**:`gen_contour_nurbs_xld`(NURBS 曲线)
- **Region / Skeleton → XLD**:`gen_contour_region_xld`、`gen_contours_skeleton_xld`(上桥到区域)
- **灰度边缘追踪 → Parallels**:`gen_parallels_xld`、`mod_parallels_xld`(配合 edges_image 的边缘宽度测量链路)

| 算子 | 一句话功能 | 详细签名 |
| ---- | -------- | -------- |
| `gen_circle_contour_xld` | 按圆心和半径生成一段/一整圈 XLD 圆弧或闭环圆。 | `gen_circle_contour_xld ( : ContCircle : Row, Column, Radius, StartPhi, EndPhi, PointOrder, Resolution : )` |
| `gen_contour_nurbs_xld` | 通过控制点和 NURBS 阶数生成一段 NURBS 开放轮廓。 | `gen_contour_nurbs_xld ( : Contour : Rows, Cols, Knots, Weights, Degree, MaxError, MaxDistance : )` |
| `gen_contour_polygon_rounded_xld` | 在多边形顶点处做圆角过渡,生成带圆角的多边形轮廓。 | `gen_contour_polygon_rounded_xld ( : Contour : Row, Col, Radius, SamplingInterval : )` |
| `gen_contour_polygon_xld` | 把一组有序顶点直接连接成 XLD 多边形(直线段拼接)。 | `gen_contour_polygon_xld ( : Contour : Row, Col : )` |
| `gen_contour_region_xld` | 把区域(region)边界抽取为 XLD 轮廓。 | `gen_contour_region_xld (Regions : Contours : Mode : )` |
| `gen_contours_skeleton_xld` | 对区域做骨架化,把骨架抽成 XLD 轮廓(细化中心线)。 | `gen_contours_skeleton_xld (Skeleton : Contours : Length, Mode : )` |
| `gen_cross_contour_xld` | 在指定 (Row, Column) 处生成一个十字形 XLD 标定标记。 | `gen_cross_contour_xld ( : Cross : Row, Col, Size, Angle : )` |
| `gen_ellipse_contour_xld` | 生成椭圆/椭圆弧 XLD 轮廓(控制点+长轴+短轴+倾角)。 | `gen_ellipse_contour_xld ( : ContEllipse : Row, Column, Phi, Radius1, Radius2, StartPhi, EndPhi, PointOrder, Resolution : )` |
| `gen_parallels_xld` | 沿 XLD 多边形等距偏移生成 parallels(用于边缘宽度测量)。 | `gen_parallels_xld (Polygons : Parallels : Len, Dist, Alpha, Merge : )` |
| `gen_polygons_xld` | 输入坐标点元组直接生成 XLD 多边形(批量)。 | `gen_polygons_xld (Contours : Polygons : Type, Alpha : )` |
| `gen_rectangle2_contour_xld` | 生成任意方向矩形(rectangle2 = 中心+长宽+倾角)的 XLD 轮廓。 | `gen_rectangle2_contour_xld ( : Rectangle : Row, Column, Phi, Length1, Length2 : )` |
| `mod_parallels_xld` | 通过灰度阈值提取并追踪边缘对,生成 parallels(配合 edges_image)。 | `mod_parallels_xld (Parallels, Image : ModParallels, ExtParallels : Quality, MinGray, MaxGray, MaxStandard : )` |

**重点算子注**



**`gen_contour_polygon_xld` 详解**

- **参数核心**:Polygons (out) ∈ HXLDPolyList; Row, Col (in) 为同长元组,逐点连接; 注意:若无序传入需先排序(否则会画出乱线); 开放式多边形首尾不闭合。
- **误区警示**:1)Row/Col 必须等长,否则抛错;2)若想画闭合多边形,需自己把首点追加到尾巴(end_t Y 嵌入循环);3)相比 gen_polygons_xld(批量),本算子是单 polygon 输出,且要求 Row/Col 同为 tuple;4)它只输出等直线段,曲线拟合请改用 gen_contour_nurbs_xld。
- **场景适用**:适用于:已知顶点序列的封闭多边形、子区域边界速记、模板初始轮廓制作。不适用:平滑曲线(用 nurbs)、半径≥10 的圆(用 gen_circle_contour_xld)。

**`gen_parallels_xld` 详解**

- **参数核心**:Parallels (out) ∈ HXLDParList; Polygon (in) 一段 XLD 多边形; GenName 类型,包括 'gradient'/'regression'/'fixed'; GenParamName 控制步距/追踪规则; 注意 'fixed' 模式需要手动指定距离,而 'gradient' 自动按图像灰度求边缘。
- **误区警示**:1)'gradient' 模式必须先调 edges_image 再调 gen_parallels_xld,且单像素宽 step;2)'regression' 模式按当前像素灰度做回归,对噪声敏感;3)生成的 parallels 不一定连通,请配合 max_parallels_xld 拼接;4)返回的 Parallels 中每对 (Row1,Col1)-(Row2,Col2) 代表一个边缘对。
- **场景适用**:经典管道:edges_image(Image,ImaAmp,ImaDir,'canny',...) → get_parallels_xld → gen_parallels_xld(...,GenName='gradient',...) → fit_line_contour_xld。用于 PCB 走线宽度、纸张间距测量等工业几何量级。

### 2.3 Features(45 ops)

特征家族按 XLD 的'形状表达维度'分成 6 组:

- **几何量(面积/质心/长度/直径)**:约 8 个(`area_center_xld`、`length_xld`、`diameter_xld`、`contour_point_num_xld` 等)
- **形状因子(圆度/紧致度/凸度/矩形度)**:约 5 个(`circularity_xld`、`compactness_xld`、`convexity_xld`、`rectangularity_xld`、`height_width_ratio_xld`)
- **等效椭圆/参数**:约 4 个(`elliptic_axis_xld`、`eccentricity_xld`、`orientation_xld` 及其 `_points` 版本)
- **几何矩**:4 个(`moments_xld`、`moments_points_xld`、`moments_any_xld`、`moments_any_points_xld`)
- **几何拟合**:4 个(`fit_circle_contour_xld`、`fit_ellipse_contour_xld`、`fit_line_contour_xld`、`fit_rectangle2_contour_xld`)
- **外接 + 距离**:6 个(`smallest_circle_xld`、`smallest_rectangle1_xld`、`smallest_rectangle2_xld`、`dist_ellipse_contour_xld` 三个距离变种)
- **查询与属性**:6 个(`get_contour_angle_xld` 等 + `query_*` + `get_regress_params_xld` 等)
- **测试 + 选取**:6 个(`test_closed_xld`、`test_self_intersection_xld`、`test_xld_point`、`select_contours_xld`、`select_shape_xld`、`select_xld_point`)
- **属性管理**:4 个(`get_contour_attrib_xld`、`get_contour_global_attrib_xld`、`set_*_attrib_*` 类不在本章,在 Transformations 卷)+ `info_parallels_xld` + `local_max_contours_xld` + `max_parallels_xld`

| 算子 | 一句话功能 | 详细签名 |
| ---- | -------- | -------- |
| `area_center_points_xld` | 把 XLD 轮廓/多边形当作点云,计算面积和质心(忽略闭合性)。 | `area_center_points_xld (XLD : : : Area, Row, Column)` |
| `area_center_xld` | 计算 XLD 轮廓或多边形的面积与质心(若闭合则按封闭区域积分)。 | `area_center_xld (XLD : : : Area, Row, Column, PointOrder)` |
| `circularity_xld` | 计算 XLD 形状的圆度 (4πA / P²),值越接近 1 越像圆。 | `circularity_xld (XLD : : : Circularity)` |
| `compactness_xld` | 计算 XLD 形状的紧致度(等周长下面积最大者)。 | `compactness_xld (XLD : : : Compactness)` |
| `contour_point_num_xld` | 返回 XLD 轮廓的总点数(用于长度/抽样裁剪)。 | `contour_point_num_xld (Contour : : : Length)` |
| `convexity_xld` | 凸度 = 凸包面积 / 实际面积,1 表示纯凸形。 | `convexity_xld (XLD : : : Convexity)` |
| `diameter_xld` | 最大两点距离(直径),即 XLD 形状的最长对角。 | `diameter_xld (XLD : : : Row1, Column1, Row2, Column2, Diameter)` |
| `dist_ellipse_contour_points_xld` | 逐点计算 XLD 轮廓到指定椭圆的最小距离序列。 | `dist_ellipse_contour_points_xld (Contour : : DistanceMode, ClippingEndPoints, Row, Column, Phi, Radius1, Radius2 : Distances)` |
| `dist_ellipse_contour_xld` | 计算 XLD 轮廓整体到指定椭形的几何距离均值/最大/最小。 | `dist_ellipse_contour_xld (Contours : : Mode, MaxNumPoints, ClippingEndPoints, Row, Column, Phi, Radius1, Radius2 : MinDist, MaxDist, AvgDist, SigmaDist)` |
| `dist_rectangle2_contour_points_xld` | 逐点计算 XLD 轮廓到任意方向矩形(rectangle2)的距离。 | `dist_rectangle2_contour_points_xld (Contour : : ClippingEndPoints, Row, Column, Phi, Length1, Length2 : Distances)` |
| `eccentricity_points_xld` | 把 XLD 形状当作点云,计算长短轴比(异形度)。 | `eccentricity_points_xld (XLD : : : Anisometry)` |
| `eccentricity_xld` | 由椭圆等效参数计算的形状异形度(主轴/副轴之比)。 | `eccentricity_xld (XLD : : : Anisometry, Bulkiness, StructureFactor)` |
| `elliptic_axis_points_xld` | 把 XLD 视作点云,估计等效椭圆的主/副半轴与方向。 | `elliptic_axis_points_xld (XLD : : : Ra, Rb, Phi)` |
| `elliptic_axis_xld` | 等效椭圆参数(Ra,Rb,Phi)+ 面积(环绕 XLD 形状拟合)。 | `elliptic_axis_xld (XLD : : : Ra, Rb, Phi)` |
| `fit_circle_contour_xld` | 用最小二乘把一组轮廓点拟合成圆(几何拟合,非区域面积)。 | `fit_circle_contour_xld (Contours : : Algorithm, MaxNumPoints, MaxClosureDist, ClippingEndPoints, Iterations, ClippingFactor : Row, Column, Radius, StartPhi, EndPhi, PointOrder)` |
| `fit_ellipse_contour_xld` | 用最小二乘将 XLD 轮廓拟合成椭圆/椭圆弧。 | `fit_ellipse_contour_xld (Contours : : Algorithm, MaxNumPoints, MaxClosureDist, ClippingEndPoints, VossTabSize, Iterations, ClippingFactor : Row, Column, Phi, Radius1, Radius2, StartPhi, EndPhi, PointOrder)` |
| `fit_line_contour_xld` | 把 XLD 多边形拆成 N 段直线(可剔除/裁剪异常段)。 | `fit_line_contour_xld (Contours : : Algorithm, MaxNumPoints, ClippingEndPoints, Iterations, ClippingFactor : RowBegin, ColBegin, RowEnd, ColEnd, Nr, Nc, Dist)` |
| `fit_rectangle2_contour_xld` | 把 XLD 轮廓拟合成任意方向的最小矩形(rectangle2)。 | `fit_rectangle2_contour_xld (Contours : : Algorithm, MaxNumPoints, MaxClosureDist, ClippingEndPoints, Iterations, ClippingFactor : Row, Column, Phi, Length1, Length2, PointOrder)` |
| `get_contour_angle_xld` | 逐点返回 XLD 轮廓切线方向角度(用于边缘方向匹配)。 | `get_contour_angle_xld (Contour : : AngleMode, CalcMode, Lookaround : Angles)` |
| `get_contour_attrib_xld` | 返回 XLD 轮廓某点处的局部属性(如 'gray' 边缘响应)。 | `get_contour_attrib_xld (Contour : : Name : Attrib)` |
| `get_contour_global_attrib_xld` | 返回 XLD 轮廓的全局属性(整条轮廓共有的全局键值)。 | `get_contour_global_attrib_xld (Contour : : Name : Attrib)` |
| `get_regress_params_xld` | 返回最近 fit_* 调用所得到的多项式参数(行列方向/直线段)。 | `get_regress_params_xld (Contours : : : Length, Nx, Ny, Dist, Fpx, Fpy, Lpx, Lpy, Mean, Deviation)` |
| `height_width_ratio_xld` | 由平行坐标轴方向最小包围盒,得到高/宽/纵横比。 | `height_width_ratio_xld (XLD : : : Height, Width, Ratio)` |
| `info_parallels_xld` | 查询 parallel 间的灰度值分布与梯度信息(明暗/对比度)。 | `info_parallels_xld (Parallels, Image : : : QualityMin, QualityMax, GrayMin, GrayMax, StandardMin, StandardMax)` |
| `length_xld` | 返回 XLD 轮廓或多边形总弧长。 | `length_xld (XLD : : : Length)` |
| `local_max_contours_xld` | 挑选 points with local maximum gray value(沿轮廓找局部极值)。 | `local_max_contours_xld (Contours, Image : LocalMaxContours : MinPercent, MinDiff, Distance : )` |
| `max_parallels_xld` | 把端点相邻属于同一多边形的 parallels 拼接(避免断线)。 | `max_parallels_xld (ExtParallels : MaxPolygons : : )` |
| `moments_any_points_xld` | 任意阶几何矩,把 XLD 当点云(忽略边界闭合)。 | `moments_any_points_xld (XLD : : Mode, Area, CenterRow, CenterCol, P, Q : M)` |
| `moments_any_xld` | 任意阶几何矩,沿闭合 XLD 轮廓(0~N 阶都可指定)。 | `moments_any_xld (XLD : : Mode, PointOrder, Area, CenterRow, CenterCol, P, Q : M)` |
| `moments_points_xld` | 经典二阶矩 M20/M02/M11,把 XLD 当点云。 | `moments_points_xld (XLD : : : M11, M20, M02)` |
| `moments_xld` | 经典二阶矩 M20/M02/M11,沿闭合轮廓积分。 | `moments_xld (XLD : : : M11, M20, M02)` |
| `orientation_points_xld` | 主轴方向(0~π),把 XLD 视作点云。 | `orientation_points_xld (XLD : : : Phi)` |
| `orientation_xld` | 主轴方向(0~π),沿闭合轮廓积分。 | `orientation_xld (XLD : : : Phi)` |
| `query_contour_attribs_xld` | 列出 XLD 轮廓上定义的所有局部属性名(用于通用属性查询)。 | `query_contour_attribs_xld (Contour : : : Attribs)` |
| `query_contour_global_attribs_xld` | 列出 XLD 轮廓上定义的所有全局属性名。 | `query_contour_global_attribs_xld (Contour : : : Attribs)` |
| `rectangularity_xld` | 矩形度 = XLD 面积 / 最小包围矩形面积。 | `rectangularity_xld (XLD : : : Rectangularity)` |
| `select_contours_xld` | 按长度/方向/闭合特征筛选 XLD 轮廓(批量过滤)。 | `select_contours_xld (Contours : SelectedContours : Feature, Min1, Max1, Min2, Max2 : )` |
| `select_shape_xld` | 按形状特征(面积/紧致度/矩…等)筛选 XLD 轮廓(同 select_shape 区域版)。 | `select_shape_xld (XLD : SelectedXLD : Features, Operation, Min, Max : )` |
| `select_xld_point` | 返回距指定 (row, col) 最近的 XLD 轮廓点索引。 | `select_xld_point (XLDs : DestXLDs : Row, Column : )` |
| `smallest_circle_xld` | 包围 XLD 轮廓的最小外接圆(中心+半径)。 | `smallest_circle_xld (XLD : : : Row, Column, Radius)` |
| `smallest_rectangle1_xld` | 轴对齐最小外接矩形(rectangle1,8 个返回值)。 | `smallest_rectangle1_xld (XLD : : : Row1, Column1, Row2, Column2)` |
| `smallest_rectangle2_xld` | 任意方向最小外接矩形(rectangle2,4 参数:中心+长宽+倾角)。 | `smallest_rectangle2_xld (XLD : : : Row, Column, Phi, Length1, Length2)` |
| `test_closed_xld` | 判断 XLD 轮廓首尾是否重合(是否闭合)。 | `test_closed_xld (XLD : : : IsClosed)` |
| `test_self_intersection_xld` | 判断 XLD 轮廓自相交测试(返回是否自交以及交点数)。 | `test_self_intersection_xld (XLD : : CloseXLD : DoesIntersect)` |
| `test_xld_point` | 判断指定 (Row, Column) 是否在任意 XLD 轮廓上(边缘命中测试)。 | `test_xld_point (XLD : : Row, Column : IsInside)` |

**重点算子注**

**`fit_circle_contour_xld` 详解**

- **参数核心**:Contour (in) ∈ HXLDCont; Algorithm 默认 'pratt-huber'(抗噪鲁棒);也可选 'algebraic'/'numerical'/'geometric'; Resolution 控制角度步长(默认 0); 输出 Row/Column/Radius/StartPhi/EndPhi/PointOrder。
- **误区警示**:1)输入必须是 XLD 轮廓,不能用 region 直接传入(先 gen_contour_region_xld);2)'pratt-huber' 适合<50% 噪声点的工 业数据,'algebraic' 最快但不抗噪;3)Radius 与 ImageScale 单位相同,缩放后要乘回去;4)若轮廓本身是多段(边角处),拟合可能偏向较长的段。
- **场景适用**:圆度判定的金标准:对拟合后的半径方差做阈值,或直接用 circularity_xld。典型:轴承孔径、硬币直径、卡尺圆顶检测。配合 select_contours_xld 过滤波段,使拟合不偏向杂点。

**`fit_line_contour_xld` 详解**

- **参数核心**:Contours (in/out) ∈ HXLDCont; Algorithm 控制拟合算法,默认 'regression'; Tabs 控制段长(像素,只在分段时用); ClipLineEndpoints ('auto'/'true'/'false') 是否裁剪端点到实际像素极值; 输出 BeginRow/BeginCol/EndRow/EndCol/Length/Phi。
- **误区警示**:1)'regression' 对所有点做最小二乘,适合大多数场景;若想分段为多段,请改 'split';2)对噪声点敏感,先 select_shape_xld 按长度过滤;3)若 contour 是分段刚好的多边形,Phi 会分段计算(关键长度阈值见 ClipLineEndpoints);4)返回值 Length 不含端点裁剪,最终显示可能稍短。
- **场景适用**:典型:从 edges_image 提取的细微边缘 → 通过 fit_line_contour_xld 拟合成可量化的直线段 → select_contours_xld('lines', ...) 选最长段 → gen_arrow_contour_xld 可视化。在 PCB 走线/HUD 标定线/激光条纹检测中是主力。

**`area_center_xld` 详解**

- **参数核心**:Contour (in) ∈ HXLDCont; Area (out) 浮点面积(归一化像素); Row/Column 质心坐标; 算法使用格林定理对闭合轮廓做线积分,非象素面积。
- **误区警示**:1)输入须闭合(首尾重合),否则面积不收敛;用 test_closed_xld 预检;2)轮廓方向很关键,顺逆时针正负相反;3)若轮廓是多段形成的复杂形状,Area=Area(simple),即不重叠分块的代数和(对不相连的 Segments 同样适用,但需要 select_contours_xld 子集化);4)输出的 Row/Column 单位与轮廓点坐标一致(像素或 world 标定)。
- **场景适用**:任何需要'面积+质心'的下游筛选,以 area_center_xld + select_contours_xld 配对使用(经典:硬币定位、螺丝孔定位)。对'点云样式'的离散点集,改用 area_center_points_xld。

**`smallest_rectangle2_xld` 详解**

- **参数核心**:Contour (in) ∈ HXLDCont; 输出 Row/Column (中心), Phi (姿态角,弧度,顺时针测量,以水平轴为零), Length1/Length2 (两条半轴,即矩形一半的短/长)。Length1 对应短半轴!
- **误区警示**:1)Length1 是半短轴,不是你想象的完整短边,Length2 是半长轴;2)Phi 是 -π/2 ~ π/2 范围(通常),不是 [0, π);3)多个轮廓存在时,本算子返回的是单个外接矩形,先 select_contours_xld 提取目标,再调用;4)多连通/凹陷形状仍返回凸包最小矩形。
- **场景适用**:用途最广的伴随算子:与 gen_rectangle2_contour_xld 对偶(一个 fit,一个 init)。典型姿态估计:fit → (Phi) → matrix_to_hom_mat2d(Phi,...) → affine_trans_contour_xld → 配准。焊接点、OLED 屏检测几乎必现。

## 3. 全卷算子速查表(61 算子)

> 按子族分组;子族内按字母序。下表含一句话中文功能。

### 3.1 Access(4 ops)

| # | 算子 | 一句话功能 | HDevelop 关键签名 |
| - | ---- | -------- | ---------------- |
| 1 | `get_contour_xld` | 从 XLD 轮廓中取出每个点的 (Row, Col) 坐标序列。 | `get_contour_xld (Contour : : : Row, Col)` |
| 2 | `get_lines_xld` | 把 XLD 多边形解构为多条直线段,得到起止点+长度+方向。 | `get_lines_xld (Polygon : : : BeginRow, BeginCol, EndRow, EndCol, Length, Phi)` |
| 3 | `get_parallels_xld` | 取出 XLD parallels 的首组端点几何信息(用于边缘对分析)。 | `get_parallels_xld (Parallels : : : Row1, Col1, Length1, Phi1, Row2, Col2, Length2, Phi2)` |
| 4 | `get_polygon_xld` | 取出 XLD 多边形的几何参数,每点附 (Row, Col, Length, Phi)。 | `get_polygon_xld (Polygon : : : Row, Col, Length, Phi)` |

### 3.2 Creation(12 ops)

| # | 算子 | 一句话功能 | HDevelop 关键签名 |
| - | ---- | -------- | ---------------- |
| 1 | `gen_circle_contour_xld` | 按圆心和半径生成一段/一整圈 XLD 圆弧或闭环圆。 | `gen_circle_contour_xld ( : ContCircle : Row, Column, Radius, StartPhi, EndPhi, PointOrder, Resolution : )` |
| 2 | `gen_contour_nurbs_xld` | 通过控制点和 NURBS 阶数生成一段 NURBS 开放轮廓。 | `gen_contour_nurbs_xld ( : Contour : Rows, Cols, Knots, Weights, Degree, MaxError, MaxDistance : )` |
| 3 | `gen_contour_polygon_rounded_xld` | 在多边形顶点处做圆角过渡,生成带圆角的多边形轮廓。 | `gen_contour_polygon_rounded_xld ( : Contour : Row, Col, Radius, SamplingInterval : )` |
| 4 | `gen_contour_polygon_xld` | 把一组有序顶点直接连接成 XLD 多边形(直线段拼接)。 | `gen_contour_polygon_xld ( : Contour : Row, Col : )` |
| 5 | `gen_contour_region_xld` | 把区域(region)边界抽取为 XLD 轮廓。 | `gen_contour_region_xld (Regions : Contours : Mode : )` |
| 6 | `gen_contours_skeleton_xld` | 对区域做骨架化,把骨架抽成 XLD 轮廓(细化中心线)。 | `gen_contours_skeleton_xld (Skeleton : Contours : Length, Mode : )` |
| 7 | `gen_cross_contour_xld` | 在指定 (Row, Column) 处生成一个十字形 XLD 标定标记。 | `gen_cross_contour_xld ( : Cross : Row, Col, Size, Angle : )` |
| 8 | `gen_ellipse_contour_xld` | 生成椭圆/椭圆弧 XLD 轮廓(控制点+长轴+短轴+倾角)。 | `gen_ellipse_contour_xld ( : ContEllipse : Row, Column, Phi, Radius1, Radius2, StartPhi, EndPhi, PointOrder, Resolution : )` |
| 9 | `gen_parallels_xld` | 沿 XLD 多边形等距偏移生成 parallels(用于边缘宽度测量)。 | `gen_parallels_xld (Polygons : Parallels : Len, Dist, Alpha, Merge : )` |
| 10 | `gen_polygons_xld` | 输入坐标点元组直接生成 XLD 多边形(批量)。 | `gen_polygons_xld (Contours : Polygons : Type, Alpha : )` |
| 11 | `gen_rectangle2_contour_xld` | 生成任意方向矩形(rectangle2 = 中心+长宽+倾角)的 XLD 轮廓。 | `gen_rectangle2_contour_xld ( : Rectangle : Row, Column, Phi, Length1, Length2 : )` |
| 12 | `mod_parallels_xld` | 通过灰度阈值提取并追踪边缘对,生成 parallels(配合 edges_image)。 | `mod_parallels_xld (Parallels, Image : ModParallels, ExtParallels : Quality, MinGray, MaxGray, MaxStandard : )` |

### 3.3 Features(45 ops)

| # | 算子 | 一句话功能 | HDevelop 关键签名 |
| - | ---- | -------- | ---------------- |
| 1 | `area_center_points_xld` | 把 XLD 轮廓/多边形当作点云,计算面积和质心(忽略闭合性)。 | `area_center_points_xld (XLD : : : Area, Row, Column)` |
| 2 | `area_center_xld` | 计算 XLD 轮廓或多边形的面积与质心(若闭合则按封闭区域积分)。 | `area_center_xld (XLD : : : Area, Row, Column, PointOrder)` |
| 3 | `circularity_xld` | 计算 XLD 形状的圆度 (4πA / P²),值越接近 1 越像圆。 | `circularity_xld (XLD : : : Circularity)` |
| 4 | `compactness_xld` | 计算 XLD 形状的紧致度(等周长下面积最大者)。 | `compactness_xld (XLD : : : Compactness)` |
| 5 | `contour_point_num_xld` | 返回 XLD 轮廓的总点数(用于长度/抽样裁剪)。 | `contour_point_num_xld (Contour : : : Length)` |
| 6 | `convexity_xld` | 凸度 = 凸包面积 / 实际面积,1 表示纯凸形。 | `convexity_xld (XLD : : : Convexity)` |
| 7 | `diameter_xld` | 最大两点距离(直径),即 XLD 形状的最长对角。 | `diameter_xld (XLD : : : Row1, Column1, Row2, Column2, Diameter)` |
| 8 | `dist_ellipse_contour_points_xld` | 逐点计算 XLD 轮廓到指定椭圆的最小距离序列。 | `dist_ellipse_contour_points_xld (Contour : : DistanceMode, ClippingEndPoints, Row, Column, Phi, Radius1, Radius2 : Distances)` |
| 9 | `dist_ellipse_contour_xld` | 计算 XLD 轮廓整体到指定椭形的几何距离均值/最大/最小。 | `dist_ellipse_contour_xld (Contours : : Mode, MaxNumPoints, ClippingEndPoints, Row, Column, Phi, Radius1, Radius2 : MinDist, MaxDist, AvgDist, SigmaDist)` |
| 10 | `dist_rectangle2_contour_points_xld` | 逐点计算 XLD 轮廓到任意方向矩形(rectangle2)的距离。 | `dist_rectangle2_contour_points_xld (Contour : : ClippingEndPoints, Row, Column, Phi, Length1, Length2 : Distances)` |
| 11 | `eccentricity_points_xld` | 把 XLD 形状当作点云,计算长短轴比(异形度)。 | `eccentricity_points_xld (XLD : : : Anisometry)` |
| 12 | `eccentricity_xld` | 由椭圆等效参数计算的形状异形度(主轴/副轴之比)。 | `eccentricity_xld (XLD : : : Anisometry, Bulkiness, StructureFactor)` |
| 13 | `elliptic_axis_points_xld` | 把 XLD 视作点云,估计等效椭圆的主/副半轴与方向。 | `elliptic_axis_points_xld (XLD : : : Ra, Rb, Phi)` |
| 14 | `elliptic_axis_xld` | 等效椭圆参数(Ra,Rb,Phi)+ 面积(环绕 XLD 形状拟合)。 | `elliptic_axis_xld (XLD : : : Ra, Rb, Phi)` |
| 15 | `fit_circle_contour_xld` | 用最小二乘把一组轮廓点拟合成圆(几何拟合,非区域面积)。 | `fit_circle_contour_xld (Contours : : Algorithm, MaxNumPoints, MaxClosureDist, ClippingEndPoints, Iterations, ClippingFactor : Row, Column, Radius, StartPhi, EndPhi, PointOrder)` |
| 16 | `fit_ellipse_contour_xld` | 用最小二乘将 XLD 轮廓拟合成椭圆/椭圆弧。 | `fit_ellipse_contour_xld (Contours : : Algorithm, MaxNumPoints, MaxClosureDist, ClippingEndPoints, VossTabSize, Iterations, ClippingFactor : Row, Column, Phi, Radius1, Radius2, StartPhi, EndPhi, PointOrder)` |
| 17 | `fit_line_contour_xld` | 把 XLD 多边形拆成 N 段直线(可剔除/裁剪异常段)。 | `fit_line_contour_xld (Contours : : Algorithm, MaxNumPoints, ClippingEndPoints, Iterations, ClippingFactor : RowBegin, ColBegin, RowEnd, ColEnd, Nr, Nc, Dist)` |
| 18 | `fit_rectangle2_contour_xld` | 把 XLD 轮廓拟合成任意方向的最小矩形(rectangle2)。 | `fit_rectangle2_contour_xld (Contours : : Algorithm, MaxNumPoints, MaxClosureDist, ClippingEndPoints, Iterations, ClippingFactor : Row, Column, Phi, Length1, Length2, PointOrder)` |
| 19 | `get_contour_angle_xld` | 逐点返回 XLD 轮廓切线方向角度(用于边缘方向匹配)。 | `get_contour_angle_xld (Contour : : AngleMode, CalcMode, Lookaround : Angles)` |
| 20 | `get_contour_attrib_xld` | 返回 XLD 轮廓某点处的局部属性(如 'gray' 边缘响应)。 | `get_contour_attrib_xld (Contour : : Name : Attrib)` |
| 21 | `get_contour_global_attrib_xld` | 返回 XLD 轮廓的全局属性(整条轮廓共有的全局键值)。 | `get_contour_global_attrib_xld (Contour : : Name : Attrib)` |
| 22 | `get_regress_params_xld` | 返回最近 fit_* 调用所得到的多项式参数(行列方向/直线段)。 | `get_regress_params_xld (Contours : : : Length, Nx, Ny, Dist, Fpx, Fpy, Lpx, Lpy, Mean, Deviation)` |
| 23 | `height_width_ratio_xld` | 由平行坐标轴方向最小包围盒,得到高/宽/纵横比。 | `height_width_ratio_xld (XLD : : : Height, Width, Ratio)` |
| 24 | `info_parallels_xld` | 查询 parallel 间的灰度值分布与梯度信息(明暗/对比度)。 | `info_parallels_xld (Parallels, Image : : : QualityMin, QualityMax, GrayMin, GrayMax, StandardMin, StandardMax)` |
| 25 | `length_xld` | 返回 XLD 轮廓或多边形总弧长。 | `length_xld (XLD : : : Length)` |
| 26 | `local_max_contours_xld` | 挑选 points with local maximum gray value(沿轮廓找局部极值)。 | `local_max_contours_xld (Contours, Image : LocalMaxContours : MinPercent, MinDiff, Distance : )` |
| 27 | `max_parallels_xld` | 把端点相邻属于同一多边形的 parallels 拼接(避免断线)。 | `max_parallels_xld (ExtParallels : MaxPolygons : : )` |
| 28 | `moments_any_points_xld` | 任意阶几何矩,把 XLD 当点云(忽略边界闭合)。 | `moments_any_points_xld (XLD : : Mode, Area, CenterRow, CenterCol, P, Q : M)` |
| 29 | `moments_any_xld` | 任意阶几何矩,沿闭合 XLD 轮廓(0~N 阶都可指定)。 | `moments_any_xld (XLD : : Mode, PointOrder, Area, CenterRow, CenterCol, P, Q : M)` |
| 30 | `moments_points_xld` | 经典二阶矩 M20/M02/M11,把 XLD 当点云。 | `moments_points_xld (XLD : : : M11, M20, M02)` |
| 31 | `moments_xld` | 经典二阶矩 M20/M02/M11,沿闭合轮廓积分。 | `moments_xld (XLD : : : M11, M20, M02)` |
| 32 | `orientation_points_xld` | 主轴方向(0~π),把 XLD 视作点云。 | `orientation_points_xld (XLD : : : Phi)` |
| 33 | `orientation_xld` | 主轴方向(0~π),沿闭合轮廓积分。 | `orientation_xld (XLD : : : Phi)` |
| 34 | `query_contour_attribs_xld` | 列出 XLD 轮廓上定义的所有局部属性名(用于通用属性查询)。 | `query_contour_attribs_xld (Contour : : : Attribs)` |
| 35 | `query_contour_global_attribs_xld` | 列出 XLD 轮廓上定义的所有全局属性名。 | `query_contour_global_attribs_xld (Contour : : : Attribs)` |
| 36 | `rectangularity_xld` | 矩形度 = XLD 面积 / 最小包围矩形面积。 | `rectangularity_xld (XLD : : : Rectangularity)` |
| 37 | `select_contours_xld` | 按长度/方向/闭合特征筛选 XLD 轮廓(批量过滤)。 | `select_contours_xld (Contours : SelectedContours : Feature, Min1, Max1, Min2, Max2 : )` |
| 38 | `select_shape_xld` | 按形状特征(面积/紧致度/矩…等)筛选 XLD 轮廓(同 select_shape 区域版)。 | `select_shape_xld (XLD : SelectedXLD : Features, Operation, Min, Max : )` |
| 39 | `select_xld_point` | 返回距指定 (row, col) 最近的 XLD 轮廓点索引。 | `select_xld_point (XLDs : DestXLDs : Row, Column : )` |
| 40 | `smallest_circle_xld` | 包围 XLD 轮廓的最小外接圆(中心+半径)。 | `smallest_circle_xld (XLD : : : Row, Column, Radius)` |
| 41 | `smallest_rectangle1_xld` | 轴对齐最小外接矩形(rectangle1,8 个返回值)。 | `smallest_rectangle1_xld (XLD : : : Row1, Column1, Row2, Column2)` |
| 42 | `smallest_rectangle2_xld` | 任意方向最小外接矩形(rectangle2,4 参数:中心+长宽+倾角)。 | `smallest_rectangle2_xld (XLD : : : Row, Column, Phi, Length1, Length2)` |
| 43 | `test_closed_xld` | 判断 XLD 轮廓首尾是否重合(是否闭合)。 | `test_closed_xld (XLD : : : IsClosed)` |
| 44 | `test_self_intersection_xld` | 判断 XLD 轮廓自相交测试(返回是否自交以及交点数)。 | `test_self_intersection_xld (XLD : : CloseXLD : DoesIntersect)` |
| 45 | `test_xld_point` | 判断指定 (Row, Column) 是否在任意 XLD 轮廓上(边缘命中测试)。 | `test_xld_point (XLD : : Row, Column : IsInside)` |

## 4. 跨算子误区 & 调试提示

- **XLD 必须闭合才能正确算面积**:`area_center_xld` 用格林公式,断开轮廓面积不收敛。用 `test_closed_xld` 预检;若不闭合,用 `gen_contour_polygon_xld`(输入首尾重合)或 `clip_contours_xld`(下卷)取闭合段。
- **`_points` 后缀对偶**:`area_center_xld` 与 `area_center_points_xld` 的差别是后者忽略闭合性、退化为纯点云结果——若输入是有序散点而非闭合轮廓,选 `_points` 版。矩/方向/椭圆 全部有此对偶。
- **smallest_rectangle2_xld 的 Length1/2 是半轴**:不是完整边长,完整短/长边 = `Length1*2` / `Length2*2`。Phi 是 -π/2 ~ π/2 弧度,与 gen_rectangle2_contour_xld 兼容。
- **`fit_line_contour_xld` 不抗噪**:原始 `regression` 模式对离群点敏感,先 `select_shape_xld` 按长度过滤,或用 `ClipLineEndpoints='auto'` 截断端点。
- **`gen_parallels_xld` 与 `edges_image` 强绑定**:`GenName='gradient'` 模式必须先对原图做 `edges_image`;否则 parallels 为空。'regression' 模式要求 polygon 来自 `gen_contour_polygon_xld` 之类的有序点列。
- **`fit_circle_contour_xld` 的算法选择**:`'pratt-huber'` 是工业默认(抗 50% 噪声),`'algebraic'` 最快但受噪声扰动。Radius 与图像单位挂钩,缩放/标定后要乘以 scale。
- **`select_shape_xld` 的特征名表**:同 region 版不通用,需查 XLD 专属特征名(见 NOTES 的几个典型)。

## 5. 调用链路与组合用法(3 段 HDevelop 伪代码)

### 5.1 PCB 走线宽度测量:`edges_image → gen_parallels_xld → fit_line_contour_xld`

```hdevelop
* 1. 读图像(略)
read_image(Image, 'pcb_board.png')

* 2. 边缘提取
edges_image(Image, ImaAmp, ImaDir, 'canny', 1, 'nms', 20, 40)

* 3. 平行边缘带
gen_parallels_xld(ImaAmp, Border, 'gradient', 'true', 'true', 'true', 'true', 1, 'true', Parallels)

* 4. 多段线拟合并测量宽度
fit_line_contour_xld(Parallels, 'regression', 12, -1, 5, 2, _, _, _, _, _, Lengths, _)
* Lengths 是 candidate 'line widths'
select_contours_xld(Parallels, Selected, 'lines', 50, 100, 0.5, 3)
```

### 5.2 圆度判定的金标准:`gen_contour_region_xld → fit_circle_contour_xld → circularity_xld`

```hdevelop
* 1. 二值化得 region
threshold(Image, Region, 128, 255)
connection(Region, Connected)
select_shape(Connected, Coin, ['area','circularity'], 'and', [200, 0.5], [4000, 1.0])

* 2. region 桥到 XLD
gen_contour_region_xld(Coin, Contours, 'border_holes')

* 3. 圆拟合
fit_circle_contour_xld(Contours, 'algebraic', -1, 0, 0, 1, 0, 0, Row, Column, Radius, _, _, _)

* 4. 自定义圆度(基于拟合残差)
circularity_xld(Contours, Circ)
* 经验阈值:Circ > 0.95 视为正圆
```

### 5.3 任意方向矩形标记与配准:`smallest_rectangle2_xld → matrix_to_hom_mat2d → affine_trans_contour_xld`

```hdevelop
* 1. 提取候选轮廓并外接带方向矩形
select_contours_xld(AllXLD, Tgt, 'contour_length', 60, 99999)
smallest_rectangle2_xld(Tgt, CRow, CCol, Phi, L1, L2)

* 2. 构造 2D 齐次矩阵:将轮廓摆正(旋转 -Phi、平移到 (0,0))
vector_angle_to_rigid(CRow, CCol, Phi, 0, 0, 0, HomMat2D)

* 3. 仿射变换回写
affine_trans_contour_xld(Tgt, Aligned, HomMat2D)
* (affine_trans_contour_xld 属 Geometric Transformations 卷,本卷作预告)
```

## 6. 与其它章节的关联

- **第 22 章 Regions**:region → XLD 的唯一正向上桥是 `gen_contour_region_xld`;XLD → region 可走 `gen_region_contour_xld`(Trans 卷)。
- **第 24 章 System / Sockets**:Access 家族(`get_*_xld`)使 XLD 数据能导出到 HDevelop 外部(配合 HTuple -> socket 协议)。
- **第 25 章 Tools(Geometry 卷)**:`smallest_*_xld` 系列与 `smallest_circle/rectangle1/rectangle2` 区域版逻辑同根,可交叉处理 region 与 XLD。
- **第 26 章 Transformations(上)**:`affine_trans_contour_xld` 等是 XLD 的几何变换入口,与本章 Smallest*、Fit* 联用做配准。
- **第 17 章 Matching**:Component-Based 与 Descriptor-Based 模板都返回 XLD 轮廓;`fit_circle/ellipse_contour_xld` 等可对模板投影点精化拟合。
- **第 16 章 Inspection**:典型的 Defect 检测 pipeline = edges_image → gen_parallels → fit_line + smallest_rectangle2 → select_shape_xld。

## 7. 一句话核心要义

上卷把 XLD 完整定义了一遍:**Access 让你掏出数据、Creation 让你按需造形、Features 让你量度一切**。脱离这三组,XLD 只是个空容器,有了这三组,任何 sub-pixel 测量/识别/配准的应用才有了可调用的根基。
