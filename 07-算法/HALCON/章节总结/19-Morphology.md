# 第 19 章 Morphology  ·  形态学 · 全章单卷

> **HALCON 官方 Operator Reference · 第 19 章**全章单卷文档，共 **43 个算子**（Gray Values 18 + Region 25）。
> 本章是 HALCON 图像/区域二值/XLD 处理的"结构元素数学"基础——一切"提取骨架、去毛刺、补孔、分离连通"的底层原理。

---

## 1. 章节定位

**形态学（Mathematical Morphology）** 是基于**结构元素 SE（Structuring Element）** 的图像处理理论。SE 是一个小模板（如 3×3 圆盘、5×5 矩形），它像"印章"一样在输入对象上滑动，对每个位置做"某种集合运算"。

| 维度 | 说明 |
| --- | --- |
| **数学本质** | 集合论 + 格论——腐蚀=求 SE 完全落入的交集，膨胀=求 SE 与之相碰的并集 |
| **核心对象** | **SE**（结构元素）——形态学的"探针"，决定算法"看到什么形状" |
| **基本算 4 个** | **腐蚀 · 膨胀 · 开 · 闭**——其他所有形态学算子都是这 4 个的组合/变体 |
| **派生算** | **顶帽 TopHat · 黑帽 BothAt · Range · Hit-or-Miss · Minkowski 加减**——求残差/局部极值 |
| **HALCON 双域** | **Gray Values**（图像灰度 18 ops）+ **Region**（二值区域 25 ops）——同一套数学，两个输入域 |
| **应用领域** | 工业去噪（开闭滤除噪声）、尺寸筛选（面积/开半径）、骨架提取（连续腐蚀中心轴）、连接体分离（分水岭预分割） |

> **形态学的"哲学"**：用形状（SE）去"探测"图像/区域中的形状——腐蚀是"刚好穿过"，膨胀是"擦边而过"，开闭是"过门锤"。

---

## 2. 两族速览

HALCON 把形态学按输入对象切成两个**正交但数学同构**的族：

### 2.1 Gray Values · 灰度形态学（18 ops）

| 子主题 | ops 数 | 代表算子 | 用途 |
| --- | ---: | --- | --- |
| **结构元素生成** | 2 | `gen_disc_se` `read_gray_se` | 构造/加载灰度形态学的 SE 模板 |
| **4 形态 × 3 SE** | 12 | `gray_{dilation,erosion,opening,closing}` × `{无, rect, shape}` | 通用版+矩形 SE 版+任意形状 SE 版 |
| **派生灰度** | 5 | `gray_tophat` `gray_bothat` `gray_range_rect` `dual_rank` | 顶帽/黑帽/局部极差/排名滤波（TopHat+BothAt 是开闭的残差） |

**关键算子**：`gray_dilation( Image , SE : ImageDilation : : )` `gray_opening_rect( Image : ImageOpening : MaskHeight , MaskWidth : )`

### 2.2 Region · 区域形态学（25 ops）

| 子主题 | ops 数 | 代表算子 | 用途 |
| --- | ---: | --- | --- |
| **基础/骨架** | 4 | `threshold` `boundary` `connection` `pruning` | 二值化、提取区域边界、连通分量分析、骨架剪枝 |
| **腐蚀 / 膨胀** | 8 | `erosion1/_2/_circle/_rectangle1` `dilation1/_2/_circle/_rectangle1` | 4 种 SE 形状 × 2 基本算，对区域做"收/放" |
| **开 / 闭** | 6 | `opening/_circle/_rectangle1` `closing/_circle/_rectangle1` | 4 形态的"过门锤"，开=先腐蚀再膨胀，闭=先膨胀再腐蚀 |
| **派生 Region** | 7 | `hit_or_miss` `top_hat` `bottom_hat` `minkowski_add1/_2/_sub1/_sub2` | 命中-击不中（找特定形状）、顶帽/黑帽残差、Minkowski 加减（凸包/腐蚀的扩展） |

**关键算子**：`opening( Region , StructElement : RegionOpening : : )` `erosion_circle( Region , StructElement : RegionErosion : Radius : )`

---

## 3. 七瓣辐射思维导图

![形态学全景图](./19-Morphology.png)

