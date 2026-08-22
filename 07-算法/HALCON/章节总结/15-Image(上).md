# 第 15 章 Image（上卷）· 图像的获取、构造、通道与域

> HALCON 20.11.1.0 Operator Reference — Image 章节上半部分
> **本卷 = 图像的"输入 + 组织"（Access / Acquisition / Channel / Creation / Domain，5 族 62 ops）**
> 下卷预告：图像的"分析 + 变换"（Features / Format / Manipulation / Type Conversion，4 族 44 ops）

---

## 0. 本卷定位

Image 是 HALCON 的**第一类对象**——所有测量、识别、3D 都从这里起步。本卷解决"图从哪儿来、图怎么拼、图的边界怎么算"：

- **Access（9）**：从已有图像对象里**读**——像素值、宽高、类型、内存指针。导出 C/C++ 时这些直接对应 `HImage::GetImage*()`。
- **Acquisition（14）**：从**相机/采集卡**实时取图。`open_framegrabber` / `grab_image` / `grab_data` 闭环，参数由 `set_framegrabber_param` 调整。
- **Channel（17）**：把多张单通道图**拼成多通道**（compose2~7、channels_to_image）或反向拆开（decompose2~7、image_to_channels）。HALCON 里"彩色图"本质是多通道。
- **Creation（16）**：**造**一张图——`gen_image_const` 给定值图、`gen_image_proto` 继承元数据、`region_to_bin/label/mean` 把 region 转 image、`gen_image_*_extern` 接管外部内存。
- **Domain（6）**：**域**——HALCON 里每个图像除了"像素"，还有一个 ROI/掩膜（域）。`reduce_domain` 把后续算子的运算范围限制在某个 Region 上，**绝大多数算子都要先 reduce_domain 才能避开背景噪声**。

> 一句话记忆：**Access 是看图，Acquisition 是取图，Channel 是拆/拼通道，Creation 是造图，Domain 是设"图上哪一块算数"。**

---

## 1. 五族速览

| 族 | 算子数 | 一句话定位 | 代表算子 |
|---|---|---|---|
| **Access** | 9 | 从已有图像读像素/元数据/指针 | `get_grayval` `get_image_pointer1` `get_image_size` `get_image_type` |
| **Acquisition** | 14 | 打开相机/采集卡、实时抓图 | `open_framegrabber` `grab_image` `grab_data` `close_framegrabber` `set_framegrabber_param` |
| **Channel** | 17 | 单通道 ↔ 多通道互转 | `compose2..7` `decompose2..7` `access_channel` `append_channel` `channels_to_image` |
| **Creation** | 16 | 凭空造一张图 / Region 转图 | `gen_image_const` `gen_image_proto` `region_to_bin` `region_to_label` `gen_image_surface_*` |
| **Domain** | 6 | 修改图像的定义域（ROI） | `reduce_domain` `full_domain` `change_domain` `get_domain` `rectangle1_domain` `add_channels` |
| **合计** | **62** | | |

---

## 2. 思维导图

![Ch15 Image 上卷 · 五族辐射图](./15-Image(上).png)

五个族均匀辐射：Access（蓝）/ Acquisition（绿）/ Channel（红）/ Creation（橙）/ Domain（紫）。
中心节点为本卷总名"图像 Image 上卷"，每族卡片包含族英文/中文/算子数三行摘要。

---

## 3. Access（访问已有图像）

### 3.1 何时用 Access

- 你已经有图，想知道**图本身**：宽高、类型、生成时间。
- 想读某个像素的灰度——`get_grayval` 单点 / `get_grayval_contour_xld` 沿 XLD 等距读 / `get_grayval_interpolated` 带插值。
- 导出 C/C++ 时为了**零拷贝接外部缓冲区**，用 `get_image_pointer1` / `get_image_pointer3` 取裸指针。

### 3.2 典型用法

