# 第 27 章 Tuple（元组）· 下卷（Selection + Sets + String Operations + Type）

> **全章位置**：第 27 章 Tuple 共 14 子族 154 算子，分三卷。**上卷 63 算子**（Arithmetic 45 + Bit Operations 6 + Comparison 12）覆盖数值算子基座；**中卷 47 算子**（Conversion 12 + Creation 5 + Containers 10 + ElementOrder 2 + Features 11 + LogicalOperations 4 + Manipulation 3）覆盖数据加工与组织；**本下卷 43 算子**专注于「数据访问 / 集合论 / 文本处理 / 类型判定」四大下游操作层。

> **本卷定位**：在 HALCON 元组体系中，下卷算子负责把上/中卷算出的元组**用起来**——索引选出目标元素（Selection）、做集合论运算（Sets）、按字符串/正则处理文本（String Operations）、判定类型与有效性（Type）。它们是 HALCON 与外部系统（数据库/文件/网络）打交道的桥梁。

> **一句话总结**：**「元组从「数据」到「应用」的最后一公里——选取、集合、文本、类型四件套」**。

![第 27 章 Tuple (下卷) 思维导图](./27-Tuple(下).png)

## 1. 全卷结构表（4 子族 / 43 ops）

| 子族 | 算子数 | 核心能力 | 典型应用场景 |
|---|---|---|---|
| 索引与筛选 Selection | 11 | 按位置（find/first_n/last_n/select/select_range/select_rank/select_mask）、按内容（find_first/find_last/str_bit_select）、按去重（uniq）三大类，共 11 算子 | 按内容/位置/位次筛选 ROI 索引、Top-K、P95 截尾、字符白名单过滤 |
| 集合运算 Sets | 4 | 集合论四件套 difference / intersection / symmdiff / union，输入自动 unique+sort，区别 tuple_difference 与 Ch17 Image "difference" 同名不同义 | ROI 集合运算（新增/移除/公共）、状态集合的差分检测 |
| 字符串操作 String Operations | 14 | 基础切片（substr/strlen/first_n/last_n）+ 字符/子串查找 4 件套（strchr/strrchr/strstr/strrstr）+ 正则 4 件套（match/replace/select/test）+ 元组切分（split）+ 环境变量（environment），共 14 算子 | CSV/JSON 解析、正则过滤日志、文件路径处理、环境变量读取 |
| 类型判定 Type | 14 | elem/非 elem 双版本的 is_int/real/string/handle/mixed 判定 + is_valid_handle handle 有效期 + 内部 C 类型（tuple_type）与语义类型（tuple_sem_type）查询，共 14 算子 | 防御性编程的类型守卫、handle 有效性判断、C 类型↔语义类型互查 |

## 2.1 子族：索引与筛选（Selection）

>按位置（find/first_n/last_n/select/select_range/select_rank/select_mask）、按内容（find_first/find_last/str_bit_select）、按去重（uniq）三大类，共 11 算子

