# 第 27 章 Tuple（元组）· 上卷（63 算子）

> 本卷覆盖 **HALCON 第 27 章 Tuple 算子上篇**：Arithmetic（算术运算 45）+ Bit Operations（位运算 6）+ Comparison（比较运算 12）= 63 个算子。Tuple 是 HALCON 所有图像/区域/XLD 算子的中间数据载体，掌握元组算子即掌握 HALCON 数据流通语法。

本卷所有算子都属于第 27 章 Tuple（元组），专门处理 `HTuple` 标量/向量/矩阵的标量数学、整数位运算与布尔比较。下卷将涵盖容器/类型/字符串/选择等操作算子（91 个）。

一句话总结：**Tuple 上卷 = HALCON 数值元组数学库的算术 + 位运算 + 比较三大基座**。

---

## 1. 全卷结构表

| 子族 | 算子数 | 核心功能 | 典型场景 |
|------|--------|----------|----------|
| **Arithmetic 算术运算** | 45 | 四则运算 + 单/双参超越函数 + 取整 + 取模 + 累积和 + 度/弧度互换 + 浮点硬件函数 | 图像灰度变换、坐标计算、数值归一化、向量内积、距离测度、几何运算 |
| **Bit Operations 位运算** | 6 | 整数按位与/或/非/异或 + 左/右移 | 像素位平面提取、标志位处理、像素打包（RGB→int）、哈希校验 |
| **Comparison 比较运算** | 12 | 整体比较（返回标量）+ 逐元素比较（返回 0/1 元组） | 阈值筛选（mask）、条件分支、字典序比较、min/max 索引 |

> **关键约定**：① 长度不等时广播（短元组复用填充）；② bool 输出 = 0/1 整数；③ `elem` 后缀表示逐元素。

---

## 2.1 子族：算术运算（Arithmetic）

> 覆盖 HALCON 所有数值计算需求：四则、取模、符号、取整、平方根、对数、指数、三角、双曲、误差函数、累积和、度/弧度互换、IEEE 浮点硬件函数。

**算子速览**：

| 算子 | 一句话功能 |
|------|------------|
| `tuple_abs` | 逐元素取绝对值（int/float 都支持） |
| `tuple_acos` | 反余弦（弧度），输入裁剪到 [-1, 1] 之外返回 HException |
| `tuple_acosh` | 反双曲余弦，要求输入 ≥ 1 |
| `tuple_add` | 对应元素相加（广播：长度不等时复制较短的） |
| `tuple_asin` | 反正弦（弧度），输入裁剪到 [-1, 1] |
| `tuple_asinh` | 反双曲正弦 |
| `tuple_atan` | 反正切（弧度，仅一个象限） |
| `tuple_atan2` | atan2 反正切（保留 Y/X 象限信息，四象限正确） |
| `tuple_atanh` | 反双曲正切，输入 |x| < 1 |
| `tuple_cbrt` | 立方根（real cube root，负数也可） |
| `tuple_ceil` | 向上取整 |
| `tuple_cos` | 余弦（弧度） |
| `tuple_cosh` | 双曲余弦 |
| `tuple_cumul` | 累积前缀和（prefix sum），Cumul[i] = sum(T[:i+1]) |
| `tuple_deg` | 弧度 → 度（乘 180/π） |
| `tuple_div` | 对应元素除法（被 0 除返回 HException） |
| `tuple_erf` | 高斯误差函数 erf(x) = (2/√π)∫₀ˣ e⁻ᵗ² dt |
| `tuple_erfc` | 余补误差函数 1-erf(x) |
| `tuple_exp` | e^x 自然指数 |
| `tuple_exp10` | 10^x |
| `tuple_exp2` | 2^x |
| `tuple_fabs` | float 绝对值（同 tuple_abs 对 float 等价） |
| `tuple_floor` | 向下取整 |
| `tuple_fmod` | 浮点取余（与 tuple_mod 区别：模运算符号规则不同） |
| `tuple_hypot` | √(a²+b²) 数值稳定版（避免 sqrt(a*a+b*b) 溢出） |
| `tuple_ldexp` | x·2^exp，与 tuple_frexp 互逆（要求 exp 为整数） |
| `tuple_lgamma` | Gamma(x) 的自然对数（Gamma 极值时不会溢出） |
| `tuple_log` | 自然对数 ln(x)，要求 x>0 |
| `tuple_log10` | 常用对数 lg(x) |
| `tuple_log2` | 以 2 为底对数 |
| `tuple_max2` | 逐元素取大者（返回同长度元组，非全局 max） |
| `tuple_min2` | 逐元素取小者 |
| `tuple_mod` | 整数取余（保留被除数符号，C/C++ 语义） |
| `tuple_mult` | 对应元素乘法 |
| `tuple_neg` | 取相反数 |
| `tuple_pow` | x^y 幂函数（注意 0^负数会抛异常） |
| `tuple_rad` | 度 → 弧度（乘 π/180） |
| `tuple_sgn` | 符号函数 sign(x)，输出 -1/0/+1 |
| `tuple_sin` | 正弦（弧度） |
| `tuple_sinh` | 双曲正弦 |
| `tuple_sqrt` | 平方根，要求 x≥0 |
| `tuple_sub` | 对应元素减法 |
| `tuple_tan` | 正切（弧度） |
| `tuple_tanh` | 双曲正切 |
| `tuple_tgamma` | Gamma(x) 真伽玛函数，x 为半负整数时返回 ±∞ |