> **左上角圆形徽章 = 主题编号**（01-07）· **右上角圆形徽章 = 族归属**（GV=GrayValues 蓝/绿/金，RG=Region 橙/红/紫）

---

## 4. 七族详解

### 4.1 [01] 派生 Region · Hit-Miss + Minkowski（7 ops）

**主题**：从区域求"特定形状"和"凸包/结构骨架"。

| 算子 | 签名 | 一句话功能 |
| --- | --- | --- |
| `hit_or_miss` | `hit_or_miss ( Region , StructElement1 , StructElement2 : RegionHitMiss : Row , Column : )` | **命中-击不中**：用两个 SE 同时找"前景+背景"配置（如找角点、十字、T 接头） |
| `top_hat` | `top_hat ( Region , StructElement : RegionTopHat : : )` | 顶帽：原区域减开运算结果 → 提取"比 SE 小"的残余亮区域 |
| `bottom_hat` | `bottom_hat ( Region , StructElement : RegionBotHat : : )` | 黑帽：闭运算结果减原区域 → 提取"比 SE 小"的暗区域（实际是补洞位置） |
| `minkowski_add1` | `minkowski_add1 ( Region , StructElement : RegionMinkAdd : : )` | Minkowski 加法 1=带 SE 旋转的膨胀 → **凸包** |
| `minkowski_add2` | `minkowski_add2 ( Region , StructElement : RegionMinkAdd : Iterations : )` | 同 add1 但 SE 不旋转 |
| `minkowski_sub1` | `minkowski_sub1 ( Region , StructElement : RegionMinkSub : : )` | Minkowski 减法 1=带 SE 旋转的腐蚀 |
| `minkowski_sub2` | `minkowski_sub2 ( Region , StructElement : RegionMinkSub : Iterations : )` | 同 sub1 但 SE 不旋转 |

**Hit-Miss** 是 HALCON 唯一支持"找出严格形状匹配"的算子——在 OCR 字符角点检测、工业部件几何验证中非常重要。

#### 4.1.1 误区
- **minkowski_add1 vs add2**：`add1` 旋转 SE 180°，`add2` 不旋转——开闭视觉上相似，但 add1 用于求**凸包**（凸多边形包络），add2 用于求**对称膨胀**（SE 原方向）。
- **top_hat / bottom_hat 不等于 morphological gradient**：前者输入是区域，输出仍是区域；后者输入是图像，输出是图像。

### 4.2 [02] 4 形态 × 3 SE · 腐蚀·膨胀·开·闭（12 ops）

**主题**：GrayValues 族的"通用 12 件套"——4 个基本算 × 3 种 SE（自由 / 矩形 rect / 任意形状 shape）。

| 算子家族 | 通用版（任意 SE） | 矩形 SE 版 | 任意形状 SE 版 |
| --- | --- | --- | --- |
| **腐蚀** | `gray_erosion ( Image , SE : ImageErosion : : )` | `gray_erosion_rect ( Image : ImageMin : MaskHeight , MaskWidth : )` | `gray_erosion_shape ( Image : ImageMin : MaskHeight , MaskWidth , MaskShape : )` |
| **膨胀** | `gray_dilation ( Image , SE : ImageDilation : : )` | `gray_dilation_rect ( Image : ImageMax : MaskHeight , MaskWidth : )` | `gray_dilation_shape ( Image : ImageMax : MaskHeight , MaskWidth , MaskShape : )` |
| **开** | `gray_opening ( Image , SE : ImageOpening : : )` | `gray_opening_rect ( Image : ImageOpening : MaskHeight , MaskWidth : )` | `gray_opening_shape ( Image : ImageOpening : MaskHeight , MaskWidth , MaskShape : )` |
| **闭** | `gray_closing ( Image , SE : ImageClosing : : )` | `gray_closing_rect ( Image : ImageClosing : MaskHeight , MaskWidth : )` | `gray_closing_shape ( Image : ImageClosing : MaskHeight , MaskWidth , MaskShape : )` |

