# 第 22 章 Regions · 上卷 —— 二值区域的「看、造、算、判」

> **HALCON 20.11.1.0 · 第 22 章 Regions · 上卷 · 35 算子 · 4 族**
>
> 主题：Iconic Region 元组的**查询 / 创建 / 集合论 / 断言**——一切区域分析的脚手架
>
> 📌 **全章 7 族 104 ops**，本章按语义切三卷：
> - **上卷**（35 ops，本篇）：Access 5 + Creation 21 + Sets 6 + Tests 3 = 「看+造+集合论+断言」基础四件套
> - **中卷**（40 ops）：Features 40 = 「测量」整章（面积/圆度/矩/Hamming 距离/形状选择...）
> - **下卷**（29 ops）：Geometric Transformations 8 + Transformations 21 = 「几何变换 + 形状变化」

---

## §1 章节定位

`Region`（区域）是 HALCON 中最重要的二值掩模数据结构——一个 Region = 一组图像像素的集合。本章上卷给出 Region 元组的"基本操作"四件套：

| 维度 | 算子族 | 类比 Python/数学 |
| --- | --- | --- |
| **看（Access）** | 5 | `numpy.where`、`list(Region)` —— 把 Region 转成坐标 / 轮廓 / 凸包 |
| **造（Creation）** | 21 | `np.zeros`、`cv2.circle`、`cv2.rectangle` —— 凭空生成几何形状 |
| **集合论（Sets）** | 6 | 布尔运算 `A∪B`、`A∩B`、`A−B`、`¬A`、`A⊕B` —— Region 的算术 |
| **断言（Tests）** | 3 | `assert`、`isinstance` —— 判断两个 Region 是否相等 / 子集 / 包含点 |

为什么上卷是"脚手架"？因为所有特征提取（中卷）和形状变换（下卷）都以这些基础操作为前提。

---

## §2 四族速览

| 族 | ops | 核心抽象 | 关键算子 | 适用条件 |
| --- | ---: | --- | --- | --- |
| **Access** | 5 | Region → 其他数据表示 | `get_region_points` / `get_region_runs` | 调试 / Region 转 XLD / Region 转 tuple |
| **Creation** | 21 | 元数据 → Region | `gen_circle` / `gen_rectangle2` / `gen_random_region` | 凭空造几何 / 标注 / 测试 |
| **Sets** | 6 | Region 集合论 | `union1` / `intersection` / `difference` | 二值掩模组合 / ROI 拼接 / Mask 相减 |
| **Tests** | 3 | Region 关系判定 | `test_equal_region` / `test_subset_region` | 单元测试 / 元组关系检查 |

合计 **35 ops**（≤60，上卷未切分）。

---

## §3 四角辐射思维导图

![22-Regions(上) Mind Map](22-Regions(上).png)

中心 `Regions` 焦点圆（深空蓝）显示 `第 22 章 · 上卷 · 35 算子`，四张子卡四角辐射：
- 左上 `01 Access` 钢蓝（5 ops）
- 右上 `02 Creation` 翠绿（21 ops）
- 左下 `03 Sets` 琥珀金（6 ops）
- 右下 `04 Tests` 玫瑰红（3 ops）

每族一组双重轨道连线（粗 + 细），从中心焦点圆辐射到四角。

---

## §4 四族详解

### 4.1 Access（5 算子）—— "Region → 其他表示"

Region 在 HALCON 内部用行程编码（run-length encoding）存储。本族算子把它**解码**为外部可见的其他数据结构（点、轮廓、凸包、多边形、行程）。

#### 4.1.1 算子清单与流水线

