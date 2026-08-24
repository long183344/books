# 第 20 章 OCR · 上卷：识别核心 33 算子

> **HALCON 20.11 官方 Operator Reference · 第 20 章 OCR · 上卷**  
> **「从图到字」的完整流水线——Deep OCR + 文本检测 + 字符切分 + 词典 + CNN 分类器**  
> 本卷收录 **4 族 33 算子**：Deep OCR 6 + Segmentation 12 + Lexica 6 + Convolutional Neural Networks 9

---

## §1. 章节定位

OCR（Optical Character Recognition）是机器视觉最古老的工业应用之一。HALCON 第 20 章围绕"从图像到文本"的完整链路展开，覆盖三大流派：

| 流派 | 代表族 | 上卷覆盖 | 下卷覆盖（61 ops） |
| --- | --- | --- | --- |
| **深度学习 OCR** | Deep OCR / MLP / CNN | ✅ Deep OCR（6）+ CNN（9） | — |
| **传统分类器** | KNN / SVM / MLP | — | ✅ KNN（13）+ SVM（19）+ MLP（20） |
| **基础文本处理** | Segmentation / Lexica / Training Files | ✅ Segmentation（12）+ Lexica（6） | ✅ Training Files（9） |

**上卷主题**：**把字从图里"找"出来**——上 Deep OCR（端到端）+ Segmentation（切字）+ Lexica（拼写纠错）+ CNN（字符级分类）。  
**下卷主题**：**训练你自己的分类器**——KNN / SVM / MLP + 训练样本管理（Training Files）。

### 1.1 上卷四大族在流水线中的位置

```
图像 ──[Deep OCR 端到端]──▶ 文本行 + 字符 + 识别结果（Deep OCR 6 ops）
   │
   └─[Segmentation 12 ops]──▶ 文本行/字符 region
        │
        └─[CNN 字符分类器 9 ops]──▶ 字符 → 类别
             │
             └─[Lexica 词典 6 ops]──▶ 拼写纠错、模糊匹配
```

---

## §2. 四族速览

### 2.1 Deep OCR（6 ops）— 端到端深度学习 OCR 引擎

HALCON 自带的最强 OCR 方案——内部由多个深度网络组合，自动完成"行检测→字符切分→识别"全链路，**无需传统字符切分**。

| 关键算子 | 功能 | 备注 |
| --- | --- | --- |
| `create_deep_ocr` | 从预训练组件构造 Deep OCR 模型 | 一次性生成 DeepOcrHandle |
| `apply_deep_ocr` | 对图像应用 Deep OCR，返回结果字典 | 替代传统 segment + do_ocr 流水线 |
| `read_ocr_class_cnn` / `write_deep_ocr` | 读取/保存 Deep OCR 模型 | `.dot` 文件 |
| `get_deep_ocr_param` / `set_deep_ocr_param` | 查询/设置参数 | 微调识别行为 |

### 2.2 Segmentation（12 ops）— 文本检测与字符切分

**传统 OCR 流水线的"前处理"**——把图像里的字先"切出来"。`find_text` + `segment_characters` + `select_characters` 三件套是工业 OCR 的主力。

| 关键算子 | 功能 | 备注 |
| --- | --- | --- |
| `create_text_model_reader` | 创建一个文本检测模型 | 配合 OCR 分类器 |
| `find_text` | 在图像中查找文本区域 | 输出 TextResultID |
| `segment_characters` | 把文本 region 切成字符 region | 字符宽度等 8 个参数 |
| `select_characters` | 从 region 中挑选可能为字符的区域 | 12 个过滤参数 |
| `text_line_orientation` / `text_line_slant` | 校正文字行倾斜/斜体 | 提升识别准确率 |
| `set_text_model_param` / `get_text_model_param` | 设置/查询文本模型参数 | 各种 gen_param |

### 2.3 Lexica（6 ops）— 词典与拼写纠错

**OCR 后的"质检员"**——识别结果送到词典检查，纠正拼写错误。建议深度 OCR 应用都带上词典后处理。

