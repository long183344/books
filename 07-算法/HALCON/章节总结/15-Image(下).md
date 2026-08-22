# 第 15 章 Image（下卷）· 图像的特征、裁剪、改写与类型转换

> HALCON 20.11.1.0 Operator Reference — Image 章节下半部分
> 上卷 = 图像的"输入 + 组织"（Access / Acquisition / Channel / Creation / Domain，5 族 62 ops）
> **本卷 = 图像的"分析 + 变换"（Features / Format / Manipulation / Type Conversion，4 族 44 ops）**

---

## 0. 本卷定位

上卷解决了"图从哪儿来、怎么拼、边界怎么算"，本卷解决"**图上能算什么、图怎么变、像素怎么改、类型怎么转**"：

- **Features（24）**：从 (Region, Image) 关系中提取**数值特征**——面积/重心、灰度直方图、共生矩阵、熵、平面拟合偏差、点/区域形状沿阈值的直方图。这是后续做分类、测量、判废的数值源泉。
- **Format（9）**：**裁剪、缩放、拼接**——`crop_*` 系列按 ROI 切；`change_format` 仅改尺寸；`tile_*` 把多张图拼一张大图。
- **Manipulation（6）**：**像素级改写**——`set_grayval` 改单点、`paint_*` 把 Region/XLD/图画到图上、`overpaint_*` 反向擦除。
- **Type Conversion（5）**：**类型互换**——byte/uint2/real/int4 之间 `convert_image_type`、complex 拆/拼成两个 real、`real_to_vector_field`/`vector_field_to_real` 用于光流/位移场。

> 一句话记忆：**Features 是算，Format 是裁/拼，Manipulation 是画，Type Conversion 是换层。**

---

## 1. 四族速览

| 族 | 算子数 | 一句话定位 | 代表算子 |
|---|---|---|---|
| **Features** | 24 | 从图/区域算数值特征 | `area_center_gray` `intensity` `entropy_gray` `gen_cooc_matrix` `fit_surface_*` `gray_features` `select_gray` |
| **Format** | 9 | 裁剪 / 改尺寸 / 拼接 | `crop_part` `crop_rectangle1/2` `crop_domain` `change_format` `tile_images` |
| **Manipulation** | 6 | 像素/Region/XLD 写图 | `set_grayval` `paint_gray/region/xld` `overpaint_gray/region` |
| **Type Conversion** | 5 | 像素类型互转 | `convert_image_type` `complex_to_real` `real_to_complex` `real_to_vector_field` `vector_field_to_real` |
| **合计** | **44** | | |

---

## 2. 思维导图

![Ch15 Image 下卷 · 四族辐射图](./15-Image(下).png)

四个族均匀辐射：Features（蓝）/ Format（绿）/ Manipulation（橙）/ Type Conversion（紫）。
中心节点为本卷总名"图像 Image 下卷"，每族卡片包含族英文/中文/算子数三行摘要。

---

## 3. Features（特征·统计·熵·拟合）

### 3.1 何时用 Features

- **基础统计**：`intensity`（均值/方差）、`min_max_gray`（极值）、`area_center_gray`（带灰度的面积/重心）、`elliptic_axis_gray`（灰度加权椭圆轴）。
- **直方图**：`gray_histo`（256 桶）/`gray_histo_abs`（自定义量化级）/`gray_histo_range`（指定灰度区间）/`histo_2dim`（双通道二维直方图）。
- **共生矩阵**：`gen_cooc_matrix`（生成）+ `cooc_feature_image`（一步算能量/相关性/同质性/对比度）/`cooc_feature_matrix`（在已生成的矩阵上算）。
- **熵与噪声**：`entropy_gray`（灰度熵 + 各向异性）、`estimate_noise`（从单图估高斯噪声 σ）。
- **曲面拟合**：`moments_gray_plane` + `fit_surface_first_order` + `fit_surface_second_order`（平面/曲面拟合）、`plane_deviation`（残差）。
- **形状沿阈值的直方图**：`shape_histo_all`/`shape_histo_point`——遍历所有阈值算 region 形状。
- **模糊版本**：`fuzzy_entropy` / `fuzzy_perimeter`（带模糊隶属度的特征）。
- **特征选择/聚合**：`gray_features`（一次算多种灰度特征）、`select_gray`（按特征筛 region）、`gray_projections`（行列灰度投影）。

