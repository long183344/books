# 第 27 章 Tuple（元组）· 中卷（47 算子）

> **全章归属**：HALCON 官方 Operator Reference 第 27 章 `Tuple`，对应元组（HTuple）的所有运算符。上卷是数学运算（算术 + 位 + 比较），中卷是元组处理（转换 + 构造 + 字典 + 顺序 + 统计 + 逻辑 + 增删改），下卷是字符串/类型/集合/选择（待续）。
>
> **中卷总数**：**47 算子 / 7 子族**
> **本章前导**：第 27 章上卷 63 算子（Arithmetic/Bit/Comparison 三族）；本卷 47 算子承接上卷算术结果，转入数据处理与统计计算。
>
> **一句话定位**：HALCON 中元组是「一切数据的 DNA」——图像是元组、坐标是元组、配置是元组、统计输出是元组；中卷 7 子族就是元组的「工厂车间」——格式化生成、字典封装、统计提炼、增删改。

---

## 1. 全卷结构表

| 子族 | 算子数 | 功能定位 | 典型场景 |
|------|--------|---------|---------|
| **数据转换 (Conversion)** | 12 | 数值 ↔ 字符串 ↔ HALCON 句柄 互转 | 数据持久化、协议生成、字符串解析、句柄调试 |
| **元组构造 (Creation)** | 5 | 动态生成/拼接/填充元组 | 初始化数组、批量构造 ID、生成随机样本 |
| **Data Containers 字典 (Containers)** | 10 | 键值对关联数组（存任意类型）| 训练参数持久化、ROI 与阈值打包、跨算子传递复杂配置 |
| **Element Order 元素序 (Element Order)** | 2 | 升序排序 + 倒置 | 排序特征、字典序索引、查找 Top-N |
| **统计特征 (Features)** | 11 | min/max/sum/mean/median/σ 直方图 + 反射句柄 | 像素统计、缺陷率分析、灰度分布、控制图 SQC |
| **逻辑运算 (Logical Operations)** | 4 | 整数按位 and/or/xor/not | 位图打包、mask 筛选、布尔代数 |
| **插入/删除/替换 (Manipulation)** | 3 | 原位（元组级）修改 | 配置动态更新、序列切片插删 |

---

## 2. 子族分述

### 2.1 数据转换 (Conversion)

> **核心定位**：数值 ↔ 字符串 ↔ 句柄互转：tuple_string 格式化 + tuple_number 自动解析 + tuple_int/real 四舍五入 + tuple_chr/ord 单字符 ASCII 互转 + handle_to_integer 取句柄 ID

| # | 算子 | 一句话 |
|---|------|--------|
| 1 | `handle_to_integer` | 取 HALCON 句柄的内部整数 ID |
| 2 | `integer_to_handle` | 由整数 ID 恢复 HALCON 句柄 |
| 3 | `tuple_chr` | 整数（ASCII 码）→ 单字符 |
| 4 | `tuple_chrt` | 整数元组（ASCII 码序列）→ 字符串 |
| 5 | `tuple_int` | 转整数（带四舍五入，0.5 入 0/1 看舍入模式） |
| 6 | `tuple_is_number` | 判断字符串/元组能否解析为数字 |
| 7 | `tuple_number` | 字符串 → 数字（自动识别 int/float，解析失败抛错） |
| 8 | `tuple_ord` | 字符串 → 整数元组（每字符 ASCII 码） |
| 9 | `tuple_ords` | 字符串 → 整数元组（多字节，按平台编码） |
| 10 | `tuple_real` | 转浮点数（整数 → float） |
| 11 | `tuple_round` | 四舍五入到指定小数位（负数 = 10 的幂） |
| 12 | `tuple_string` | 数字 → 字符串（Format 控制格式：%.3f / %d / %x 等） |

**重点算子三段注**：

- **`tuple_chr`** (T: 整数（0-255 ASCII 码或 0-0x10FFFF Unicode）；返回单字符串)
  - **坑**：`负数/超界会抛错。tuple_chrt 才是**整数元组 → 多字符串**（用于打包 SVG/JSON 等二进制控制字符）。`
  - **签名**：`tuple_chr ( : : T : Chr)`

- **`tuple_number`** (T: 字符串/字符串元组（支持小数、指数、空格、Tab）；返回同长度浮点元组)
  - **坑**：`解析失败抛错而非返回 NaN（区别于 Python float() 返回 NaN）。空字符串会抛错。`
  - **签名**：`tuple_number ( : : T : Number)`