**重点算子三段注（算术运算）**：

- **`tuple_add`**：对应元素相加（广播：长度不等时复制较短的）
  - 参数：`tuple_add ( : : S1, S2 : Sum)`
  - 关键参数说明：S1, S2: 任意长度/任意数值元组；Sum: 输出（长度 = max(|S1|,|S2|)）。
  - 易踩坑：广播规则：长度相等时逐元素；一长一短时短元组被复用填充整个长量；空元组会被忽略。绝不抛长度不匹配异常！

- **`tuple_mult`**：对应元素乘法
  - 参数：`tuple_mult ( : : P1, P2 : Prod)`
  - 关键参数说明：T1, T2: 同 tuple_add。
  - 易踩坑：同样支持广播；对整数与浮点混合时自动提升为 float。

- **`tuple_sub`**：对应元素减法
  - 参数：`tuple_sub ( : : D1, D2 : Diff)`
  - 关键参数说明：Minuend, Subtrahend: 输入；Diff: 输出。
  - 易踩坑：与 tuple_add 广播规则相同；负数结果正常返回（不像 tuple_div 触发除零）。

- **`tuple_div`**：对应元素除法（被 0 除返回 HException）
  - 参数：`tuple_div ( : : Q1, Q2 : Quot)`
  - 关键参数说明：Q1, Q2: 输入；Quot: 输出。
  - 易踩坑：**除零抛 HException**！工程中务必先 `if (Q2[i] != 0)` 或用 `tuple_select_mask` 过滤；这是新手最常见崩溃源。

- **`tuple_cumul`**：累积前缀和（prefix sum），Cumul[i] = sum(T[:i+1])
  - 参数：`tuple_cumul ( : : Tuple : Cumul)`
  - 关键参数说明：Tuple: 输入；Cumul: 输出，长度相同，Cumul[0]=T[0]，Cumul[i]=T[0]+…+T[i]。
  - 易踩坑：**与 numpy.cumsum 等价**，区别是 HALCON 不支持 axis 参数（一维展平）；二维先 tuple_gen_const+reshape 或 region_to_mlabel 才能做。

- **`tuple_pow`**：x^y 幂函数（注意 0^负数会抛异常）
  - 参数：`tuple_pow ( : : T1, T2 : Pow)`
  - 关键参数说明：Base, ExpNumber: 任意数值；Pow: 输出。
  - 易踩坑：0^负数抛异常；负数底数+非整数指数=NaN；HALCON 不支持复数输出（如需复数域请用 tuple_exp+三角函数组合）。

- **`tuple_sqrt`**：平方根，要求 x≥0
  - 参数：`tuple_sqrt ( : : T : Sqrt)`
  - 关键参数说明：Q: 输入（必须 ≥0）；Sqrt: 输出。
  - 易踩坑：**负数输入抛 HException**！工程中常用 `tuple_max2(tuple_const(0,Q),Q)` 兜底，但这样会改变语义——最好在调用前剔除负值。

- **`tuple_log`**：自然对数 ln(x)，要求 x>0
  - 参数：`tuple_log ( : : T : Log)`
  - 关键参数说明：Q: 必须 >0；LN: 输出。
  - 易踩坑：0 或负数抛异常；图像里要先 `scale_image` 偏移到正区间，或用 tuple_log1p 系替代（HALCON 无此函数，需手写 log(1+x)）。

