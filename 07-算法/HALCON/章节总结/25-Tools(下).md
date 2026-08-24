# 第 25 章 Tools · 下卷：图像几何增强与拼接（29 算子 · 5 子族）

> HALCON '图像域几何增强' 全套收尾 —— 网格校正 / 霍夫变换 / 散点插值 / 直线属性 / 图像拼接 5 子族。从 '棋盘格拉正' 到 '360° 全景合成',从 '圆孔检测' 到 'RANSAC 鲁棒配准' —— 这是把'单张照片'变成'可测量、可拼接、可重建'的关键工具链,广泛应用于: 文档扫描、大幅面质检、全景监控、医学/遥感影像融合、机器人地图构建等。

---

## 1. 全卷结构：5 子族总览

| 子族 | 算子数 | 一句话功能 | 典型场景 |
|---|---|---|---|
| **① Grid Rectification 网格校正** | 5 | 镜头畸变+透视倾斜双重校正，把歪斜网格拉正为正交正视图 | 文档扫描、电路板/瓶盖质检、大幅面标定 |
| **② Hough 霍夫变换** | 7 | 把图像空间的线/圆映射到参数空间累加，用峰值鲁棒检测全局几何结构 | 车道线、表格线、圆孔/焊点检测 |
| **③ Interpolation 散点插值** | 5 | 给非规则采样的散点建立连续函数，支持任意位置求值并栅格化成图像 | 地形/温度场重建、3D 残差可视化、点云→图像 |
| **④ Lines 直线属性** | 2 | 从直线两端点算方向角与中点/长度，几何决策的基础量 | 方向对齐、尺寸测量、姿态估计 |
| **⑤ Mosaicking 图像拼接** | 10 | 多视角图像配准+变换融合成一张大图/全景，支持投影/球面/立方贴图 | 大幅面拼接、360° 全景、多相机融合 |

**与上下卷的分工**：
- **上卷** = HALCON 的'数学小工具'（背景估计 7 + 1D 函数 25 = 32 算子）
- **中卷** = HALCON 的'几何度量与空间求解'（42 算子）—— 距离变换 + 测距 + 角度 + 求交 + 面积
- **下卷（本卷）** = HALCON 的'图像域几何增强与拼接'（29 算子）—— 网格校正 + 霍夫 + 散点插值 + 直线属性 + 图像拼接

**全章收官**：8 子族 103 算子（上 32 + 中 42 + 下 29）全部完成。

---

### ① Grid Rectification 网格校正（5 算子）

**核心思想**：用已知网格（如棋盘格）作为参照，估计镜头径向畸变 + 透视变换，把扭曲图像校正为正交正视图，从而能在正视图上精确量尺寸。
**典型用途**：文档/票据扫描、PCB/瓶盖质检（需正视图量距）、大幅面相机标定、畸变预补偿。
**算法族**：create_rectification_grid（造标准网格）→ find_rectification_grid（在图中定位网格点）→ connect_grid_points（把点连成 XLD 轮廓）→ gen_grid_rectification_map / gen_arbitrary_distortion_map（生成像素重映射图）。

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **connect_grid_points** | 把网格交点按拓扑顺序连接成 XLD 轮廓（网格点→连续轮廓） · `connect_grid_points ( Image : ConnectingLines : Row , Column , Sigma , MaxDist : )` |
| **create_rectification_grid** | 创建一个标准校正网格（指定行数/列数/间距，作为畸变参考） · `create_rectification_grid ( : : Width , NumSquares , GridFile : )` |
| **find_rectification_grid** | 在图像中自动定位校正网格，返回所有网格点的行列坐标 · `find_rectification_grid ( Image : GridRegion : MinContrast , Radius : )` |
| **gen_arbitrary_distortion_map** | 由任意给定的映射点（非网格）生成像素重映射图，实现手动畸变校正 · `gen_arbitrary_distortion_map ( : Map : GridSpacing , Row , Column , GridWidth , ImageWidth , ImageHeight , MapType : )` |
| **gen_grid_rectification_map** | 使用定位到的网格点生成透视/畸变校正映射图（网格→正视图） · `gen_grid_rectification_map ( Image , ConnectingLines : Map , Meshes : GridSpacing , Rotation , Row , Column , MapType : )` |