| 算子 | 一句话功能 |
|---|---|
| [`tuple_find`](#op-tuple-find) | 在元组里查找子串/值的下标（可多值查多索引） |
| [`tuple_find_first`](#op-tuple-find-first) | 查找首次出现的下标（只一个） |
| [`tuple_find_last`](#op-tuple-find-last) | 查找最后一次出现的下标（只一个） |
| [`tuple_first_n`](#op-tuple-first-n) | 取前 N 个元素 |
| [`tuple_last_n`](#op-tuple-last-n) | 取后 N 个元素 |
| [`tuple_select`](#op-tuple-select) | 按下标列表取值（多个） |
| [`tuple_select_mask`](#op-tuple-select-mask) | 按 0/1 掩码筛选元素（最常用，配合比较运算） |
| [`tuple_select_range`](#op-tuple-select-range) | 按 [Min,Max] 区间选下标在范围内的元素 |
| [`tuple_select_rank`](#op-tuple-select-rank) | 按排序位选第 K 小/第 K 大的元素（可多 K） |
| [`tuple_str_bit_select`](#op-tuple-str-bit-select) | 从字符串元组中筛选只含指定字符集的元素（白名单） |
| [`tuple_uniq`](#op-tuple-uniq) | 去掉相邻重复元素（只去邻近重复，区别 numpy unique） |

### 2.1 重点算子详解

<a name="op-tuple-find"></a>

#### `tuple_find`

**签名**：`tuple_find ( : : Tuple, ToFind : Indices)`

**用法**。tuple_find (Items, [Item1,Item2,...] : Indices)，支持字符串/数值/混合查找；多 ToFind → 多 Indices

**坑**。1) 返回下标从 0 开始（与 HDevelop 1-based 下标不同） 2) 多 ToFind 时每个输入元组长度不同广播 3) 找不到返空元组（不是 -1） 4) 用 'all_strings' 参数控制是否按字符串序比较

**组合**。配合 tuple_select(T,Indices,Selected) 做按内容筛选

<a name="op-tuple-select-mask"></a>

#### `tuple_select_mask`

**签名**：`tuple_select_mask ( : : Tuple, Mask : Selected)`

**用法**。tuple_select_mask (Tuple, Mask, Selected)，Mask 为同长度 0/1 元组

**坑**。1) 必须先有 mask：tuple_greater_elem/equal_elem 等比较运算返回 0/1 元组 2) Mask = 全 0 返回空元组，不报错 3) 区别 tuple_find（按内容找位置）vs tuple_select_mask（按已知位置选元素）

**组合**。经典 pipeline：tuple_greater_elem(...) → tuple_select_mask(...) → 选目标像素或 ROI

<a name="op-tuple-uniq"></a>

#### `tuple_uniq`

**签名**：`tuple_uniq ( : : Tuple : Uniq)`

**用法**。tuple_uniq (Tuple, Uniq)，按出现顺序保留首次，后续重复丢弃

**坑**。1) **只去相邻重复**！[1,1,2,1,1] → [1,2,1]，要去全局重复先 tuple_sort 再 tuple_uniq 2) 不排序，所以输出顺序与首次出现相同 3) 字符串字典序比较（不是 C++ sort）

**组合**。去重 + 排序 = SortedUniq = tuple_uniq(tuple_sort(t))

---

## 2.2 子族：集合运算（Sets）

>集合论四件套 difference / intersection / symmdiff / union，输入自动 unique+sort，区别 tuple_difference 与 Ch17 Image "difference" 同名不同义

| 算子 | 一句话功能 |
|---|---|
| [`tuple_difference`](#op-tuple-difference) | 集合差：A - B（A 中不在 B 的元素） |
| [`tuple_intersection`](#op-tuple-intersection) | 集合交：A ∩ B（公共元素） |
| [`tuple_symmdiff`](#op-tuple-symmdiff) | 集合对称差：(A∪B) - (A∩B)，即 XOR |
| [`tuple_union`](#op-tuple-union) | 集合并：A ∪ B（自动去重） |

### 2.2 重点算子详解

<a name="op-tuple-difference"></a>

#### `tuple_difference`

**签名**：`tuple_difference ( : : Set1, Set2 : Difference)`

**用法**。tuple_difference (DecSet, SubSet : Difference)，返回 DecSet 中所有不在 SubSet 的元素

**坑**。1) 自动按 unique 处理（与 Python set 不同，先 uniq+sort） 2) 输出是 sorted+uniq 的 3) tuple_xxx 与 Ch17 Image 算子 'difference' 同名不同义

**组合**。常用于 ROI 集合运算：找新增点 = difference(now, last)

---

## 2.3 子族：字符串操作（String Operations）

>基础切片（substr/strlen/first_n/last_n）+ 字符/子串查找 4 件套（strchr/strrchr/strstr/strrstr）+ 正则 4 件套（match/replace/select/test）+ 元组切分（split）+ 环境变量（environment），共 14 算子

| 算子 | 一句话功能 |
|---|---|
| [`tuple_environment`](#op-tuple-environment) | 读环境变量值（一次一个名字） |
| [`tuple_regexp_match`](#op-tuple-regexp-match) | 正则匹配，返回所有匹配字符串 |
| [`tuple_regexp_replace`](#op-tuple-regexp-replace) | 正则替换（一次一条），返回新字符串元组 |
| [`tuple_regexp_select`](#op-tuple-regexp-select) | 正则筛选：选出匹配的元素（按整串匹配/部分匹配） |
| [`tuple_regexp_test`](#op-tuple-regexp-test) | 正则测试：返回 0/1 mask（哪些元素匹配） |
| [`tuple_split`](#op-tuple-split) | 按分隔符把字符串切分为字符串元组 |
| [`tuple_str_first_n`](#op-tuple-str-first-n) | 取每串的前 N 个字符 |
| [`tuple_str_last_n`](#op-tuple-str-last-n) | 取每串的后 N 个字符 |
| [`tuple_strchr`](#op-tuple-strchr) | 在字符串里查找字符首次出现下标（C 风格） |
| [`tuple_strlen`](#op-tuple-strlen) | 字符串长度（按字节） |
| [`tuple_strrchr`](#op-tuple-strrchr) | 反向找字符最后一次出现下标 |
| [`tuple_strrstr`](#op-tuple-strrstr) | 反向找子串最后一次出现下标 |
| [`tuple_strstr`](#op-tuple-strstr) | 正向找子串首次出现下标（C strstr） |
| [`tuple_substr`](#op-tuple-substr) | 子串切片 [Start, End)，按索引位置 |

### 2.3 重点算子详解

<a name="op-tuple-environment"></a>

#### `tuple_environment`

**签名**：`tuple_environment ( : : Names : Values)`

**用法**。tuple_environment (Variable : Value)，读 HALCON 环境变量值

**坑**。1) 常见：'HALCON_ROOT' / 'HALCON_ARCH' / 'HALCON_VERSION' / 'TMPDIR' 等 2) 变量名不存在抛错 3) **不要用于读系统环境变量**（如 PATH），用 set_system('export',...) 间接读

**组合**。诊断信息：get_system('image_dir'), tuple_environment('HALCON_VERSION')

<a name="op-tuple-regexp-match"></a>

#### `tuple_regexp_match`

**签名**：`tuple_regexp_match ( : : Data, Expression : Matches)`

**用法**。tuple_regexp_match (Data, Expression : Matches)，按 Expression 模式匹配，返回所有匹配的子串

**坑**。1) Expression 是 POSIX ERE 语法（不是 PCRE，**没有\d\s\w**，要写 [0-9][ 	][a-zA-Z]）2) 元组长度不等会广播 3) 找不到匹配返回空元组 4) Group capture 用 ( )

**组合**。OCR 后处理：tuple_regexp_replace(Str, '[^0-9.]', '', CleanedStr)

<a name="op-tuple-split"></a>

#### `tuple_split`

**签名**：`tuple_split ( : : String, Separator : Substrings)`

**用法**。tuple_split (String, Separator : Substrings)，按 Separator 切分每个字符串

**坑**。1) 返回字符串**元组的元组**（每个原字符串 → 切分结果）2) Separator 不能是正则（是正则用 tuple_regexp_*）3) 空分隔符会切单字符 4) 末尾部空串会被丢弃

**组合**。CSV 解析：tuple_split(Line, ',') → 字段元组

<a name="op-tuple-strlen"></a>

#### `tuple_strlen`

**签名**：`tuple_strlen ( : : T1 : Length)`

**用法**。tuple_strlen (String : Length)，返回每个字符串的字节长度

**坑**。1) **字节数**不是字符数！'你' = 3 字节（UTF-8）2) Python len('你') = 1 字符（Unicode）3) 批量长度，传入字符串元组返回长度元组

**组合**。日志校验：all(len(s)==N for s in tuple_strlen(Log))

<a name="op-tuple-strstr"></a>

#### `tuple_strstr`

**签名**：`tuple_strstr ( : : String, ToFind : Position)`

**用法**。tuple_strstr (String, ToFind : Position)，返回子串 ToFind 在 String 中首次出现的下标（字节）

**坑**。1) **字节位置**不是字符位置（UTF8 中文一个字 3 字节）2) 找不到返回 -1（HDevelop 中是 -1 整数，不是空元组）3) 与 tuple_find 区别：strstr 在单字符串内查子串；find 在元组里查值

