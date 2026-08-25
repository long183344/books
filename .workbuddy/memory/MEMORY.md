# HALCON 章节总结长期笔记（项目级）

## 工作区结构
- 章节文档目录：`07-算法/HALCON/章节总结/`
- 命名格式：`NN-{ChapterName}{（上|中|下）}.md` + 同名 .png
- 顶层 + 子目录双 README 索引（`README.md` 和 `07-算法/README.md`）

## HTML 文档位置
- `/e/HALCON-20.11-Steady/doc/html/reference/operators/`（HALCON 20.11.1.0 Operator Reference）
- 每个算子一个 .html，含同步中文 6 语言 translation token

## 抽取策略（稳定版 Strategy G）

### 入口三模式
1. `<h2 id="sec_synopsis">Signature</h2>`（最常见，BG/Function/Morphology/OCR）
2. `<h2 id="sec_signature">Signature</h2>`（备用）
3. `<h2>Signature</h2>`（fallback）

匹配关键：`.*?</h2>(.*?)<h2` 跳到下一段，避免 `.*?</h2>` 最短匹配只抓到 "Signature" 字面量

### 签名提取
- `op_name[\s\S]{0,80}?\(` 模式定锚点
- 平衡括号扫描定位签名结束
- 清洁流程（4 步）：
  1. 剥 `display:none` 跨语言 span
  2. 还原 `<i>` 斜体（纯文本即可）
  3. 剥 `<a>` 但保留显示文字
  4. 剥其余标签 + 压缩空白

### 描述提取
- 找 `<h2>Description</h2>` 后第一段（**不是 Signature 后首段！** 那是跨语言签名短行）
- 关键字黑名单过滤：`HTuple/Herror/HMessageQueue/HOperatorSet./static void/public static/private static/def/HInstance/-> Herror/void XXX(`
- 同样做 4 步清洁
- 然后丢弃长度 < 5 的纯符号行

### toc 伪链接黑名单（必须过滤）
- `index.html`、`index_by_name.html`、`toc_*.html`、`../../documentation.html`
- 否则计数虚高（Ch22 86→52、Ch24 下 52→36 都因为这个）

## MD 文档统一结构
1. **引言三段**（全章 → 本卷 → 一句话总结）
2. **1. 全卷结构表**（子族×算子数×功能×场景）
3. **2. 子族分述（详细模式）**——每个算子一行 + 重点算子三段注（参数/误区）
4. **3. 全卷算子速查表**
5. **4. 跨算子误区 & 调试提示**
6. **5. 调用链路与组合用法**（3 个 HDevelop 代码块）
7. **6. 与其它章节的关联**
8. **7. 一句话核心要义**

## 思维导图布局美学版（matplotlib + SimHei）
- 1 子族 / 2 子族 / 3 子族 / 4 子族 / 5 子族 / 6 子族 / 7+ 子族 各有最优布局
  - 单子：垂直或水平单链
  - 双子：双子星（左上 + 右上 + 中心）
  - 三角 / 四角 / 五瓣 / 六瓣辐射 / 七瓣辐射
- **防重叠技巧**：7 张子卡均匀 360°/7 时，若用大椭圆作标题条会与正上/正下的卡片重叠。**改用纯背景圆 + 左下/右下角图例区**
- 配色：中心深蓝、每族独立主题色（橙/青/紫/红/绿）
- 中文字体：SimHei (`C:\Windows\Fonts\simhei.ttf`)

## Git 工作流
- SSH 私钥：`/c/Users/Administrator/.ssh/ai`
- 每次 `GIT_SSH_COMMAND='ssh -i /c/Users/Administrator/.ssh/ai -o StrictHostKeyChecking=no'` 包装 git 命令
- 提交后 `git ls-remote origin main` 验证远端 SHA 与本地一致
- 提交信息格式：`docs(halcon-chNN-XXX): 第 NN 章 ...`
- `.workbuddy/memory/YYYY-MM-DD.md` 必须 add（保留工作区数据约定）

