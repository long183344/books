# 第 25 章 Tools · 上卷：背景估计与 1D 函数（32 算子 · 2 子族）

> **HALCON 官方手册第 25 章 Tools** 全章 8 子族 103 算子——HALCON 的 **数学小工具箱**，覆盖 1D 函数处理、背景建模、Hough 变换、Hypot 插值、栅格矫正等 miscellaneous 数学/几何 工具。

> **上卷 2 子族 32 算子** = Background Estimator(7) + Function(25)——**视频流建模 + 1D 信号处理**。两套算子在 HALCON 中是并列且互相独立的：前者专攻像素时间序列、后者专攻标量一维曲线。

> 一句话总结：**本卷的本质 = HALCON 与 非图像 数学对象打交道的双门神。**

---

## 1. 全卷结构：2 子族总览

| 子族 | 算子数 | 一句话功能 | 典型场景 |
|---|---|---|---|
| **① Background Estimator** | 7 | Kalman 自适应背景建模 + 运动前景输出 | 工业产线视频流运动检测 |
| **② Function（1D）** | 25 | 1D 函数构造/变换/分析/存取全套 | 传感器曲线/轮廓投影/采样序列 |

**与中/下卷的分工**：

- **上卷（本卷）** = 视频流 + 1D 信号（最 数学 的两族）
- **中卷**（待做）= Geometry(42) —— 几何基元构造/分区/拟合/凸壳/三角化
- **下卷**（待做）= Grid Rectification(5) + Hough(7) + Interpolation(5) + Lines(2) + Mosaicking(10) = 29 — 栅格/Hough/插值/线条/马赛克

---

## 2. 2 子族分述（详细模式）

### ②1 背景估计器（Background Estimator）（7 算子）

> **背景估计：用 Kalman 滤波 + 多参数自适应更新 在视频流中实时建模背景，输出当前帧的前景区域——典型应用是工业产线视频流中的运动目标检测，相比传统帧差法/平均法对光照抖动更鲁棒。**


**用途**：视频流背景建模与运动检测——自动适配光照渐变（GainMode auto）和场景突变（GainMode fixed），返回前景区域每像素已知 vs 未知。


| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **close_bg_esti** | close_bg_esti deletes the background estimation data set and releases  · `close_bg_esti( : : BgEstiHandle : )` |
| **create_bg_esti** | create_bg_esti creates a new data set for the background estimation an · `create_bg_esti(InitializeImage : : Syspar1, Syspar2, GainMode, Gain1, Gain2, AdaptMode, MinDiff, StatNum, ConfidenceC, TimeC : BgEstiHandle)` |
| **get_bg_esti_params** | get_bg_esti_params returns the parameters of the data set. The returne · `get_bg_esti_params( : : BgEstiHandle : Syspar1, Syspar2, GainMode, Gain1, Gain2, AdaptMode, MinDiff, StatNum, ConfidenceC, TimeC)` |
| **give_bg_esti** | give_bg_esti returns the estimated background image of the current BgE · `give_bg_esti( : BackgroundImage : BgEstiHandle : )` |
| **run_bg_esti** | run_bg_esti adapts the background image stored in the BgEsti data set  · `run_bg_esti(PresentImage : ForegroundRegion : BgEstiHandle : )` |
| **set_bg_esti_params** | set_bg_esti_params is used to change the parameters of the data set. T · `set_bg_esti_params( : : BgEstiHandle, Syspar1, Syspar2, GainMode, Gain1, Gain2, AdaptMode, MinDiff, StatNum, ConfidenceC, TimeC : )` |
| **update_bg_esti** | update_bg_esti overwrites the image stored in the current BgEsti data  · `update_bg_esti(PresentImage, UpDateRegion : : BgEstiHandle : )` |

**重点算子注记**：

- **`close_bg_esti`** — 参数：`**0 入参** — : : BgEstiHandle`
  - 误区：[1] BgEstiHandle 不能 close 后再用 — 解引用即作废.
  - [2] 关闭后 give_bg_esti 等会触发异常.
  - [3] HALCON 没有显式 close_all_bg_esti，循环关闭所有 create 出来的 handle 即可.