- **`tuple_round`** (T: 数字元组；Decimals: 小数位数（**负数 = 10 的幂**位置：-1=十位，-2=百位）)
  - **坑**：`Decimals=2 时 0.005 → 0.00（二进制浮点表示错位，不是 bug）。需要 Banker's rounding 用 `tuple_real(tuple_int(T+0.5))`。`
  - **签名**：`tuple_round ( : : T : Round)`

- **`tuple_string`** (T: 输入数字/字符串；Format: C 字符串格式（如 '%.3f'、'%d'、'\\x%02x'）；空 Format='' 时整数直接 .Tostring())
  - **坑**：`Format 是 **C printf 风格**而非 C# format（用 %f 不是 {0:F3}）。负零 -0.0 会被格式化为 "-0.000"。`
  - **签名**：`tuple_string ( : : T, Format : String)`

---

### 2.2 元组构造 (Creation)

> **核心定位**：动态生成元组：tuple_gen_const 填充常数 + tuple_gen_sequence 等差数列 + tuple_concat 拼接 + tuple_rand [0,1) 均匀分布 + clear_handle 释放句柄

| # | 算子 | 一句话 |
|---|------|--------|
| 1 | `clear_handle` | 释放 HALCON 句柄（dict/obj/类） |
| 2 | `tuple_concat` | 拼接多元组（不改变元素顺序，O(n) 重分配） |
| 3 | `tuple_gen_const` | 生成 N 个相同元素的常数元组 |
| 4 | `tuple_gen_sequence` | 生成等差数列（Start, End, Step） |
| 5 | `tuple_rand` | 生成 [0,1) 均匀分布随机浮点元组（每次结果不同） |

**重点算子三段注**：

- **`tuple_gen_sequence`** (Start: 起始；End: 终止（**含**）；Step: 步长（默认 1，可负）)
  - **坑**：`End=10, Step=3 → [10, 7, 4, 1] 而不是 [1,4,7,10]（逻辑是 while(abs(End-Cur) > eps)：从 Start 一直加 Step 直到越过 End）。`
  - **签名**：`tuple_gen_sequence ( : : Start, End, Step : Sequence)`

- **`tuple_rand`** (Length: 返回长度；Seed 负数=固定 RNG，多次一致)
  - **坑**：`未设 Seed 时每次调用结果不同，并行运算也不确定。Seed=0 等价未设。`
  - **签名**：`tuple_rand ( : : Length : Rand)`

---

### 2.3 Data Containers 字典 (Containers)

> **核心定位**：HALCON 内置字典（关联数组）：create_dict 新建 + set/get_dict_tuple/Object 存取值/对象 + read/write_dict 序列化文件 + copy_dict/remove_dict_key + get_dict_param 模式查询

| # | 算子 | 一句话 |
|---|------|--------|
| 1 | `copy_dict` | 深复制字典 |
| 2 | `create_dict` | 新建空字典 |
| 3 | `get_dict_object` | 从字典取 HALCON 对象（Image/Region/XLD） |
| 4 | `get_dict_param` | 查询字典的键/类型元信息 |
| 5 | `get_dict_tuple` | 从字典取元组值 |
| 6 | `read_dict` | 从 .hdict 文件加载字典 |
| 7 | `remove_dict_key` | 删除字典的指定键 |
| 8 | `set_dict_object` | 向字典存 HALCON 对象 |
| 9 | `set_dict_tuple` | 向字典存元组值 |
| 10 | `write_dict` | 字典序列化到 .hdict 文件 |

**重点算子三段注**：

- **`create_dict`** (无参；返回 DictHandle)
  - **坑**：`字典**只在 process 局部有效**；HDevelop 跨算子自动管，C#/C++ 必须 `Dispose()` 或 `ClearDict()`。Dictionary 在 HALCON 中是 **case-sensitive**。`
  - **签名**：`create_dict ( : : : DictHandle)`

- **`read_dict`** (FileName(.hdict 文件)；返回 DictHandle)
  - **坑**：`.hdict 是私有协议，**不能给 OpenCV/MATLAB 用**。需要互通用 `serialize_dict` 文本 JSON 后再 deserialize。`
  - **签名**：`read_dict ( : : FileName, GenParamName, GenParamValue : DictHandle)`