### 3.2 标准流水线

```text
1) threshold(Image, Region, MinGray, MaxGray)
   ── 切出 ROI（参考第 12 章 Thresholding）
2) 基础统计（必做 1 步）
   area_center_gray(Regions, Image : : : Area, Row, Column)
   intensity(Regions, Image : : : Mean, Deviation)
3) 进一步特征（按需）
   entropy_gray(Regions, Image : : : Entropy, Anisotropy)
   gen_cooc_matrix(Regions, Image : Matrix : LdGray, Direction : )
   cooc_feature_image(Regions, Image : : LdGray, Direction : Energy, Correlation, Homogeneity, Contrast)
   fit_surface_first_order(Regions, Image : : Algorithm, Iterations, ClippingFactor : Alpha, Beta, Gamma)
   plane_deviation(Regions, Image : : : Deviation)
4) 用特征筛 region
   select_gray(Regions, Image : SelectedRegions : Features, Operation, Min, Max :)
   ── Features 例 'mean'/'min'/'max'/'area'/'anisotropy'
   ── Operation 'and'/'or' 配 Min/Max 区间
5) 形状直方图（高级分析）
   shape_histo_all(Region, Image : : Feature : AbsoluteHisto, RelativeHisto)
   shape_histo_point(Region, Image : : Feature, Row, Column : AbsoluteHisto, RelativeHisto)
```

### 3.3 五大类特征速记

| 类 | 算子 | 输入 | 输出 |
|---|---|---|---|
| **基础** | `area_center_gray` `intensity` `min_max_gray` `elliptic_axis_gray` | Regions, Image | 面积/重心/均值/方差/极值/椭圆轴 |
| **熵/噪声** | `entropy_gray` `estimate_noise` | Regions, Image / Image | Entropy/Anisotropy / Sigma |
| **共生矩阵** | `gen_cooc_matrix` + `cooc_feature_image/matrix` | Regions, Image | 矩阵 / Energy, Correlation, Homogeneity, Contrast |
| **曲面拟合** | `fit_surface_first_order/second_order` `moments_gray_plane` `plane_deviation` | Regions, Image | Alpha,Beta,Gamma / Alpha..Zeta / MRow,MCol,Alpha,Beta,Mean / Deviation |
| **直方图/选择** | `gray_histo*` `histo_2dim` `gray_features` `select_gray` `shape_histo_*` `gray_projections` | Regions, Image | Histo / Value / SelectedRegions / 行列投影 |

### 3.4 注意事项

| 易踩坑 | 解释 |
|---|---|
| **域不一致** | `area_center_gray` 等在 Region 域上算；先 `reduce_domain` 再传 Image；否则算的是整图。 |
| **共生的 LdGray** | `'ldgray'` 配 256 级；`'uint2'` 图配 1024 桶；不匹配能量/对比度数值差异大。 |
| **`estimate_noise` Method** | `'foerstner'` / `'immerkaer'` / `'perez'` / `'shapiro'`——不同算法对噪声大小假设不同，建议先 `'immerkaer'`。 |
| **`fit_surface_second_order` 6 项系数** | α + β·r + γ·c + δ·r² + ε·c² + ζ·r·c；`Algorithm='mean'` 是简单均值。 |
| **`select_gray` 的 Operation** | `'and'` / `'or'` 决定 Min/Max 之间的"且/或"；中文翻"且/或"易混淆。 |
| **`histo_2dim` 输入 2 张图** | 必须两张同尺寸 Image；输出 `Histo2Dim` 是 Matrix 类型（不是 Image）。 |
| **`shape_histo_*` 阈值遍历** | 输出直方图长度=256（byte 图），用于自适应阈值分析。 |

---

## 4. Format（裁剪·缩放·拼接）

### 4.1 何时用 Format

- **裁剪**：算完结果只关心 ROI 时——`crop_part` 按 (Row, Col, W, H) 切、`crop_rectangle1` 同上按两点、`crop_rectangle2` 任意角度带插值、`crop_domain` 直接切到当前域。
- **缩放**：`change_format` 改 image 存储的 Width/Height 但**像素值不重采样**——通常用于 OpenGL 显示对齐。
- **拼接**：多张图并列显示——`tile_images`（按行列数）/ `tile_channels`（按通道拼）/ `tile_images_offset`（带显式偏移）。