```text
1) get_image_size(Image : : : Width, Height)
   ── 取尺寸
2) get_image_type(Image : : : Type)
   ── 取像素类型（byte / uint2 / real / int4 / …）
3) get_grayval(Image : : Row, Column : Grayval)
   ── 单像素灰度（HDevelop 的 `grayval := ...` 语法糖）
4) get_image_pointer1(Image : : : Pointer, Type, Width, Height)
   ── 取裸指针，传递给 C/C++ 外部库处理（仅 1 通道）
5) get_image_pointer3(ImageRGB : : : PointerRed, PointerGreen, PointerBlue, Type, Width, Height)
   ── 彩色图分通道指针
```

子线 `get_image_pointer1_rect`：**只返回 ROI（域）内的最小外接矩形**对应的指针与尺寸，适合外部算子只关心有效区域时减少传输。

### 3.3 注意事项

| 易踩坑 | 解释 |
|---|---|
| **row/col 越界** | `get_grayval` 行列超过图像大小返回 0；提前 `tuple_is_int_elem` 校验。 |
| **指针生命周期** | `get_image_pointer*` 返回的指针仅在该 Image 对象未 `clear_*` 前有效；不要外部库异步持有。 |
| **指针通道顺序** | RGB 是 R/G/B 分别三指针，**不是 BGR**——OpenCV 是 BGR 别搞混。 |
| **`get_image_time` 异常** | 部分读图路径没填时间字段，会返回 1970/0 时戳；别做精度比较。 |
| **`get_image_type` 返回字符串** | 是 `'byte'`/`'uint2'`/`'real'` 等字符串，配合 `if (Type = 'byte')` 即可分派。 |

---

## 4. Acquisition（相机/采集卡取图）

### 4.1 何时用 Acquisition

- 实时相机（GigE Vision / USB3 Vision / Camera Link / DirectShow / GenICam）拉流。
- 采集卡同时输出**图像 + 预处理 Region/Contour**（`grab_data`）。
- 异步抓图——前端采，后端处理（`grab_image_async` / `grab_data_async` / `grab_image_start`）。

### 4.2 标准 5 步流水线

```text
1) open_framegrabber(: : Name, HorizontalResolution, VerticalResolution,
                      ImageWidth, ImageHeight, StartRow, StartColumn,
                      Field, BitsPerChannel, ColorSpace, Generic,
                      ExternalTrigger, CameraType, Device, Port, LineIn : AcqHandle)
   ── 打开相机/接口；Name 例 'GigEVision' / 'File' / 'DirectShow'；Generic 是参数串
2) set_framegrabber_param(: : AcqHandle, Param, Value :)
   ── 调整曝光、增益、白平衡、触发模式等
   ── set_framegrabber_lut(: : AcqHandle, ImageRed, ImageGreen, ImageBlue :)
   ── 调整相机内嵌 LUT
3) set_framegrabber_callback(: : AcqHandle, CallbackType, CallbackFunction, UserContext :)
   ── 注册回调（事件驱动编程）
4) grab_image(: Image : AcqHandle :)
   ── 同步抓一帧；或 grab_image_async(: Image : AcqHandle, MaxDelay :)
   ── 异步：快门快，处理慢也跟得上；grab_image_start(: : AcqHandle, MaxDelay :)
   ── 单独启动采图
   ── grab_data(: Image, Region, Contours : AcqHandle : Data)
   ── 同步抓"图 + 预处理 Region + Contour + 元数据"（HALCON 自带解析）
5) close_framegrabber(: : AcqHandle :)
   ── 关闭（必做，否则相机被独占锁死）
```

辅助：
- `info_framegrabber(: : Name, Query : Information, ValueList)` — 查接口支持哪些参数/型号。
- `get_framegrabber_param(: : AcqHandle, Param : Value)` — 反查当前参数值。
- `get_framegrabber_callback(: : AcqHandle, CallbackType : CallbackFunction, UserContext)` / `get_framegrabber_lut(: : AcqHandle : ImageRed, ImageGreen, ImageBlue)` — 读回调与 LUT。

### 4.3 同步 vs 异步