- **`tuple_atan2`**：atan2 反正切（保留 Y/X 象限信息，四象限正确）
  - 参数：`tuple_atan2 ( : : Y, X : ATan)`
  - 关键参数说明：Y, X: 同长度；ATan: 输出，弧度，范围 (-π, π]。
  - 易踩坑：**参数顺序是 Y/X，不是 X/Y**！与 C/C++ atan2(y,x) 相反——因为 HALCON 是为图像坐标 (Row=Y, Col=X) 而设计。混乱会导致角度差 90°。

- **`tuple_deg`**：弧度 → 度（乘 180/π）
  - 参数：`tuple_deg ( : : Rad : Deg)`
  - 关键参数说明：Rad: 弧度；Deg: 度数。
  - 易踩坑：与 tuple_rad 互逆；与 `tuple_atan2` 串联时务必注意输入是度还是弧度——最常见 bug。

- **`tuple_rad`**：度 → 弧度（乘 π/180）
  - 参数：`tuple_rad ( : : Deg : Rad)`
  - 关键参数说明：Deg: 度数；Rad: 弧度。
  - 易踩坑：输入是「度数」输出「弧度」，注意与 `tuple_deg` 方向。

- **`tuple_max2`**：逐元素取大者（返回同长度元组，非全局 max）
  - 参数：`tuple_max2 ( : : T1, T2 : Max2)`
  - 关键参数说明：T1, T2: 任意长度（广播）；Max: 输出。
  - 易踩坑：**逐元素 max，不是 max(T)**！要全局最大值应配合 tuple_max 一类（HALCON 没内置 tuple_max 全局，请用 `tuple_sort` 取末尾，或用 `tuple_greater_elem` 自身累计）。

- **`tuple_min2`**：逐元素取小者
  - 参数：`tuple_min2 ( : : T1, T2 : Min2)`
  - 关键参数说明：T1, T2: 输入；Min: 输出。
  - 易踩坑：同上，全局最小值请用 tuple_sort 取首元。

- **`tuple_fmod`**：浮点取余（与 tuple_mod 区别：模运算符号规则不同）
  - 参数：`tuple_fmod ( : : T1, T2 : Fmod)`
  - 关键参数说明：A, B: float；Mod: 输出。
  - 易踩坑：**与 tuple_mod 区别**：tuple_fmod 结果符号与 B 同（多数语言 % 规则），tuple_mod 结果符号与 A 同（C/C++ 语义）；浮点场景用 fmod 更稳定。

- **`tuple_hypot`**：√(a²+b²) 数值稳定版（避免 sqrt(a*a+b*b) 溢出）
  - 参数：`tuple_hypot ( : : T1, T2 : Hypot)`
  - 关键参数说明：Y, X: 浮点；Hypot: 输出 = √(X²+Y²)。
  - 易踩坑：**比 sqrt(X*X+Y*Y) 数值稳定**——后者当 X,Y 各超 √max_float 时会 INF；做距离/法向计算务必用本算子。

- **`tuple_sgn`**：符号函数 sign(x)，输出 -1/0/+1
  - 参数：`tuple_sgn ( : : T : Sgn)`
  - 关键参数说明：T: 任意数值元组；Sgn: 输出，每个元素 = sign(T[i])。
  - 易踩坑：0 输出 0；正数输出 1；负数输出 -1；NaN 在 HALCON 中通常转 0（行为依赖版本）。

- **`tuple_ceil`**：向上取整
  - 参数：`tuple_ceil ( : : T : Ceil)`
  - 关键参数说明：T: float；Ceil: 输出，整数型。
  - 易踩坑：对负数 -2.3 输出 -2（向上=朝 +∞），区别于 C/C++ trunc（朝 0 截断）。

- **`tuple_floor`**：向下取整
  - 参数：`tuple_floor ( : : T : Floor)`
  - 关键参数说明：T: float；Floor: 输出。
  - 易踩坑：对负数 -2.3 输出 -3（向下=朝 -∞）。

- **`tuple_erf`**：高斯误差函数 erf(x) = (2/√π)∫₀ˣ e⁻ᵗ² dt
  - 参数：`tuple_erf ( : : T : Erf)`
  - 关键参数说明：T: float；Erf: 输出。
  - 易踩坑：高斯分布 CDF 计算常用 erf((x-μ)/(σ√2))；HALCON 输出的 tuple_gen_distrib 已经是正态分布采样，但 CDF/分位点计算需手搓。