### 4.2 标准流水线

```text
1) 裁出 ROI
   crop_part(Image : ImagePart : Row, Column, Width, Height :)
   ── 或 crop_rectangle1(Image : ImagePart : Row1, Column1, Row2, Column2 :)
   ── 或 crop_rectangle2(Image : ImagePart : Row, Column, Phi, Length1, Length2, AlignToAxis, Interpolation :)
   ── 或 crop_domain(Image : ImagePart : :)   ── 直接裁到当前域（域变成全图）
   ── 或 crop_domain_rel(Image : ImagePart : Top, Left, Bottom, Right :)
2) 改尺寸（不重采样）
   change_format(Image : ImagePart : Width, Height :)
   ── 适合显示对齐，不适合算法——要做插值请用 zoom_image_factor（Ch12）
3) 拼图
   tile_images(Images : TiledImage : NumColumns, TileOrder :)
   ── NumColumns=N 表示每行 N 张；TileOrder='horizontal'/'vertical'/'row-major'
   tile_images_offset(Images : TiledImage : OffsetRow, OffsetCol, Row1, Col1, Row2, Col2, Width, Height :)
   ── 各图指定偏移；常用于做 calibration 标定板的多相机拼接
   tile_channels(Image : TiledImage : NumColumns, TileOrder :)
   ── 把多通道图拆开平铺成大图（常用于显示/对比）
```

### 4.3 注意事项

| 易踩坑 | 解释 |
|---|---|
| **`crop_part` 越界** | Row+Height > image.height 时会 clamp；先做范围校验。 |
| **`crop_domain` vs `full_domain`** | `crop_domain` 把域外的像素**丢掉**；`full_domain` 恢复域但**像素值仍为 0**——使用场景不同。 |
| **`change_format` 不插值** | 只是改存储的 Width/Height，像素值被重新映射到新尺寸的"等长像素块"——**慎用**于算法。 |
| **`tile_images` NumColumns** | 输入图数 = 10、NumColumns=3 时，第四行只有 1 张图；可用 `tile_images_offset` 精确控制。 |
| **`crop_rectangle2` 旋转** | Phi 是弧度（注意 ch13 Graphics 也是）；Length1/Length2 是矩形半轴长。 |
| **`tile_channels` 对彩色图** | 把 R/G/B 拆 3 块拼一起，方便看每个通道的细节。 |

---

## 5. Manipulation（像素改写）

### 5.1 何时用 Manipulation

- **改单个像素**：`set_grayval(Image : : Row, Column, Grayval :)` —— 不常用，但做像素级算法时必备。
- **画 Region/XLD 到图上**：`paint_region` / `paint_xld` / `paint_gray`。
- **擦除/覆盖**：`overpaint_gray` / `overpaint_region`。
- 典型用途：**生成可视化标记图**（画 ROI、画匹配结果、画缺陷区）。

### 5.2 标准流水线

```text
1) paint_region(Region, Image : ImageResult : Grayval, Type :)
   ── 把 Region 按 Grayval 写到 Image；Type 'fill'/'margin'/'border'
2) paint_xld(XLD, Image : ImageResult : Grayval :)
   ── 把 XLD 轮廓按 Grayval 写到 Image
3) paint_gray(ImageSource, ImageDestination : MixedImage : :)
   ── 把源图按域叠加到目标图
4) overpaint_gray(ImageDestination, ImageSource : : :)
   ── 域内的源图覆盖到目标图，域外保留
5) overpaint_region(Image, Region : : Grayval, Type :)
   ── 用 Grayval 覆盖 Region 区域
6) set_grayval(Image : : Row, Column, Grayval :)
   ── 单像素改写（debug/特殊场景）
```

### 5.3 注意事项

| 易踩坑 | 解释 |
|---|---|
| **paint_region 的 Type** | `'fill'` 填充整个 region、`'margin'` 仅边缘、`'border'` 仅最外圈像素。 |
| **paint_xld 不填中间** | XLD 是轮廓线，画到 Image 上是细线；要填充请用 `paint_region(Region, ..., Type='fill')`。 |
| **`overpaint_gray` vs `paint_gray`** | 前者是"覆盖"，后者是"按域混合"——overpaint 域外不动，paint 把域外当透明。 |
| **`set_grayval` 越界** | 行列超界时静默无效；循环前先判 `tuple_in_range`。 |
| **`paint_region` 与原图叠加** | 不会修改原图，返回 `ImageResult` 是新图；要原地改可 `overpaint_*`。 |