- **`set_dict_tuple`** (DictHandle, Key(字符串), Tuple: 任意类型元组；**空 Key 字符串**)
  - **坑**：`Key 含小数点会被嵌套访问解释为子字典（`a.b` 表示 dict['a']['b']）。所有算子多 Key 都用小数点访问/赋值。`
  - **签名**：`set_dict_tuple ( : : DictHandle, Key, Tuple : )`

---

### 2.4 Element Order 元素序 (Element Order)

> **核心定位**：顺序调整：tuple_sort 升序排序（按值字符串化字典序）+ tuple_inverse 倒置（[a,b,c]→[c,b,a]）

| # | 算子 | 一句话 |
|---|------|--------|
| 1 | `tuple_inverse` | 倒置元组（[a,b,c] → [c,b,a]） |
| 2 | `tuple_sort` | 升序排序（数字按数值；字符串按字典序；混合类型需一致） |

**重点算子三段注**：

- **`tuple_inverse`** (Tuple: 任意长度元组；返回倒序)
  - **坑**：`**不修改输入**元组（HALCON 大部分算子是 immutable 风格，调用方变量不变）。倒置 = [::-1] in Python。`
  - **签名**：`tuple_inverse ( : : Tuple : Inverted)`

- **`tuple_sort`** (Tuple: 任意类型；返回 Sorted（升序）)
  - **坑**：`字符串按**字典序**而非字母序：'Z' < 'a'。混合数字+字符串会抛错。空元组返回空。`
  - **签名**：`tuple_sort ( : : Tuple : Sorted)`

---

### 2.5 统计特征 (Features)

> **核心定位**：数学统计：tuple_min/max/sum/mean/median/deviation 中间统计 + tuple_length 元素数 + get_handle_* 反射取对象元数据 + tuple_histo_range 直方图桶分布

| # | 算子 | 一句话 |
|---|------|--------|
| 1 | `get_handle_object` | 句柄 → 内部对象（Image/Region/XLD） |
| 2 | `get_handle_param` | 查询句柄的元参数（Key='key_name'） |
| 3 | `get_handle_tuple` | 句柄 → 关联元组 |
| 4 | `tuple_deviation` | 标准差（默认总体 σ，分母 N；有 Sample 参数选样本 σ，分母 N-1） |
| 5 | `tuple_histo_range` | 在 [Min,Max] 区间等距分桶，返回各桶计数 |
| 6 | `tuple_length` | 返回元素个数（不是字节/字符数） |
| 7 | `tuple_max` | 最大值（广播前提：仅一个标量/一个元组，或两个等长元组） |
| 8 | `tuple_mean` | 算术平均（非整数自动浮点，避免溢出可分批累加） |
| 9 | `tuple_median` | 中位数（奇数取中间；偶数取中间两数算术平均） |
| 10 | `tuple_min` | 最小值（同 max 规则） |
| 11 | `tuple_sum` | 求和（字符串拼接也算 sum；混合类型抛错） |

**重点算子三段注**：

- **`tuple_deviation`** (Tuple: 数字元组；返回标准差 σ)
  - **坑**：`**默认是总体 σ（除 N）**，不是样本 σ（除 N-1）！要样本 σ 用 `sqrt(tuple_sum((T-mean)^2) / (N-1))` 自己算。`
  - **签名**：`tuple_deviation ( : : Tuple : Deviation)`

- **`tuple_histo_range`** (Tuple: 值序列；Min, Max: 区间端点；NumBins: 桶数；返回 Histo: 各桶计数 + BinSize)
  - **坑**：`**桶不包含 Max**（[Min+i*BinSize, Min+(i+1)*BinSize)）。值 < Min 或 > Max 不计入任何桶。浮点比较用 BinSize 倍数以避免误差。`
  - **签名**：`tuple_histo_range ( : : Tuple, Min, Max, NumBins : Histo, BinSize)`

- **`tuple_median`** (Tuple: 数字元组)
  - **坑**：`偶数长度取中间两数**算术平均**（不是任一）。要先整数再平均用 `tuple_real(tuple_median(T))`。`
  - **签名**：`tuple_median ( : : Tuple : Median)`

---

### 2.6 逻辑运算 (Logical Operations)

> **核心定位**：布尔按位：tuple_and/or/xor/not，**仅整数**+广播长度复用；返回 0/1 mask