#### ★ gen_grid_rectification_map — 使用定位到的网格点生成透视/畸变校正映射图（网格→正视图）
用途：镜头畸变 + 透视倾斜的双重校正，把歪斜的网格区域拉正为正交视图（如瓶盖、电路板、文档扫描）。
参数：GridRows/GridColumns 网格点坐标 + 期望输出尺寸，返回 MappingMap（配合 map_image 使用）。
误区：网格点必须按 create_rectification_grid 的顺序排列，乱序会映射出乱码；先 find 再 gen，两步缺一不可。

---

### ② Hough 霍夫变换（7 算子）

**核心思想**：将'边缘存在性'投票到参数空间（ρ-θ 或 中心-半径），共线/共圆的点在参数空间同一位置累加形成峰值，因此抗噪远强于直接拟合。
**典型用途**：车道线/表格线提取、圆孔/焊点/引脚检测、工业件几何定位。
**算法族**：hough_*_trans（投票到参数空间）+ hough_*（峰值→几何对象）+ hough_line_trans_dir / hough_lines_dir（带边缘方向加权，减少假峰）。

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **hough_circle_trans** | 圆霍夫变换：把图像累加进 (中心x,中心y,半径) 三维参数空间 · `hough_circle_trans ( Region : HoughImage : Radius : )` |
| **hough_circles** | 从圆霍夫累加空间中提取峰值，得到圆（无需 edge 子像素） · `hough_circles ( RegionIn : RegionOut : Radius , Percent , Mode : )` |
| **hough_line_trans** | 标准直线霍夫变换：图像→(ρ,θ) 累加空间 · `hough_line_trans ( Region : HoughImage : AngleResolution : )` |
| **hough_line_trans_dir** | 带方向加权直线霍夫变换（用边缘梯度方向约束投票） · `hough_line_trans_dir ( ImageDir : HoughImage : DirectionUncertainty , AngleResolution : )` |
| **hough_lines** | 从霍夫空间提取直线，返回线段端点坐标 · `hough_lines ( RegionIn : : AngleResolution , Threshold , AngleGap , DistGap : Angle , Dist )` |
| **hough_lines_dir** | 从带方向的霍夫空间提取直线（精度更高、抗噪更强） · `hough_lines_dir ( ImageDir : HoughImage , Lines : DirectionUncertainty , AngleResolution , Smoothing , FilterSize , Threshold , AngleGap , DistGap , GenLines : Angle , Dist )` |
| **select_matching_lines** | 在霍夫空间中按几何约束筛选/合并匹配的直线 · `select_matching_lines ( RegionIn : RegionLines : AngleIn , DistIn , LineWidth , Thresh : AngleOut , DistOut )` |

#### ★ hough_line_trans — 标准直线霍夫变换：图像→(ρ,θ) 累加空间
用途：把'边缘存在性'投影到 ρ-θ 参数空间，共线点会在同一 (ρ,θ) 处累加，抗噪强于直接拟合。
参数：HoughImage(0/1 边缘图) + 角度分辨率 + 距离分辨率，返回带峰值的 Hough 空间图。
误区：输入必须是二值边缘图（用 edges_image/threshold 预处理），原始灰度图直接喂会全糊。

#### ★ hough_lines — 从霍夫空间提取直线，返回线段端点坐标
用途：hough_line_trans 的'后处理'——在累加空间找局部峰值，反算回图像中的直线端点。
参数：输入 Hough 空间图 + 阈值，返回 LinesRow1/Col1/Row2/Col2 端点。
误区：阈值过低会吐出大量噪声线段；配合 hough_line_trans_dir 可大幅减少假峰。

---

### ③ Interpolation 散点插值（5 算子）