**SE 3 版本选择**：
- **通用版（`gray_*`）**：用 `gen_disc_se` 预先生成 SE 对象，最灵活，可任意旋转/缩放
- **`_rect` 版**：直接给高宽参数（MaskHeight, MaskWidth）→ **速度最快**，推荐 90% 场景
- **`_shape` 版**：多一个 MaskShape（'octagon'/'rectangle'/'rhombus'），可指定八角/菱形等特殊 SE

#### 4.2.1 误区
- **腐蚀不等于变小**：腐蚀是"邻域 min"，会让暗的细节扩大、亮的细节缩小。
- **开闭的可分离性**：开 = 先腐蚀后膨胀；闭 = 先膨胀后腐蚀。两者**幂等**（再开/再闭结果不变）。
- **SE 太小则无效**：如果 SE 半径 < 噪声像素，开/闭无法滤除。

### 4.3 [03] 派生 TopHat · BothAt + Range（5 ops）

**主题**：4 个基本算的"残差/局部极值/排名"。

| 算子 | 签名 | 一句话功能 |
| --- | --- | --- |
| `gray_tophat` | `gray_tophat ( Image , SE : ImageTopHat : : )` | **白帽**：原图减开运算 → 提取"比 SE 小的亮区域" |
| `gray_bothat` | `gray_bothat ( Image , SE : ImageBotHat : : )` | **黑帽**：闭运算减原图 → 提取"比 SE 小的暗区域" |
| `gray_range_rect` | `gray_range_rect ( Image : ImageResult : MaskHeight , MaskWidth : )` | **局部灰度极差**：max - min in window → 边缘/纹理强度图 |
| `dual_rank` | `dual_rank ( Image : ImageRank : MaskType , Radius , ModePercent , Margin : )` | **双边排序**：maskType='circle' 时做圆盘排名滤波（同形态学）；'rect' 时做矩形排名 |

**TopHat 的应用**：背景不均匀时提取前景（如印章、文档上白色印章）。**Range** 是 **Canny/Sobel 边缘**的形态学替代——对噪声稍敏感但无方向性。

#### 4.3.1 误区
- **gray_tophat 不是 "extract white"**：背景暗前景亮 → 用 tophat；背景亮前景暗 → 用 bothat。
- **dual_rank 不是双线性滤波**：它的"rank"是灰度排序，不是矩阵分解。

### 4.4 [04] 基础 Region · 骨架处理（4 ops）

**主题**：进入区域形态学前的"预处理"——把图像变成 Region，再做骨架/连通分量分析。

| 算子 | 签名 | 一句话功能 |
| --- | --- | --- |
| `threshold` | `threshold ( Image : Region : MinGray , MaxGray : )` | **灰度阈值**→Region：所有灰度在 [MinGray, MaxGray] 的像素纳入 Region |
| `boundary` | `boundary ( Region : RegionBoundary : BoundaryType : )` | **提取区域边界**：BoundaryType='inner' 内边界，'outer' 外边界 |
| `connection` | `connection ( Region : ConnectedRegions : : )` | **连通分量**：把 Region 切成"各自连通的子区域"——是计数/分析的基础 |
| `pruning` | `pruning ( Region : RegionPruned : Length : )` | **剪枝**：去掉"长度 < Length"的骨架分支（`skeleton` 之后的清理步骤） |

#### 4.4.1 误区
- **threshold 不是 binary_threshold**：threshold 只接受标量 [Min, Max]；二值化建议 `binary_threshold`。
- **connection 对椭圆/长条形很敏感**：会按像素邻接（4 或 8 邻域）分裂。
- **pruning 必须接 skeleton 之后**：`pruning` 用于骨架剪枝，不是任意区域。

### 4.5 [05] 开 / 闭 · 3 SE × 2 算子（6 ops）

**主题**：开闭运算的 Region 版——同 GrayValues，但输入是 Region，输出也是 Region。

| 算子族 | 通用版 | 圆形 SE 版 | 矩形 SE 版 |
| --- | --- | --- | --- |
| **开运算** | `opening ( Region , StructElement : RegionOpening : : )` | `opening_circle ( Region , StructElement : RegionOpening : Radius : )` | `opening_rectangle1 ( Region : RegionOpening : MaskHeight , MaskWidth : )` |
| **闭运算** | `closing ( Region , StructElement : RegionClosing : : )` | `closing_circle ( Region , StructElement : RegionClosing : Radius : )` | `closing_rectangle1 ( Region : RegionClosing : MaskHeight , MaskWidth : )` |