```text
            grab_image（同步）          grab_image_async（异步）
   ┌───────────────────────┐    ┌───────────────────────────┐
   │  等待相机曝光完成       │    │ 触发后立刻返回，不阻塞      │
   │  读数据到内存          │    │ 等下次访问再读，未完成可续等 │
   └───────────────────────┘    └───────────────────────────┘
   简单流水线首选              高速运动 / 多相机并行 / 触发响应
```

### 4.4 注意事项

| 易踩坑 | 解释 |
|---|---|
| **Name 拼错** | `'GigEVision'` vs `'GigE Vision'` vs `'GigEVision2'`；`info_framegrabber` 先查。 |
| **`Device` 不对** | 工业相机常有 `device='00:0B:...'` 这种 MAC/序列号；`info_framegrabber` 列出所有。 |
| **ImageWidth/Height 与 ROI 冲突** | 这两个参数设的不是"ROI"而是"输出图像大小"；ROI 用 `StartRow/StartColumn`。 |
| **Field = ' interlaced' 不分场** | 隔行相机忘记设 `'interlaced'` 会得到锯齿；设 `'both'`/`'first'`/`'second'` 分清。 |
| **颜色空间不对** | `'rgb'` vs `'bayer'` vs `'yuv'` 决定 HALCON 是否做内插解码；错配出现彩色花屏。 |
| **触发模式** | `ExternalTrigger='true'` 后必须给硬件触发信号，否则一直阻塞。 |
| **忘记 close** | 进程退出未 close 会让相机被独占占用，下次重连失败。 |

---

## 5. Channel（通道拆分/合并）

### 5.1 何时用 Channel

- 拿到的多通道图，想**只处理一个通道**（如 RGB 中只取 R 通道做阈值）→ `decompose` / `access_channel` / `image_to_channels`。
- 想把多张单通道图**拼成一张多通道**（如不同传感器、不同波段）→ `compose` / `channels_to_image` / `interleave_channels`。
- 想在多通道图上**追加一个新通道**（如彩色 + 深度）→ `append_channel`。

### 5.2 拆分与合并速记

```text
  单通道图  ──── compose2..7 / channels_to_image ────►  多通道图
  (Image1..N)                                          (MultiChannelImage)
       ▲                                                     │
       │                                                     ▼
  decompose2..7 / image_to_channels / access_channel  (读其中某通道)
                                                          单/多通道图
```

- `compose<N>` 与 `decompose<N>` 是**固定 N 个通道**的便捷版（最高 7）。
- `channels_to_image` / `image_to_channels` 是**通用版**——把一个 1×N tuple 输入，输出多通道图（或反之）。
- `interleave_channels` 是**通用版的字节交错版**——把多通道包装成 `PixelFormat='rgba'` 这种 RGB 字节序列；用于保存为 PNG/JPEG 原始数据。
- `access_channel(MultiChannelImage : Image : Channel :)`：**不复制内存**，只换视图——索引 0~N-1；最快。
- `append_channel(MultiChannelImage, Image : ImageExtended :)`：把 `Image` 追加为新通道。
- `count_channels(MultiChannelImage : : : Channels)`：取通道数。

### 5.3 注意事项

| 易踩坑 | 解释 |
|---|---|
| **N 不匹配** | `compose3` 喂 4 张图会崩；要么改用 `channels_to_image` 喂 N 元组。 |
| **Image 类型不一致** | 各输入图必须**同类型**（都 byte 或都 real）；否则 HALCON 静默取高类型。 |
| **`decompose2` vs `access_channel`** | 性能上 `access_channel` 零拷贝；`decompose` 会复制内存到新图对象。 |
| **`channels_to_image` 反向** | 输入是单通道图 tuple `(Image1, Image2, Image3)` → 输出多通道；输入顺序对应通道顺序。 |
| **彩色 vs 多通道** | `'rgb'` 3 通道图、`'rgba'` 4 通道图、`'hsv'` 3 通道图都是多通道图；语义不同但都进 decompose。 |
| **`interleave_channels` 的 PixelFormat** | `'rgb'`/`'bgr'`/`'rgba'`/`'bgra'`/`'abgr'`/`'argb'` 顺序决定字节布局。 |

---