| 关键算子 | 功能 | 备注 |
| --- | --- | --- |
| `create_lexicon` / `import_lexicon` | 从内存列表/文件创建词典 | 支持 .lex 字典文件 |
| `lookup_lexicon` | 检查单词是否在词典中 | 返回 0/1 |
| `suggest_lexicon` | 计算最小编辑距离给修正建议 | 拼写纠错核心 |
| `inspect_lexicon` | 导出词典全部词 | 调试用 |
| `clear_lexicon` | 释放词典内存 | 三件套收尾 |

### 2.4 Convolutional Neural Networks（9 ops）— CNN 字符分类器

**字符级深度学习分类器**——传统字符识别需要先训练 CNN，再用 `do_ocr_*_class_cnn` 推理。完整生命周期：create → train → read → do_ocr → clear。

| 关键算子 | 功能 | 备注 |
| --- | --- | --- |
| `read_ocr_class_cnn` / `write_ocr_class_cnn` | 读取/保存 CNN 分类器 | 序列化跨进程 |
| `serialize_ocr_class_cnn` / `deserialize_ocr_class_cnn` | 序列化/反序列化 | 嵌入 HALCON 句柄 |
| `do_ocr_multi_class_cnn` / `do_ocr_single_class_cnn` | 多类/单类识别 | 多类带 NMS |
| `do_ocr_word_cnn` | 单词级识别（带词典纠错） | 集成 `Expression` |
| `get_params_ocr_class_cnn` / `query_params_ocr_class_cnn` | 查询参数 | 调试用 |

---

## §3. 思维导图：四方辐射（识别核心）

![四方辐射：Deep OCR（6）+ Segmentation（12）+ Lexica（6）+ CNN Classifier（9）= 33 ops](../20-OCR(上).png)

四族按 OCR 流水线"**深度引擎→基础切分→词典纠错→字符分类**"四方排列，主副标题清晰展示「第 20 章 OCR · 上卷 · 33 算子」。

---

## §4. 四族详解

### 4.1 Deep OCR（6 ops）�� 端到端深度学习 OCR

**核心思想**：传统 OCR 需要"切字→分类"两步，而 Deep OCR 把这两步合一。`create_deep_ocr` 生成一个 `DeepOcrHandle`，内部封装行检测 CNN + 字符识别 CNN，对新图直接 `apply_deep_ocr` 即可。返回 `DeepOcrResult` 是一个**字典**——包含每行的字符、置信度、文本框坐标。

**流水线**（训练好模型后 3 步）：

```hdevelop
* 1. 加载预训练模型
read_deep_ocr ('universal_deep_ocr.hdl', DeepOcrHandle)

* 2. 应用 OCR
apply_deep_ocr (Image, DeepOcrHandle, 'auto', DeepOcrResult)

* 3. 读取结果（DeepOcrResult 是一个 dict）
get_dict_tuple (DeepOcrResult, 'words', Words)
get_dict_tuple (DeepOcrResult, 'confidences', Confidences)

* 收尾
clear_deep_ocr (DeepOcrHandle)
```

**关键参数**（`apply_deep_ocr` 的 Mode）：

| Mode | 说明 |
| --- | --- |
| `'auto'` | 自动识别（默认） |
| `'rectification'` | 校正倾斜文本 |
| `'word'` | 单词级识别 |
| `'character'` | 字符级识别（输出更细） |

**Deep OCR 选型决策**：

| 场景 | 推荐 |
| --- | --- |
| 通用印刷体（中英文混排） | ✅ **Deep OCR 一键搞定**，无需字符切分 |
| 工业 PCB 字符 / 喷码 / 严重失真 | ⚠️ Deep OCR + 传统 `segment_characters` 双保险 |
| 手写体 | ❌ Deep OCR 通用模型不佳，需自训练 CNN（见下卷 MLP） |
| 大批量离线数据 | ⚠️ Deep OCR 推理慢，建议 batch + GPU 加速 |