**Region 版 vs GrayValues 版**：
- **输入域**：Region（binary mask）vs Image（灰度图）
- **开效果**：去除小亮点/小区域（开=先腐蚀去小，再膨胀恢复主体）；平滑边界，断开细连接
- **闭效果**：填补小暗点/小孔（闭=先膨胀补小，再腐蚀恢复主体）；连接窄缝

#### 4.5.1 误区
- **`opening_circle` 必须先传 StructElement**：很多 HALCON 版本的 `opening_circle` 第一个参数仍是 SE 对象，Radius 只是 SE 参数。
- **闭不会增加新边界**：闭运算的边界 = 原始边界 ∪ 膨胀边界，但闭结果边界可能比原区域更"圆滑"。

### 4.6 [06] 结构元素 SE（2 ops）

**主题**：所有形态学算子的"探针"——没有 SE 就没有形态学。

| 算子 | 签名 | 一句话功能 |
| --- | --- | --- |
| `gen_disc_se` | `gen_disc_se ( : SE : Type , Width , Height , Smax : )` | **生成椭球 SE**：Type='byte'/'real'，Width/Height 像素，Smax 灰度衰减斜率 |
| `read_gray_se` | `read_gray_se ( : SE : FileName : )` | **从文件加载 SE**：如 `\se\ball` `\se\noise`（HALCON 内置 SE 库） |

**SE 数据结构**：`SE = Image + Mask`：
- **Image**：SE 灰度值分布（球形 SE 中心值高，边缘低）
- **Mask**：SE 形状掩码（圆/矩形/自定义）

#### 4.6.1 误区
- **Type='byte' (0-255) vs 'int4'/ 'real'**：非 byte SE 在腐蚀/膨胀时用整数/浮点算，结果精度不同。
- **Smax 控制 SE "圆滑度"**：Smax 越大，SE 边缘越平滑（接近高斯）；Smax=0 则是平顶圆柱 SE。

### 4.7 [07] 腐蚀 / 膨胀 · 4 SE × 4 算子（8 ops）

**主题**：Region 族的腐蚀膨胀——4 种 SE 形状（任意/圆/矩形/小 SE） × 2 个基本算。

| 算子族 | 通用版（任意 SE） | 双点 SE 版 | 圆形 SE 版 | 矩形 SE 版 |
| --- | --- | --- | --- | --- |
| **腐蚀** | `erosion1 ( Region , StructElement : RegionErosion : Iterations : )` | `erosion2 ( Region , StructElement : RegionErosion : Iterations : )` | `erosion_circle ( Region , StructElement : RegionErosion : Radius : )` | `erosion_rectangle1 ( Region : RegionErosion : MaskHeight , MaskWidth : )` |
| **膨胀** | `dilation1 ( Region , StructElement : RegionDilation : Iterations : )` | `dilation2 ( Region , StructElement : RegionDilation : Iterations : )` | `dilation_circle ( Region , StructElement : RegionDilation : Radius : )` | `dilation_rectangle1 ( Region : RegionDilation : MaskHeight , MaskWidth : )` |

**4 种 SE 区别**：
- **任意 SE（erosion1/dilation1）**：用 `gen_disc_se`/`read_gray_se` 生成的复杂 SE
- **双点 SE（erosion2/dilation2）**：SE 含两个中心点 → 用于"相邻点配对"操作（如 OCR 字符断行）
- **圆形 SE**：`erosion_circle` 给 Radius 参数，`erosion_golay` 给 Golay 字母表
- **矩形 SE**：最快，直接给高宽

#### 4.7.1 误区
- **`erosion2` 的 Iterations 是 SE 应用次数**（不是腐蚀半径），多次迭代 = 半径叠加。
- **`dilation_rectangle1` MaskHeight/Width 单位是像素**：3×3 矩形 = (3, 3)，不是 (3.0, 3.0)。

---

## 5. 通用工作流

### 5.1 形态学基本定理（4 个恒等式）

