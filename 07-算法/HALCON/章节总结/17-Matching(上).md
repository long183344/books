# 17 · Matching（上卷）

> HALCON 官方手册第 17 章 Matching **上卷** — 经典模板匹配 3 族 65 算子：相关性 (NCC) 14 + 形状 (Shape-Based) 28 + 可形变 (Deformable) 23。
> 主题：**模板的形状**——图像本身就是模板，像素或轮廓是匹配依据。
> 下卷 (Component + Descriptor) 介绍"模板的部件"——把目标拆成多个组件或局部特征点后匹配。

**数据基准**：HALCON 20.11.1.0 官方 Operator Reference。
**匹配定位**：所有 `find_*` 返回的是模型实例在搜索图中的位置（Row/Column/Angle）和得分 (Score)，不是分类。

---

## §0 本卷定位与适用读者

匹配（Matching）= 在搜索图里"找到和模板长得像的东西"。HALCON 提供 **5 族**算法，按模板的抽象层次从粗到精：

| 族 | 模板表示 | 适用场景 | 在本卷？ |
| --- | --- | --- | --- |
| **NCC**（相关性） | 像素灰度块 | 光照稳定、纹理丰富的印刷电���/对齐标记 | ✅ 上卷 |
| **Shape**（形状） | 边缘/轮廓 | 工业零件轮廓、字符、机械特征 | ✅ 上卷 |
| **Deformable**（可形变） | 局部可形变轮廓 | 印刷字符(变形)、弹性物体、轻微褶皱 | ✅ 上卷 |
| **Component**（组件） | 多组件模型 + 关系 | 装配验证、印刷电路多焊盘 | ⬇️ 下卷 |
| **Descriptor**（描述子） | 局部特征点 | 大幅旋转/缩放、3D 投影失真 | ⬇️ 下卷 |

> **怎么读**：先选"族"，再看 create / find / IO 三件套。上卷 3 族都是"全局单模板"思路，create 一次只能装一个模板（find_*_models 是同族多模板的批量版）；下卷 2 族则引入了"组件树 / 局部点云"概念。

---

## §1 三族速览

| 族 | 算子数 | 核心抽象 | 关键参数 | 适用条件 |
| --- | --- | --- | --- | --- |
| **Correlation-Based (NCC)** | 14 | `ModelID`（NCC 灰度块） | `NumLevels`, `AngleStart/Extent/Step`, `Metric` | 光照稳定 + 纹理丰富 + 缩放 ±10% 内 |
| **Shape-Based** | 28 | `ModelID`（轮廓金字塔） | `NumLevels`, `Angle/Scale*`, `Contrast`, `Optimization` | 工件轮廓清晰 + 对比度足够 |
| **Deformable** | 23 | `ModelID`（可形变网格 + 局部刚度） | `ScaleR*/ScaleC*`, `CamParam`(calib), `Pose`(calib) | 形变 < 模板 1/3 尺寸 |

> 三族共用 5 件套：**create → find → get/set → serialize/deserialize → clear**。区别在于 create 的输入（灰度图/轮廓 XLD）和 find 的输出（位姿 Pose 或 6D 位姿）。

---

## §2 思维导图

![Ch17 Matching 上卷 思维导图](./17-Matching(上).png)

> **三族三角辐射**：顶部 NCC（钢蓝）、右下 Shape（翠绿）、左下 Deformable（琥珀金）。中心焦点圆写"17·MATCHING·上卷"。每个花瓣卡片列出 4 个代表性算子 + 族计数。

---

## §3 Correlation-Based (NCC) 详解

### 3.1 一句话

**把模板图当作灰度"印章"，逐位置算归一化互相关 (Normalized Cross Correlation)**，得分越高越像。

### 3.2 7 步流水线