- **`tuple_lgamma`**：Gamma(x) 的自然对数（Gamma 极值时不会溢出）
  - 参数：`tuple_lgamma ( : : T : LogGamma)`
  - 关键参数说明：T: float > 0（半负整数抛异常）；LGamma: 输出。
  - 易踩坑：对应 numpy gammaln，对极大/极小 x 不会 overflow（直接用 tuple_tgamma 会 INF）；贝叶斯/B 分布对数计算必备。

- **`tuple_tgamma`**：Gamma(x) 真伽玛函数，x 为半负整数时返回 ±∞
  - 参数：`tuple_tgamma ( : : T : Gamma)`
  - 关键参数说明：T: float；TGam: 输出。
  - 易踩坑：对 x = -1, -2, -3… 返回 ±∞（极点）；HALCON 不像 Python 有 math.gamma 抛 ValueError，会直接输出 INF——务必先判别输入域。

- **`tuple_neg`**：取相反数
  - 参数：`tuple_neg ( : : T : Neg)`
  - 关键参数说明：T: 输入；Neg: 输出。
  - 易踩坑：对无符号/正数有符号整型（如 16-bit 灰度 65535）会回卷成 1！要做图像取反请用 scale_image(In, Out, -1, 255) 替代。

- **位运算通用坑**：`tuple_band`
  - 关键参数说明：无单独算子
  - 易踩坑：位运算 6 个算子全部仅支持 int；HALCON 图像灰度值默认 int1（0-255）可直接用，浮点图像（如 FFT 频域）必须先 `tuple_round`。

---

## 2.2 子族：位运算（Bit Operations）

> 6 个整数按位运算与移位：仅适用整数型元组，浮点输入会抛 HException。

**算子速览**：

| 算子 | 一句话功能 |
|------|------------|
| `tuple_band` | 按位与 & （整数限定） |
| `tuple_bnot` | 按位取反 ~（整数限定，输入必须整数） |
| `tuple_bor` | 按位或 | |
| `tuple_bxor` | 按位异或 ^ |
| `tuple_lsh` | 逻辑左移 <<（等价乘 2） |
| `tuple_rsh` | 逻辑右移 >>（无符号语义，C/C++ 行为） |

**重点算子三段注（位运算）**：

- **`tuple_band`**：按位与 & （整数限定）
  - 参数：`tuple_band ( : : T1, T2 : BAnd)`
  - 关键参数说明：T1, T2: **整数型**；BAnd: 输出。
  - 易踩坑：**浮点输入抛 HException**！标定/标志位提取前务必 `tuple_round` 转 int。常用于 `(R<<16)|(G<<8)|B` 像素打包后逐通道剥离。

- **`tuple_bnot`**：按位取反 ~（整数限定，输入必须整数）
  - 参数：`tuple_bnot ( : : T : BNot)`
  - 关键参数说明：T: **整数型**；BNot: 输出。
  - 易踩坑：C/C++ 中 ~0xFF = 0xFFFFFF00（位宽决定），HALCON 元组位宽由实际位数决定（int32）——`~5 = -6`（按补码）。

- **`tuple_lsh`**：逻辑左移 <<（等价乘 2）
  - 参数：`tuple_lsh ( : : T, Shift : Lsh)`
  - 关键参数说明：T: 整数；Shift: 整数（左移位数，可负）；LSH: 输出。
  - 易踩坑：左移等价乘 2；Shift 过大导致回卷是正常行为，不抛异常；负数 Shift 退化为右移。

- **`tuple_rsh`**：逻辑右移 >>（无符号语义，C/C++ 行为）
  - 参数：`tuple_rsh ( : : T, Shift : Rsh)`
  - 关键参数说明：T: 整数；Shift: 整数（右移位数）；RSH: 输出。
  - 易踩坑：**逻辑右移，无符号语义**（高位补 0）；不像 C++ 对 signed int 走算术右移（保留符号位）。如需算术右移，请先 tuple_band 屏蔽符号位。

- **位运算通用坑**：`tuple_band`
  - 关键参数说明：无单独算子
  - 易踩坑：位运算 6 个算子全部仅支持 int；HALCON 图像灰度值默认 int1（0-255）可直接用，浮点图像（如 FFT 频域）必须先 `tuple_round`。

---