## 6. Creation（造图）

### 6.1 何时用 Creation

- 测试/调试时造一张**已知值的图**做夹具：`gen_image_const` / `gen_image_proto`。
- 从**外部内存**接管 HALCON 图——`gen_image1` / `gen_image1_extern` / `gen_image1_rect`。
- 彩色图从外部交错字节接管——`gen_image_interleaved`。
- 造**带斜率/曲面的灰度图**做配准测试——`gen_image_surface_first_order` / `gen_image_surface_second_order` / `gen_image_gray_ramp`。
- 把 **Region 转 Image**：`region_to_bin`（0/1 图）/ `region_to_label`（每 region 一号灰度）/ `region_to_mean`（每 region 内像素平均值）。
- `copy_image`：图复制（独立内存）。
- `interleave_channels`：见上一节，**打包多通道为字节交错**。

### 6.2 4 类造图速记

| 类型 | 函数 | 用途 |
|---|---|---|
| **常量图** | `gen_image_const` / `gen_image_proto` | 给定值图；proto 继承原图的域 |
| **接管外部内存** | `gen_image1` / `gen_image1_extern` / `gen_image1_rect` | 接管 C/C++ 像素 buffer，零拷贝 |
| **造测试图** | `gen_image_gray_ramp` / `gen_image_surface_first_order` / `gen_image_surface_second_order` | 灰度斜坡/一阶平面/二阶曲面 |
| **Region 转图** | `region_to_bin` / `region_to_label` / `region_to_mean` | Region 形态 → 像素图 |

### 6.3 注意事项

| 易踩坑 | 解释 |
|---|---|
| **`gen_image1` 不释放** | `gen_image1` 不会接管 buffer 所有权；`_extern` 版本才会。 |
| **`PixelPointer` 类型对齐** | `gen_image1` 拿到的 C 数组必须按 4/8/16-byte 对齐，否则 HALCON 段错误。 |
| **`gen_image_surface_*` 的 α/β/γ/δ/ε/ζ** | 一阶曲面 `f(r,c) = α + β*r + γ*c`；二阶多 δ/ε/ζ 三项二次项。 |
| **`region_to_label` 的 Type** | 类别数 ≤ 256 用 `byte`，否则 `uint2`/`int4`——按 region 数选。 |
| **`region_to_bin` 的 ForegroundGray/BackgroundGray** | 默认 0/255；要前景 1 / 背景 0 显式设。 |
| **`gen_image_interleaved` 的 BitsPerChannel / BitShift** | 12 位 Bayer 数据时通常 `bits_per_channel=16, bit_shift=4`。 |

---

## 7. Domain（域）

### 7.1 何时用 Domain

- **绝大多数算子在 reduce_domain 后只在 ROI 内运算**——这是 HALCON 处理"非矩形对象"的根本机制。
- `get_domain(Image : Domain :)` 把域取出来作为 Region。
- `full_domain` 把域扩到全图（消除之前 reduce_domain 的影响）。
- `change_domain` 直接把域换成一个 Region（保留原图像素值不变）。
- `rectangle1_domain` 快速把域设成给定矩形。
- `add_channels` 把 Region 的灰度值叠加到 Image 上作为"灰度 Region"——其实是把 0 像素设为特定灰度。

### 7.2 reduce_domain 是 HALCON 的 ROI 工具

```text
                全图 Image
                     │
                     ▼ reduce_domain(Image, Region)
                ┌─────────┐
                │ 域=Region│   ← 后续算子只在这块"算"
                │ 其他区域 │     "其他区域" 像素值仍存在，但被忽略
                └─────────┘
```

应用：
- 减少后续算子计算量。
- 屏蔽背景噪声。
- 多 ROI 轮流处理（多次 reduce_domain + 同一段流程）。

### 7.3 注意事项