| 算子 | 一句话功能 | HDevelop 关键签名 | 典型用途 |
| --- | --- | --- | --- |
| `get_region_contour` | Region 边界 → `(Rows, Columns)` 像素坐标序列 | `get_region_contour(Region : : : Rows, Columns)` | 提取边界像素 |
| `get_region_convex` | Region 凸包 → 多边形 `(Rows, Columns)` | `get_region_convex(Region : : : Rows, Columns)` | 凸包拟合 / 简化 |
| `get_region_points` | Region 所有像素 → `(Rows, Columns)` | `get_region_points(Region : : : Rows, Columns)` | 像素级遍历 / 调试 |
| `get_region_polygon` | Region 边界 → 近似多边形（Douglas-Peucker） | `get_region_polygon(Region : : Tolerance : Rows, Columns)` | 用更少顶点近似边界 |
| `get_region_runs` | Region → 行程编码 `(Row, ColumnBegin, ColumnEnd)` | `get_region_runs(Region : : : Row, ColumnBegin, ColumnEnd)` | 提取行程 / 调试内部表示 |

#### 4.1.2 典型流水线

```hdevelop
* 从 Region 提取所有像素 → 用 tuple 函数做后续处理
get_region_points (Region, Rows, Columns)
* Rows 和 Columns 是等长 tuple，可统计像素数
tuple_length (Rows, NumPixels)
```

#### 4.1.3 误区

| 误区 | 正确做法 |
| --- | --- |
| 把 `get_region_polygon` 当凸包 | 它是 **Douglas-Peucker 近似**，不是凸包；凸包要用 `get_region_convex` |
| `get_region_points` 处理大 Region 性能差 | 大 Region 用 `get_region_runs`（行程编码更高效） |

### 4.2 Creation（21 算子）—— "凭空造几何"

21 算子按"几何来源"分组：**基础几何 5**（圆/椭圆/矩形）+ **派生 3**（环/扇形/网格）+ **从数据造 8**（从坐标/行程/XLD/label 图）+ **空集与随机 5**（空/随机/点列）。

#### 4.2.1 基础几何（5 算子）

| 算子 | 一句话功能 | HDevelop 关键签名 | 几何参数 |
| --- | --- | --- | --- |
| `gen_circle` | 一个或多个**整圆** | `gen_circle(: Circle : Row, Column, Radius :)` | 圆心 + 半径 |
| `gen_circle_sector` | **扇形/圆环扇形** | `gen_circle_sector(: CircleSector : Row, Column, Radius, StartAngle, EndAngle :)` | 圆心 + 半径 + 起止角（度） |
| `gen_ellipse` | **椭圆** | `gen_ellipse(: Ellipse : Row, Column, Phi, Radius1, Radius2 :)` | 中心 + 角度 + 长短半径 |
| `gen_ellipse_sector` | **椭圆扇形** | `gen_ellipse_sector(: EllipseSector : Row, Column, Phi, Radius1, Radius2, StartAngle, EndAngle :)` | 同上 + 起止角 |
| `gen_rectangle1` | **轴对齐矩形** | `gen_rectangle1(: Rectangle : Row1, Column1, Row2, Column2 :)` | 左上 + 右下两点 |
| `gen_rectangle2` | **任意角度矩形** | `gen_rectangle2(: Rectangle : Row, Column, Phi, Length1, Length2 :)` | 中心 + 角度 + 半长 + 半宽 |

#### 4.2.2 派生几何（3 算子）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `gen_checker_region` | **棋盘格 Region**（测试/标定用） | `gen_checker_region(: RegionChecker : WidthRegion, HeightRegion, WidthPattern, HeightPattern :)` |
| `gen_grid_region` | **网格线**或**网格点** | `gen_grid_region(: RegionGrid : RowSteps, ColumnSteps, Type, Width, Height :)` |
| `gen_region_hline` | **Hesse 法式直线**（带方向/距离） | `gen_region_hline(: Regions : Orientation, Distance :)` |

#### 4.2.3 从数据造（8 算子）