**Deep OCR 6 算子族表**：

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `apply_deep_ocr` | 对图像应用 Deep OCR 模型 | `apply_deep_ocr ( Image : : DeepOcrHandle , Mode : DeepOcrResult )` |
| `create_deep_ocr` | 从预训练组件构造 Deep OCR 模型 | `create_deep_ocr ( : : GenParamName , GenParamValue : DeepOcrHandle )` |
| `get_deep_ocr_param` | 查询 Deep OCR 参数 | `get_deep_ocr_param ( : : DeepOcrHandle , GenParamName : GenParamValue )` |
| `read_deep_ocr` | 读取 Deep OCR 模型 | `read_deep_ocr ( : : FileName : DeepOcrHandle )` |
| `set_deep_ocr_param` | 设置 Deep OCR 参数 | `set_deep_ocr_param ( : : DeepOcrHandle , GenParamName , GenParamValue : )` |
| `write_deep_ocr` | 保存 Deep OCR 模型 | `write_deep_ocr ( : : DeepOcrHandle , FileName : )` |

**Deep OCR 误区速查表**：

| 误区 | 后果 | 正确做法 |
| --- | --- | --- |
| ❌ 用 `create_deep_ocr` 调空参数 | 模型加载失败 | 用 `read_deep_ocr` 加载预训练 `.hdl` |
| ❌ `apply_deep_ocr` 直接传彩色图 | 内部自动灰度化 | 想提速：先 `rgb1_to_gray` |
| ❌ 不释放 `DeepOcrHandle` | 内存泄漏 | 每次使用后 `clear_deep_ocr` |

### 4.2 Segmentation（12 ops）— 文本检测与字符切分

**核心思想**：**传统 OCR 流水线的第一步**——把字从图里"找"出来。`find_text` 自动检测文本行；`segment_characters` 切出字符；`text_line_orientation` 校正倾斜。这一族是**所有 OCR 应用的基础**。

**两套工作流**：

**流 A：find_text 自动文本行检测（推荐）**

```hdevelop
* 1. 创建文本模型（绑定 OCR 分类器）
create_text_model_reader ('manual', [], TextModel)

* 2. 在图中找文本行
find_text (Image, TextModel, TextResultID)

* 3. 取出文本行 region
get_text_object (TextLines, TextResultID, 'text_lines')

* 4. 切出字符
segment_characters (TextLines, Image, ImageForeground, RegionForeground, \
                    'local_auto_shape', 'false', 'false', 'medium', \
                    25, 25, 0, 10, UsedThreshold)

* 5. 识别字符（需要分类器，详见下卷）
do_ocr_multi_class_mlp (RegionForeground, ImageForeground, OCRHandle, Class, Confidence)

* 收尾
clear_text_model (TextModel)
clear_text_result (TextResultID)
```

**流 B：手动 ROI + 文本方向校正（受控场景）**

```hdevelop
* 1. 提取文本行 region（手动 ROI）
threshold (Image, Region, 0, 128)

* 2. 检测方向并校正
text_line_orientation (Region, Image, 50, -0.5236, 0.5236, OrientationAngle)
text_line_slant (Region, Image, 50, -0.5236, 0.5236, SlantAngle)
rotate_image (Image, ImageRot, -OrientationAngle * 180 / 3.14159, 'constant')

* 3. 切字 + 识别（同流 A 第 4-5 步）
```

**关键参数**（`segment_characters` 12 个）：

| 参数 | 类型 | 典型值 | 说明 |
| --- | --- | --- | --- |
| `Method` | string | `'local_auto_shape'` | 切字算法：`auto_shape`/`auto_contrast`/`manual` |
| `EliminateLines` | bool | `'true'` | 消除文本下划线 |
| `DotPrint` | bool | `'false'` | 处理点阵打印字体 |
| `StrokeWidth` | int | 5 | 笔画宽度（像素），决定字符大小估计 |
| `CharWidth`/`CharHeight` | int | 25/25 | 字符宽高像素估计 |
| `ThresholdOffset` | int | 0 | 二值化阈值偏移 |
| `Contrast` | int | 10 | 最小对比度 |