---

## 6. Type Conversion（类型转换）

### 6.1 何时用 Type Conversion

- **像素类型升级/降级**：`convert_image_type` 在 byte/uint2/int1/int2/int4/real/direction/cyclic 之间互转。
- **FFT 频域**：`complex_to_real` 把 FFT 输出（complex 图）拆成实部+虚部两张 real 图；`real_to_complex` 反向。
- **光流/位移场**：`real_to_vector_field` 把两张 real 图（row 方向 + col 方向）合并成 vector_field 图；`vector_field_to_real` 反向。

### 6.2 速记

```text
   byte / uint2 / int1 / int2 / int4 / real / direction / cyclic
                          │
                          ▼ convert_image_type
                  (放大/缩小数值范围，钳位到新类型)
                          │
                          ▼ fft_image (Ch12 中卷 FFT)
                  complex 图 (实部+虚部打包)
                          │
                          ▼ complex_to_real
                  两张 real 图（ImageReal + ImageImaginary）
                          │
                          ▼ (做算法: ifft / 滤波)
                          ▲ real_to_complex
                          │
                  complex 图 → fft_image → ...
```

Vector Field 用于把 `optical_flow_*`（Ch12 下卷）的输出 (Row, Col) 合并成 vector_field 图便于显示，或反向拆开做算法。

### 6.3 注意事项

| 易踩坑 | 解释 |
|---|---|
| **类型范围溢出** | `convert_image_type(Image, ImageConverted, 'byte')` 把 uint2 (>255) 截断；要归一化先用 `scale_image`。 |
| **`direction` / `cyclic` 类型** | 灰度角（弧度）映射成 int2/uint2 等；用于梯度方向显示。 |
| **complex 图不能直接 `disp_image`** | 先 `complex_to_real` 拆开，或 `phase_complex` / `amplitude_complex`（Ch12 中卷）。 |
| **`real_to_vector_field` 的 Type** | `'vector_field'` / `'d_xy'`——前者绝对位移，后者增量位移。 |
| **`vector_field_to_real` 输出顺序** | 先 Row 后 Col���对应光流 (dy, dx)。 |

---

## 7. 通用工作流（跨族）

```text
              原始 Image（来自上卷 Acquisition）
                          │
            ┌─────────────┼────────────────┐
            ▼             ▼                ▼
        Features        Format          Type Conversion
     （算特征）       （裁/拼接）       （换类型）
     intensity        crop_part        convert_image_type
     entropy_gray     tile_images      complex_to_real
            │             │                │
            └─────────────┼────────────────┘
                          │
                          ▼
                    Manipulation（改写/画）
                    paint_region / set_grayval
                          │
                          ▼
                    输出图（可视化/标注/再处理）
```

---

## 8. 常见误区

| 误区 | 正确做法 |
|---|---|
| **直接对彩色图算 `intensity`** | `intensity` 期望单通道；多通道先 `decompose3`/`access_channel`。 |
| **`crop_part` 当 resize** | `crop_part` 只是裁剪，不缩放；要缩放用 `zoom_image_factor`（Ch12 中卷）。 |
| **`convert_image_type` 不知道范围** | 转 `byte` 时>255 会截断；先 `scale_image` 归一化到 0~255。 |
| **`paint_*` 不指定 Type** | `paint_region` 不指定 Type 时默认 `'fill'`；要画边框需显式 `'margin'`/`'border'`。 |
| **`overpaint_*` 与 paint_* 混淆** | `overpaint` 原地覆盖，`paint` 返回新图。 |
| **`complex_to_real` 输出顺序** | 第一参数是实部 ImageReal，第二是虚部 ImageImaginary；做相位时记得 `phase = atan2(Im, Re)`。 |
| **域没设就 `select_gray`** | `select_gray` 依赖 Regions，先确保 Regions 非空、Image 与 Regions 对齐。 |
| **`tile_images` 显示截断** | 大图拼起来超分辨率时 `disp_image` 只显示一部分；用 `crop_part` 再切。 |