**组合**。文件路径处理：tuple_strstr(Path, '/', Pos); tuple_substr(Path, 0, Pos) 取目录

<a name="op-tuple-substr"></a>

#### `tuple_substr`

**签名**：`tuple_substr ( : : String, Position1, Position2 : Substring)`

**用法**。tuple_substr (String, Start, End : Substring)，切子串 [Start, End)，左闭右开

**坑**。1) **0-based 索引**（不是 HDevelop 1-based）2) 字节粒度，不是字符粒度 3) 负数索引不支持（-1 = -1，越界抛错）4) End 越界自动夹紧

**组合**。扩展名提取：tuple_strrchr(File, '.', DotPos); tuple_substr(File, DotPos, tuple_strlen(File))

---

## 2.4 子族：类型判定（Type）

>elem/非 elem 双版本的 is_int/real/string/handle/mixed 判定 + is_valid_handle handle 有效期 + 内部 C 类型（tuple_type）与语义类型（tuple_sem_type）查询，共 14 算子

| 算子 | 一句话功能 |
|---|---|
| [`tuple_is_handle`](#op-tuple-is-handle) | 测试 tuple 是否含 handle 类型（数值 0/1 mask） |
| [`tuple_is_handle_elem`](#op-tuple-is-handle-elem) | 逐元素版 is_handle（返回同长度 0/1 元组） |
| [`tuple_is_int`](#op-tuple-is-int) | 测试 tuple 是否含 int 类型（数值 0/1 mask） |
| [`tuple_is_int_elem`](#op-tuple-is-int-elem) | 逐元素版 is_int（返回同长度 0/1 元组） |
| [`tuple_is_mixed`](#op-tuple-is-mixed) | 测试 tuple 是否含混合类型（数值 0/1 mask） |
| [`tuple_is_real`](#op-tuple-is-real) | 测试 tuple 是否含 real 类型（数值 0/1 mask） |
| [`tuple_is_real_elem`](#op-tuple-is-real-elem) | 逐元素版 is_real（返回同长度 0/1 元组） |
| [`tuple_is_string`](#op-tuple-is-string) | 测试 tuple 是否含 string 类型（数值 0/1 mask） |
| [`tuple_is_string_elem`](#op-tuple-is-string-elem) | 逐元素版 is_string（返回同长度 0/1 元组） |
| [`tuple_is_valid_handle`](#op-tuple-is-valid-handle) | 测试 handle 是否还有效（handle 可被释放/失效） |
| [`tuple_sem_type`](#op-tuple-sem-type) | 读元组的语义类型（HALCON 自定义类型如 rectangle/iconic、int/real/string） |
| [`tuple_sem_type_elem`](#op-tuple-sem-type-elem) | 逐元素读语义类型 |
| [`tuple_type`](#op-tuple-type) | 读内部 C 数据类型（整数 0x... 编码 INT/REAL/STRING/HANDLE 等） |
| [`tuple_type_elem`](#op-tuple-type-elem) | 逐元素读内部类型 |

### 2.4 重点算子详解

<a name="op-tuple-is-int"></a>

#### `tuple_is_int`

**签名**：`tuple_is_int ( : : T : IsInt)`

**用法**。tuple_is_int (T : IsInt)，返回 0/1 单整数：T 是否全为 int 类型

**坑**。1) elem 版本对每个元素判（返回同长 0/1 元组）；非 elem 对整个元组判（返回单个 0/1）2) 区别 tuple_type 返回 C 编码（INT=2, REAL=4, STRING=8, HANDLE=16）；tuple_sem_type 返回 HALCON 语义类型编码 3) 字符串 '123' 不是 int（要 tuple_number 转换）

**组合**。类型防御性编程：if(tuple_is_int(T), ...)

<a name="op-tuple-sem-type"></a>

#### `tuple_sem_type`

**签名**：`tuple_sem_type ( : : T : SemType)`

**用法**。tuple_sem_type (T : SemType)，返回单个整数：T 中所有元素的语义类型编码

**坑**。1) 区别 tuple_type（HALCON 内部 C 类型编码） vs tuple_sem_type（HALCON 语义层类型） 2) 语义类型可区分 'rectangle1' / 'iconic_object' / 'region' / 'xld' 等 3) elem 版返回同长度整数元组

**组合**。语义路由：switch(SemType, region -> ..., xld -> ..., rectangle1 -> ...)

<a name="op-tuple-type"></a>

#### `tuple_type`

**签名**：`tuple_type ( : : T : Type)`

**用法**。tuple_type (T : Type)，返回单个整数：T 的 C 内部类型编码

**坑**。1) 编码：INT=2, REAL=4, STRING=8, MIXED=1, HANDLE=16 (实际以 HALCON 定义为准) 2) 若 T 是 mixed，返回 1（混合）3) elem 版返回同长度整数元组

**组合**。导出前类型化：if(Type#1, ConvertToJSON())

---

## 3. 全卷算子速查表（43 行）

| # | 算子 | 功能 | HDevelop 签名 |
|---|---|---|---|
| 1 | `tuple_find` | 在元组里查找子串/值的下标（可多值查多索引） | `tuple_find ( : : Tuple, ToFind : Indices)` |
| 2 | `tuple_find_first` | 查找首次出现的下标（只一个） | `tuple_find_first ( : : Tuple, ToFind : Index)` |
| 3 | `tuple_find_last` | 查找最后一次出现的下标（只一个） | `tuple_find_last ( : : Tuple, ToFind : Index)` |
| 4 | `tuple_first_n` | 取前 N 个元素 | `tuple_first_n ( : : Tuple, Index : Selected)` |
| 5 | `tuple_last_n` | 取后 N 个元素 | `tuple_last_n ( : : Tuple, Index : Selected)` |
| 6 | `tuple_select` | 按下标列表取值（多个） | `tuple_select ( : : Tuple, Index : Selected)` |
| 7 | `tuple_select_mask` | 按 0/1 掩码筛选元素（最常用，配合比较运算） | `tuple_select_mask ( : : Tuple, Mask : Selected)` |
| 8 | `tuple_select_range` | 按 [Min,Max] 区间选下标在范围内的元素 | `tuple_select_range ( : : Tuple, Leftindex, Rightindex : Selected)` |
| 9 | `tuple_select_rank` | 按排序位选第 K 小/第 K 大的元素（可多 K） | `tuple_select_rank ( : : Tuple, RankIndex : Selected)` |
| 10 | `tuple_str_bit_select` | 从字符串元组中筛选只含指定字符集的元素（白名单） | `tuple_str_bit_select ( : : Tuple, Index : Selected)` |
| 11 | `tuple_uniq` | 去掉相邻重复元素（只去邻近重复，区别 numpy unique） | `tuple_uniq ( : : Tuple : Uniq)` |
| 12 | `tuple_difference` | 集合差：A - B（A 中不在 B 的元素） | `tuple_difference ( : : Set1, Set2 : Difference)` |
| 13 | `tuple_intersection` | 集合交：A ∩ B（公共元素） | `tuple_intersection ( : : Set1, Set2 : Intersection)` |
| 14 | `tuple_symmdiff` | 集合对称差：(A∪B) - (A∩B)，即 XOR | `tuple_symmdiff ( : : Set1, Set2 : SymmDiff)` |
| 15 | `tuple_union` | 集合并：A ∪ B（自动去重） | `tuple_union ( : : Set1, Set2 : Union)` |
| 16 | `tuple_environment` | 读环境变量值（一次一个名字） | `tuple_environment ( : : Names : Values)` |
| 17 | `tuple_regexp_match` | 正则匹配，返回所有匹配字符串 | `tuple_regexp_match ( : : Data, Expression : Matches)` |
| 18 | `tuple_regexp_replace` | 正则替换（一次一条），返回新字符串元组 | `tuple_regexp_replace ( : : Data, Expression, Replace : Result)` |
| 19 | `tuple_regexp_select` | 正则筛选：选出匹配的元素（按整串匹配/部分匹配） | `tuple_regexp_select ( : : Data, Expression : Selection)` |
| 20 | `tuple_regexp_test` | 正则测试：返回 0/1 mask（哪些元素匹配） | `tuple_regexp_test ( : : Data, Expression : NumMatches)` |
| 21 | `tuple_split` | 按分隔符把字符串切分为字符串元组 | `tuple_split ( : : String, Separator : Substrings)` |
| 22 | `tuple_str_first_n` | 取每串的前 N 个字符 | `tuple_str_first_n ( : : String, Position : Substring)` |
| 23 | `tuple_str_last_n` | 取每串的后 N 个字符 | `tuple_str_last_n ( : : String, Position : Substring)` |
| 24 | `tuple_strchr` | 在字符串里查找字符首次出现下标（C 风格） | `tuple_strchr ( : : String, ToFind : Position)` |
| 25 | `tuple_strlen` | 字符串长度（按字节） | `tuple_strlen ( : : T1 : Length)` |
| 26 | `tuple_strrchr` | 反向找字符最后一次出现下标 | `tuple_strrchr ( : : String, ToFind : Position)` |
| 27 | `tuple_strrstr` | 反向找子串最后一次出现下标 | `tuple_strrstr ( : : String, ToFind : Position)` |
| 28 | `tuple_strstr` | 正向找子串首次出现下标（C strstr） | `tuple_strstr ( : : String, ToFind : Position)` |
| 29 | `tuple_substr` | 子串切片 [Start, End)，按索引位置 | `tuple_substr ( : : String, Position1, Position2 : Substring)` |
| 30 | `tuple_is_handle` | 测试 tuple 是否含 handle 类型（数值 0/1 mask） | `tuple_is_handle ( : : T : IsHandle)` |
| 31 | `tuple_is_handle_elem` | 逐元素版 is_handle（返回同长度 0/1 元组） | `tuple_is_handle_elem ( : : T : IsHandle)` |
| 32 | `tuple_is_int` | 测试 tuple 是否含 int 类型（数值 0/1 mask） | `tuple_is_int ( : : T : IsInt)` |
| 33 | `tuple_is_int_elem` | 逐元素版 is_int（返回同长度 0/1 元组） | `tuple_is_int_elem ( : : T : IsInt)` |
| 34 | `tuple_is_mixed` | 测试 tuple 是否含混合类型（数值 0/1 mask） | `tuple_is_mixed ( : : T : IsMixed)` |
| 35 | `tuple_is_real` | 测试 tuple 是否含 real 类型（数值 0/1 mask） | `tuple_is_real ( : : T : IsReal)` |
| 36 | `tuple_is_real_elem` | 逐元素版 is_real（返回同长度 0/1 元组） | `tuple_is_real_elem ( : : T : IsReal)` |
| 37 | `tuple_is_string` | 测试 tuple 是否含 string 类型（数值 0/1 mask） | `tuple_is_string ( : : T : IsString)` |
| 38 | `tuple_is_string_elem` | 逐元素版 is_string（返回同长度 0/1 元组） | `tuple_is_string_elem ( : : T : IsString)` |
| 39 | `tuple_is_valid_handle` | 测试 handle 是否还有效（handle 可被释放/失效） | `tuple_is_valid_handle ( : : Handle : IsValid)` |
| 40 | `tuple_sem_type` | 读元组的语义类型（HALCON 自定义类型如 rectangle/iconic、int/real/string） | `tuple_sem_type ( : : T : SemType)` |
| 41 | `tuple_sem_type_elem` | 逐元素读语义类型 | `tuple_sem_type_elem ( : : T : SemTypes)` |
| 42 | `tuple_type` | 读内部 C 数据类型（整数 0x... 编码 INT/REAL/STRING/HANDLE 等） | `tuple_type ( : : T : Type)` |
| 43 | `tuple_type_elem` | 逐元素读内部类型 | `tuple_type_elem ( : : T : Types)` |

## 4. 跨算子误区 & 调试提示

### **`tuple_find` vs `tuple_select_mask` 区别**

`tuple_find(T, [a,b,c])` 按内容找位置，返回**下标元组**（值→位置）；`tuple_select_mask(T, Mask)` 用已知 0/1 mask 选元素，返回**值元组**（mask→值）。典型 pipeline 是 find 出位置，再用 select 选元素，或比较运算得到 mask 直接 select_mask。

### **`tuple_uniq` 的相邻去重陷阱**

HALCON `tuple_uniq` 只去除相邻重复，与 Python `set(list)` 的全局去重不同。要全局 uniq + 排序，先 `tuple_sort` 再 `tuple_uniq`。例如 `[1,2,1] → [1,2,1]`（保留两个 1），而全局 uniq 应为 `[1,2]`。

### **集合运算自动 sort+uniq**

`tuple_difference/intersection/union/symmdiff` 输出是已排序+去重的，输入也按内部唯一集合处理。例如 `tuple_difference([3,1,2,1], [2])` 返回 `[1,3]`。若要保序用 `tuple_select_mask + tuple_select` 自己实现。

### **正则语法不是 PCRE，是 POSIX ERE**

HALCON `tuple_regexp_*` 使用 POSIX 扩展正则（ERE），**没有** `\d \s \w \b` 字符类简写，要写 `[0-9] [ 	] [a-zA-Z] [^0-9]`。词边界 `( )` group 写法也不同，匹配中文要 UTF-8 locale 配合。

### **`tuple_str*` 与字符串字面量**

`tuple_strstr` / `tuple_strchr` / `tuple_strlen` / `tuple_substr` 操作的是「字符串元组」而非单字符串，但允许单字符串自动包装。**字节粒度**而非字符粒度：UTF-8 中 `tuple_strlen('你') = 3`，与 Python `len('你') = 1` 不同。

### **`tuple_split` 返回元组的元组**

`tuple_split(Line, ",")` 返回结构是 `[["a", "b"], ["c"]]`，一个嵌套两层的列表。要展平需 `tuple_uniq` 后再用 `tuple_concat` 拼接，或写循环。

### **Type 子族的 elem/非 elem 之分**

非 elem 版（`tuple_is_int`/`tuple_type`/`tuple_sem_type` 等）测试**整个元组**，返回单个 0/1 或单个整数；elem 版（`tuple_is_int_elem`/`tuple_type_elem`/`tuple_sem_type_elem`）测试**每个元素**，返回同长度整数元组。配合 `tuple_and` 做 AND mask 累加。

### **`tuple_is_valid_handle` 是判释放**

HALCON handle（region/xld/dataset 等）可能被算子释放/失效。`tuple_is_valid_handle` 用于检测 handle 是否仍然有效（不抛异常），常放 ROI 操作前做防御。可与 `tuple_is_handle` 联合：先判类型再判有效。

### **`tuple_type` vs `tuple_sem_type` 编码不同**

`tuple_type` 返回 HALCON 内部 C 类型编码（INT=2, REAL=4, STRING=8, HANDLE=16, MIXED=1）；`tuple_sem_type` 返回更细粒度的语义类型（"region"/"xld"/"rectangle1"/"rectangle2"/"image" 等）。使用时注意区分：前者导出兼容性好，后者路由策略强。

### **`tuple_select_range` 是按值范围筛元素，不是按下标筛**

`tuple_select_range(T, [10,100])` 返回 T 中 10 ≤ 值 ≤ 100 的所有元素（按值过滤），区别 `tuple_select` 按下标索引选。这是和 Python `range(10,101)` 完全不同的语义。

### **`tuple_select_rank` 排序位 + 多 K 同时返回**

`tuple_select_rank(T, K)` 中 K 可以是元组 `[k1,k2,k3,...]`，返回多个排序位。但 `tuple_sort_index` 与本算子不同：`sort_index` 返回**下标**，`select_rank` 返回**值**。

### **`tuple_str_bit_select` 字符白名单筛元组**

从字符串元组中筛选**只含指定字符集**的元素（如只要数字：`tuple_str_bit_select(["a1", "123", "x"], "0123456789", Result)` → `["123"]`）。与 `tuple_regexp_select` 区别：白名单比正则快，适合固定字符集（如数字/字母/中文区段）。

## 5. 调用链路与组合用法

### 5.1 ROI 像素级筛选 — tuple_find + tuple_select_mask

```hdevelop
* 场景：对积分图筛选 > 阈值的像素坐标
read_image (Image, 'fabrik')
intensity (Image, GrayImage, Mean, Deviation)

* 1. 找亮斑像素下标
threshold (GrayImage, BrightRegions, 200, 255)
get_region_points (BrightRegions, Rows, Columns)

* 2. 找出亮度大于 250 的下标（局部掩码）
get_grayval (GrayImage, Rows, Columns, GrayValues)
tuple_greater_elem (GrayValues, 250, Mask)
tuple_select_mask (Rows, Mask, HotRows)
tuple_select_mask (Columns, Mask, HotCols)
tuple_find (Mask, 1, Indices)  // 可选：等价于 HotRows 的下标列表
```

### 5.2 字符串解析 — tuple_split + tuple_regexp + tuple_substr

```hdevelop
* 场景：从文件名提取日期+编号
* 形如 "img_20240825_001.bmp"
filename := 'img_20240825_001.bmp'

* 1. 按 _ 切分
tuple_split (filename, '_', Parts)
* Parts = ['img', '20240825', '001.bmp']

* 2. 日期段校验
tuple_regexp_test (Parts, '^[0-9]{8}$', IsDate)
* IsDate = [0, 1, 0]

* 3. 取扩展名前缀
tuple_strrchr (filename, '.', DotPos)
tuple_substr (filename, DotPos+1, tuple_strlen(filename)-1, Ext)
* Ext = 'bmp'
```

### 5.3 集合运算 — ROI 增量差分

```hdevelop
* 场景：当前帧 ROI 元组 vs 上一帧 ROI 元组，找出新增点
* 上次：LastPoints = [10, 20, 30]
* 这次：CurrPoints = [10, 20, 30, 40, 50]

* 全局唯一+排序
tuple_sort (LastPoints, LastSorted)
tuple_sort (CurrPoints, CurrSorted)

* 集合差 = 新增点
tuple_difference (CurrSorted, LastSorted, NewPoints)
* NewPoints = [40, 50]

* 集合并 = 所有点
tuple_union (CurrSorted, LastSorted, AllPoints)

* 集合交 = 公有点
tuple_intersection (CurrSorted, LastSorted, CommonPoints)
```

### 5.4 类型守卫 — tuple_is_xxx_elem + tuple_and

```hdevelop
* 场景：读 CSV 行后判断每字段类型，路由到不同处理
* Row = ['100', '3.14', 'abc', 'true', '200']

tuple_is_int_elem (Row, IntMask)       * [1, 0, 0, 0, 1]
tuple_is_real_elem (Row, RealMask)     * [0, 1, 0, 0, 0]
tuple_is_string_elem (Row, StrMask)    * [1, 1, 1, 1, 1]

* 字符串且非数 → 文本字段
tuple_and (StrMask, tuple_not(IntMask), TextIdx_ones?)<-- 这个组合不对，重写
* 简化版：用 StringMask AND NOT(IntMask OR RealMask)
tuple_or_elem (IntMask, RealMask, NumMask)
tuple_not (NumMask, NotNumMask)        * 注意 tuple_not 也接受 0/1 mask
tuple_and (StrMask, NotNumMask, TextFieldMask)
tuple_select_mask (Row, TextFieldMask, TextFields)
```

## 6. 与其它章节的关联

- **Ch21 Object**：底层元组表达（HTuple/tuple 数据结构），本卷所有 `tuple_*` 算子最终都生成/消费 HTuple 数据。
- **Ch22 I/O**：tuple_environment/tuple_regexp_* 用于解析外部配置（JSON/XML 字符串字典），与 `read_dict`/`write_dict` 配合。
- **Ch27 上卷 Comparison**：本卷 `tuple_find / tuple_select_mask` 的输入通常是比较运算输出的 0/1 mask；上卷 `tuple_equal_elem / tuple_greater_elem` 等是核心 mask 源。
- **Ch27 中卷 Creation / Conversion**：本卷 `tuple_type / tuple_is_int_elem` 等用于防御性编程，配合中卷 `tuple_number / tuple_string / create_dict` 做格式互转。
- **Ch17 Matching / Ch23 Segmentation**：find/select 操作 ROI/像素坐标，与匹配输出和区域筛选深度集成。
- **Ch11 File I/O**：`tuple_split / tuple_substr / tuple_regexp_match` 用于解析文本配置文件（.ini/.csv/.json），与 `read_string`/`write_string` 配合。

## 7. 一句话核心要义

> **第 27 章 Tuple 下卷 = 「四把尺子」：Selection 量位置（find）、Sets 算集合（union/diff）、String 切文本（split/regexp）、Type 判性质（is_int/type）。**

> **入口判断：要先找位置（find）→ 先有 mask（comparison 算子）→ 再选元素（select_mask）；要不要去重（uniq），要先排序（sort）再 uniq；要处理文本先 split 再 regexp；要做防御性编程先用 is_int 判类型。**

---

> 本卷共 **43 个算子**、4 个子族、13 个重点算子详解、12 条跨算子误区、4 段 HDevelop 调用链路示例。