```
1) 准备模板图 Template（crop_domain + reduce_domain 到 ROI）
2) determine_ncc_model_params   ← 自动建议 NumLevels/Angle/Metric
3) create_ncc_model              ← 生成多级金字塔多角度的 NCC 模型
4) find_ncc_model (或 find_ncc_models 批量多个模型)
5) 拿到 Row, Column, Angle, Score
6) 序列化 save / 读取 read_ncc_model
7) 销毁 clear_ncc_model
```

### 3.3 关键参数解释

| 参数 | 类型 | 默认 | 含义 |
| --- | --- | --- | --- |
| `NumLevels` | 整数 | `'auto'` | 金字塔层数，值越大速度越快但精度越低 |
| `AngleStart/Extent/Step` | 角度 tuple | `[0,360,auto]` | 搜索角度范围与步长，步长大速度快 |
| `Metric` | string | `'use_polarity'` | `'use_polarity'` 同向灰度匹配；`'ignore_global_polarity'` 灰度反转仍匹配；`'ignore_local_polarity'` 局部反转也匹配 |
| `MinScore` | 0~1 | 0.8 | 最低得分，<此值丢弃 |
| `MaxOverlap` | 0~1 | 0.5 | 两个匹配框重叠 > 此值时丢弃得分低的 |
| `SubPixel` | string | `'false'` | `'interpolation'`/`'least_squares'`/`'least_squares_high'` 提高亚像素精度 |

### 3.4 4 类典型误用

| 误用 | 后果 | 正确做法 |
| --- | --- | --- |
| 把光照变化的图当模板 | 得分永远 < 0.5 | 用 `'ignore_global_polarity'` 或换 Shape-Based |
| 模板包含太多背景 | 匹配精度下降 | `reduce_domain` 抠出 ROI 再 create |
| 不设 NumLevels 直接默认 | 大图搜索极慢 | 先 `determine_ncc_model_params` 看建议值 |
| `AngleStep='auto'` 期望 0.1° | 角度步长被自动放大 | 显式传小步长，但要更久 |

### 3.5 NCC 的优势与局限

**优势**：速度最快、原理最简单、对纹理敏感。
**局限**：对光照敏感、对缩放容忍度低（±10%）、不抗遮挡（部分被遮就掉分）。

---

## §4 Shape-Based 详解

### 4.1 一句话

**把模板图的边缘（轮廓）抽出来建金字塔多角度模型**，搜索时也是抽边缘比轮廓相似度。

### 4.2 8 步流水线

```
1) 准备 Template（同 NCC），或准备 XLD Contours
2) create_shape_model (或 scaled/aniso 缩放版，或 _xld 版)
3) 拿到 ModelID 后可 inspect_shape_model 检查可视化
4) find_shape_model 搜索
5) get_shape_model_contours 取模型轮廓 + get_shape_model_origin 取参考点
6) find_shape_models 批量搜索（多个模型）
7) 序列化 + 读写
8) clear_shape_model
```

### 4.3 4 种 create 变体对比

| 算子 | 缩放类型 | 输入 | 适用 |
| --- | --- | --- | --- |
| `create_shape_model` | 不缩放 | 灰度图 | 固定距离相机 |
| `create_scaled_shape_model` | 各向同性 | 灰度图 | 距离变化 ±20% |
| `create_aniso_shape_model` | 各向异性（行/列独立） | 灰度图 | 透视/斜视 |
| `create_shape_model_xld` | 不缩放 | XLD 轮廓 | 用 CAD 轮廓做模板 |

### 4.4 关键参数

| 参数 | 含义 | 典型值 |
| --- | --- | --- |
| `NumLevels` | 边缘金字塔层数 | `'auto'` 或 4-6 |
| `AngleStart/Extent/Step` | 角度范围步长 | `[0,360,1]` 度 |
| `ScaleMin/Max/Step` (scaled) | 各向同性缩放 | `[0.8,1.2,0.02]` |
| `ScaleR*` / `ScaleC*` (aniso) | 行/列独立缩放 | `[0.8,1.2,0.02]` |
| `Optimization` | 优化策略 | `'none'`/`'point_reduction_low'`/`'point_reduction_high'`/`'pregeneration'` |
| `Metric` | 匹配度量 | `'use_polarity'`/`'ignore_global_polarity'` |
| `Contrast` / `MinContrast` | 边缘对比度阈值 | 阈值越高边缘越稀疏 |
| `Greediness` | 搜索贪婪度 | 0=全搜索(慢)，1=最快 |