| 易踩坑 | 解释 |
|---|---|
| **域太大** | `reduce_domain` 后算子依然遍历所有像素——域设小了才会省算力。 |
| **域=空 Region** | 给空 Region 时算子返回空结果；先 `test_region` 或判 `count_obj`。 |
| **`change_domain` vs `reduce_domain`** | `change_domain` **不改图像内容**只换域；`reduce_domain` 删掉域外像素。 |
| **`add_channels` 误解** | 它把 region 当成"灰度图"：region 内 = ForegroundGray, region 外 = BackgroundGray。 |
| **`rectangle1_domain` 行/列边界** | 矩形坐标按图像坐标，不是域坐标；用 `Row1,Column1,Row2,Column2`。 |
| **`get_domain` 返回 Region** | 域是 Region；要用面积或形状就 `area_center` 或 `get_region_*`。 |

---

## 8. 通用工作流（跨族）

```text
        ┌────────── Acquisition (相机/采集卡) ──────────┐
        │    open_framegrabber → grab_image → close    │
        └─────────────────────┬────────────────────────┘
                              │
                  ┌───────────▼────────────┐
                  │   原始图 Image（多通道）│
                  └───────────┬────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        Domain（域/ROI）   Channel（拆/拼）  Creation（造图）
        reduce_domain     decompose3      gen_image_const
        full_domain       compose3        region_to_bin
                              │               │
                              ▼               ▼
                       ┌─────────────────────────┐
                       │  处理后的单通道图/ROI图  │
                       └─────────────────────────┘
                              │
                              ▼
                    Access（读像素/取元数据）
                    get_grayval / get_image_size
```

---

## 9. 常见误区

| 误区 | 正确做法 |
|---|---|
| **彩色图直接阈值** | 多通道图要先 `decompose3` 拆成 R/G/B 单通道再阈，或 `trans_from_rgb` 转 HSV 后取 V 通道。 |
| **忘 close_framegrabber** | 每个 open 必须有 close；推荐 try-finally 包裹。 |
| **reduce_domain(Image, EmptyRegion)** | 全域 reduce 等价于 no-op，但后续算子返回空结果——`full_domain` 撤销。 |
| **图尺寸不变就能直接拼** | `compose` 要求同尺寸同类型；用 `crop_part` / `zoom_image_factor` 对齐。 |
| **域 vs Region 混淆** | Image 的域本质上是一个 Region；`reduce_domain` 等于"裁出 region 内的图像"。 |
| **用 gen_image_const 造大图太慢** | 别用真实采集的图像做循环测试，`gen_image_const` 给小图 1×1 也能跑（域缩到点）。 |
| **指针记得清** | `get_image_pointer*` 拿到的指针仅在本 Image 未释放前有效；不要存到 `global_tuple`。 |

---

## 10. 完整签名速查表（62 ops）

### 10.1 Access 子表（9）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `get_grayval` | Access the gray values of an image object. | `Image : : Row, Column : Grayval` |
| `get_grayval_contour_xld` | Return gray values of an image at the positions of an XLD contour. | `Image, Contour : : Interpolation : Grayval` |
| `get_grayval_interpolated` | Return gray values of an image at the positions given by tuples of rows and columns. | `Image : : Row, Column, Interpolation : Grayval` |
| `get_image_pointer1` | Access the pointer of a channel. | `Image : : : Pointer, Type, Width, Height` |
| `get_image_pointer1_rect` | Access to the image data pointer and the image data inside the smallest rectangle of the domain of the input image. | `Image : : : PixelPointer, Width, Height, VerticalPitch, HorizontalBitPitch, BitsPerPixel` |
| `get_image_pointer3` | Access the pointers of a colored image. | `ImageRGB : : : PointerRed, PointerGreen, PointerBlue, Type, Width, Height` |
| `get_image_size` | Return the size of an image. | `Image : : : Width, Height` |
| `get_image_time` | Request time at which the image was created. | `Image : : : MSecond, Second, Minute, Hour, Day, YDay, Month, Year` |
| `get_image_type` | Return the type of an image. | `Image : : : Type` |