## 2.3 子族：比较运算（Comparison）

> 12 个比较算子分两类：非 elem 版返回标量 0/1；elem 版返回同长度 0/1 元组用于 mask 筛选。

**算子速览**：

| 算子 | 一句话功能 |
|------|------------|
| `tuple_equal` | 整体相等（标量返回 0/1 整数） |
| `tuple_equal_elem` | 逐元素相等（同长度返回同长度 0/1 元组） |
| `tuple_greater` | 整体 > 比较，返回标量 |
| `tuple_greater_elem` | 逐元素 >，返回 0/1 元组 |
| `tuple_greater_equal` | 整体 ≥，返回标量 |
| `tuple_greater_equal_elem` | 逐元素 ≥ |
| `tuple_less` | 整体 < |
| `tuple_less_elem` | 逐元素 < |
| `tuple_less_equal` | 整体 ≤ |
| `tuple_less_equal_elem` | 逐元素 ≤ |
| `tuple_not_equal` | 整体 ≠ |
| `tuple_not_equal_elem` | 逐元素 ≠ |

**重点算子三段注（比较运算）**：

- **`tuple_equal_elem`**：逐元素相等（同长度返回同长度 0/1 元组）
  - 参数：`tuple_equal_elem ( : : T1, T2 : Equal)`
  - 关键参数说明：T1, T2: 任意同长度元组；Equal: 输出同长度 0/1 元组。
  - 易踩坑：与 tuple_equal 的关键区别：elem 版输出「逐元素」结果用于 tuple_select_mask；非 elem 版做整体相等输出单值。`elem` 后缀是 HALCON 元组算子的重要命名约定！

- **`tuple_greater`**：整体 > 比较，返回标量
  - 参数：`tuple_greater ( : : T1, T2 : Greater)`
  - 关键参数说明：T1, T2: 任意长度；Greater: 输出（0 或 1 标量）。
  - 易踩坑：**字典序比较**！先比第一个元素，相等再比第二个；不是「所有元素都大于」；输出是标量不是元组。

- **`tuple_greater_elem`**：逐元素 >，返回 0/1 元组
  - 参数：`tuple_greater_elem ( : : T1, T2 : Greater)`
  - 关键参数说明：T1, T2: 任意长度（广播）；Greater: 输出同长度 0/1 元组。
  - 易踩坑：与 tuple_greater 区别：输出长度 = max(len(T1),len(T2))，每个元素是 T1[i] > T2[i] 的布尔值。常配合 tuple_select_mask 做条件筛选。

- **`tuple_less_elem`**：逐元素 <
  - 参数：`tuple_less_elem ( : : T1, T2 : Less)`
  - 关键参数说明：T1, T2; Less: 输出。
  - 易踩坑：与 tuple_greater_elem 完全对称；选择 mask 后经常接着 `tuple_find` 取出下标。

- **`tuple_not_equal_elem`**：逐元素 ≠
  - 参数：`tuple_not_equal_elem ( : : T1, T2 : Nequal)`
  - 关键参数说明：T1, T2; NEqual: 输出 0/1 元组。
  - 易踩坑：比 tuple_equal_elem 取反更高效（HALCON 实现层面优化过）；但语义等价。

- **位运算通用坑**：`tuple_band`
  - 关键参数说明：无单独算子
  - 易踩坑：位运算 6 个算子全部仅支持 int；HALCON 图像灰度值默认 int1（0-255）可直接用，浮点图像（如 FFT 频域）必须先 `tuple_round`。

---

## 3. 全卷算子速查表