### 4.5 高级用法：adapt + clutter

- `adapt_shape_model_high_noise`：用高噪声测试图调参，返回更鲁棒的 `ResultDict`
- `set_shape_model_clutter`：用 ClutterRegion 告诉模型"这块区域不要匹配"
- `set_shape_model_metric`：动态改 metric（比如有遮挡时换 `'ignore_local_polarity'`）

### 4.6 4 类典型误用

| 误用 | 后果 | 正确做法 |
| --- | --- | --- |
| Contrast 阈值给太低 | 大量噪声边缘，匹配慢且不准 | 用 `inspect_shape_model` 看可视化 |
| `Optimization='pregeneration'` + 大角度范围 | 内存爆炸 | 只在角度范围小时用 |
| 忽视 `Greediness` | 默认太慢 | 调大到 0.7-0.9 |
| 用 _xld 版的优势被忽略 | 还是从位图抠 | CAD 工程图直接用 _xld |

---

## §5 Deformable 详解

### 5.1 一句话

**Shape-Based 的扩展**：模板轮廓被建成可形变的网格，搜索时不仅找位置，还能承受轮廓的局部非线性形变。

### 5.2 6 种 create 变体对比

| 算子 | 匹配模式 | 输入 | 输出姿态 |
| --- | --- | --- | --- |
| `create_planar_uncalib_deformable_model` | 平面 + 透视 | 灰度图 | 2D HomMat2D |
| `create_planar_calib_deformable_model` | 平面 + 相机标定 | 灰度图+CamParam+Pose | 3D Pose |
| `create_local_deformable_model` | 局部形变 | 灰度图 | 形变图 + 形变矢量场 |
| `_xld` 三个对应版 | 用 XLD 轮廓做模板 | XLD | 同上 |

### 5.3 6 步流水线

```
1) 选 create 变体（按相机标定情况）
2) create_*_deformable_model  关键参数：ScaleR*/ScaleC*, CamParam(若 calib), Pose(若 calib)
3) find_*_deformable_model
   - local  → 返回 ImageRectified + VectorField + DeformedContours
   - planar calib    → 返回 Pose + CovPose + Score
   - planar uncalib  → 返回 HomMat2D + Score
4) get_deformable_model_contours 取模型轮廓
5) set_*_metric 动态调 metric
6) clear_deformable_model
```

### 5.4 关键参数

| 参数 | 含义 | 适用 |
| --- | --- | --- |
| `ScaleR*/ScaleC*` | 行/列方向允许的仿射缩放 | 透视失真 |
| `CamParam` | 相机内参（仅 calib 版） | 已知相机标定 |
| `ReferencePose` | 模板在标定坐标系下的初始姿态（仅 calib 版） | 已知世界位姿 |
| `Pose`(find 返回) | 6D 姿态 | robot pick-and-place |
| `VectorField`(local find 返回) | 逐像素形变矢量 | 印刷字符变形分析 |

### 5.5 与 Shape 的本质区别

Shape-Based 假设模板与目标的差异只有**全局刚体变换**（平移+旋转+缩放）；Deformable 允许**局部非线性形变**。代价是计算量更大、参数更复杂。

### 5.6 4 类典型误用

| 误用 | 后果 | 正确做法 |
| --- | --- | --- |
| 全局缩放能用 Shape 解决的也用 Deformable | 慢 10x + 不准 | ScaleR/ScaleC 范围小就用 Shape |
| 不给 `CamParam` 就用 calib 版 | 报错或位姿错 | 有相机标定才用 calib 版 |
| local 版的输出图像直接当 rectified 用 | 形变区域有边缘伪影 | 仅看 ROI 内的形变量 |
| 用 `set_planar_calib_deformable_model_metric` 改 metric 但漏 Pose | metric 不更新 | 一定要传 Pose 参数 |