| 算子 | 一句话功能 | HDevelop 关键签名 | 数据源 |
| --- | --- | --- | --- |
| `gen_region_points` | 从像素坐标造 Region | `gen_region_points(: Region : Rows, Columns :)` | `(Rows, Columns)` tuple |
| `gen_region_line` | 从线段造 Region | `gen_region_line(: RegionLines : BeginRow, BeginCol, EndRow, EndCol :)` | 线段端点 |
| `gen_region_polygon` | 从折线造空心多边形 | `gen_region_polygon(: Region : Rows, Columns :)` | 折线坐标 |
| `gen_region_polygon_filled` | 从折线造**填充**多边形 | `gen_region_polygon_filled(: Region : Rows, Columns :)` | 同上 |
| `gen_region_polygon_xld` | 从 XLD 多边形造 Region | `gen_region_polygon_xld(Polygon : Region : Mode :)` | XLD 多边形句柄 |
| `gen_region_contour_xld` | 从 XLD 轮廓造 Region | `gen_region_contour_xld(Contour : Region : Mode :)` | XLD 轮廓句柄 |
| `gen_region_runs` | 从行程编码造 Region | `gen_region_runs(: Region : Row, ColumnBegin, ColumnEnd :)` | 行程三元组 |
| `gen_region_histo` | 从直方图造 Region | `gen_region_histo(: Region : Histogram, Row, Column, Scale :)` | 灰度直方图 |

#### 4.2.4 空集与随机（5 算子）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `gen_empty_region` | 创建空 Region | `gen_empty_region(: EmptyRegion :)` |
| `gen_random_region` | 全图随机像素 Region | `gen_random_region(: RegionRandom : Width, Height :)` |
| `gen_random_regions` | **多个随机形状**（圆/矩/椭圆） | `gen_random_regions(: Regions : Type, WidthMin, WidthMax, HeightMin, HeightMax, Density, Seed :)` |
| `label_to_region` | 从 label 图转 Region 元组 | `label_to_region(LabelImage : Regions :)` |
| `gen_region_*` （其他 4 个见 4.2.3） | —— | —— |

#### 4.2.5 典型流水线：构造测试模板

```hdevelop
* 用基础几何 + 集合论造一个 L 形测试 Region
gen_rectangle1 (Rect1, 10, 10, 100, 30)
gen_rectangle1 (Rect2, 10, 10, 30, 100)
union1 ([Rect1, Rect2], LShape)
```

#### 4.2.6 误区

| 误区 | 正确做法 |
| --- | --- |
| `gen_circle` 的 `Radius` 用整数 | HALCON 允许 HTuple（自动转 int/float），但建议显式 `real(R)` |
| `gen_rectangle2` 的角度用度 | **用弧度**（HALCON 几何算子统一用弧度） |
| `gen_region_polygon` 与 `gen_region_polygon_filled` 互换 | 前者造**边界**（1 像素宽），后者造**填充**多边形 |

### 4.3 Sets（6 算子）—— "Region 的布尔算术"

6 算子是 Region 的集合论根基，对应数学 `A∪B / A∩B / A−B / A⊕B / ¬A`。

#### 4.3.1 算子清单

| 算子 | 集合论符号 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- | --- |
| `union1` | `∪A` | 多 Region 合并成单个 Region | `union1(Region : RegionUnion :)` |
| `union2` | `A ∪ B` | 两元组 Region 逐对合并 | `union2(Region1, Region2 : RegionUnion :)` |
| `intersection` | `A ∩ B` | 两元组逐对求交 | `intersection(Region1, Region2 : RegionIntersection :)` |
| `difference` | `A − B` | 两元组逐对求差 | `difference(Region, Sub : RegionDifference :)` |
| `symm_difference` | `A ⊕ B` | 对称差 `(A∪B) − (A∩B)` | `symm_difference(Region1, Region2 : RegionDifference :)` |
| `complement` | `¬A`（相对 ROI） | Region 补集（限制在 `'clip_region'` 或 image domain 内） | `complement(Region : RegionComplement :)` |

#### 4.3.2 9 种典型用法