---

## 9. 完整签名速查表（44 ops）

### 9.1 全章汇总

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `area_center_gray` | Compute the area and center of gravity of a region in a gray value image. | `Regions, Image : : : Area, Row, Column` |
| `change_format` | Change image size. | `Image : ImagePart : Width, Height : ` |
| `cooc_feature_image` | Calculate a co-occurrence matrix and derive gray value features thereof. | `Regions, Image : : LdGray, Direction : Energy, Correlation, Homogeneity, Contrast` |
| `cooc_feature_matrix` | Calculate gray value features from a co-occurrence matrix. | `CoocMatrix : : : Energy, Correlation, Homogeneity, Contrast` |
| `complex_to_real` | Convert a complex image into two real images. | `ImageComplex : ImageReal, ImageImaginary : : ` |
| `convert_image_type` | Convert the type of an image. | `Image : ImageConverted : NewType : ` |
| `crop_domain` | Cut out of defined gray values. | `Image : ImagePart : : ` |
| `crop_domain_rel` | Cut out an image area relative to the domain. | `Image : ImagePart : Top, Left, Bottom, Right : ` |
| `crop_part` | Cut out one or more rectangular image areas. | `Image : ImagePart : Row, Column, Width, Height : ` |
| `crop_rectangle1` | Cut out one or more rectangular image areas. | `Image : ImagePart : Row1, Column1, Row2, Column2 : ` |
| `crop_rectangle2` | Cut out one or more arbitrarily oriented rectangular image areas. | `Image : ImagePart : Row, Column, Phi, Length1, Length2, AlignToAxis, Interpolation : ` |
| `elliptic_axis_gray` | Compute the orientation and major axes of a region in a gray value image. | `Regions, Image : : : Ra, Rb, Phi` |
| `entropy_gray` | Determine the entropy and anisotropy of images. | `Regions, Image : : : Entropy, Anisotropy` |
| `estimate_noise` | Estimate the image noise from a single image. | `Image : : Method, Percent : Sigma` |
| `fit_surface_first_order` | Calculate gray value moments and approximation by a first order surface (plane). | `Regions, Image : : Algorithm, Iterations, ClippingFactor : Alpha, Beta, Gamma` |
| `fit_surface_second_order` | Calculate gray value moments and approximation by a second order surface. | `Regions, Image : : Algorithm, Iterations, ClippingFactor : Alpha, Beta, Gamma, Delta, Epsilon, Zeta` |
| `fuzzy_entropy` | Determine the fuzzy entropy of regions. | `Regions, Image : : Apar, Cpar : Entropy` |
| `fuzzy_perimeter` | Calculate the fuzzy perimeter of a region. | `Regions, Image : : Apar, Cpar : Perimeter` |
| `gen_cooc_matrix` | Calculate the co-occurrence matrix of a region in an image. | `Regions, Image : Matrix : LdGray, Direction : ` |
| `gray_features` | Calculates gray value features for a set of regions. | `Regions, Image : : Features : Value` |
| `gray_histo` | Calculate the gray value distribution. | `Regions, Image : : : AbsoluteHisto, RelativeHisto` |
| `gray_histo_abs` | Calculate the gray value distribution. | `Regions, Image : : Quantization : AbsoluteHisto` |
| `gray_histo_range` | Calculate the gray value distribution of a single channel image within a certain gray value range. | `Regions, Image : : Min, Max, NumBins : Histo, BinSize` |
| `gray_projections` | Calculate horizontal and vertical gray-value projections. | `Region, Image : : Mode : HorProjection, VertProjection` |
| `histo_2dim` | Calculate the histogram of two-channel gray value images. | `Regions, ImageCol, ImageRow : Histo2Dim : : ` |
| `intensity` | Calculate the mean and deviation of gray values. | `Regions, Image : : : Mean, Deviation` |
| `min_max_gray` | Determine the minimum and maximum gray values within regions. | `Regions, Image : : Percent : Min, Max, Range` |
| `moments_gray_plane` | Calculate gray value moments and approximation by a plane. | `Regions, Image : : : MRow, MCol, Alpha, Beta, Mean` |
| `overpaint_gray` | Overpaint the gray values of an image. | `ImageDestination, ImageSource : : : ` |
| `overpaint_region` | Overpaint regions in an image. | `Image, Region : : Grayval, Type : ` |
| `paint_gray` | Paint the gray values of an image into another image. | `ImageSource, ImageDestination : MixedImage : : ` |
| `paint_region` | Paint regions into an image. | `Region, Image : ImageResult : Grayval, Type : ` |
| `paint_xld` | Paint XLD objects into an image. | `XLD, Image : ImageResult : Grayval : ` |
| `plane_deviation` | Calculate the deviation of the gray values from the approximating image plane. | `Regions, Image : : : Deviation` |
| `real_to_complex` | Convert two real images into a complex image. | `ImageReal, ImageImaginary : ImageComplex : : ` |
| `real_to_vector_field` | Convert two real-valued images into a vector field image. | `Row, Col : VectorField : Type : ` |
| `select_gray` | Select regions based on gray value features. | `Regions, Image : SelectedRegions : Features, Operation, Min, Max : ` |
| `set_grayval` | Set single gray values in an image. | `Image : : Row, Column, Grayval : ` |
| `shape_histo_all` | Determine a histogram of features along all threshold values. | `Region, Image : : Feature : AbsoluteHisto, RelativeHisto` |
| `shape_histo_point` | Determine a histogram of features along all threshold values. | `Region, Image : : Feature, Row, Column : AbsoluteHisto, RelativeHisto` |
| `tile_channels` | Tile multiple images into a large image. | `Image : TiledImage : NumColumns, TileOrder : ` |
| `tile_images` | Tile multiple image objects into a large image. | `Images : TiledImage : NumColumns, TileOrder : ` |
| `tile_images_offset` | Tile multiple image objects into a large image with explicit positioning information. | `Images : TiledImage : OffsetRow, OffsetCol, Row1, Col1, Row2, Col2, Width, Height : ` |
| `vector_field_to_real` | Convert a vector field image into two real-valued images. | `VectorField : Row, Col : : ` |