| 算子 | 一句话功能 | HDevelop 关键签名 |
|------|------------|-------------------|
| `tuple_abs` | 逐元素取绝对值（int/float 都支持） | `tuple_abs ( : : T : Abs)` |
| `tuple_acos` | 反余弦（弧度），输入裁剪到 [-1, 1] 之外返回 HException | `tuple_acos ( : : T : ACos)` |
| `tuple_acosh` | 反双曲余弦，要求输入 ≥ 1 | `tuple_acosh ( : : T : Acosh)` |
| `tuple_add` | 对应元素相加（广播：长度不等时复制较短的） | `tuple_add ( : : S1, S2 : Sum)` |
| `tuple_asin` | 反正弦（弧度），输入裁剪到 [-1, 1] | `tuple_asin ( : : T : ASin)` |
| `tuple_asinh` | 反双曲正弦 | `tuple_asinh ( : : T : Asinh)` |
| `tuple_atan` | 反正切（弧度，仅一个象限） | `tuple_atan ( : : T : ATan)` |
| `tuple_atan2` | atan2 反正切（保留 Y/X 象限信息，四象限正确） | `tuple_atan2 ( : : Y, X : ATan)` |
| `tuple_atanh` | 反双曲正切，输入 |x| < 1 | `tuple_atanh ( : : T : Atanh)` |
| `tuple_cbrt` | 立方根（real cube root，负数也可） | `tuple_cbrt ( : : T : Cbrt)` |
| `tuple_ceil` | 向上取整 | `tuple_ceil ( : : T : Ceil)` |
| `tuple_cos` | 余弦（弧度） | `tuple_cos ( : : T : Cos)` |
| `tuple_cosh` | 双曲余弦 | `tuple_cosh ( : : T : Cosh)` |
| `tuple_cumul` | 累积前缀和（prefix sum），Cumul[i] = sum(T[:i+1]) | `tuple_cumul ( : : Tuple : Cumul)` |
| `tuple_deg` | 弧度 → 度（乘 180/π） | `tuple_deg ( : : Rad : Deg)` |
| `tuple_div` | 对应元素除法（被 0 除返回 HException） | `tuple_div ( : : Q1, Q2 : Quot)` |
| `tuple_erf` | 高斯误差函数 erf(x) = (2/√π)∫₀ˣ e⁻ᵗ² dt | `tuple_erf ( : : T : Erf)` |
| `tuple_erfc` | 余补误差函数 1-erf(x) | `tuple_erfc ( : : T : Erfc)` |
| `tuple_exp` | e^x 自然指数 | `tuple_exp ( : : T : Exp)` |
| `tuple_exp10` | 10^x | `tuple_exp10 ( : : T : Exp)` |
| `tuple_exp2` | 2^x | `tuple_exp2 ( : : T : Exp)` |
| `tuple_fabs` | float 绝对值（同 tuple_abs 对 float 等价） | `tuple_fabs ( : : T : Abs)` |
| `tuple_floor` | 向下取整 | `tuple_floor ( : : T : Floor)` |
| `tuple_fmod` | 浮点取余（与 tuple_mod 区别：模运算符号规则不同） | `tuple_fmod ( : : T1, T2 : Fmod)` |
| `tuple_hypot` | √(a²+b²) 数值稳定版（避免 sqrt(a*a+b*b) 溢出） | `tuple_hypot ( : : T1, T2 : Hypot)` |
| `tuple_ldexp` | x·2^exp，与 tuple_frexp 互逆（要求 exp 为整数） | `tuple_ldexp ( : : T1, T2 : Ldexp)` |
| `tuple_lgamma` | Gamma(x) 的自然对数（Gamma 极值时不会溢出） | `tuple_lgamma ( : : T : LogGamma)` |
| `tuple_log` | 自然对数 ln(x)，要求 x>0 | `tuple_log ( : : T : Log)` |
| `tuple_log10` | 常用对数 lg(x) | `tuple_log10 ( : : T : Log)` |
| `tuple_log2` | 以 2 为底对数 | `tuple_log2 ( : : T : Log)` |
| `tuple_max2` | 逐元素取大者（返回同长度元组，非全局 max） | `tuple_max2 ( : : T1, T2 : Max2)` |
| `tuple_min2` | 逐元素取小者 | `tuple_min2 ( : : T1, T2 : Min2)` |
| `tuple_mod` | 整数取余（保留被除数符号，C/C++ 语义） | `tuple_mod ( : : T1, T2 : Mod)` |
| `tuple_mult` | 对应元素乘法 | `tuple_mult ( : : P1, P2 : Prod)` |
| `tuple_neg` | 取相反数 | `tuple_neg ( : : T : Neg)` |
| `tuple_pow` | x^y 幂函数（注意 0^负数会抛异常） | `tuple_pow ( : : T1, T2 : Pow)` |
| `tuple_rad` | 度 → 弧度（乘 π/180） | `tuple_rad ( : : Deg : Rad)` |
| `tuple_sgn` | 符号函数 sign(x)，输出 -1/0/+1 | `tuple_sgn ( : : T : Sgn)` |
| `tuple_sin` | 正弦（弧度） | `tuple_sin ( : : T : Sin)` |
| `tuple_sinh` | 双曲正弦 | `tuple_sinh ( : : T : Sinh)` |
| `tuple_sqrt` | 平方根，要求 x≥0 | `tuple_sqrt ( : : T : Sqrt)` |
| `tuple_sub` | 对应元素减法 | `tuple_sub ( : : D1, D2 : Diff)` |
| `tuple_tan` | 正切（弧度） | `tuple_tan ( : : T : Tan)` |
| `tuple_tanh` | 双曲正切 | `tuple_tanh ( : : T : Tanh)` |
| `tuple_tgamma` | Gamma(x) 真伽玛函数，x 为半负整数时返回 ±∞ | `tuple_tgamma ( : : T : Gamma)` |
| `tuple_band` | 按位与 & （整数限定） | `tuple_band ( : : T1, T2 : BAnd)` |
| `tuple_bnot` | 按位取反 ~（整数限定，输入必须整数） | `tuple_bnot ( : : T : BNot)` |
| `tuple_bor` | 按位或 | | `tuple_bor ( : : T1, T2 : BOr)` |
| `tuple_bxor` | 按位异或 ^ | `tuple_bxor ( : : T1, T2 : BXor)` |
| `tuple_lsh` | 逻辑左移 <<（等价乘 2） | `tuple_lsh ( : : T, Shift : Lsh)` |
| `tuple_rsh` | 逻辑右移 >>（无符号语义，C/C++ 行为） | `tuple_rsh ( : : T, Shift : Rsh)` |
| `tuple_equal` | 整体相等（标量返回 0/1 整数） | `tuple_equal ( : : T1, T2 : Equal)` |
| `tuple_equal_elem` | 逐元素相等（同长度返回同长度 0/1 元组） | `tuple_equal_elem ( : : T1, T2 : Equal)` |
| `tuple_greater` | 整体 > 比较，返回标量 | `tuple_greater ( : : T1, T2 : Greater)` |
| `tuple_greater_elem` | 逐元素 >，返回 0/1 元组 | `tuple_greater_elem ( : : T1, T2 : Greater)` |
| `tuple_greater_equal` | 整体 ≥，返回标量 | `tuple_greater_equal ( : : T1, T2 : Greatereq)` |
| `tuple_greater_equal_elem` | 逐元素 ≥ | `tuple_greater_equal_elem ( : : T1, T2 : Greatereq)` |
| `tuple_less` | 整体 < | `tuple_less ( : : T1, T2 : Less)` |
| `tuple_less_elem` | 逐元素 < | `tuple_less_elem ( : : T1, T2 : Less)` |
| `tuple_less_equal` | 整体 ≤ | `tuple_less_equal ( : : T1, T2 : Lesseq)` |
| `tuple_less_equal_elem` | 逐元素 ≤ | `tuple_less_equal_elem ( : : T1, T2 : Lesseq)` |
| `tuple_not_equal` | 整体 ≠ | `tuple_not_equal ( : : T1, T2 : Nequal)` |
| `tuple_not_equal_elem` | 逐元素 ≠ | `tuple_not_equal_elem ( : : T1, T2 : Nequal)` |