```hdevelop
* 1. 多个 ROI 合并成一个
union1 (ROIs, CombinedROI)

* 2. 两个 mask 求交集（仅保留共同区域）
intersection (Mask1, Mask2, CommonMask)

* 3. 减去已知背景
difference (Foreground, Background, PureForeground)

* 4. XOR 抠图（对称差）
symm_difference (ImageA, ImageB, SymMask)

* 5. 反转 ROI（在 image domain 内取反）
complement (ROI, InverseROI)
```

#### 4.3.3 `union1` 与 `union2` 的关键区别

| 算子 | 输入 | 输出 | 类比 |
| --- | --- | --- | --- |
| `union1` | 一个 Region 元组（含 N 个） | 单个 Region（所有 N 个合并） | `sum(tuple)` |
| `union2` | 两个 Region 元组（A、B） | 元组（C[i] = A[i] ∪ B[i]） | `tuple_add` |

#### 4.3.4 `complement` 的关键参数

`complement` 受系统标志 `'clip_region'` 影响：
- `'clip_region' = 'true'`：补集被裁剪到 image domain 内（默认）
- `'clip_region' = 'false'`：补集是"全局无限大"（不推荐，可能 OOM）

#### 4.3.5 误区

| 误区 | 正确做法 |
| --- | --- |
| `union2(A,B)` 想合并成一个 Region | 用 `union1` 或 `concat_obj(A,B,Tmp) → union1(Tmp, X)` |
| `difference(A, B)` 期望单点删除 | 集合差是 A 中**所有**与 B 任一元素"逻辑相等"的部分 |
| `symm_difference` 期望 A∪B | 它是 A∪B − A∩B（去掉公共部分） |

### 4.4 Tests（3 算子）—— "断言 / 比较"

3 算子是 Region 元组的关系断言，**纯函数**（无副作用），返回布尔值。

#### 4.4.1 算子清单

| 算子 | 判定 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- | --- |
| `test_equal_region` | `A == B`？ | 元组逐元素比较（像素级严格相等） | `test_equal_region(Regions1, Regions2 : : : IsEqual)` |
| `test_subset_region` | `A ⊆ B`？ | Region1 是否 Region2 的子集 | `test_subset_region(Region1, Region2 : : : IsSubset)` |
| `test_region_point` | `(r, c) ∈ A`？ | 测试点是否在 Region 内 | `test_region_point(Regions : : Row, Column : IsInside)` |

#### 4.4.2 典型流水线：管线自检

```hdevelop
* 断言两元组相等
test_equal_region (Result, Expected, IsEqual)
if (IsEqual # 'true')
    dev_disp_text ('测试失败：结果不等于期望', 'window', 'top', 'red', [])
    return ()
endif
```

#### 4.4.3 误区

| 误区 | 正确做法 |
| --- | --- |
| 用 `test_equal_region` 做容差比较 | 它是**严格像素级相等**，不容差；容差用 `compare_obj`（Object 章） |
| `test_region_point` 期望每个 Region 都返回结果 | 它返回**整体判定**：只要**至少一个** Region 包含该点就返回 true |

---

## §5 通用工作流

### 5.1 模板：从坐标造 Region → 转 XLD → 拟合

```hdevelop
* Step 1: 从坐标造填充多边形
gen_region_polygon_filled (PolyRegion, Rows, Columns)
* Step 2: 提取轮廓像素
get_region_contour (PolyRegion, ContourRows, ContourCols)
* Step 3: 转 XLD 轮廓（用 gen_contours + 简化）
gen_contours_skeleton_xld (ContourRows, ContourCols, Contour, 1, 'filter')
```

### 5.2 模板：ROI 联合与 Mask 抠图

```hdevelop
* Step 1: 用基础几何造多个 ROI
gen_circle (Circle1, 100, 100, 50)
gen_rectangle2 (Rect, 200, 200, rad(45), 60, 30)
* Step 2: union1 合并
union1 ([Circle1, Rect], CombinedROI)
* Step 3: 与全图 mask 求交，抠出 ROI
reduce_domain (Image, CombinedROI, ImageROI)
```

### 5.3 模板：单元测试断言