**Segmentation 12 算子族表**：

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `clear_text_model` | 释放文本模型 | `clear_text_model ( : : TextModel : )` |
| `clear_text_result` | 释放文本结果 | `clear_text_result ( : : TextResultID : )` |
| `create_text_model_reader` | 创建文本检测模型 | `create_text_model_reader ( : : Mode , OCRClassifier : TextModel )` |
| `find_text` | 在图像中查找文本区域 | `find_text ( Image : : TextModel : TextResultID )` |
| `get_text_model_param` | 查询文本模型参数 | `get_text_model_param ( : : TextModel , GenParamName : GenParamValue )` |
| `get_text_object` | 取出文本对象（如文本行 region） | `get_text_object ( : Characters : TextResultID , ResultName : )` |
| `get_text_result` | 取出文本结果（控制型） | `get_text_result ( : : TextResultID , ResultName : ResultValue )` |
| `segment_characters` | 把文本 region 切成字符 region | `segment_characters ( Region , Image : ImageForeground , RegionForeground : Method , EliminateLines , DotPrint , StrokeWidth , CharWidth , CharHeight , ThresholdOffset , Contrast : UsedThreshold )` |
| `select_characters` | 从 region 中挑选可能为字符的区域 | `select_characters ( Region : RegionCharacters : DotPrint , StrokeWidth , CharWidth , CharHeight , Punctuation , DiacriticMarks , PartitionMethod , PartitionLines , FragmentDistance , ConnectFragments , ClutterSizeMax , StopAfter : )` |
| `set_text_model_param` | 设置文本模型参数 | `set_text_model_param ( : : TextModel , GenParamName , GenParamValue : )` |
| `text_line_orientation` | 检测文本行方向 | `text_line_orientation ( Region , Image : : CharHeight , OrientationFrom , OrientationTo : OrientationAngle )` |
| `text_line_slant` | 检测文本行斜度 | `text_line_slant ( Region , Image : : CharHeight , SlantFrom , SlantTo : SlantAngle )` |

**Segmentation 误区速查表**：

| 误区 | 后果 | 正确做法 |
| --- | --- | --- |
| ❌ `segment_characters` 字符宽度不调 | 字符断裂/粘连 | 估算 `StrokeWidth` ≈ 字宽/3 |
| ❌ 文本行倾斜未校正 | 识别率大幅下降 | 先 `text_line_orientation` → `rotate_image` |
| ❌ 忽略 `clear_text_model` | 内存泄漏 | 用完立刻 `clear_*` |
| ❌ `find_text` 找不到字 | 文本对比度太低 | 调整 `min_contrast` 或 `min_char_height` |

### 4.3 Lexica（6 ops）— 词典与拼写纠错

**核心思想**：OCR 总是会出错（特别是低分辨率、字符粘连、噪声）。**词典后处理**能在不重训模型的前提下把识别率从 95% 提到 99%。`lookup_lexicon` 是字典查询，`suggest_lexicon` 是基于编辑距离的智能纠错。

**典型流水线**（OCR + 词典后处理）：

```hdevelop
* 1. 加载词典（项目专属词表，如汽车零件编号）
import_lexicon ('auto_parts', 'lexicon.lex', LexiconHandle)

* 2. 假设已有 OCR 识别结果 Word
do_ocr_word_cnn (Character, Image, OCRHandle, '[A-Z][0-9]+', 3, 5, Word, Score, Score)

* 3. 词典后处理：检查/纠错
lookup_lexicon (LexiconHandle, Word, Found)
if (Found == 0)
    suggest_lexicon (LexiconHandle, Word, Suggestion, NumCorrections)
    * Suggestion 是最接近的词典词
endif

* 收尾
clear_lexicon (LexiconHandle)
```

**词典文件格式**（`.lex`，每行一个词）：

```
PART-1234
PART-5678
WIDGET-001
COVER-2024
```

**关键算子详解**：