---

## 4. 跨算子误区 & 调试提示

1. **长度不等不报错，会广播！** `tuple_add([1,2,3], [10])` 输出 `[11, 12, 13]`。若本意是逐元素且长度需严格相等，请先用 `tuple_equal_elem` 做长度检查。
2. **bool 输出 = 0/1 整数**：不要用 `if (result)`，要 `if (result == 1)`；或显式 `tuple_equal_elem(result, 1)` 转布尔。
3. **`elem` 后缀语义**：非 elem 版返回标量（一个 0/1 整数），elem 版返回同长度 0/1 元组。混淆会得到完全不同的结果。
4. **除零抛 HException**：`tuple_div(a, b)` 当 b 含 0 时整个调用失败！务必先用 `tuple_select_mask(b, tuple_not_equal_elem(b, 0))` 过滤。
5. **负数开方抛异常**：`tuple_sqrt(-1)` 报错；图像处理建议先 `tuple_max2(t, tuple_const(0, t))` 兜底（注意会改变语义）。
6. **`atan2` 参数顺序是 Y/X**：与 C/C++ 相反，因为 HALCON 面向图像坐标 (Row=Y, Col=X)；混乱会导致角度差 90°。
7. **位运算仅限整数**：浮点元组先 `tuple_round` 转 int；负数右移走**逻辑**右移（高位补 0），不是算术右移。
8. **`tuple_pow(0, -1)` 抛异常**；负数底数 + 非整数指数 = NaN；HALCON 不支持复数输出。
9. **整体比较的字典序**：`tuple_greater([3,1], [2,9])` 返回 1（先比首元素 3>2），不是「所有元素都大于」。
10. **`tuple_tgamma` 极点不抛异常**：x = -1, -2, -3... 返回 ±∞，需手动判别输入域。