---

## §6 三族关系图

```
                       ┌──────────────────────┐
                       │  Matching 选型入口    │
                       └──────────┬───────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
   │  NCC (像素级)    │  │ Shape (轮廓级)   │  │ Deformable      │
   │  最快 / 最简单   │  │ 工业检测主力     │  │ 抗形变 / 抗失真  │
   │ 14 算子         │  │ 28 算子          │  │ 23 算子         │
   └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
            │                    │                    │
            ▼                    ▼                    ▼
      find_ncc_model      find_shape_model    find_*_deformable_model
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 ▼
                       Row, Column, Angle, Score
                       (+ Pose for Deformable calib)
```

> **共同点**：都遵循 `create_*_model` → `find_*_model` → `clear_*_model` 三件套；都返回 `Score`（越大越像）。
> **差异**：NCC 抗旋转不抗缩放；Shape 抗旋转+缩放；Deformable 还抗局部形变。

---

## §7 选型决策矩阵

| 场景 | 推荐族 | 原因 |
| --- | --- | --- |
| 印刷电路字符定位（光照稳定） | NCC | 字符纹理丰富，最快 |
| 工件边缘定位（对比度足） | Shape | 工业首选 |
| 印刷变形字符（OCR 前置） | Deformable local | 抗字符变形 |
| 远近距离变化的工件 | Shape aniso/scaled | 抗缩放 |
| 已知相机标定 + 6D 位姿 | Deformable planar_calib | 直接返 Pose |
| 训练样本少 + 强形变 | Deformable local | 不需要预先训练形变 |
| 多组件布局（电路多焊盘） | Component（下卷） | 多组件 + 关系 |
| 大幅旋转 + 缩放 + 失真 | Descriptor（下卷） | 局部特征点鲁棒 |

---

## §8 10 条误区

1. **不调 `NumLevels`**——直接用默认 `'auto'`，大图搜索时间翻倍。**正解**：先 `determine_*_model_params` 看到建议再调。
2. **NCC 用于光照变化场景**——NCC 默认 `'use_polarity'` 对光照反转敏感。**正解**：用 `'ignore_global_polarity'`。
3. **用 Shape 但忘了 `Contrast`**——对比度阈值太低导致大量噪声边缘。**正解**：用 `inspect_shape_model` 看可视化。
4. **Deformable 全局缩放也能干却用了**——Deformable 比 Shape 慢一个数量级。**正解**：全局刚体变换用 Shape。
5. **calib 版不传 CamParam**——运行时报错或位姿错误。**正解**：相机标定后才用 calib 版。
6. **`set_*_model_param` 名字记错**——NCC/Shape/Deformable 的 GenParam 不同。**正解**：查官方 `*_model_params`。
7. **大角度范围 + 高 NumLevels**——内存爆炸。**正解**：按 `determine_*_model_params` 建议调小。
8. **不 `clear_*_model`**——HALCON 进程内存泄漏。**正解**：脚本结束或换图时 clear。
9. **`find_*_model` 不设 `MinScore`**——返回大量低质量匹配。**正解**：先看 Score 分布定阈值。
10. **跨相机改变焦后 Shape 模型失效**——Shape 缩放搜索范围有限。**正解**：用 scaled/aniso 或重新 create。

---

## §9 完整签名速查

> 三张子表，**先看族**，再按「create / get-set / find / IO」分组快速定位。