| 算子 | 编辑距离？ | 典型用法 |
| --- | --- | --- |
| `lookup_lexicon` | 否（精确匹配） | 验证识别结果是否合法 |
| `suggest_lexicon` | 是（编辑距离 ≤ N） | 给出 Top N 修正候选 |
| `create_lexicon` | — | 程序内动态构造词典 |
| `import_lexicon` | — | 从 `.lex` 文件加载 |

**Lexica 6 算子族表**：

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `clear_lexicon` | 释放词典 | `clear_lexicon ( : : LexiconHandle : )` |
| `create_lexicon` | 从内存词列表创建词典 | `create_lexicon ( : : Name , Words : LexiconHandle )` |
| `import_lexicon` | 从 .lex 文件加载词典 | `import_lexicon ( : : Name , FileName : LexiconHandle )` |
| `inspect_lexicon` | 导出词典全部词 | `inspect_lexicon ( : : LexiconHandle : Words )` |
| `lookup_lexicon` | 检查单词是否在词典中 | `lookup_lexicon ( : : LexiconHandle , Word : Found )` |
| `suggest_lexicon` | 给出拼写修正建议 | `suggest_lexicon ( : : LexiconHandle , Word : Suggestion , NumCorrections )` |

**Lexica 误区速查表**：

| 误区 | 后果 | 正确做法 |
| --- | --- | --- |
| ❌ 词典为空时 `lookup_lexicon` | 返回 0 全无意义 | 检查 `inspect_lexicon(Words)` 是否非空 |
| ❌ 不释放 `LexiconHandle` | 内存泄漏 | 用完 `clear_lexicon` |
| ❌ 词典超 10 万词 | 查询变慢 | 用 Trie 或分领域多个词典 |

### 4.4 Convolutional Neural Networks（9 ops）— CNN 字符分类器

**核心思想**：CNN 是字符识别的主力——`do_ocr_*_class_cnn` 系列对已经切好的字符 region 直接分类。区别于 Deep OCR（端到端），CNN 分类器是**单字符级**——先把字切出来，再分类。CNN 的优势：抗字体变化、抗轻微畸变。

**完整生命周期**（先训练，再用）：

```hdevelop
* 1. 准备训练样本（字符 image + 标签 .trf 文件）
read_ocr_trainf_names ('train_samples.trf', CharacterNames, CharacterCount)

* 2. 读取训练好的 CNN 模型（来自下卷 MLP/CNN 训练，详见 MLP 章）
read_ocr_class_cnn ('cnn_ocr_classifier.hdl', OCRHandle)

* 3. 假设已有字符 region（来自 4.2 segment_characters）
do_ocr_multi_class_cnn (CharacterRegions, Image, OCRHandle, Class, Confidence)

* 4. 单词级（带词典纠错）
do_ocr_word_cnn (CharacterRegions, Image, OCRHandle, '[A-Z]+', 5, 3, Word, Score, Score)

* 收尾
clear_ocr_class_cnn (OCRHandle)
```

**三种 do_ocr 变体对比**：

| 算子 | 输出粒度 | 返回 | 适用场景 |
| --- | --- | --- | --- |
| `do_ocr_multi_class_cnn` | 字符级 N 类 | `Class`, `Confidence` | 通用场景，一次性给所有候选 |
| `do_ocr_single_class_cnn` | 单字符 + N 候选 | `Class`, `Confidence`（TopN） | 一字多解需人确认 |
| `do_ocr_word_cnn` | 单词级（带正则） | `Word`, `Score` | 工业 OCR（编码、序列号） |