- **`create_bg_esti`** — 参数：`**10 参数** — InitializeImage(初始预测), Syspar1/Syspar2(系统噪声), GainMode(['fixed', 'onion', 'onion2', 'auto']), Gain1/Gain2(更新增益 0~1), AdaptMode(['on', 'off']), MinDiff(像素阈值), StatNum(静止帧数阈值), ConfidenceC, TimeC — BgEstiHandle`
  - 误区：[1] GainMode='auto' 是动态学习率 — 静态场景会出现渐变伪影.
  - [2] Syspar1/Syspar2 越大越能跟踪快速变化，但噪声敏感.
  - [3] 同一个 BgEstiHandle 可多路 PresentImage 串行喂入（视频流）.
- **`get_bg_esti_params`** — 参数：`**2 参数** — GenParamName: GenParamValue — : BgEstiHandle`
  - 误区：[1] 参数名跟 set_bg_esti_params 完全对偶.
  - [2] 用于运行时可视化参数 — 比如打印 gain_1 看自适应学习率变化.
- **`give_bg_esti`** — 参数：`**0 入参** — : EstimatedBackgroundImage: BgEstiHandle`
  - 误区：[1] 返回的是当前估计的背景图像 — 跟 PresentImage 同尺寸.
  - [2] 必须先 create + run 才能 give，否则崩.
  - [3] 想看历史背景可以用 get_bg_esti_params 读取 StateGrad/StateMean.
- **`run_bg_esti`** — 参数：`**3 参数** — PresentImage(当前帧): ForegroundRegion(输出前景区域): BgEstiHandle`
  - 误区：[1] PresentImage 与 InitializeImage 必须是同尺寸同类型.
  - [2] 输出的 ForegroundRegion 是所有未知像素（大于 MinDiff 还没被纳入背景）.
  - [3] 多个 BgEstiHandle 之间互不影响（线程安全）.
- **`set_bg_esti_params`** — 参数：`**2 参数** — GenParamName (gain_mode/gain_1/gain_2/syspar_1/syspar_2/min_diff/stat_num/confidence_c/time_c/adapt_mode): GenParamValue — BgEstiHandle`
  - 误区：[1] 参数名用字符串（不是数值枚举）.
  - [2] 修改 gain_mode 后建议重置 StatNum.
  - [3] 修改 min_diff 会立即影响 run_bg_esti 阈值.
- **`update_bg_esti`** — 参数：`**3 参数** — PresentImage, UpdatesGainedImage: : BgEstiHandle`
  - 误区：[1] PresentImage 是输入帧 — 用于反馈训练背景但不输出前景.
  - [2] UpdatesGainedImage 是要学习的二值 mask（=1 的像素被认为前景，不参与背景更新）— 相当于半监督忽略运动.
  - [3] 配合 run_bg_esti 一起用：先用 run 检测，再用 update 把真正的永久背景灌进去.

---

### ②2 1D 函数（Function 1D）（25 算子）

> **1D 离散函数：一维 y=f(x) 曲线的构造、变换、积分、求导、平滑、极值、文件 IO 全套——是 HALCON 里处理一维信号（传感器曲线、轮廓投影、采样序列）的专用工具集，与 tuple 类似但语义上是数学意义上的 函数 ，能直接 smooth/integrate/derivate。**


**用途**：1D 信号处理——从零构造（pairs/array）、变换（compose/transform/negate/invert）、分析（integrate/derivate/zero_crossings/local_min_max）、平滑（gauss/mean）、存取（read/write/scale_y）全栈。


| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **abs_funct_1d** | abs_funct_1d calculates the absolute values of all y values of Functio · `abs_funct_1d( : : Function : FunctionAbsolute)` |
| **compose_funct_1d** | compose_funct_1d composes two functions, i.e., calculates ComposedFunc · `compose_funct_1d( : : Function1, Function2, Border : ComposedFunction)` |
| **create_funct_1d_array** | create_funct_1d_array creates a one-dimensional function from a set of · `create_funct_1d_array( : : YValues : Function)` |
| **create_funct_1d_pairs** | create_funct_1d_pairs creates a one-dimensional function from a set of · `create_funct_1d_pairs( : : XValues, YValues : Function)` |
| **derivate_funct_1d** | derivate_funct_1d calculates the derivatives of the function Function  · `derivate_funct_1d( : : Function, Mode : Derivative)` |
| **distance_funct_1d** | distance_funct_1d calculates the distance of two functions. The two fu · `distance_funct_1d( : : Function1, Function2, Mode, Sigma : Distance)` |
| **funct_1d_to_pairs** | funct_1d_to_pairs splits the input function Function into tuples for t · `funct_1d_to_pairs( : : Function : XValues, YValues)` |
| **get_pair_funct_1d** | get_pair_funct_1d accesses a function value of Function . This is done · `get_pair_funct_1d( : : Function, Index : X, Y)` |
| **get_y_value_funct_1d** | get_y_value_funct_1d returns the y value of the function Function at t · `get_y_value_funct_1d( : : Function, X, Border : Y)` |
| **integrate_funct_1d** | integrate_funct_1d integrates the function Function (see create_funct_ · `integrate_funct_1d( : : Function : Positive, Negative)` |
| **invert_funct_1d** | invert_funct_1d calculates the inverse function of the input function  · `invert_funct_1d( : : Function : InverseFunction)` |
| **local_min_max_funct_1d** | local_min_max_funct_1d searches for the local minima Min and maxima Ma · `local_min_max_funct_1d( : : Function, Mode, Interpolation : Min, Max)` |
| **match_funct_1d_trans** | match_funct_1d_trans calculates the transformation parameters between  · `match_funct_1d_trans( : : Function1, Function2, Border, ParamsConst, UseParams : Params, ChiSquare, Covar)` |
| **negate_funct_1d** | negate_funct_1d negates all y values of Function . · `negate_funct_1d( : : Function : FunctionInverted)` |
| **num_points_funct_1d** | num_points_funct_1d calculates the number of control points of Functio · `num_points_funct_1d( : : Function : Length)` |
| **read_funct_1d** | The operator read_funct_1d reads the contents of FileName and converts · `read_funct_1d( : : FileName : Function)` |
| **sample_funct_1d** | sample_funct_1d samples the input function Function in the interval [  · `sample_funct_1d( : : Function, XMin, XMax, XDist, Border : SampledFunction)` |
| **scale_y_funct_1d** | scale_y_funct_1d multiplies and adds the y values of Function with the · `scale_y_funct_1d( : : Function, Mult, Add : FunctionScaled)` |
| **smooth_funct_1d_gauss** | The operator smooth_funct_1d_gauss smooths a one-dimensional function  · `smooth_funct_1d_gauss( : : Function, Sigma : SmoothedFunction)` |
| **smooth_funct_1d_mean** | The operator smooth_funct_1d_mean smooths a one dimensional function b · `smooth_funct_1d_mean( : : Function, SmoothSize, Iterations : SmoothedFunction)` |
| **transform_funct_1d** | transform_funct_1d transforms the input function Function using the tr · `transform_funct_1d( : : Function, Params : TransformedFunction)` |
| **write_funct_1d** | The operator write_funct_1d writes the contents of Function to a file. · `write_funct_1d( : : Function, FileName : )` |
| **x_range_funct_1d** | x_range_funct_1d calculates the smallest and the largest x value of Fu · `x_range_funct_1d( : : Function : XMin, XMax)` |
| **y_range_funct_1d** | y_range_funct_1d calculates the smallest and the largest y value of Fu · `y_range_funct_1d( : : Function : YMin, YMax)` |
| **zero_crossings_funct_1d** | zero_crossings_funct_1d calculates the zero crossings ZeroCrossings of · `zero_crossings_funct_1d( : : Function : ZeroCrossings)` |

**重点算子注记**：

- **`abs_funct_1d`** — 参数：`**2 参数** — Function(1D 函数): AbsFunction — :`
  - 误区：[1] 输出函数与输入同 x-range 同采样点数.
  - [2] 与 negate_funct_1d 同类，但 abs 把 y < 0 部分翻上去.
  - [3] 零函数 abs 后仍是零函数.
- **`compose_funct_1d`** — 参数：`**3 参数** — Function1, Function2, Border ([zero, constant, mirror, cyclic]): ComposedFunction`
  - 误区：[1] 嵌套复合 y = f(g(x))，不是 y = f(x) + g(x).
  - [2] Border 只在 Function1 跑到 Function2 定义域外时生效.
  - [3] 等 x 范围才能 compose（采样点可不同）.
- **`create_funct_1d_array`** — 参数：`**2 参数** — YValues(等距采样点的 y 值数组): X — Function`
  - 误区：[1] YValues 长度 ≥ 2 — 1 个点不算函数.
  - [2] X 自动推算为 0..N-1 的等差序列.
  - [3] 等距采样 — 非等距用 create_funct_1d_pairs.
- **`create_funct_1d_pairs`** — 参数：`**2 参数** — XValues, YValues — Function`
  - 误区：[1] 任意 x 间隔（不必等距）.
  - [2] X 和 Y 必须等长.
  - [3] HALCON 函数是连续插值 — 两点之间自动线性.
- **`derivate_funct_1d`** — 参数：`**2 参数** — Function: Derivative — :`
  - 误区：[1] 用中心差分求导.
  - [2] 端点用线性外推.
  - [3] 输出与输入同 x-range — 不同于 xy_range_funct_1d 后再 derivate.
- **`distance_funct_1d`** — 参数：`**3 参数** — Function1, Function2: Distance — :`
  - 误区：[1] 算的是 L2 距离平方和积分（不归一化）.
  - [2] Function1/Function2 必须同 x-range 同采样.
  - [3] 与 compose_funct_1d 的 f(g(x)) 完全不同 — 距离越小说明两个函数越相似.
- **`funct_1d_to_pairs`** — 参数：`**2 参数** — Function: X, Y — :`
  - 误区：[1] 把等距采样的 Function 转回离散点对.
  - [2] 输出 X/Y 是 HTuple 数组.
  - [3] 与 create_funct_1d_pairs 互逆.
- **`get_pair_funct_1d`** — 参数：`**3 参数** — Function, Index(索引): X, Y — :`
  - 误区：[1] Index 从 0 开始 — 超界报异常.
  - [2] 等距采样时 x = X0 + Index*Step.
  - [3] 与 funct_1d_to_pairs 的整列抽取相比，这个算子是索引随机访问.
- **`get_y_value_funct_1d`** — 参数：`**3 参数** — Function, X(任意 x): Y — :`
  - 误区：[1] 任意 x（含小数、非采样点）— 自动线性插值.
  - [2] 超过定义域返回 0（除非 compose_funct_1d 时 Border='cyclic' 之类）.
  - [3] 与 get_pair_funct_1d 的整数索引不同 — 这是连续采样.
- **`integrate_funct_1d`** — 参数：`**2 参数** — Function: IntegralFunction — :`
  - 误区：[1] 计算累计分布 / Riemann 和 ∫f(x)dx.
  - [2] 输出同 x-range，y 是从原点累计的面积.
  - [3] 与 derivate_funct_1d 大致互逆（差一个常数）.
- **`invert_funct_1d`** — 参数：`**3 参数** — Function, Border ([zero, constant, mirror, cyclic]): InverseFunction`
  - 误区：[1] 算反函数 y=x 对折 — 严格单调函数才完全可逆.
  - [2] 同值水平段（如 y=1 平台）会折叠丢失.
  - [3] 输出 x-range 是原函数的 y-range，y-range 是原函数的 x-range — 变量互换.
- **`local_min_max_funct_1d`** — 参数：`**3 参数** — Function, Mode ([strict_min, strict_max, plateau_min, plateau_max, all_min, all_max]): Min, Max — :`
  - 误区：[1] strict vs plateau — strict 只取单点极值，plateau 是整个平台.
  - [2] all_* 模式把所有临界点（端点也算）都返回.
  - [3] 输出的 Min/Max 是坐标数组（不是值）.
- **`match_funct_1d_trans`** — 参数：`**4 参数** — Function1(模板), Function2(待匹配), Border: Match — :`
  - 误区：[1] 算的是平移匹配 — 找 Function2 在 Function1 上的最佳水平位移.
  - [2] 不是形态相关/NCC — 而是把 Function2 沿 x 轴滑动找最小距离.
  - [3] 输出 Match 是位移数值.
- **`negate_funct_1d`** — 参数：`**2 参数** — Function: NegFunction — :`
  - 误区：[1] 简单 y = -f(x).
  - [2] 与 abs_funct_1d 不同 — abs 把负值翻正，negate 整体翻负.
  - [3] 零函数不变.
- **`num_points_funct_1d`** — 参数：`**2 参数** — Function: Length — :`
  - 误区：[1] 返回采样点数 N（不是数组），2≤N.
  - [2] 没有 size_funct_1d，用这个代替.
  - [3] 跟 x_range_funct_1d 返回的 dx 相关：Length = (x_max - x_min) / dx + 1.
- **`read_funct_1d`** — 参数：`**2 参数** — FileName: Function — :`
  - 误区：[1] 读 .fun 二进制文件 — 必须 write_funct_1d 写的.
  - [2] 不是 csv/txt — 文本格式另用其他工具.
  - [3] 文件不存在会抛错.
- **`sample_funct_1d`** — 参数：`**4 参数** — Function, XInterval(采样间距), Border: SampledFunction — :`
  - 误区：[1] 把函数重采样到新间距.
  - [2] Border 处理超出原定义域的端点.
  - [3] 输出的 SampledFunction 是等距的.
- **`scale_y_funct_1d`** — 参数：`**4 参数** — Function, Mult, Add: ScaledFunction — :`
  - 误区：[1] 线性变换 y = Mult * f(x) + Add.
  - [2] Mult=1, Add=0 是恒等.
  - [3] 不改 x-range — 只改 y.
- **`smooth_funct_1d_gauss`** — 参数：`**3 参数** — Function, Sigma(高斯核 σ): SmoothedFunction — :`
  - 误区：[1] 端点镜像处理（不是 cyclic）.
  - [2] Sigma 越大越平滑 — 但特征也越模糊.
  - [3] 输入必须是等距采样 — sample_funct_1d 后再用.
- **`smooth_funct_1d_mean`** — 参数：`**3 参数** — Function, SmoothSize(滑动窗口大小): SmoothedFunction — :`
  - 误区：[1] 算术移动平均 — 比 gauss 噪声更敏感但快.
  - [2] SmoothSize 越大越平滑.
  - [3] 端点镜像.
- **`transform_funct_1d`** — 参数：`**3 参数** — Function, Type ([signed_log, log, signed_inv, inv, sqrt, signed_sqrt, square, exp, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, erf, erfc, binomial]): TransformedFunction`
  - 误区：[1] 一组常用逐点变换 — log/exp/sqrt/trig/erf 等.
  - [2] signed_* 类（如 signed_log）支持负数输入.
  - [3] 输入合法性由 type 决定 — log 不能吃 ≤0.
- **`write_funct_1d`** — 参数：`**2 参数** — Function, FileName — :`
  - 误区：[1] 写为 .fun 二进制格式 — 含 x/y 全部信息.
  - [2] 配合 read_funct_1d 完全可逆.
  - [3] 文件路径要可写.
- **`x_range_funct_1d`** — 参数：`**2 参数** — Function: XMin, XMax — :`
  - 误区：[1] 输出定义域左右端点.
  - [2] 配合 y_range_funct_1d 求完整 bbox.
  - [3] 与 create_funct_1d_array 的隐式 0..N-1 不同 — 这里返回真实的 x 范围.
- **`y_range_funct_1d`** — 参数：`**2 参数** — Function: YMin, YMax — :`
  - 误区：[1] 输出值域上下界.
  - [2] 不含 x 信息 — 纯 y 极值.
- **`zero_crossings_funct_1d`** — 参数：`**2 参数** — Function: ZeroCrossings — :`
  - 误区：[1] 通过 f(x)=0 的所有 x 坐标.
  - [2] 用线性插值精确定位（不是采样点近似）.
  - [3] 切线过零也算 — 但与符号变换关联.

---

## 3. 全卷算子速查表（32 算子）

### 背景估计器（Background Estimator）（7 个）

| 算子 | 一句话功能 | HDevelop 关键签名 |
|---|---|---|
| `close_bg_esti` | close_bg_esti deletes the background estimation data se… | `close_bg_esti( : : BgEstiHandle : )` |
| `create_bg_esti` | create_bg_esti creates a new data set for the backgroun… | `create_bg_esti(InitializeImage : : Syspar1, Syspar2, GainMode, Gain1, Gain2, AdaptMode, MinDiff, StatNum, ConfidenceC, TimeC : BgEstiHandle)` |
| `get_bg_esti_params` | get_bg_esti_params returns the parameters of the data s… | `get_bg_esti_params( : : BgEstiHandle : Syspar1, Syspar2, GainMode, Gain1, Gain2, AdaptMode, MinDiff, StatNum, ConfidenceC, TimeC)` |
| `give_bg_esti` | give_bg_esti returns the estimated background image of … | `give_bg_esti( : BackgroundImage : BgEstiHandle : )` |
| `run_bg_esti` | run_bg_esti adapts the background image stored in the B… | `run_bg_esti(PresentImage : ForegroundRegion : BgEstiHandle : )` |
| `set_bg_esti_params` | set_bg_esti_params is used to change the parameters of … | `set_bg_esti_params( : : BgEstiHandle, Syspar1, Syspar2, GainMode, Gain1, Gain2, AdaptMode, MinDiff, StatNum, ConfidenceC, TimeC : )` |
| `update_bg_esti` | update_bg_esti overwrites the image stored in the curre… | `update_bg_esti(PresentImage, UpDateRegion : : BgEstiHandle : )` |

### 1D 函数（Function 1D）（25 个）

| 算子 | 一句话功能 | HDevelop 关键签名 |
|---|---|---|
| `abs_funct_1d` | abs_funct_1d calculates the absolute values of all y va… | `abs_funct_1d( : : Function : FunctionAbsolute)` |
| `compose_funct_1d` | compose_funct_1d composes two functions, i.e., calculat… | `compose_funct_1d( : : Function1, Function2, Border : ComposedFunction)` |
| `create_funct_1d_array` | create_funct_1d_array creates a one-dimensional functio… | `create_funct_1d_array( : : YValues : Function)` |
| `create_funct_1d_pairs` | create_funct_1d_pairs creates a one-dimensional functio… | `create_funct_1d_pairs( : : XValues, YValues : Function)` |
| `derivate_funct_1d` | derivate_funct_1d calculates the derivatives of the fun… | `derivate_funct_1d( : : Function, Mode : Derivative)` |
| `distance_funct_1d` | distance_funct_1d calculates the distance of two functi… | `distance_funct_1d( : : Function1, Function2, Mode, Sigma : Distance)` |
| `funct_1d_to_pairs` | funct_1d_to_pairs splits the input function Function in… | `funct_1d_to_pairs( : : Function : XValues, YValues)` |
| `get_pair_funct_1d` | get_pair_funct_1d accesses a function value of Function… | `get_pair_funct_1d( : : Function, Index : X, Y)` |
| `get_y_value_funct_1d` | get_y_value_funct_1d returns the y value of the functio… | `get_y_value_funct_1d( : : Function, X, Border : Y)` |
| `integrate_funct_1d` | integrate_funct_1d integrates the function Function (se… | `integrate_funct_1d( : : Function : Positive, Negative)` |
| `invert_funct_1d` | invert_funct_1d calculates the inverse function of the … | `invert_funct_1d( : : Function : InverseFunction)` |
| `local_min_max_funct_1d` | local_min_max_funct_1d searches for the local minima Mi… | `local_min_max_funct_1d( : : Function, Mode, Interpolation : Min, Max)` |
| `match_funct_1d_trans` | match_funct_1d_trans calculates the transformation para… | `match_funct_1d_trans( : : Function1, Function2, Border, ParamsConst, UseParams : Params, ChiSquare, Covar)` |
| `negate_funct_1d` | negate_funct_1d negates all y values of Function .… | `negate_funct_1d( : : Function : FunctionInverted)` |
| `num_points_funct_1d` | num_points_funct_1d calculates the number of control po… | `num_points_funct_1d( : : Function : Length)` |
| `read_funct_1d` | The operator read_funct_1d reads the contents of FileNa… | `read_funct_1d( : : FileName : Function)` |
| `sample_funct_1d` | sample_funct_1d samples the input function Function in … | `sample_funct_1d( : : Function, XMin, XMax, XDist, Border : SampledFunction)` |
| `scale_y_funct_1d` | scale_y_funct_1d multiplies and adds the y values of Fu… | `scale_y_funct_1d( : : Function, Mult, Add : FunctionScaled)` |
| `smooth_funct_1d_gauss` | The operator smooth_funct_1d_gauss smooths a one-dimens… | `smooth_funct_1d_gauss( : : Function, Sigma : SmoothedFunction)` |
| `smooth_funct_1d_mean` | The operator smooth_funct_1d_mean smooths a one dimensi… | `smooth_funct_1d_mean( : : Function, SmoothSize, Iterations : SmoothedFunction)` |
| `transform_funct_1d` | transform_funct_1d transforms the input function Functi… | `transform_funct_1d( : : Function, Params : TransformedFunction)` |
| `write_funct_1d` | The operator write_funct_1d writes the contents of Func… | `write_funct_1d( : : Function, FileName : )` |
| `x_range_funct_1d` | x_range_funct_1d calculates the smallest and the larges… | `x_range_funct_1d( : : Function : XMin, XMax)` |
| `y_range_funct_1d` | y_range_funct_1d calculates the smallest and the larges… | `y_range_funct_1d( : : Function : YMin, YMax)` |
| `zero_crossings_funct_1d` | zero_crossings_funct_1d calculates the zero crossings Z… | `zero_crossings_funct_1d( : : Function : ZeroCrossings)` |

---

## 4. 跨算子常见误区 & 调试提示

1. **create_bg_esti vs run_bg_esti 的硬件时间约定** —— `create_bg_esti` 用一帧作为初始估计（InitializeImage），`run_bg_esti` 之后每帧都看一次，**不要把 InitializeImage 留空**（默认会用首帧 PresentImage 替换）。
2. **bg_esti 的 GainMode 选择** —— `onion`（洋葱模型）适合户外变化光照，`auto` 适合场景不变，`fixed` 适合带显式 syspar 的算法派。`onion2` 是 `onion` 改进版，对噪声更稳健但慢。
3. **funct_1d 等距 vs 自定义点对** —— `create_funct_1d_array` 用等距 Y 数组（X 自动 0..N-1），`create_funct_1d_pairs` 用任意 X/Y 点对。**smooth 系算子只接受等距**——非等距先 sample_funct_1d。
4. **compose vs invert 不可逆混用** —— `compose_funct_1d` 是嵌套应用 f(g(x))，`invert_funct_1d` 是反函数（沿 y=x 对折）。两者对单调函数大致对偶，但**水平段会塌陷丢失**。
5. **smooth 算法选择** —— 高斯（`smooth_funct_1d_gauss`）适合连续曲线（轮廓投影），移动平均（`smooth_funct_1d_mean`）适合采样序列（时间序列）。`Sigma` 或 `SmoothSize` 越大越平滑，但**特征宽度**必须 > 滤波核。
6. **distance_funct_1d 与 match_funct_1d_trans 差** —— `distance_funct_1d` 是 L2 距离积分（同 x-range），`match_funct_1d_trans` 是平移对齐（沿 x 滑动找最小）。前者测相似度，后者在做模板匹配。
7. **transform_funct_1d 的负数支持** —— `sqrt/log/asin` 类对负输入会无效，HALCON 提供 `signed_sqrt/signed_log` 变体允许负数（走复数映射）。
8. **abs vs negate vs scale_y** —— `abs` 是 y=|y|（只翻正），`negate` 是 y=-y（整体翻负），`scale_y` 是 y=Mult*f(x)+Add（线性仿射）。

---

## 5. 调用链路与组合用法

### 5.1 视频流背景建模（4 步）

```
* 读首帧（InitializeImage）
read_image(Init, 'frame_000.png')
create_bg_esti(Init, ...)              → BgEstiHandle
* 循环喂入帧
for i := 1 to 255 by 1
  read_image(Frame, 'frame_' + i$'.3.png')
  run_bg_esti(Frame, Foreground, BgEstiHandle)
  * Foreground 是运动目标区域（连通域），做后续 blob 分析
endfor
close_bg_esti(BgEstiHandle)
```

### 5.2 1D 曲线信号处理（5 步）

```
* 1) 构造（等距采样）
create_funct_1d_array([0,1,4,9,16,25], X)  → Function
* 2) 求导 / 积分
derivate_funct_1d(Function, Derivative)
integrate_funct_1d(Function, Integral)
* 3) 平滑
smooth_funct_1d_gauss(Function, 1.5, Smoothed)
* 4) 极值 / 过零分析
local_min_max_funct_1d(Smoothed, 'plateau_min', MinX, MaxX)
zero_crossings_funct_1d(Derivative, ZC)  ← 导数过零即是极值 x
* 5) 反函数 / 变换
invert_funct_1d(Function, 'cyclic', InvFunction)
transform_funct_1d(Function, 'log', LogFunc)
* 6) 持久化
write_funct_1d(Smoothed, 'curve.fun')
read_funct_1d('curve.fun', Reloaded)
```

### 5.3 bg_esti 自适应调参热更新

```
set_bg_esti_params(BgEsti, 'gain_mode', 'onion')
set_bg_esti_params(BgEsti, 'min_diff', 8)         ← 阈值紧一点
set_bg_esti_params(BgEsti, 'adapt_mode', 'on')    ← 持续自适应
run_bg_esti(Frame, Foreground, BgEsti)
* 如果检测到前景溢出（光照突变），临时关 adapt
set_bg_esti_params(BgEsti, 'gain_mode', 'fixed')
```

---

## 6. 与其它章节的关联

| 章节 | 接口算子 | 上卷用法 |
|---|---|---|
| **Ch11 File** | read_image / write_image | bg_esti 的 InitializeImage 与结果回灌 |
| **Ch15 Image** | threshold / sub_image | bg_esti 输出的 ForegroundRegion 二值化 |
| **Ch16 Inspection** | dyn_threshold | bg_esti 与阈值结合的动态检测（如金属划痕） |
| **Ch18 Matrix** | 矩阵运算 | distance_funct_1d 在矩阵意义上是 L2 范数 |
| **Ch19 Morphology** | gray_closing 等 | bg_esti 替代品：形态学开运算也能做粗背景建模 |
| **Ch21 Object** | serialize / deserialize | BgEstiHandle 序列化跨进程复用 |

---

## 7. 一句话核心要义

> 本卷 = **背景建模 + 1D 函数 双生套件**：Background Estimator 用 **Kalman 自适应** 实时剥前景；Function 1D 提供**数学函数的构造/变换/分析/存取全套**。两套不共享算子但**共享应用场景**：产线视频监控 + 1D 传感器信号处理都是 HALCON 的 非 2D 延伸能力。