### §9.1 Correlation-Based (NCC) — 14 ops

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| clear_ncc_model | 释放 NCC 模型内存 | `clear_ncc_model ( : : ModelID : )` |
| create_ncc_model | 从灰度图创建 NCC 模板 | `create_ncc_model ( Template : : NumLevels , AngleStart , AngleExtent , AngleStep , Metric : ModelID )` |
| deserialize_ncc_model | 从序列化数据恢复 NCC 模型 | `deserialize_ncc_model ( : : SerializedItemHandle : ModelID )` |
| determine_ncc_model_params | 自动建议 NCC 模型参数 | `determine_ncc_model_params ( Template : : NumLevels , AngleStart , AngleExtent , Metric , Parameters : ParameterName , ParameterValue )` |
| find_ncc_model | 在图中搜索单个 NCC 模型 | `find_ncc_model ( Image : : ModelID , AngleStart , AngleExtent , MinScore , NumMatches , MaxOverlap , SubPixel , NumLevels : Row , Column , Angle , Score )` |
| find_ncc_models | 在图中搜索多个 NCC 模型 | `find_ncc_models ( Image : : ModelIDs , AngleStart , AngleExtent , MinScore , NumMatches , MaxOverlap , SubPixel , NumLevels : Row , Column , Angle , Score , Model )` |
| get_ncc_model_origin | 取 NCC 模型参考点 | `get_ncc_model_origin ( : : ModelID : Row , Column )` |
| get_ncc_model_params | 取 NCC 模型创建参数 | `get_ncc_model_params ( : : ModelID : NumLevels , AngleStart , AngleExtent , AngleStep , Metric )` |
| get_ncc_model_region | 取 NCC 模型的 ROI 区域 | `get_ncc_model_region ( : ModelRegion : ModelID : )` |
| read_ncc_model | 从磁盘读取 NCC 模型 | `read_ncc_model ( : : FileName : ModelID )` |
| serialize_ncc_model | 序列化 NCC 模型 | `serialize_ncc_model ( : : ModelID : SerializedItemHandle )` |
| set_ncc_model_origin | 改 NCC 模型参考点 | `set_ncc_model_origin ( : : ModelID , Row , Column : )` |
| set_ncc_model_param | 改 NCC 模型 GenParam | `set_ncc_model_param ( : : ModelID , GenParamName , GenParamValue : )` |
| write_ncc_model | 把 NCC 模型写盘 | `write_ncc_model ( : : ModelID , FileName : )` |