**CNN Classifier 9 算子族表**：

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `clear_ocr_class_cnn` | 释放 CNN OCR 分类器 | `clear_ocr_class_cnn ( : : OCRHandle : )` |
| `deserialize_ocr_class_cnn` | 反序列化 CNN OCR 分类器 | `deserialize_ocr_class_cnn ( : : SerializedItemHandle : OCRHandle )` |
| `do_ocr_multi_class_cnn` | CNN 多类字符识别 | `do_ocr_multi_class_cnn ( Character , Image : : OCRHandle : Class , Confidence )` |
| `do_ocr_single_class_cnn` | CNN 单类字符识别（Top N） | `do_ocr_single_class_cnn ( Character , Image : : OCRHandle , Num : Class , Confidence )` |
| `do_ocr_word_cnn` | CNN 单词级识别 | `do_ocr_word_cnn ( Character , Image : : OCRHandle , Expression , NumAlternatives , NumCorrections : Class , Confidence , Word , Score )` |
| `get_params_ocr_class_cnn` | 查询分类器参数 | `get_params_ocr_class_cnn ( : : OCRHandle , GenParamName : GenParamValue )` |
| `query_params_ocr_class_cnn` | 列出可查询参数名 | `query_params_ocr_class_cnn ( : : OCRHandle : GenParamName )` |
| `read_ocr_class_cnn` | 读取 CNN 分类器 | `read_ocr_class_cnn ( : : FileName : OCRHandle )` |
| `serialize_ocr_class_cnn` | 序列化 CNN 分类器 | `serialize_ocr_class_cnn ( : : OCRHandle : SerializedItemHandle )` |

**CNN Classifier 误区速查表**：

| 误区 | 后果 | 正确做法 |
| --- | --- | --- |
| ❌ CNN 模型未训练就 `do_ocr_*_class_cnn` | 全返回随机分类 | 先 `read_ocr_class_cnn` 加载训练好的 `.hdl` |
| ❌ 字符 region 错误切分 | 识别率骤降 | 先用 `segment_characters` 正确切字 |
| ❌ 多语言混排 | 分类器只认识一类 | 训练多类或多分类器并联 |
| ❌ CNN 模型未释放 | 内存泄漏 | 用完 `clear_ocr_class_cnn` |

---

## §5. 通用工作流：3 个 OCR 落地模板

### 5.1 模板一：Deep OCR 一键识别（最简单）

```hdevelop
* 适用：通用印刷体，无定制需求
read_deep_ocr ('universal_deep_ocr.hdl', DeepOcrHandle)
apply_deep_ocr (Image, DeepOcrHandle, 'auto', DeepOcrResult)
* ... 处理 DeepOcrResult ...
clear_deep_ocr (DeepOcrHandle)
```

### 5.2 模板二：传统 OCR 流水线（精度可控）

```hdevelop
* 适用：工业场景，需精细调参
create_text_model_reader ('manual', OCRClassifier, TextModel)
find_text (Image, TextModel, TextResultID)
segment_characters (Region, Image, ImageFG, RegionFG, 'local_auto_shape', 'false', 'false', 'medium', 25, 25, 0, 10, Thresh)
do_ocr_multi_class_cnn (RegionFG, ImageFG, OCRHandle, Class, Confidence)
* ... 词典后处理 ...
clear_text_model (TextModel)
clear_text_result (TextResultID)
clear_ocr_class_cnn (OCRHandle)
```

### 5.3 模板三：OCR + 词典纠错（高识别率场景）

```hdevelop
* 适用：零件编号、序列号、规整字段
read_ocr_class_cnn ('cnn_ocr_classifier.hdl', OCRHandle)
import_lexicon ('auto_parts', 'parts.lex', LexiconHandle)
segment_characters (Region, Image, ImageFG, RegionFG, 'local_auto_shape', 'false', 'false', 'medium', 25, 25, 0, 10, Thresh)
do_ocr_word_cnn (RegionFG, ImageFG, OCRHandle, '[A-Z][0-9]+-?[0-9]+', 5, 3, Word, Score, Conf)
lookup_lexicon (LexiconHandle, Word, Found)
if (Found == 0)
    suggest_lexicon (LexiconHandle, Word, Suggestion, NumErr)
    Word := Suggestion  * 用词典修正
endif
clear_ocr_class_cnn (OCRHandle)
clear_lexicon (LexiconHandle)
```

---

## §6. 选型决策矩阵：Deep OCR vs 传统 OCR