### 10.2 Acquisition 子表（14）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `close_framegrabber` | Close specified image acquisition device. | ` : : AcqHandle : ` |
| `get_framegrabber_callback` | Query callback function of an image acquisition device. | ` : : AcqHandle, CallbackType : CallbackFunction, UserContext` |
| `get_framegrabber_lut` | Query look-up table of the image acquisition device. | ` : : AcqHandle : ImageRed, ImageGreen, ImageBlue` |
| `get_framegrabber_param` | Query specific parameters of an image acquisition device. | ` : : AcqHandle, Param : Value` |
| `grab_data` | Synchronous grab of images and preprocessed image data from the specified image acquisition device. | ` : Image, Region, Contours : AcqHandle : Data` |
| `grab_data_async` | Asynchronous grab of images and preprocessed image data from the specified image acquisition device. | ` : Image, Region, Contours : AcqHandle, MaxDelay : Data` |
| `grab_image` | Synchronous grab of an image from the specified image acquisition device. | ` : Image : AcqHandle : ` |
| `grab_image_async` | Asynchronous grab of an image from the specified image acquisition device. | ` : Image : AcqHandle, MaxDelay : ` |
| `grab_image_start` | Start an asynchronous grab from the specified image acquisition device. | ` : : AcqHandle, MaxDelay : ` |
| `info_framegrabber` | Query information about the specified image acquisition interface. | ` : : Name, Query : Information, ValueList` |
| `open_framegrabber` | Open and configure an image acquisition device. | ` : : Name, HorizontalResolution, VerticalResolution, ImageWidth, ImageHeight, StartRow, StartColumn, Field, BitsPerChannel, ColorSpace, Generic, ExternalTrigger, CameraType, Device, Port, LineIn : AcqHandle` |
| `set_framegrabber_callback` | Register a callback function for an image acquisition device. | ` : : AcqHandle, CallbackType, CallbackFunction, UserContext : ` |
| `set_framegrabber_lut` | Set look-up table of the image acquisition device. | ` : : AcqHandle, ImageRed, ImageGreen, ImageBlue : ` |
| `set_framegrabber_param` | Set specific parameters of an image acquisition device. | ` : : AcqHandle, Param, Value : ` |

### 10.3 Channel 子表（17）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `access_channel` | Access a channel of a multi-channel image. | `MultiChannelImage : Image : Channel : ` |
| `append_channel` | Append additional matrices (channels) to the image. | `MultiChannelImage, Image : ImageExtended : : ` |
| `channels_to_image` | Convert one-channel images into a multi-channel image | `Images : MultiChannelImage : : ` |
| `compose2` | Convert two images into a two-channel image. | `Image1, Image2 : MultiChannelImage : : ` |
| `compose3` | Convert 3 images into a three-channel image. | `Image1, Image2, Image3 : MultiChannelImage : : ` |
| `compose4` | Convert 4 images into a four-channel image. | `Image1, Image2, Image3, Image4 : MultiChannelImage : : ` |
| `compose5` | Convert 5 images into a five-channel image. | `Image1, Image2, Image3, Image4, Image5 : MultiChannelImage : : ` |
| `compose6` | Convert 6 images into a six-channel image. | `Image1, Image2, Image3, Image4, Image5, Image6 : MultiChannelImage : : ` |
| `compose7` | Convert 7 images into a seven-channel image. | `Image1, Image2, Image3, Image4, Image5, Image6, Image7 : MultiChannelImage : : ` |
| `count_channels` | Count channels of image. | `MultiChannelImage : : : Channels` |
| `decompose2` | Convert a two-channel image into two images. | `MultiChannelImage : Image1, Image2 : : ` |
| `decompose3` | Convert a three-channel image into three images. | `MultiChannelImage : Image1, Image2, Image3 : : ` |
| `decompose4` | Convert a four-channel image into four images. | `MultiChannelImage : Image1, Image2, Image3, Image4 : : ` |
| `decompose5` | Convert a five-channel image into five images. | `MultiChannelImage : Image1, Image2, Image3, Image4, Image5 : : ` |
| `decompose6` | Convert a six-channel image into six images. | `MultiChannelImage : Image1, Image2, Image3, Image4, Image5, Image6 : : ` |
| `decompose7` | Convert a seven-channel image into seven images. | `MultiChannelImage : Image1, Image2, Image3, Image4, Image5, Image6, Image7 : : ` |
| `image_to_channels` | Convert a multi-channel image into One-channel images | `MultiChannelImage : Images : : ` |