### 9.2 Features 子表（24）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `area_center_gray` | Compute the area and center of gravity of a region in a gray value image. | `Regions, Image : : : Area, Row, Column` |
| `cooc_feature_image` | Calculate a co-occurrence matrix and derive gray value features thereof. | `Regions, Image : : LdGray, Direction : Energy, Correlation, Homogeneity, Contrast` |
| `cooc_feature_matrix` | Calculate gray value features from a co-occurrence matrix. | `CoocMatrix : : : Energy, Correlation, Homogeneity, Contrast` |
| `elliptic_axis_gray` | Compute the orientation and major axes of a region in a gray value image. | `Regions, Image : : : Ra, Rb, Phi` |
| `entropy_gray` | Determine the entropy and anisotropy of images. | `Regions, Image : : : Entropy, Anisotropy` |
| `estimate_noise` | Estimate the image noise from a single image. | `Image : : Method, Percent : Sigma` |
| `fit_surface_first_order` | Calculate gray value moments and approximation by a first order surface (plane). | `Regions, Image : : Algorithm, Iterations, ClippingFactor : Alpha, Beta, Gamma` |
| `fit_surface_second_order` | Calculate gray value moments and approximation by a second order surface. | `Regions, Image : : Algorithm, Iterations, ClippingFactor : Alpha, Beta, Gamma, Delta, Epsilon, Zeta` |
| `fuzzy_entropy` | Determine the fuzzy entropy of regions. | `Regions, Image : : Apar, Cpar : Entropy` |
| `fuzzy_perimeter` | Calculate the fuzzy perimeter of a region. | `Regions, Image : : Apar, Cpar : Perimeter` |
| `gen_cooc_matrix` | Calculate the co-occurrence matrix of a region in an image. | `Regions, Image : Matrix : LdGray, Direction : ` |
| `gray_features` | Calculates gray value features for a set of regions. | `Regions, Image : : Features : Value` |
| `gray_histo` | Calculate the gray value distribution. | `Regions, Image : : : AbsoluteHisto, RelativeHisto` |
| `gray_histo_abs` | Calculate the gray value distribution. | `Regions, Image : : Quantization : AbsoluteHisto` |
| `gray_histo_range` | Calculate the gray value distribution of a single channel image within a certain gray value range. | `Regions, Image : : Min, Max, NumBins : Histo, BinSize` |
| `gray_projections` | Calculate horizontal and vertical gray-value projections. | `Region, Image : : Mode : HorProjection, VertProjection` |
| `histo_2dim` | Calculate the histogram of two-channel gray value images. | `Regions, ImageCol, ImageRow : Histo2Dim : : ` |
| `intensity` | Calculate the mean and deviation of gray values. | `Regions, Image : : : Mean, Deviation` |
| `min_max_gray` | Determine the minimum and maximum gray values within regions. | `Regions, Image : : Percent : Min, Max, Range` |
| `moments_gray_plane` | Calculate gray value moments and approximation by a plane. | `Regions, Image : : : MRow, MCol, Alpha, Beta, Mean` |
| `plane_deviation` | Calculate the deviation of the gray values from the approximating image plane. | `Regions, Image : : : Deviation` |
| `select_gray` | Select regions based on gray value features. | `Regions, Image : SelectedRegions : Features, Operation, Min, Max : ` |
| `shape_histo_all` | Determine a histogram of features along all threshold values. | `Region, Image : : Feature : AbsoluteHisto, RelativeHisto` |
| `shape_histo_point` | Determine a histogram of features along all threshold values. | `Region, Image : : Feature, Row, Column : AbsoluteHisto, RelativeHisto` |