| # | 算子 | 一句话 |
|---|------|--------|
| 1 | `tuple_and` | 按位与（**仅整数** + 广播长度复用） |
| 2 | `tuple_not` | 按位取反（**仅整数**；bool 也算 0/1） |
| 3 | `tuple_or` | 按位或（**仅整数**） |
| 4 | `tuple_xor` | 按位异或（**仅整数**） |

**重点算子三段注**：

- **`tuple_and`** (T1, T2: 整数元组（**仅整数**）；返回 And)
  - **坑**：`**非整数抛错**（区别于 NumPy 把 True 当 1.0）。bool 也算 0/1 整数。广播规则：长度不等时短元组从 0 索引开始复用。`
  - **签名**：`tuple_and ( : : T1, T2 : And)`

---

### 2.7 插入/删除/替换 (Manipulation)

> **核心定位**：原位修改：tuple_insert 在 Index 插入 + tuple_remove 删一段 + tuple_replace 替换一段；Index 超界自动夹紧

| # | 算子 | 一句话 |
|---|------|--------|
| 1 | `tuple_insert` | 在 Index 处插入 InsertTuple（Index=-1 追加；超界夹紧） |
| 2 | `tuple_remove` | 删除 [Index1, Index2) 区间元素 |
| 3 | `tuple_replace` | 替换 [Index1, Index2) 区间为 ReplaceTuple |

**重点算子三段注**：

- **`tuple_insert`** (Tuple, Index: 插入位置（-1=末尾追加；超界夹紧）；InsertTuple: 待插入元组)
  - **坑**：`Index 超界**夹紧**而不报错。InsertTuple 空 = 不变。Index=-1 是末尾追加而非所有负索引（区别于 Python list 负索引语义）。`
  - **签名**：`tuple_insert ( : : Tuple, Index, InsertTuple : Extended)`

- **`tuple_remove`** (Tuple, Index1, Index2: 删除 [Index1, Index2) 区间（半开，Index2 不删）)
  - **坑**：`Index1 == Index2 返回原元组。Index1 >= TupleLength 抛错。**返回值是新元组**，原 Tuple 不变。`
  - **签名**：`tuple_remove ( : : Tuple, Index : Reduced)`

- **`tuple_replace`** (Tuple, Index1, Index2: 替换区间（半开）; ReplaceTuple: 替换元组)
  - **坑**：`新元组长度 != (Index2-Index1) 时**整体替换**（不要求等长）。若 ReplaceTuple 为空，效果等同 tuple_remove。`
  - **签名**：`tuple_replace ( : : Tuple, Index, ReplaceTuple : Replaced)`

---

## 3. 全卷 47 算子速查表