### 10.4 Creation 子表（16）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `copy_image` | Copy an image and allocate new memory for it. | `Image : DupImage : : ` |
| `gen_image1` | Create an image from a pointer to the pixels. | ` : Image : Type, Width, Height, PixelPointer : ` |
| `gen_image1_extern` | Create an image from a pointer on the pixels with storage management. | ` : Image : Type, Width, Height, PixelPointer, ClearProc : ` |
| `gen_image1_rect` | Create an image with a rectangular domain from a pointer on the pixels (with storage management). | ` : Image : PixelPointer, Width, Height, VerticalPitch, HorizontalBitPitch, BitsPerPixel, DoCopy, ClearProc : ` |
| `gen_image3` | Create an image from three pointers to the pixels (red/green/blue). | ` : ImageRGB : Type, Width, Height, PixelPointerRed, PixelPointerGreen, PixelPointerBlue : ` |
| `gen_image3_extern` | Create a three-channel image from three pointers on the pixels with storage management. | ` : Image : Type, Width, Height, PointerRed, PointerGreen, PointerBlue, ClearProc : ` |
| `gen_image_const` | Create an image with constant gray value. | ` : Image : Type, Width, Height : ` |
| `gen_image_gray_ramp` | Create a gray value ramp. | ` : ImageGrayRamp : Alpha, Beta, Mean, Row, Column, Width, Height : ` |
| `gen_image_interleaved` | Create a three-channel image from a pointer to the interleaved pixels. | ` : ImageRGB : PixelPointer, ColorFormat, OriginalWidth, OriginalHeight, Alignment, Type, ImageWidth, ImageHeight, StartRow, StartColumn, BitsPerChannel, BitShift : ` |
| `gen_image_proto` | Create an image with a specified constant gray value. | `Image : ImageCleared : Grayval : ` |
| `gen_image_surface_first_order` | Create a tilted gray surface with first order polynomial. | ` : ImageSurface : Type, Alpha, Beta, Gamma, Row, Column, Width, Height : ` |
| `gen_image_surface_second_order` | Create a curved gray surface with second order polynomial. | ` : ImageSurface : Type, Alpha, Beta, Gamma, Delta, Epsilon, Zeta, Row, Column, Width, Height : ` |
| `interleave_channels` | Create an interleaved image from a multichannel image. | `MultichannelImage : InterleavedImage : PixelFormat, RowBytes, Alpha : ` |
| `region_to_bin` | Convert a region into a binary byte-image. | `Region : BinImage : ForegroundGray, BackgroundGray, Width, Height : ` |
| `region_to_label` | Convert regions to a label image. | `Region : ImageLabel : Type, Width, Height : ` |
| `region_to_mean` | Paint regions with their average gray value. | `Regions, Image : ImageMean : : ` |

### 10.5 Domain 子表（6）

| 算子 | 一句话功能 | HDevelop 签名 |
|---|---|---|
| `add_channels` | Add gray values to regions. | `Regions, Image : GrayRegions : : ` |
| `change_domain` | Change definition domain of an image. | `Image, NewDomain : ImageNew : : ` |
| `full_domain` | Expand the domain of an image to maximum. | `Image : ImageFull : : ` |
| `get_domain` | Get the domain of an image. | `Image : Domain : : ` |
| `rectangle1_domain` | Reduce the domain of an image to a rectangle. | `Image : ImageReduced : Row1, Column1, Row2, Column2 : ` |
| `reduce_domain` | Reduce the domain of an image. | `Image, Region : ImageReduced : : ` |

---

## 11. 一句话总结

> **Ch15 Image 上卷 = 图像的"输入与组织"五件套**：Access 看图、Acquisition 取图、Channel 拆拼通道、Creation 造图、Domain 设 ROI；共 62 ops，全部围绕"图从哪儿来、怎么拼、边界怎么算"。