| 定理 | 公式 | 应用 |
| --- | --- | --- |
| **对偶性** | `(f ⊕ B)^c = f^c ⊖ B̂`（膨胀对偶 = 腐蚀补） | 腐蚀膨胀互转：先反色再换 SE 方向 |
| **开闭幂等** | `(f ◦ B) ◦ B = f ◦ B`（开运算再做不变） | 滤波只需一次 |
| **单调性** | SE₁ ⊂ SE₂ ⇒ f ⊕ SE₁ ⊆ f ⊕ SE₂` | 大 SE 腐蚀半径更大 |
| **平移不变** | `(f + x) ⊕ B = (f ⊕ B) + x` | 平移输入 = 平移输出 |

### 5.2 模板 1：图像灰度去噪（开/闭）

```hdevelop
read_image (Image, 'pattern_with_salt_pepper')
* 用 3×3 矩形 SE 开运算：去除亮噪声
gray_opening_rect (Image, ImageOpening, 3, 3)
* 用 3×3 矩形 SE 闭运算：去除暗噪声（可叠加）
gray_closing_rect (ImageOpening, ImageClean, 3, 3)
```

### 5.3 模板 2：区域去毛刺（开运算 + 选择面积）

```hdevelop
threshold (Image, Region, 128, 255)
* 圆形 SE 开运算：磨平边界，去掉细丝毛刺
opening_circle (Region, Region, gen_disc_se(...), 2.5)
* 计算连通分量
connection (Region, ConnRegions)
* 面积选择
select_shape (ConnRegions, Selected, 'area', 'and', 100, 99999)
```

### 5.4 模板 3：背景不均匀文档的字符提取（TopHat）

```hdevelop
read_image (Doc, 'document_with_stamp')
* 用大圆盘 SE 做白帽（提取亮字符，抑制渐变背景）
gray_tophat (Doc, DocTopHat, gen_disc_se('byte', 50, 50, 0))
* 阈值化
threshold (DocTopHat, CharRegions, 50, 255)
```

### 5.5 模板 4：查找特定形状（Hit-Miss · 角点）

```hdevelop
* 查找"左上角点"：前景=像素，背景=邻接东南西三方向
gen_struct_element (StructElement1, 'rectangle', 3, 3)
hit_or_miss (Region, StructElement1, StructElement2, Corners, Row, Column)
* 输出 Corners 是角点位置集合，可直接计数
```

### 5.6 模板 5：提取连通区域中心轴（Skeleton + Pruning）

```hdevelop
threshold (Image, Region, 100, 200)
connection (Region, ConnectedRegions)
select_shape (ConnectedRegions, Selected, 'area', 'and', 500, 10000)
skeleton (Selected, Skeleton)
* 剪枝：去掉 < 5 像素的末梢
pruning (Skeleton, SkeletonPruned, 5)
```

---

## 6. GrayValues vs Region 选型决策表

| 场景特征 | 推荐族 | 推荐算子 |
| --- | --- | --- |
| 输入是灰度图像，要平滑/去噪 | **GrayValues** | `gray_{opening,closing}_rect` |
| 输入是二值 Region，要去毛刺/补孔 | **Region** | `opening_circle` `closing_circle` |
| 背景渐变，前景均匀 | **GrayValues** | `gray_tophat` (白前景) 或 `gray_bothat` (暗前景) |
| 找特定形状（角点/十字/T 接） | **Region** | `hit_or_miss` |
| 求局部边缘强度图 | **GrayValues** | `gray_range_rect` |
| 用 SE 旋转求凸包 | **Region** | `minkowski_add1` |
| 需要非矩形 SE（菱形/八角） | **GrayValues** | `gray_*_shape` (MaskShape 参数) |
| 处理速度优先 | **GrayValues `_rect`** 或 **Region `_rectangle1`** | 直接高宽 |
| OCR 字符识别 | **Region** | `connection` + `select_shape` + `pruning` |

---

## 7. 误区速查 10 条

1. **腐蚀≠变小、膨胀≠变大**：腐蚀是"邻域 min"，膨胀是"邻域 max"；前者使暗区扩张，后者使亮区扩张。
2. **`opening_circle` 必须先有 SE 对象**：HALCON 20.11 中第 2 个参数仍是 StructElement（不是元组），Radius 只是 SE 半径。
3. **开/闭幂等**：再开一次结果不变，多开无益。
4. **Hit-Miss 找不到"凸包"**：要用 `minkowski_add1`。
5. **`top_hat` / `bottom_hat` 输入为图像**：形态学 gradient 用 `gray_range_rect`，不是 tophat。
6. **`threshold` 不等于 `binary_threshold`**：前者要手动给 [Min, Max]，后者自动用 Otsu 等算法找。
7. **`pruning` 必须先 `skeleton`**：`pruning` 是"骨架剪枝"，对实心区域无意义。
8. **`erosion_rectangle1` MaskHeight=0 等于无操作**：SE 高度至少为 1。
9. **`dual_rank` 的 rank percent 影响中值滤波**：ModePercent=50 = 中值，ModePercent=100 = 膨胀，ModePercent=0 = 腐蚀。
10. **形态学不抗噪声严重**：如果 SNR<2，形态学先去噪再分析或用其他方法。

---

## 8. 完整签名速查表（43 算子全）

### 8.1 Gray Values 子表（18 算子）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `dual_rank` | 双边排序（圆/矩形 mask）排名滤波 | `dual_rank ( Image : ImageRank : MaskType , Radius , ModePercent , Margin : )` |
| `gen_disc_se` | 生成椭球结构元素 SE（by 宽度/高度/斜率） | `gen_disc_se ( : SE : Type , Width , Height , Smax : )` |
| `read_gray_se` | 从文件加载灰度形态学 SE | `read_gray_se ( : SE : FileName : )` |
| `gray_dilation` | 灰度膨胀（任意 SE）——邻域 max | `gray_dilation ( Image , SE : ImageDilation : : )` |
| `gray_dilation_rect` | 灰度膨胀（矩形 SE）——同 rect 卷积 | `gray_dilation_rect ( Image : ImageMax : MaskHeight , MaskWidth : )` |
| `gray_dilation_shape` | 灰度膨胀（任意形状 SE） | `gray_dilation_shape ( Image : ImageMax : MaskHeight , MaskWidth , MaskShape : )` |
| `gray_erosion` | 灰度腐蚀（任意 SE）——邻域 min | `gray_erosion ( Image , SE : ImageErosion : : )` |
| `gray_erosion_rect` | 灰度腐蚀（矩形 SE） | `gray_erosion_rect ( Image : ImageMin : MaskHeight , MaskWidth : )` |
| `gray_erosion_shape` | 灰度腐蚀（任意形状 SE） | `gray_erosion_shape ( Image : ImageMin : MaskHeight , MaskWidth , MaskShape : )` |
| `gray_opening` | 灰度开（任意 SE）——先腐蚀后膨胀，去亮噪声 | `gray_opening ( Image , SE : ImageOpening : : )` |
| `gray_opening_rect` | 灰度开（矩形 SE） | `gray_opening_rect ( Image : ImageOpening : MaskHeight , MaskWidth : )` |
| `gray_opening_shape` | 灰度开（任意形状 SE） | `gray_opening_shape ( Image : ImageOpening : MaskHeight , MaskWidth , MaskShape : )` |
| `gray_closing` | 灰度闭（任意 SE）——先膨胀后腐蚀，去暗噪声 | `gray_closing ( Image , SE : ImageClosing : : )` |
| `gray_closing_rect` | 灰度闭（矩形 SE） | `gray_closing_rect ( Image : ImageClosing : MaskHeight , MaskWidth : )` |
| `gray_closing_shape` | 灰度闭（任意形状 SE） | `gray_closing_shape ( Image : ImageClosing : MaskHeight , MaskWidth , MaskShape : )` |
| `gray_bothat` | 灰度黑帽——闭 - 原，提取暗前景 | `gray_bothat ( Image , SE : ImageBotHat : : )` |
| `gray_tophat` | 灰度顶帽——原 - 开，提取亮前景 | `gray_tophat ( Image , SE : ImageTopHat : : )` |
| `gray_range_rect` | 灰度局部极差——max - min，边缘强度图 | `gray_range_rect ( Image : ImageResult : MaskHeight , MaskWidth : )` |

### 8.2 Region 子表（25 算子）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `threshold` | 灰度阈值转二值 Region | `threshold ( Image : Region : MinGray , MaxGray : )` |
| `boundary` | 提取 Region 内/外边界 | `boundary ( Region : RegionBoundary : BoundaryType : )` |
| `connection` | 切分连通分量（4/8 邻域） | `connection ( Region : ConnectedRegions : : )` |
| `pruning` | 骨架剪枝（去掉 < Length 末梢） | `pruning ( Region : RegionPruned : Length : )` |
| `dilation1` | 区域膨胀（任意 SE） | `dilation1 ( Region , StructElement : RegionDilation : Iterations : )` |
| `dilation2` | 区域膨胀（双点 SE——对称应用） | `dilation2 ( Region , StructElement : RegionDilation : Iterations : )` |
| `dilation_circle` | 区域膨胀（圆形 SE） | `dilation_circle ( Region , StructElement : RegionDilation : Radius : )` |
| `dilation_rectangle1` | 区域膨胀（矩形 SE） | `dilation_rectangle1 ( Region : RegionDilation : MaskHeight , MaskWidth : )` |
| `erosion1` | 区域腐蚀（任意 SE） | `erosion1 ( Region , StructElement : RegionErosion : Iterations : )` |
| `erosion2` | 区域腐蚀（双点 SE） | `erosion2 ( Region , StructElement : RegionErosion : Iterations : )` |
| `erosion_circle` | 区域腐蚀（圆形 SE） | `erosion_circle ( Region , StructElement : RegionErosion : Radius : )` |
| `erosion_rectangle1` | 区域腐蚀（矩形 SE） | `erosion_rectangle1 ( Region : RegionErosion : MaskHeight , MaskWidth : )` |
| `opening` | 区域开（任意 SE）——去亮岛 | `opening ( Region , StructElement : RegionOpening : : )` |
| `opening_circle` | 区域开（圆形 SE） | `opening_circle ( Region , StructElement : RegionOpening : Radius : )` |
| `opening_rectangle1` | 区域开（矩形 SE） | `opening_rectangle1 ( Region : RegionOpening : MaskHeight , MaskWidth : )` |
| `closing` | 区域闭（任意 SE）——补暗洞 | `closing ( Region , StructElement : RegionClosing : : )` |
| `closing_circle` | 区域闭（圆形 SE） | `closing_circle ( Region , StructElement : RegionClosing : Radius : )` |
| `closing_rectangle1` | 区域闭（矩形 SE） | `closing_rectangle1 ( Region : RegionClosing : MaskHeight , MaskWidth : )` |
| `hit_or_miss` | 命中-击不中（找特定形状配置） | `hit_or_miss ( Region , StructElement1 , StructElement2 : RegionHitMiss : Row , Column : )` |
| `top_hat` | 区域顶帽——原 - 开，提取小亮区 | `top_hat ( Region , StructElement : RegionTopHat : : )` |
| `bottom_hat` | 区域黑帽——闭 - 原，提取小暗区 | `bottom_hat ( Region , StructElement : RegionBotHat : : )` |
| `minkowski_add1` | Minkowski 加法（SE 旋转 180°）——凸包 | `minkowski_add1 ( Region , StructElement : RegionMinkAdd : : )` |
| `minkowski_add2` | Minkowski 加法（SE 不旋转） | `minkowski_add2 ( Region , StructElement : RegionMinkAdd : Iterations : )` |
| `minkowski_sub1` | Minkowski 减法（SE 旋转 180°） | `minkowski_sub1 ( Region , StructElement : RegionMinkSub : : )` |
| `minkowski_sub2` | Minkowski 减法（SE 不旋转） | `minkowski_sub2 ( Region , StructElement : RegionMinkSub : Iterations : )` |

---

## 9. 一句话总结

> **形态学 = SE 印章 + 4 基本算（腐蚀/膨胀/开/闭）+ 4 派生（TopHat/BothAt/Range/Hit-Miss）。HALCON 把这套数学切成 GrayValues（图像灰度 18 ops）和 Region（二值区域 25 ops）两个输入域，前者光滑/提取特征，后者整形/分离连通；SE 选择 = 算法效果，决定"看到什么形状"。**