| # | 算子 | 一句话功能 | HDevelop 关键签名 |
|---|------|-----------|------------------|
| 1 | `handle_to_integer` | 取 HALCON 句柄的内部整数 ID | `handle_to_integer ( : : Handle : CastedHandle)` |
| 2 | `integer_to_handle` | 由整数 ID 恢复 HALCON 句柄 | `integer_to_handle ( : : IntegerHandle : Handle)` |
| 3 | `tuple_chr` | 整数（ASCII 码）→ 单字符 | `tuple_chr ( : : T : Chr)` |
| 4 | `tuple_chrt` | 整数元组（ASCII 码序列）→ 字符串 | `tuple_chrt ( : : T : Chrt)` |
| 5 | `tuple_int` | 转整数（带四舍五入，0.5 入 0/1 看舍入模式） | `tuple_int ( : : T : Int)` |
| 6 | `tuple_is_number` | 判断字符串/元组能否解析为数字 | `tuple_is_number ( : : T : IsNumber)` |
| 7 | `tuple_number` | 字符串 → 数字（自动识别 int/float，解析失败抛错） | `tuple_number ( : : T : Number)` |
| 8 | `tuple_ord` | 字符串 → 整数元组（每字符 ASCII 码） | `tuple_ord ( : : T : Ord)` |
| 9 | `tuple_ords` | 字符串 → 整数元组（多字节，按平台编码） | `tuple_ords ( : : T : Ords)` |
| 10 | `tuple_real` | 转浮点数（整数 → float） | `tuple_real ( : : T : Real)` |
| 11 | `tuple_round` | 四舍五入到指定小数位（负数 = 10 的幂） | `tuple_round ( : : T : Round)` |
| 12 | `tuple_string` | 数字 → 字符串（Format 控制格式：%.3f / %d / %x 等） | `tuple_string ( : : T, Format : String)` |
| 13 | `clear_handle` | 释放 HALCON 句柄（dict/obj/类） | `clear_handle ( : : Handle : )` |
| 14 | `tuple_concat` | 拼接多元组（不改变元素顺序，O(n) 重分配） | `tuple_concat ( : : T1, T2 : Concat)` |
| 15 | `tuple_gen_const` | 生成 N 个相同元素的常数元组 | `tuple_gen_const ( : : Length, Const : Newtuple)` |
| 16 | `tuple_gen_sequence` | 生成等差数列（Start, End, Step） | `tuple_gen_sequence ( : : Start, End, Step : Sequence)` |
| 17 | `tuple_rand` | 生成 [0,1) 均匀分布随机浮点元组（每次结果不同） | `tuple_rand ( : : Length : Rand)` |
| 18 | `copy_dict` | 深复制字典 | `copy_dict ( : : DictHandle, GenParamName, GenParamValue : CopiedDictHandle)` |
| 19 | `create_dict` | 新建空字典 | `create_dict ( : : : DictHandle)` |
| 20 | `get_dict_object` | 从字典取 HALCON 对象（Image/Region/XLD） | `get_dict_object ( : Object : DictHandle, Key : )` |
| 21 | `get_dict_param` | 查询字典的键/类型元信息 | `get_dict_param ( : : DictHandle, GenParamName, Key : GenParamValue)` |
| 22 | `get_dict_tuple` | 从字典取元组值 | `get_dict_tuple ( : : DictHandle, Key : Tuple)` |
| 23 | `read_dict` | 从 .hdict 文件加载字典 | `read_dict ( : : FileName, GenParamName, GenParamValue : DictHandle)` |
| 24 | `remove_dict_key` | 删除字典的指定键 | `remove_dict_key ( : : DictHandle, Key : )` |
| 25 | `set_dict_object` | 向字典存 HALCON 对象 | `set_dict_object (Object : : DictHandle, Key : )` |
| 26 | `set_dict_tuple` | 向字典存元组值 | `set_dict_tuple ( : : DictHandle, Key, Tuple : )` |
| 27 | `write_dict` | 字典序列化到 .hdict 文件 | `write_dict ( : : DictHandle, FileName, GenParamName, GenParamValue : )` |
| 28 | `tuple_inverse` | 倒置元组（[a,b,c] → [c,b,a]） | `tuple_inverse ( : : Tuple : Inverted)` |
| 29 | `tuple_sort` | 升序排序（数字按数值；字符串按字典序；混合类型需一致） | `tuple_sort ( : : Tuple : Sorted)` |
| 30 | `get_handle_object` | 句柄 → 内部对象（Image/Region/XLD） | `get_handle_object ( : Object : Handle, Key : )` |
| 31 | `get_handle_param` | 查询句柄的元参数（Key='key_name'） | `get_handle_param ( : : Handle, GenParamName, Key : GenParamValue)` |
| 32 | `get_handle_tuple` | 句柄 → 关联元组 | `get_handle_tuple ( : : Handle, Key : Tuple)` |
| 33 | `tuple_deviation` | 标准差（默认总体 σ，分母 N；有 Sample 参数选样本 σ，分母 N-1） | `tuple_deviation ( : : Tuple : Deviation)` |
| 34 | `tuple_histo_range` | 在 [Min,Max] 区间等距分桶，返回各桶计数 | `tuple_histo_range ( : : Tuple, Min, Max, NumBins : Histo, BinSize)` |
| 35 | `tuple_length` | 返回元素个数（不是字节/字符数） | `tuple_length ( : : Tuple : Length)` |
| 36 | `tuple_max` | 最大值（广播前提：仅一个标量/一个元组，或两个等长元组） | `tuple_max ( : : Tuple : Max)` |
| 37 | `tuple_mean` | 算术平均（非整数自动浮点，避免溢出可分批累加） | `tuple_mean ( : : Tuple : Mean)` |
| 38 | `tuple_median` | 中位数（奇数取中间；偶数取中间两数算术平均） | `tuple_median ( : : Tuple : Median)` |
| 39 | `tuple_min` | 最小值（同 max 规则） | `tuple_min ( : : Tuple : Min)` |
| 40 | `tuple_sum` | 求和（字符串拼接也算 sum；混合类型抛错） | `tuple_sum ( : : Tuple : Sum)` |
| 41 | `tuple_and` | 按位与（**仅整数** + 广播长度复用） | `tuple_and ( : : T1, T2 : And)` |
| 42 | `tuple_not` | 按位取反（**仅整数**；bool 也算 0/1） | `tuple_not ( : : T : Not)` |
| 43 | `tuple_or` | 按位或（**仅整数**） | `tuple_or ( : : T1, T2 : Or)` |
| 44 | `tuple_xor` | 按位异或（**仅整数**） | `tuple_xor ( : : T1, T2 : Xor)` |
| 45 | `tuple_insert` | 在 Index 处插入 InsertTuple（Index=-1 追加；超界夹紧） | `tuple_insert ( : : Tuple, Index, InsertTuple : Extended)` |
| 46 | `tuple_remove` | 删除 [Index1, Index2) 区间元素 | `tuple_remove ( : : Tuple, Index : Reduced)` |
| 47 | `tuple_replace` | 替换 [Index1, Index2) 区间为 ReplaceTuple | `tuple_replace ( : : Tuple, Index, ReplaceTuple : Replaced)` |