**核心思想**：输入一组非规则 (x,y,z) 散点，用 Radial Basis / 薄板样条 / 反距离权重等方法建立连续函数，之后可对任意坐标求值，或整张栅格化成图像。
**典型用途**：地形/温度场/曲率场重建、3D 测量残差可视化、散点云转规则网格。
**算法族**：create_scattered_data_interpolator（建模型）+ interpolate_scattered_data / _image / _points_to_image（求值/成图）+ clear_scattered_data_interpolator（释放）。

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **clear_scattered_data_interpolator** | 释放散点插值器句柄（清理内存） · `clear_scattered_data_interpolator ( : : ScatteredDataInterpolatorHandle : )` |
| **create_scattered_data_interpolator** | 创建散点数据插值器（Radial Basis / 反距离权重等） · `create_scattered_data_interpolator ( : : Method , Rows , Columns , Values , GenParamName , GenParamValue : ScatteredDataInterpolatorHandle )` |
| **interpolate_scattered_data** | 对散点插值器在给定坐标处求函数值 · `interpolate_scattered_data ( : : ScatteredDataInterpolatorHandle , Row , Column : ValueInterpolated )` |
| **interpolate_scattered_data_image** | 把散点插值结果直接写成一张规则图像 · `interpolate_scattered_data_image ( Image , RegionInterpolate : ImageInterpolated : Method , GenParamName , GenParamValue : )` |
| **interpolate_scattered_data_points_to_image** | 把一组散点投影到图像网格完成插值（散点→图像） · `interpolate_scattered_data_points_to_image ( : ImageInterpolated : Method , Rows , Columns , Values , Width , Height , GenParamName , GenParamValue : )` |

#### ★ create_scattered_data_interpolator — 创建散点数据插值器（Radial Basis / 反距离权重等）
用途：给一组'非规则采样'的 (x,y,z) 散点建立连续函数，之后可对任意位置求值（地形、温度场、3D 重建残差）。
参数：散点坐标 + 方法('radial_basis_function'/'thin_plate_splines'/'inverse_distance' 等) + 平滑因子。
误区：方法选错会过拟合/欠拟合；点数太少（<3）无法建 RBF 模型；outlier 会严重扭曲整个场。

---

### ④ Lines 直线属性（2 算子）

**核心思想**：基于已提取的直线端点，计算其方向角（带符号）与几何中心/长度，是后续对齐、测量、姿态估计的基础量。
**典型用途**：工件方向判定、尺寸测量、抓取姿态估计、角度公差判定。
**算法族**：line_orientation（方向角，带符号 -π/2~π/2）+ line_position（中点+长度+方向，信息更全）。

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **line_orientation** | 计算直线的方向角（带符号，范围 -π/2 ~ π/2） · `line_orientation ( : : RowBegin , ColBegin , RowEnd , ColEnd : Phi )` |
| **line_position** | 计算直线的中点、长度与方向（比 line_orientation 信息更全） · `line_position ( : : RowBegin , ColBegin , RowEnd , ColEnd : RowCenter , ColCenter , Length , Phi )` |

#### ★ line_orientation — 计算直线的方向角（带符号，范围 -π/2 ~ π/2）
用途：判断一条线的'指向'——比 angle_ll 多了符号信息（区分 0° 与 180°）。
参数：输入两端点 Row1/Col1/Row2/Col2，返回 Phi（弧度，右手系 y 向下）。
误区：角度是相对图像行方向（水平）的夹角，注意图像 y 轴向下，与数学坐标相反。

---

### ⑤ Mosaicking 图像拼接（10 算子）