## 已完成的章节
| Ch | 卷 | 算子数 | 子族数 | commit | 关键特色 |
|---|---|---|---|---|---|
| 1 | 单卷 1D测量 | 18 | 6 | - | PCB 焊盘宽实战 |
| 2 | 单卷 2D测量 | 30 | 7 | - | MetrologyHandle 抽象 |
| 3 | 单卷 3D匹配 | 40 | 4 | - | 6D Pose 给机器人 |
| 4 | 单卷 3D对象模型 | 52 | 4 | - | ObjectModel3D 4 步流水线 |
| 5 | 单卷 3D重建 | 65 | 5 | - | 5 种物理路径互补 |
| 6 | 单卷 标定 | 64 | 10 | - | 三套 API 老 flat → 新 CalibData |
| 7 | 单卷 分类 | 101 | 6 | - | LUT 极速查表 |
| 8 | 单卷 控制 | 35 关键字 | 7 | - | 不是图像算子 |
| 10 | 单卷 开发 | 42 dev_* | 8 | - | HDevelop IDE 限定 |
| 11 | 单卷 File I/O | 51 | 7 | a7d332b | 导出可移植性最高 |
| 12 | 上/中/下 三卷 | 41+87+59=187 | 3+7+8 | 94053a3, 505e3f2 | 最大单章 |
| 13 | 上/下 双卷 | 78+87=165 | 5+4 | 13d65fe, c4bdc74 | 主动绘图+窗口系统 |
| 14 | 单卷 识别 | 44 | 3 | f37929a | 三范式 |
| 15 | 上/下 双卷 | 62+44=106 | 5+4 | 464c4ea, bd326cf | 输入组织+分析变换 |
| 16 | 单卷 检测 | 53 | 5 | ea51fd7 | 五朵金花 |
| 17 | 上卷 Matching | 65 | 3 | c312395 | 经典模板匹配（上卷）|
| 18 | 单卷 Matrix | 57 | 7 | 6f56415 | 七星连珠思维导图 |
| 19 | 单卷 Morphology | 43 | 2 | 211f7f4 | 形态学七瓣辐射 |
| 20 | 上卷 OCR | 33 | 4 | 533ef7e | 识别核心 |
| 21 | 单卷 Object | 16 | 2 | 2d41b8f | 元组管家 |
| 22 | 上/中/下 三卷 | 35+41+29=105 | 4+1+2 | 044be24, 02e120b, a346a3d | 全章收官 |
| 23 | 单卷 Segmentation | 53 | 6 | 73ac0f9 | 6 套分割武器 |
| 24 | 上/中/下 三卷 | 47+52+36=135 | 5+4+4 | 1a99b88, bb2e80c, a458ece | 系统资源全栈（含 Sockets）|
| 25 | 上卷 Tools | 32 | 2 | b7365d4 | 数学小工具箱（背景估计+1D 函数）|
| 25 | 中卷 Tools | 42 | 5 | a16a9b0 | Geometry 5 主题（距离变换+测距+角度投影+求交+面积）|
| 25 | 下卷 Tools | 29 | 5 | 2a9afce | Grid Rect + Hough + Interpolation + Lines + Mosaicking 全章收官 |
| 26 | 上卷 Transformations | 51 | 2 | b6e4334 | 齐次矩阵决策库（2D 32 + 3D 19）|
| 26 | 下卷 Transformations | 40 | 4 | 907c009 | 3D 位姿数学（Poses 19 + Quat 9 + DualQuat 10 + Misc 2），四角辐射思维导图 |
| 27 | 上卷 Tuple | 63 | 3 | e2b71f9 | 元组数值算子基座（Arithmetic 45 + Bit 6 + Comparison 12），三角辐射思维导图 |

## 待完成的章节
- Ch27 下卷（Containers 10 + Conversion 12 + Creation 5 + ElementOrder 2 + Features 11 + LogicalOperations 4 + Manipulation 3 + Selection 11 + Sets 4 + StringOperations 15 + Type 14 = 91 ops）
- Ch17 Matching 下卷（Component-Based 24 + Descriptor-Based 15 = 39 ops）
- Ch20 OCR 下卷（MLP 20 + SVM 19 + KNN 13 + Training Files 9 = 61 ops）
- 后续章节：Ch27+ 待确认

## Python 环境
- 系统 Python：`C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe`
- 隔离 venv：`C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe`（用于 matplotlib）
- matplotlib 中文字体：SimHei + Microsoft YaHei + STXihei
- Bash 调用 Python 含中文字符串字面量容易 SyntaxError，**强烈推荐**：把含 unicode 的数据（描述/参数/误区）剥离到独立的 .json 配置文件