---

## 4. 跨算子误区 & 调试提示

> **中卷 10 大高频坑**，每个都来自实战：

1. **`tuple_string` 的 Format 是 C printf 风格，不是 C# `{0:F3}`**。C# 集成时要把 `"%.3f"` 当字符串传，不能用 `.ToString("F3")`。
2. **`tuple_number` 失败抛错而不是返回 NaN**（区别于 Python `float()`）。要在循环里加 try-except，或先用 `tuple_is_number` 判断。
3. **`tuple_round` 用二进制舍入**，不是银行家舍入。`0.005 → 0.00` 因为二进制无法精确表示。要 Banker's rounding 用 `tuple_real(tuple_int(T + 0.5 * sgn(T)))`。
4. **`tuple_gen_sequence(End=10, Step=3)` 不是等差数列**！实际从 Start 一直加 Step 直到越过 End（**含 End**）。算子文档要慢读。
5. **`clear_handle` 不存在**（错把 create_dict 返回的句柄当 dict 类型），实际 `clear_handle` 已存在；**释放字典用 `clear_dict`** 而不是 `clear_handle`，否则报 'no such operator'。
6. **HALCON 字典的 Key 含小数点会被嵌套访问**：`a.b` 实际是 `dict['a']['b']`。要存原始 key 用反斜杠转义或自定义分隔符。
7. **`tuple_deviation` 默认是总体 σ（除 N）**，不是样本 σ（除 N-1）！统计学教材都说样本标准差，HALCON 反着。
8. **`tuple_median` 偶数长度取中间两数的算术平均**，不是任一个，也不是下取整。
9. **`tuple_histo_range` 的桶不包含 Max**（左闭右开）。值 > Max 不计入任何桶。要包含 Max 自己 +1 BinSize 或调整 Max。
10. **`tuple_and/or/xor/not` 仅整数**——传 float 抛错（区别于 NumPy）。bool 也算 0/1 整数。

---

## 5. 调用链路与组合用法

### 5.1 HALCON 字典存储图像处理元数据（Containers 综合用法）

```hdevelop
* 1. 创建或读取字典（持久化训练/标定结果）
create_dict(Params)
* read_dict('/path/to/params.hdict', Params)

* 2. 写入 ROI 区域（任意 HALCON 对象都可存）
set_dict_object(Params, 'roi', ROI_Region)
set_dict_tuple(Params, 'threshold', [100, 200])

* 3. 业务计算中...读取
get_dict_object(Params, 'roi', [], ROI)
get_dict_tuple(Params, 'threshold', [], Thresh)

* 4. 写回新结果
set_dict_tuple(Params, 'score', 0.95)
set_dict_object(Params, 'result_image', ResultImg)

* 5. 序列化到文件
write_dict(Params, '/path/to/results.hdict', [], [])
```

### 5.2 元组直方图 + 峰值检测（Features + Element Order）

```hdevelop
* 1. 计算灰度直方图（0..255 分 256 桶）
tuple_histo_range(GrayImage, 0, 255, 256, Histo, BinSize)

* 2. 找最大峰值
tuple_max(Histo, MaxCount)
* MaxCount / tuple_length(Histo) = 主峰占比

* 3. 算统计量
tuple_mean(Histo, MeanCount)
tuple_deviation(Histo, SigmaCount)

* 4. 找 Top-N（tuple_sort_index 在下卷 Selection，本例用 sort 替代）
tuple_sort(Histo, SortedHisto)
* SortedHisto[length-1] = 最高峰
```