**核心思想**：先在两图重叠区用 RANSAC 鲁棒估计投影/畸变变换矩阵（剔除误匹配），再把各图投影到参考平面融合；支持平面投影、球面、立方贴图及光束法平差联合优化。
**典型用途**：大幅面/长卷拼接、360° 环视全景、多相机立面融合、航空/卫星影像拼接。
**算法族**：proj_match_points_ransac（含 _guided / _distortion 变体）做配准 → gen_*_mosaic（projective/spherical/cube/bundle_adjusted）做融合 → adjust / bundle_adjust 做全局优化。

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **adjust_mosaic_images** | 对拼接图像做全局微调对齐（优化重叠区一致性） · `adjust_mosaic_images ( Images : CorrectedImages : From , To , ReferenceImage , HomMatrices2D , EstimationMethod , EstimateParameters , OECFModel : )` |
| **bundle_adjust_mosaic** | 光束法平差：多图联合优化相机/映射参数，最小化重投影误差 · `bundle_adjust_mosaic ( : : NumImages , ReferenceImage , MappingSource , MappingDest , HomMatrices2D , Rows1 , Cols1 , Rows2 , Cols2 , NumCorrespondences , Transformation : MosaicMatrices2D , Rows , Cols , Error )` |
| **gen_bundle_adjusted_mosaic** | 生成光束法平差优化后的拼接全景图 · `gen_bundle_adjusted_mosaic ( Images : MosaicImage : HomMatrices2D , StackingOrder , TransformDomain : TransMat2D )` |
| **gen_cube_map_mosaic** | 生成立方体贴图拼接（6 面立方展开） · `gen_cube_map_mosaic ( Images : Front , Rear , Left , Right , Top , Bottom : CameraMatrices , RotationMatrices , CubeMapDimension , StackingOrder , Interpolation : )` |
| **gen_projective_mosaic** | 用投影变换把多图拼成一张无缝大图 · `gen_projective_mosaic ( Images : MosaicImage : StartImage , MappingSource , MappingDest , HomMatrices2D , StackingOrder , TransformDomain : MosaicMatrices2D )` |
| **gen_spherical_mosaic** | 生成球面（全景）拼接图（适用于 360° 环视） · `gen_spherical_mosaic ( Images : MosaicImage : CameraMatrices , RotationMatrices , LatMin , LatMax , LongMin , LongMax , LatLongStep , StackingOrder , Interpolation : )` |
| **proj_match_points_distortion_ransac** | RANSAC 估计带畸变模型的投影匹配点（相机标定级精度） · `proj_match_points_distortion_ransac ( Image1 , Image2 : : Rows1 , Cols1 , Rows2 , Cols2 , GrayMatchMethod , MaskSize , RowMove , ColMove , RowTolerance , ColTolerance , Rotation , MatchThreshold , EstimationMethod , DistanceThreshold , RandSeed : HomMat2D , Kappa , Error , Points1 , Points2 )` |
| **proj_match_points_distortion_ransac_guided** | 带初始引导的 RANSAC 畸变匹配（加速收敛） · `proj_match_points_distortion_ransac_guided ( Image1 , Image2 : : Rows1 , Cols1 , Rows2 , Cols2 , GrayMatchMethod , MaskSize , HomMat2DGuide , KappaGuide , DistanceTolerance , MatchThreshold , EstimationMethod , DistanceThreshold , RandSeed : HomMat2D , Kappa , Error , Points1 , Points2 )` |
| **proj_match_points_ransac** | RANSAC 估计投影（单应）匹配点（标准配准） · `proj_match_points_ransac ( Image1 , Image2 : : Rows1 , Cols1 , Rows2 , Cols2 , GrayMatchMethod , MaskSize , RowMove , ColMove , RowTolerance , ColTolerance , Rotation , MatchThreshold , EstimationMethod , DistanceThreshold , RandSeed : HomMat2D , Points1 , Points2 )` |
| **proj_match_points_ransac_guided** | 带初始引导的 RANSAC 投影匹配（更快更稳） · `proj_match_points_ransac_guided ( Image1 , Image2 : : Rows1 , Cols1 , Rows2 , Cols2 , GrayMatchMethod , MaskSize , HomMat2DGuide , DistanceTolerance , MatchThreshold , EstimationMethod , DistanceThreshold , RandSeed : HomMat2D , Points1 , Points2 )` |

#### ★ gen_projective_mosaic — 用投影变换把多图拼成一张无缝大图
用途：把同一平面（如大幅海报、墙面、地面）从不同视角拍的多张图，统一投影到参考平面合成一张正视图。
参数：输入各图 + 重叠区匹配点（来自 proj_match_points_ransac 系列）+ 参考图索引，返回 MosaicImage。
误区：被拍物体必须近似共面；非平面场景用球面/柱状拼接（gen_spherical_mosaic）更合适。

#### ★ proj_match_points_distortion_ransac — RANSAC 估计带畸变模型的投影匹配点（相机标定级精度）
用途：拼接/配准的核心——在两张图重叠区找匹配点并用 RANSAC 鲁棒估计'投影+径向畸变'变换矩阵，剔除误匹配。
参数：两张图的匹配点(行/列) + 畸变阶数，返回变换矩阵 HomMat2D + 内点。
误区：重叠区至少要 4 对不共线点；畸变阶数设太高会把噪声当畸变，设太低校正不干净。

---