```hdevelop
* Step 1: 跑算法得到结果
threshold (Image, Region, 128, 255)
* Step 2: 断言像素数 == 期望
count_obj (Region, N)
if (N # ExpectedN)
    return ()
endif
* Step 3: 断言与期望 mask 完全相等
test_equal_region (Region, ExpectedMask, IsEqual)
```

---

## §6 选型决策矩阵

| 需求 | 用 Access 族 | 用 Creation 族 | 用 Sets 族 | 用 Tests 族 |
| --- | --- | --- | --- | --- |
| 我想知道 Region 里有哪些像素 | `get_region_points` | —— | —— | —— |
| 我想用近似多边形简化 Region | `get_region_polygon` | —— | —— | —— |
| 我想凭空造一个圆 | —— | `gen_circle` | —— | —— |
| 我想造一个填充多边形 | —— | `gen_region_polygon_filled` | —— | —— |
| 我想合并多个 Region | —— | —— | `union1` | —— |
| 我想抠出 ROI 与图像的交集 | —— | —— | `intersection` | —— |
| 我想判断两 Region 是否相等 | —— | —— | —— | `test_equal_region` |
| 我想测试点是否在 Region 内 | —— | —— | —— | `test_region_point` |

---

## §7 误区速查（10 条）

1. **`gen_rectangle2` 角度用弧度不是度**——所有 HALCON 几何算��统一用弧度（`Phi ∈ [0, 2π)`）。
2. **`gen_circle` 圆心 `(Row, Column)` 是图像坐标 (y, x)**——不是 (x, y)。
3. **`gen_region_polygon` 造的是边界不是填充**——要用 `gen_region_polygon_filled` 才能造填充多边形。
4. **`union1` 与 `union2` 用途不同**——`union1` 把元组合并成单个 Region；`union2` 逐元素配对合并。
5. **`difference` 是集合差不是单点删除**——A−B 移除 A 中**所有**与 B 任一元素"逻辑相等"的部分。
6. **`complement` 受 `'clip_region'` 系统标志影响**——默认裁剪到 image domain。
7. **`test_equal_region` 不容差**——严格像素级相等；容差比较用 `compare_obj`（Ch21）。
9. **`test_region_point` 是"或"语义**——只要**至少一个** Region 包含点就返回 true，不逐 Region 判定。
10. **`get_region_runs` 输出的是行程**——`(Row, ColumnBegin, ColumnEnd)` 三元组，与 `get_region_points` 输出的 `(Rows, Columns)` 不同。

---

## §8 完整签名速查（35 算子全）

### §8.1 Access 族（5 算子）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `get_region_contour` | Region 边界 → 像素坐标 | `get_region_contour(Region : : : Rows, Columns)` |
| `get_region_convex` | Region 凸包 → 多边形 | `get_region_convex(Region : : : Rows, Columns)` |
| `get_region_points` | Region 所有像素坐标 | `get_region_points(Region : : : Rows, Columns)` |
| `get_region_polygon` | Region 近似多边形 | `get_region_polygon(Region : : Tolerance : Rows, Columns)` |
| `get_region_runs` | Region → 行程编码 | `get_region_runs(Region : : : Row, ColumnBegin, ColumnEnd)` |