### 5.3 Conversion 字符串拼装（含 Statistics）

```hdevelop
* 1. 计算指标的统计量
tuple_mean(GrayTuple, MeanGray)
tuple_deviation(GrayTuple, SigmaGray)
tuple_max(GrayTuple, MaxGray)
tuple_min(GrayTuple, MinGray)

* 2. 格式化为字符串（Conversion）
tuple_string(MeanGray, '%.3f', MeanStr)
tuple_string(SigmaGray, '%.3f', SigmaStr)
tuple_string([MaxGray, MinGray], '%d', [MaxStr, MinStr])

* 3. 元组拼接（Creation）
tuple_concat(['mean=', MeanStr, ' (σ=', SigmaStr, '), max=', MaxStr, ', min=', MinStr], Report)
* Report: 'mean=128.456 (σ=2.345), max=255, min=0'
```

### 5.4 mask 过滤（Logical Operations + Features）

```hdevelop
* 1. 比较生成 0/1 mask（上卷 Comparison）
tuple_greater_elem(GrayTuple, 200, Mask)

* 2. 与原值按位与保留，其他位置清 0
ValueMask := Mask * GrayTuple  * broadcast mask

* 3. 统计有效像素数（Features）
tuple_sum(ValueMask, ValidCount)
* 也可直接 tuple_sum(Mask) — 但只能算 mask 个数，不能加权均值

* 4. 用 Selection 子族（tuple_find）找出有效坐标（待下卷）
```

---

## 6. 与其它章节的关联

- **上卷（第 27 章 Arithmetic/Bit/Comparison）**：本卷算术结果（数值、布尔）通过 Conversion 输出为字符串；本卷 Features 提炼统计量；本卷 Logical 在算术比较结果之上做组合布尔。
- **下卷（第 27 章 Selection/Sets/StringOperations/Type）**：本卷 Element Order 排序后的索引查找（tuple_sort_index / tuple_find）将在下卷；本卷 Containers 字典的 Key 元组操作将在下卷 Selection；本卷 Conversion 的字符串操作的衍生（正则/分隔）将在下卷 StringOperations。
- **第 13 章 Control / Graphics**：本卷 `clear_handle` 释放 HALCON 句柄，配合窗口/窗口对象进行生命周期管理。
- **第 21 章 Object**：本卷 `get_handle_object` / `set_dict_object` 是 Object 类的反射门面；`tuple_*` 不直接处理图像，但通过 dict 可以存 Image/Region/XLD。
- **第 8 章 Control / 第 11 章 File I/O**：本卷 `read_dict` / `write_dict` 是 .hdict 持久化利器（私有协议）；需要互通用 `serialize_dict`（待下卷 Type）。
- **HDevelop 集成**：本卷算子大都对应底层 `HTuple` 方法；C# 集成通过 `HOperatorSet.TupleXxx(...)`；Python 用 `halcon.tuple_xxx(...)`。

## 7. 一句话核心要义

> **中卷 47 算子 = 元组的「数据处理车间」**：Conversion 是「格式化打印机」、Creation 是「生产流水线」、Containers 是「仓库」、Element Order 是「传送带」、Features 是「质检仪」、Logical 是「电路」、Manipulation 是「装配台」——掌握这一车间，下卷 Selection 与 Type 就是直接出货。

---

**附**：同目录下 `27-Tuple(中).png` 为本章思维导图（七瓣辐射，7 子族色谱对应，中心圆「Tuple 中卷」），原文件路径 `E:/ProgramData/WorkBreak/2026-08-04-09-51-45/07-算法/HALCON/章节总结/27-Tuple(中).png`。

**附**：本章算子离线抽取自 HALCON 20.11.1.0 Operator Reference（`/e/HALCON-20.11-Steady/doc/html/reference/operators/*.html`），抽取策略为 Strategy G：先抓 `<h2 id="sec_synopsis">Signature</h2>` 区域，按 `<b>op_name</b>` 锚点 + 平衡括号扫描定位完整签名；再剥所有 `display:none` 多语言 span/div；最后 `<a>`/`<i>` 标签还原文本。