| 维度 | Deep OCR | 传统 OCR（CNN/MLP 分类器） |
| --- | --- | --- |
| **精度** | ⭐⭐⭐⭐⭐（通用场景） | ⭐⭐⭐⭐⭐（专业场景） |
| **开发速度** | ⭐⭐⭐⭐⭐（3 行代码） | ⭐⭐⭐（需要切分+训练） |
| **可调可控** | ⭐⭐（黑盒） | ⭐⭐⭐⭐⭐（每步可调） |
| **训练成本** | 无 | 需标注训练样本 |
| **推理速度** | 较慢 | 快（CPU 即可实时） |
| **多语言** | 自动支持 | 需分类器训练 |
| **适合场景** | 通用 OCR、PoC | 工业 PCB/喷码/规整字符 |

---

## §7. 误区速查（10 条）

| # | 误区 | 后果 | 正确做法 |
| ---: | --- | --- | --- |
| 1 | 字符 region 切错了还怪识别率低 | 识别率骤降 | 先调 `segment_characters` 的 `CharWidth/Height` |
| 2 | Deep OCR 加载彩色图 | 性能损耗 | 提前 `rgb1_to_gray` |
| 3 | 文本行倾斜未校正 | 字符旋转角度超容忍 | 先 `text_line_orientation` + `rotate_image` |
| 4 | 词典和 OCR 结果单位不一致 | 全是 0 Found | 检查 `Word` 字符串大小写 |
| 5 | CNN 分类器未释放 | 内存泄漏 | 用完 `clear_ocr_class_cnn` |
| 6 | `find_text` 找不到字 | 文本对比度太低 | 调 `min_contrast` 或先 `emphasize` |
| 7 | 词典文件 `.lex` 格式错 | `import_lexicon` 失败 | 每行一词，UTF-8 编码 |
| 8 | Deep OCR 误用 `create_deep_ocr` | 参数不全报错 | 用 `read_deep_ocr` 加载预训练 `.hdl` |
| 9 | 训练样本不平衡（数字多字母少） | 字母识别率低 | 分层采样，每类最少 50 样本 |
| 10 | 未用词典纠错 | 工业场景识别率低 5% | OCR 后必走 `lookup_lexicon` |

---

## §8. 完整签名速查表

### 8.1 Deep OCR 子表（6 ops）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `apply_deep_ocr` | 对图像应用 Deep OCR 模型 | `apply_deep_ocr ( Image : : DeepOcrHandle , Mode : DeepOcrResult )` |
| `create_deep_ocr` | 从预训练组件构造 Deep OCR 模型 | `create_deep_ocr ( : : GenParamName , GenParamValue : DeepOcrHandle )` |
| `get_deep_ocr_param` | 查询 Deep OCR 参数 | `get_deep_ocr_param ( : : DeepOcrHandle , GenParamName : GenParamValue )` |
| `read_deep_ocr` | 读取 Deep OCR 模型 | `read_deep_ocr ( : : FileName : DeepOcrHandle )` |
| `set_deep_ocr_param` | 设置 Deep OCR 参数 | `set_deep_ocr_param ( : : DeepOcrHandle , GenParamName , GenParamValue : )` |
| `write_deep_ocr` | 保存 Deep OCR 模型 | `write_deep_ocr ( : : DeepOcrHandle , FileName : )` |