---

## 5. 调用链路与组合用法（HDevelop 代码片段）

### 5.1 图像灰度归一化（min-max + 线性拉伸）

```hdevelop
* 1. 读取图像得到 Region → tuple 灰度值
get_region_points (Region, Rows, Columns)
get_grayval (Image, Rows, Columns, Grayvals)

* 2. 计算 min/max（无 tuple_max/tuple_min，用 tuple_min2 累累）
tuple_min2 (Grayvals, tuple_const(|Grayvals|, 255), TmpMax)  * 这里只是示例
* 实际全局 min/max 需要先 tuple_sort 然后取首尾（或者用 reduce_domain+min_max_gray）
tuple_sort (Grayvals, Sorted)
GrayMin := Sorted[0]
GrayMax := Sorted[|Sorted|-1]

* 3. 防除零 + 线性拉伸到 [0, 255]
tuple_sub (Grayvals, tuple_const(|Grayvals|, GrayMin), Shifted)
Range := GrayMax - GrayMin
if (Range > 0)
    tuple_mult (Shifted, tuple_const(|Grayvals|, 255.0 / Range), Stretched)
    tuple_round (Stretched, StretchedInt)
else
    StretchedInt := Grayvals
endif
```

### 5.2 阈值筛选 mask + 下标提取

```hdevelop
* Scores: 模型对每个目标的得分（0~1 浮点）
tuple_greater_elem (Scores, tuple_const(|Scores|, 0.5), Mask)
tuple_select_mask (Scores, Mask, HighScores)
tuple_find (Mask, 1, Indices)  * 找出通过阈值的下标

* 等价：找下标
tuple_equal_elem (Mask, 1, BoolMask)
tuple_find (BoolMask, 1, Indices2)  * Indices2 == Indices
```

### 5.3 像素位平面提取 + RGB 打包

```hdevelop
* 1. 分离 R/G/B 通道（输入已是灰度 tuple）
tuple_band (PixelVal, tuple_const(|PixelVal|, 0x00FF00), GreenBits)
tuple_rsh (GreenBits, 8, GreenChannel)

* 2. RGB → packed int (0xRRGGBB)
tuple_lsh (RedChannel, 16, RShifted)
tuple_lsh (GreenChannel, 8, GShifted)
tuple_bor (RShifted, GShifted, RG)
tuple_bor (RG, BlueChannel, PackedRGB)
```

---

## 6. 与其它章节的关联

- **Ch1 1D Metrology**：边缘点列坐标求距离、角度会用到 `tuple_hypot`/`tuple_atan2`/`tuple_sqrt`。
- **Ch2 2D Metrology**：MetrologyHandle 输出点位后用 `tuple_mean`/`tuple_deviation` 等做统计分析（注：HALCON 无 `tuple_mean`，需 `tuple_sum`/len）。
- **Ch18 Matrix**：元组可视为 1D 向量；与 `tuple_to_matrix`/`matrix_to_tuple` 互转做矩阵运算。
- **Ch24 System / Sockets**：tuple 是网络消息载荷的常用格式，`tuple_to_string`+`tuple_strlen`+`tuple_concat` 拼包。
- **Ch25 Tools Geometry**：`distance_pl`/`distance_pp` 等返回的 tuple 坐标常用 `tuple_select_mask` 过滤。
- **Ch26 Transformations**：`hom_mat2d_to_affine_par` 返回 6 元数组（旋转/平移/缩放/剪切），需 `tuple_select` 取分量。
- **Ch27 下卷**：Container/Type/Selection/Conversion/Logical Operations 全部接收/返回本卷算子的结果。

---

## 7. 一句话核心要义

> **Ch27 Tuple 上卷 = 算术 + 位运算 + 比较** —— 三大数值元组数学基座，45+6+12=63 算子全部以「长度不等广播 / bool=0,1 / elem 后缀逐元素」三约定为根语法，所有 HALCON 数据流通的起点。