### §9.2 Shape-Based — 28 ops

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| adapt_shape_model_high_noise | 用高噪声图调 Shape 模型参数 | `adapt_shape_model_high_noise ( ImageReduced : : ModelID , GenParam : ResultDict )` |
| clear_shape_model | 释放 Shape 模型内存 | `clear_shape_model ( : : ModelID : )` |
| create_aniso_shape_model | 创建各向异性缩放 Shape 模型（灰度输入） | `create_aniso_shape_model ( Template : : NumLevels , AngleStart , AngleExtent , AngleStep , ScaleRMin , ScaleRMax , ScaleRStep , ScaleCMin , ScaleCMax , ScaleCStep , Optimization , Metric , Contrast , MinContrast : ModelID )` |
| create_aniso_shape_model_xld | 创建各向异性缩放 Shape 模型（XLD 输入） | `create_aniso_shape_model_xld ( Contours : : NumLevels , AngleStart , AngleExtent , AngleStep , ScaleRMin , ScaleRMax , ScaleRStep , ScaleCMin , ScaleCMax , ScaleCStep , Optimization , Metric , MinContrast : ModelID )` |
| create_scaled_shape_model | 创建各向同性缩放 Shape 模型（灰度输入） | `create_scaled_shape_model ( Template : : NumLevels , AngleStart , AngleExtent , AngleStep , ScaleMin , ScaleMax , ScaleStep , Optimization , Metric , Contrast , MinContrast : ModelID )` |
| create_scaled_shape_model_xld | 创建各向同性缩放 Shape 模型（XLD 输入） | `create_scaled_shape_model_xld ( Contours : : NumLevels , AngleStart , AngleExtent , AngleStep , ScaleMin , ScaleMax , ScaleStep , Optimization , Metric , MinContrast : ModelID )` |
| create_shape_model | 创建不缩放 Shape 模型（灰度输入） | `create_shape_model ( Template : : NumLevels , AngleStart , AngleExtent , AngleStep , Optimization , Metric , Contrast , MinContrast : ModelID )` |
| create_shape_model_xld | 创建不缩放 Shape 模型（XLD 输入） | `create_shape_model_xld ( Contours : : NumLevels , AngleStart , AngleExtent , AngleStep , Optimization , Metric , MinContrast : ModelID )` |
| deserialize_shape_model | 从序列化数据恢复 Shape 模型 | `deserialize_shape_model ( : : SerializedItemHandle : ModelID )` |
| determine_shape_model_params | 自动建议 Shape 模型参数 | `determine_shape_model_params ( Template : : NumLevels , AngleStart , AngleExtent , ScaleMin , ScaleMax , Optimization , Metric , Contrast , MinContrast , Parameters : ParameterName , ParameterValue )` |
| find_aniso_shape_model | 在图中搜索单个各向异性 Shape 模型 | `find_aniso_shape_model ( Image : : ModelID , AngleStart , AngleExtent , ScaleRMin , ScaleRMax , ScaleCMin , ScaleCMax , MinScore , NumMatches , MaxOverlap , SubPixel , NumLevels , Greediness : Row , Column , Angle , ScaleR , ScaleC , Score )` |
| find_aniso_shape_models | 在图中搜索多个各向异性 Shape 模型 | `find_aniso_shape_models ( Image : : ModelIDs , AngleStart , AngleExtent , ScaleRMin , ScaleRMax , ScaleCMin , ScaleCMax , MinScore , NumMatches , MaxOverlap , SubPixel , NumLevels , Greediness : Row , Column , Angle , ScaleR , ScaleC , Score , Model )` |
| find_scaled_shape_model | 在图中搜索单个各向同性 Shape 模型 | `find_scaled_shape_model ( Image : : ModelID , AngleStart , AngleExtent , ScaleMin , ScaleMax , MinScore , NumMatches , MaxOverlap , SubPixel , NumLevels , Greediness : Row , Column , Angle , Scale , Score )` |
| find_scaled_shape_models | 在图中搜索多个各向同性 Shape 模型 | `find_scaled_shape_models ( Image : : ModelIDs , AngleStart , AngleExtent , ScaleMin , ScaleMax , MinScore , NumMatches , MaxOverlap , SubPixel , NumLevels , Greediness : Row , Column , Angle , Scale , Score , Model )` |
| find_shape_model | 在图中搜索单个 Shape 模型 | `find_shape_model ( Image : : ModelID , AngleStart , AngleExtent , MinScore , NumMatches , MaxOverlap , SubPixel , NumLevels , Greediness : Row , Column , Angle , Score )` |
| find_shape_models | 在图中搜索多个 Shape 模型 | `find_shape_models ( Image : : ModelIDs , AngleStart , AngleExtent , MinScore , NumMatches , MaxOverlap , SubPixel , NumLevels , Greediness : Row , Column , Angle , Score , Model )` |
| get_shape_model_clutter | 取 Shape 模型的 clutter 参数 | `get_shape_model_clutter ( : ClutterRegion : ModelID , GenParamName : GenParamValue , HomMat2D , ClutterContrast )` |
| get_shape_model_contours | 取 Shape 模型的可视化轮廓 | `get_shape_model_contours ( : ModelContours : ModelID , Level : )` |
| get_shape_model_origin | 取 Shape 模型参考点 | `get_shape_model_origin ( : : ModelID : Row , Column )` |
| get_shape_model_params | 取 Shape 模型创建参数 | `get_shape_model_params ( : : ModelID : NumLevels , AngleStart , AngleExtent , AngleStep , ScaleMin , ScaleMax , ScaleStep , Metric , MinContrast )` |
| inspect_shape_model | 可视化 Shape 模型 | `inspect_shape_model ( Image : ModelImages , ModelRegions : NumLevels , Contrast : )` |
| read_shape_model | 从磁盘读取 Shape 模型 | `read_shape_model ( : : FileName : ModelID )` |
| serialize_shape_model | 序列化 Shape 模型 | `serialize_shape_model ( : : ModelID : SerializedItemHandle )` |
| set_shape_model_clutter | 设置 Shape 模型的 clutter 区域 | `set_shape_model_clutter ( ClutterRegion : : ModelID , HomMat2D , ClutterContrast , GenParamName , GenParamValue : )` |
| set_shape_model_metric | 改 Shape 模型的 metric | `set_shape_model_metric ( Image : : ModelID , HomMat2D , Metric : )` |
| set_shape_model_origin | 改 Shape 模型参考点 | `set_shape_model_origin ( : : ModelID , Row , Column : )` |
| set_shape_model_param | 改 Shape 模型 GenParam | `set_shape_model_param ( : : ModelID , GenParamName , GenParamValue : )` |
| write_shape_model | 把 Shape 模型写盘 | `write_shape_model ( : : ModelID , FileName : )` |