### 9.3 Format 子表（9）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `change_format` | Change image size. | `Image : ImagePart : Width, Height : ` |
| `crop_domain` | Cut out of defined gray values. | `Image : ImagePart : : ` |
| `crop_domain_rel` | Cut out an image area relative to the domain. | `Image : ImagePart : Top, Left, Bottom, Right : ` |
| `crop_part` | Cut out one or more rectangular image areas. | `Image : ImagePart : Row, Column, Width, Height : ` |
| `crop_rectangle1` | Cut out one or more rectangular image areas. | `Image : ImagePart : Row1, Column1, Row2, Column2 : ` |
| `crop_rectangle2` | Cut out one or more arbitrarily oriented rectangular image areas. | `Image : ImagePart : Row, Column, Phi, Length1, Length2, AlignToAxis, Interpolation : ` |
| `tile_channels` | Tile multiple images into a large image. | `Image : TiledImage : NumColumns, TileOrder : ` |
| `tile_images` | Tile multiple image objects into a large image. | `Images : TiledImage : NumColumns, TileOrder : ` |
| `tile_images_offset` | Tile multiple image objects into a large image with explicit positioning information. | `Images : TiledImage : OffsetRow, OffsetCol, Row1, Col1, Row2, Col2, Width, Height : ` |

### 9.4 Manipulation 子表（6）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `overpaint_gray` | Overpaint the gray values of an image. | `ImageDestination, ImageSource : : : ` |
| `overpaint_region` | Overpaint regions in an image. | `Image, Region : : Grayval, Type : ` |
| `paint_gray` | Paint the gray values of an image into another image. | `ImageSource, ImageDestination : MixedImage : : ` |
| `paint_region` | Paint regions into an image. | `Region, Image : ImageResult : Grayval, Type : ` |
| `paint_xld` | Paint XLD objects into an image. | `XLD, Image : ImageResult : Grayval : ` |
| `set_grayval` | Set single gray values in an image. | `Image : : Row, Column, Grayval : ` |

### 9.5 Type Conversion 子表（5）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `complex_to_real` | Convert a complex image into two real images. | `ImageComplex : ImageReal, ImageImaginary : : ` |
| `convert_image_type` | Convert the type of an image. | `Image : ImageConverted : NewType : ` |
| `real_to_complex` | Convert two real images into a complex image. | `ImageReal, ImageImaginary : ImageComplex : : ` |
| `real_to_vector_field` | Convert two real-valued images into a vector field image. | `Row, Col : VectorField : Type : ` |
| `vector_field_to_real` | Convert a vector field image into two real-valued images. | `VectorField : Row, Col : : ` |

---

## 10. 一句话总结

> **Ch15 Image 下卷 = 图像的"分析 + 变换"四件套**：Features 算数值特征、Format 裁/拼、Manipulation 像素改写、Type Conversion 类型互换；共 44 ops，是把上卷得到的图"榨出信息 + 重塑形状"的全部工具。