### 8.2 Segmentation 子表（12 ops）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `clear_text_model` | 释放文本模型 | `clear_text_model ( : : TextModel : )` |
| `clear_text_result` | 释放文本结果 | `clear_text_result ( : : TextResultID : )` |
| `create_text_model_reader` | 创建文本检测模型 | `create_text_model_reader ( : : Mode , OCRClassifier : TextModel )` |
| `find_text` | 在图像中查找文本区域 | `find_text ( Image : : TextModel : TextResultID )` |
| `get_text_model_param` | 查询文本模型参数 | `get_text_model_param ( : : TextModel , GenParamName : GenParamValue )` |
| `get_text_object` | 取出文本对象 | `get_text_object ( : Characters : TextResultID , ResultName : )` |
| `get_text_result` | 取出文本结果（控制型） | `get_text_result ( : : TextResultID , ResultName : ResultValue )` |
| `segment_characters` | 把文本 region 切成字符 region | `segment_characters ( Region , Image : ImageForeground , RegionForeground : Method , EliminateLines , DotPrint , StrokeWidth , CharWidth , CharHeight , ThresholdOffset , Contrast : UsedThreshold )` |
| `select_characters` | 从 region 中挑选可能为字符的区域 | `select_characters ( Region : RegionCharacters : DotPrint , StrokeWidth , CharWidth , CharHeight , Punctuation , DiacriticMarks , PartitionMethod , PartitionLines , FragmentDistance , ConnectFragments , ClutterSizeMax , StopAfter : )` |
| `set_text_model_param` | 设置文本模型参数 | `set_text_model_param ( : : TextModel , GenParamName , GenParamValue : )` |
| `text_line_orientation` | 检测文本行方向 | `text_line_orientation ( Region , Image : : CharHeight , OrientationFrom , OrientationTo : OrientationAngle )` |
| `text_line_slant` | 检测文本行斜度 | `text_line_slant ( Region , Image : : CharHeight , SlantFrom , SlantTo : SlantAngle )` |

### 8.3 Lexica 子表（6 ops）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `clear_lexicon` | 释放词典 | `clear_lexicon ( : : LexiconHandle : )` |
| `create_lexicon` | 从内存词列表创建词典 | `create_lexicon ( : : Name , Words : LexiconHandle )` |
| `import_lexicon` | 从 .lex 文件加载词典 | `import_lexicon ( : : Name , FileName : LexiconHandle )` |
| `inspect_lexicon` | 导出词典全部词 | `inspect_lexicon ( : : LexiconHandle : Words )` |
| `lookup_lexicon` | 检查单词是否在词典中 | `lookup_lexicon ( : : LexiconHandle , Word : Found )` |
| `suggest_lexicon` | 给出拼写修正建议 | `suggest_lexicon ( : : LexiconHandle , Word : Suggestion , NumCorrections )` |

### 8.4 Convolutional Neural Networks 子表（9 ops）

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| `clear_ocr_class_cnn` | 释放 CNN OCR 分类器 | `clear_ocr_class_cnn ( : : OCRHandle : )` |
| `deserialize_ocr_class_cnn` | 反序列化 CNN OCR 分类器 | `deserialize_ocr_class_cnn ( : : SerializedItemHandle : OCRHandle )` |
| `do_ocr_multi_class_cnn` | CNN 多类字符识别 | `do_ocr_multi_class_cnn ( Character , Image : : OCRHandle : Class , Confidence )` |
| `do_ocr_single_class_cnn` | CNN 单类字符识别（Top N） | `do_ocr_single_class_cnn ( Character , Image : : OCRHandle , Num : Class , Confidence )` |
| `do_ocr_word_cnn` | CNN 单词级识别 | `do_ocr_word_cnn ( Character , Image : : OCRHandle , Expression , NumAlternatives , NumCorrections : Class , Confidence , Word , Score )` |
| `get_params_ocr_class_cnn` | 查询分类器参数 | `get_params_ocr_class_cnn ( : : OCRHandle , GenParamName : GenParamValue )` |
| `query_params_ocr_class_cnn` | 列出可查询参数名 | `query_params_ocr_class_cnn ( : : OCRHandle : GenParamName )` |
| `read_ocr_class_cnn` | 读取 CNN 分类器 | `read_ocr_class_cnn ( : : FileName : OCRHandle )` |
| `serialize_ocr_class_cnn` | 序列化 CNN 分类器 | `serialize_ocr_class_cnn ( : : OCRHandle : SerializedItemHandle )` |

---

## §9. 一句话总结

**OCR 上卷 = Deep OCR + Segmentation + Lexica + CNN 分类器**——「**先找字 → 切字 → 识字符 → 词典纠错**」的识别核心 33 算子；**Deep OCR 一键搞定通用场景，传统四步走精控专业场景，词典后处理永远加分**。