### §8.2 Creation 族（21 算子）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `gen_checker_region` | 棋盘格 Region | `gen_checker_region(: RegionChecker : WidthRegion, HeightRegion, WidthPattern, HeightPattern :)` |
| `gen_circle` | 圆 | `gen_circle(: Circle : Row, Column, Radius :)` |
| `gen_circle_sector` | 扇形/圆环扇形 | `gen_circle_sector(: CircleSector : Row, Column, Radius, StartAngle, EndAngle :)` |
| `gen_ellipse` | 椭圆 | `gen_ellipse(: Ellipse : Row, Column, Phi, Radius1, Radius2 :)` |
| `gen_ellipse_sector` | 椭圆扇形 | `gen_ellipse_sector(: EllipseSector : Row, Column, Phi, Radius1, Radius2, StartAngle, EndAngle :)` |
| `gen_empty_region` | 空 Region | `gen_empty_region(: EmptyRegion :)` |
| `gen_grid_region` | 网格线/点 | `gen_grid_region(: RegionGrid : RowSteps, ColumnSteps, Type, Width, Height :)` |
| `gen_random_region` | 全图随机像素 | `gen_random_region(: RegionRandom : Width, Height :)` |
| `gen_random_regions` | 多个随机形状 | `gen_random_regions(: Regions : Type, WidthMin, WidthMax, HeightMin, HeightMax, Density, Seed :)` |
| `gen_rectangle1` | 轴对齐矩形 | `gen_rectangle1(: Rectangle : Row1, Column1, Row2, Column2 :)` |
| `gen_rectangle2` | 任意角度矩形 | `gen_rectangle2(: Rectangle : Row, Column, Phi, Length1, Length2 :)` |
| `gen_region_contour_xld` | XLD 轮廓 → Region | `gen_region_contour_xld(Contour : Region : Mode :)` |
| `gen_region_histo` | 直方图 → Region | `gen_region_histo(: Region : Histogram, Row, Column, Scale :)` |
| `gen_region_hline` | Hesse 法式直线 | `gen_region_hline(: Regions : Orientation, Distance :)` |
| `gen_region_line` | 线段 → Region | `gen_region_line(: RegionLines : BeginRow, BeginCol, EndRow, EndCol :)` |
| `gen_region_points` | 像素坐标 → Region | `gen_region_points(: Region : Rows, Columns :)` |
| `gen_region_polygon` | 折线 → 边界多边形 | `gen_region_polygon(: Region : Rows, Columns :)` |
| `gen_region_polygon_filled` | 折线 → 填充多边形 | `gen_region_polygon_filled(: Region : Rows, Columns :)` |
| `gen_region_polygon_xld` | XLD 多边形 → Region | `gen_region_polygon_xld(Polygon : Region : Mode :)` |
| `gen_region_runs` | 行程 → Region | `gen_region_runs(: Region : Row, ColumnBegin, ColumnEnd :)` |
| `label_to_region` | label 图 → Region 元组 | `label_to_region(LabelImage : Regions :)` |

### §8.3 Sets 族（6 算子）

| 算子 | 集合论 | HDevelop 关键签名 |
| --- | --- | --- |
| `complement` | `¬A` | `complement(Region : RegionComplement :)` |
| `difference` | `A − B` | `difference(Region, Sub : RegionDifference :)` |
| `intersection` | `A ∩ B` | `intersection(Region1, Region2 : RegionIntersection :)` |
| `symm_difference` | `A ⊕ B` | `symm_difference(Region1, Region2 : RegionDifference :)` |
| `union1` | `∪A` | `union1(Region : RegionUnion :)` |
| `union2` | `A ∪ B` | `union2(Region1, Region2 : RegionUnion :)` |

### §8.4 Tests 族（3 算子）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `test_equal_region` | 元组逐元素相等 | `test_equal_region(Regions1, Regions2 : : : IsEqual)` |
| `test_region_point` | 测试点在 Region 内 | `test_region_point(Regions : : Row, Column : IsInside)` |
| `test_subset_region` | Region1 ⊆ Region2 | `test_subset_region(Region1, Region2 : : : IsSubset)` |

---

## §9 一句话总结

第 22 章 Regions 上卷是 HALCON 二值掩模的「看、造、算、判」基础四件套——**5 个 Access 算子让你看（points/runs/polygon/convex/contour）、21 个 Creation 算子让你造（圆/椭圆/矩形/扇形/随机/网格/从坐标/从 XLD/从 label/空）、6 个 Sets 算子让你算集合论（union/intersection/difference/symm_difference/complement）、3 个 Tests 算子让你判（equal/subset/point-in）**，所有 Region 高级算法（中卷测量、下卷变换）都以这一卷为脚手架。