### §9.3 Deformable — 23 ops

| 算子 | 一句话功能 | HDevelop 关键签名 |
| --- | --- | --- |
| clear_deformable_model | 释放 Deformable 模型内存 | `clear_deformable_model ( : : ModelID : )` |
| create_local_deformable_model | 创建局部可形变模型（灰度输入） | `create_local_deformable_model ( Template : : NumLevels , AngleStart , AngleExtent , AngleStep , ScaleRMin , ScaleRMax , ScaleRStep , ScaleCMin , ScaleCMax , ScaleCStep , Optimization , Metric , Contrast , MinContrast , GenParamName , GenParamValue : ModelID )` |
| create_local_deformable_model_xld | 创建局部可形变模型（XLD 输入） | `create_local_deformable_model_xld ( Contours : : NumLevels , AngleStart , AngleExtent , AngleStep , ScaleRMin , ScaleRMax , ScaleRStep , ScaleCMin , ScaleCMax , ScaleCStep , Optimization , Metric , MinContrast , GenParamName , GenParamValue : ModelID )` |
| create_planar_calib_deformable_model | 创建平面+相机标定的可形变模型 | `create_planar_calib_deformable_model ( Template : : CamParam , ReferencePose , NumLevels , AngleStart , AngleExtent , AngleStep , ScaleRMin , ScaleRMax , ScaleRStep , ScaleCMin , ScaleCMax , ScaleCStep , Optimization , Metric , Contrast , MinContrast , GenParamName , GenParamValue : ModelID )` |
| create_planar_calib_deformable_model_xld | 同上（XLD 输入） | `create_planar_calib_deformable_model_xld ( Contours : : CamParam , ReferencePose , NumLevels , AngleStart , AngleExtent , AngleStep , ScaleRMin , ScaleRMax , ScaleRStep , ScaleCMin , ScaleCMax , ScaleCStep , Optimization , Metric , MinContrast , GenParamName , GenParamValue : ModelID )` |
| create_planar_uncalib_deformable_model | 创建平面+无标定的可形变模型 | `create_planar_uncalib_deformable_model ( Template : : NumLevels , AngleStart , AngleExtent , AngleStep , ScaleRMin , ScaleRMax , ScaleRStep , ScaleCMin , ScaleCMax , ScaleCStep , Optimization , Metric , Contrast , MinContrast , GenParamName , GenParamValue : ModelID )` |
| create_planar_uncalib_deformable_model_xld | 同上（XLD 输入） | `create_planar_uncalib_deformable_model_xld ( Contours : : NumLevels , AngleStart , AngleExtent , AngleStep , ScaleRMin , ScaleRMax , ScaleRStep , ScaleCMin , ScaleCMax , ScaleCStep , Optimization , Metric , MinContrast , GenParamName , GenParamValue : ModelID )` |
| deserialize_deformable_model | 从序列化数据恢复可形变模型 | `deserialize_deformable_model ( : : SerializedItemHandle : ModelID )` |
| determine_deformable_model_params | 自动建议可形变模型参数 | `determine_deformable_model_params ( Template : : NumLevels , AngleStart , AngleExtent , ScaleMin , ScaleMax , Optimization , Metric , Contrast , MinContrast , GenParamName , GenParamValue , Parameters : ParameterName , ParameterValue )` |
| find_local_deformable_model | 在图中搜索局部可形变模型（返 VectorField） | `find_local_deformable_model ( Image : ImageRectified , VectorField , DeformedContours : ModelID , AngleStart , AngleExtent , ScaleRMin , ScaleRMax , ScaleCMin , ScaleCMax , MinScore , NumMatches , MaxOverlap , NumLevels , Greediness , ResultType , GenParamName , GenParamValue : Score , Row , Column )` |
| find_planar_calib_deformable_model | 在图中搜索平面标定可形变模型（返 Pose） | `find_planar_calib_deformable_model ( Image : : ModelID , AngleStart , AngleExtent , ScaleRMin , ScaleRMax , ScaleCMin , ScaleCMax , MinScore , NumMatches , MaxOverlap , NumLevels , Greediness , GenParamName , GenParamValue : Pose , CovPose , Score )` |
| find_planar_uncalib_deformable_model | 在图中搜索平面无标定可形变模型（返 HomMat2D） | `find_planar_uncalib_deformable_model ( Image : : ModelID , AngleStart , AngleExtent , ScaleRMin , ScaleRMax , ScaleCMin , ScaleCMax , MinScore , NumMatches , MaxOverlap , NumLevels , Greediness , GenParamName , GenParamValue : HomMat2D , Score )` |
| get_deformable_model_contours | 取可形变模型可视化轮廓 | `get_deformable_model_contours ( : ModelContours : ModelID , Level : )` |
| get_deformable_model_origin | 取可形变模型参考点 | `get_deformable_model_origin ( : : ModelID : Row , Column )` |
| get_deformable_model_params | 取可形变模型 GenParam | `get_deformable_model_params ( : : ModelID , GenParamName : GenParamValue )` |
| read_deformable_model | 从磁盘读取可形变模型 | `read_deformable_model ( : : FileName : ModelID )` |
| serialize_deformable_model | 序列化可形变模型 | `serialize_deformable_model ( : : ModelID : SerializedItemHandle )` |
| set_deformable_model_origin | 改可形变模型参考点 | `set_deformable_model_origin ( : : ModelID , Row , Column : )` |
| set_deformable_model_param | 改可形变模型 GenParam | `set_deformable_model_param ( : : ModelID , GenParamName , GenParamValue : )` |
| set_local_deformable_model_metric | 改 local 版的 metric | `set_local_deformable_model_metric ( Image , VectorField : : ModelID , Metric : )` |
| set_planar_calib_deformable_model_metric | 改 planar calib 版的 metric | `set_planar_calib_deformable_model_metric ( Image : : ModelID , Pose , Metric : )` |
| set_planar_uncalib_deformable_model_metric | 改 planar uncalib 版的 metric | `set_planar_uncalib_deformable_model_metric ( Image : : ModelID , HomMat2D , Metric : )` |
| write_deformable_model | 把可形变模型写盘 | `write_deformable_model ( : : ModelID , FileName : )` |

---

## §10 与下卷衔接

| 上卷 (本卷) | 下卷预告 |
| --- | --- |
| **NCC** — 单像素块模板 |  |
| **Shape** — 单轮廓模板 |  |
| **Deformable** — 单可形变轮廓 |  |
|  | **Component-Based (24 ops)** — 多组件 + 关系树，适合装配/电路多焊盘 |
|  | **Descriptor-Based (15 ops)** — 局部特征点 + 描述子，大幅旋转/缩放/失真鲁棒 |

> **下卷预告**：Component 解决"一个目标里多个零件的相对关系"；Descriptor 解决"大幅旋转缩放下传统模板失效"。两者配合可以处理从微观芯片到宏观场景的多层次匹配。