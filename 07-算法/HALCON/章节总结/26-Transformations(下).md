# Ch26 Transformations（下卷）— 3D 姿态 / 四元数 / 双四元数数学体系

## 引言

HALCON 第 26 章《Transformations》共 119 个算子，本卷承接上卷 2D/3D 几何变换，处理 **3D 姿态**（Pose）的核心数学表示：**Poses 19 ops**、**Quaternions 9 ops**、**Dual Quaternions 10 ops**、**Misc 2 ops**，共 40 ops。本卷与上卷合起来构成完整的 3D 刚体变换数学工具链：Pose 7 元组描述位置+旋转；Quat 紧凑无奇点；Dual Quat 把旋转+平移合一为 8 元数，适合做平滑插值与螺旋运动；Cart↔Spher 互换便于球面/经纬度场景。

本卷（Ch26 下）按主题分到 4 个子族：Poses（19）、Quaternions（9）、Dual Quaternions（10）、Misc（2），共 **40** 个算子。一句话总结：**3D 位姿的所有数学表示方式（Pose 7 元 / Quat 4 元 / 双四元数 8 元）及其相互转换与序列化，是 3D 视觉、机器人、SLAM、动画的数学底座。**

## 1. 全卷结构表

| 子族 | 算子数 | 功能概述 | 典型场景 |
|------|--------|----------|----------|
| Poses 姿态 | 19 | 7 元数描述刚体位姿：构造、约定转换、与 Quat/Dual Quat 互换、序列化、文件读写、平均/复合 | 机器人末端位姿、相机外参、3D 匹配输出、文件持久化 |
| Quaternions 四元数 | 9 | 单位四元数描述 3D 旋转：构造、复合、共轭、归一化、SLERP 插值、点旋转、↔ 旋转矩阵、↔ 轴角、序列化 | 3D 旋转插值（避免万向锁）、SLAM 后端、姿态融合 |
| Dual Quaternions 双四元数 | 10 | 对偶四元数把旋转+平移合并为 8 元数（Screw 螺旋理论）：构造、复合、共轭、插值、↔ 同次矩阵、↔ 螺旋、序列化 | 骨骼蒙皮、关节运动平滑过渡、运动学逆解 |
| Misc 杂项 | 2 | 3D 点笛卡尔↔球坐标互换 | 全向相机/激光雷达→经纬度、球面分布点云 |

## 2. 子族分述（详细模式）

### 2.1 Dual Quaternions（10 ops）

- **功能**：
- **场景**：

**算子清单**（一行速览）：

- `dual_quat_compose`：复合两个双四元数（对偶数乘法，同时表达旋转+平移）
- `dual_quat_conjugate`：对偶四元数共轭（实部与对偶部取反，实现旋转反向）
- `dual_quat_interpolate`：双四元数线性混合插值（dual quaternion blending，动画级最短路径）
- `dual_quat_normalize`：归一化双四元数以保证单位长度（复合/插值前必做）
- `dual_quat_to_hom_mat3d`：双四元数→4×4 同次变换矩阵（含旋转+平移）
- `dual_quat_to_screw`：双四元数→螺旋轴表示（Chasles 定理：刚体=绕轴旋转+沿轴平移）
- `dual_quat_trans_line_3d`：用双四元数变换 3D 直线（点+方向，比点云高效）
- `screw_to_dual_quat`：螺旋轴表示→双四元数（与 dual_quat_to_screw 互逆）
- `serialize_dual_quat`：双四元数序列化（进程间/网络传输）
- `deserialize_dual_quat`：反序列化还原双四元数

**重点算子详解**：

#### dual_quat_compose

- **关键签名**：`dual_quat_compose ( : : DualQuaternionLeft, DualQuaternionRight : DualQuaternionComposed)`
- **参数 / 取值**：DualQuaternionLeft ⊗ DualQuaternionRight
- **常见误区**：复合遵循与 Pose 相同的右乘约定，但**内部用对偶数乘法，可同时表达旋转和平移**，比 Pose 少一个旋转约定参数。

#### dual_quat_interpolate

- **关键签名**：`dual_quat_interpolate ( : : DualQuaternionStart, DualQuaternionEnd, InterpPos : DualQuaternionInterpolated)`
- **参数 / 取值**：DualQuat1 + DualQuat2 + Fraction → DualQuatInterpolated
- **常见误区**：比 Pose 的 SLERP 更平滑，对**骨骼蒙皮和连续关节动画**极其重要；插值前必归一化。

#### dual_quat_to_hom_mat3d

- **关键签名**：`dual_quat_to_hom_mat3d ( : : DualQuaternion : HomMat3D)`
- **参数 / 取值**：DualQuat → 4×4 同次变换矩阵（含旋转+平移）
- **常见误区**：是 **双四元数 → 齐次矩阵的最常用出口**，可直接喂给 affine_trans_point_3d。

#### dual_quat_to_screw

- **关键签名**：`dual_quat_to_screw ( : : DualQuaternion, ScrewFormat : AxisDirectionX, AxisDirectionY, AxisDirectionZ, AxisMomentOrPointX, AxisMomentOrPointY, AxisMomentOrPointZ, Rotation, Translation)`
- **参数 / 取值**：DualQuat → ScrewAxis (axisX,axisY,axisZ,angleX4,angleY4,angleZ4) + ScrewAngle + ScrewTranslation
- **常见误区**：Screw（Chasles 定理）：任何刚体运动可表示为绕某轴的旋转+沿该轴的平移；适合运动学分解。

#### dual_quat_trans_line_3d

- **关键签名**：`dual_quat_trans_line_3d ( : : DualQuaternion, LineFormat, LineDirectionX, LineDirectionY, LineDirectionZ, LineMomentOrPointX, LineMomentOrPointY, LineMomentOrPointZ : TransLineDirectionX, TransLineDirectionY, TransLineDirectionZ, TransLineMomentOrPointX, TransLineMomentOrPointY, TransLineMomentOrPointZ)`
- **参数 / 取值**：DualQuat + 3D 直线 → 变换后直线
- **常见误区**：在标定和机器人坐标系变换中**用直线（点+方向）作输入，比点云高效得多**，10⁶ 点降为 10² 直线段。

#### screw_to_dual_quat

- **关键签名**：`screw_to_dual_quat ( : : ScrewFormat, AxisDirectionX, AxisDirectionY, AxisDirectionZ, AxisMomentOrPointX, AxisMomentOrPointY, AxisMomentOrPointZ, Rotation, Translation : DualQuaternion)`
- **参数 / 取值**：ScrewAxis + ScrewAngle + ScrewTranslation → DualQuat
- **常见误区**：与 dual_quat_to_screw 互逆，**配合 motion_estimators 的位姿平滑输出**可直接重建运动轨迹。

### 2.2 Poses 姿态（19 ops）

- **功能**：3D 刚体变换的 7 元数表示（Tx,Ty,Tz,Rx,Ry,Rz + 旋转约定/视角）；含构造、类型转换、与四元数/双四元数互换、读写文件、序列化、姿态平均等。
- **场景**：机器人末端位姿、相机外参、3D 匹配后的位姿输出与文件持久化

**算子清单**（一行速览）：

- `convert_pose_type`：改变姿态变换约定（OrderOfTransform/OrderOfRotation/ViewOfTransform）
- `create_pose`：从 6 自由度+约定创建 7 元姿态 Pose
- `deserialize_pose`：反序列化还原姿态
- `dual_quat_to_pose`：双四元数→姿态（自带归一化）
- `get_circle_pose`：由共圆 3D 点估计圆所在平面姿态（快速 6D 定位）
- `get_pose_type`：查询姿态的变换约定
- `get_rectangle_pose`：由矩形轮廓估计姿态（平面工件定位）
- `pose_average`：多姿态加权平均（几何/迭代加权，重建必备）
- `pose_compose`：复合两个姿态（HALCON 右乘约定）
- `pose_invert`：求逆姿态（旋转转置+平移取反）
- `pose_to_dual_quat`：姿态→双四元数
- `pose_to_quat`：姿态旋转部分→单位四元数
- `proj_hom_mat2d_to_pose`：2D 同次矩阵→3D 姿态（平面假设）
- `quat_to_pose`：四元数→姿态旋转部分
- `read_pose`：从 .pos 文件读取姿态
- `serialize_pose`：姿态序列化（进程间/网络传输）
- `set_origin_pose`：平移偏移姿态原点（改变平移分量）
- `vector_to_pose`：6 元素向量→姿态
- `write_pose`：姿态写 .pos 文件

**重点算子详解**：

#### convert_pose_type

- **关键签名**：`convert_pose_type ( : : PoseIn, OrderOfTransform, OrderOfRotation, ViewOfTransform : PoseOut)`
- **参数 / 取值**：Pose + OrderOfTransform + OrderOfRotation + ViewOfTransform → PoseNew
- **常见误区**：用于把外部库（如 OpenCV 的轴角+前乘/后乘约定）的姿态归一化为 HALCON 标准，方便跨框架对齐。

#### create_pose

- **关键签名**：`create_pose ( : : TransX, TransY, TransZ, RotX, RotY, RotZ, OrderOfTransform, OrderOfRotation, ViewOfTransform : Pose)`
- **参数 / 取值**：7 元数 (Tx,Ty,Tz,Rx,Ry,Rz) + OrderOfTransform('Rp+T'/'Tb+R'/'Rt+T') + OrderOfRotation 旋转顺序 + ViewOfTransform 'point'/'coordinate_system'
- **常见误区**：ViewOfTransform 默认 'point'：姿态作用于点（机器人世界→工具）；'coordinate_system' 作用于坐标系（标定板→相机），**方向相反**，机器人与视觉对接时极易踩坑。

#### dual_quat_to_pose

- **关键签名**：`dual_quat_to_pose ( : : DualQuaternion : Pose)`
- **参数 / 取值**：DualQuat → Pose
- **常见误区**：会自动归一化，**转换前后平移分量的尺度会缩放**，不要做线性插值（必须用 dual_quat_interpolate）。

#### get_circle_pose

- **关键签名**：`get_circle_pose (Contour : : CameraParam, Radius, OutputType : Pose1, Pose2)`
- **参数 / 取值**：已知至少 3 个 3D 点共圆，输入 Contour/Points → Pose + Quality
- **常见误区**：是 3D 匹配的轻量替代，适合圆盘零件的快速 6D 定位；点少于 3 个或退化共线时 Quality 会很低。

#### pose_average

- **关键签名**：`pose_average ( : : Poses, Weights, Mode, SigmaT, SigmaR : AveragePose, Quality)`
- **参数 / 取值**：Poses 元组 + Weights 元组 + Mode('geometric'/'iterative'/'weighted') + SigmaT 平移噪声 + SigmaR 旋转噪声 → AveragePose + Quality (0-1)
- **常见误区**：Mode='geometric' 闭式解速度快但精度差；'iterative' 用 SigmaT/SigmaR 做迭代加权，最稳；多视图 SfM 重建必有这一步。

#### pose_compose

- **关键签名**：`pose_compose ( : : PoseLeft, PoseRight : PoseCompose)`
- **参数 / 取值**：PoseLeft ⊕ PoseRight = PoseComposed，等价齐次矩阵右乘
- **常见误区**：组合顺序与机器人学约定相反，HALCON 中 PoseComposed = PoseLeft · PoseRight（先 Right 后 Left），与多数 SLAM 框架相反，**阅读时一定看箭头**。

#### pose_invert

- **关键签名**：`pose_invert ( : : Pose : PoseInvert)`
- **参数 / 取值**：输出 PoseInverted，旋转取转置、平移取反
- **常见误区**：对带噪声的姿态求逆误差会放大，求逆前后插值比反向追踪更稳。

#### proj_hom_mat2d_to_pose

- **关键签名**：`proj_hom_mat2d_to_pose ( : : Homography, CameraMatrix, Method : Pose)`
- **参数 / 取值**：2D 同次矩阵 + CameraMatrix + 其中一行相机平移 z=0 的假设 → 3D Pose
- **常见误区**：N 透视矩阵 → 位姿的近似还原，平面假设强；适合 AOI 平面工件定位，不适合 6D 抓取。

#### read_pose

- **关键签名**：`read_pose ( : : PoseFile : Pose)`
- **参数 / 取值**：FileName (.dat) → Pose
- **常见误区**：默认文件后缀 .pos 不是 .dat；HALCON 20 之前是 .dat，新版统一为 .pos，注意旧文件迁移。

#### serialize_pose

- **关键签名**：`serialize_pose ( : : Pose : SerializedItemHandle)`
- **参数 / 取值**：Pose → SerializedItemHandle，含版本号和 OrderOfTransform 等元数据
- **常见误区**：**二进制序列化 vs read_pose .dat 文本格式是两个体系**，serialize_pose 用于进程间传递，write_pose 用于持久化文件，**不要混用**。

### 2.3 Quaternions 四元数（9 ops）

- **功能**：单位四元数 q=(x,y,z,w) 描述 3D 旋转，无奇点、便于插值。含构造、复合、共轭、归一化、SLERP 插值、点旋转、↔ 旋转矩阵、↔ 轴角、序列化。
- **场景**：3D 旋转插值（避免万向锁）、SLAM 后端、姿态融合、动画关键帧

**算子清单**（一行速览）：

- `axis_angle_to_quat`：轴角→单位四元数（轴必须单位向量）
- `deserialize_quat`：反序列化还原四元数
- `quat_compose`：复合两个四元数（Hamilton 约定，与部分引擎相反）
- `quat_conjugate`：四元数共轭（旋转反向，q⁻¹）
- `quat_interpolate`：四元数球面线性插值 SLERP（最短路径，fraction∈[0,1]）
- `quat_normalize`：归一化四元数（复合/插值前必做）
- `quat_rotate_point_3d`：用四元数旋转 3D 点（比矩阵路径快一个数量级）
- `quat_to_hom_mat3d`：四元数→3×3 旋转矩阵（无平移）
- `serialize_quat`：四元数序列化（进程间/网络传输）

**重点算子详解**：

#### axis_angle_to_quat

- **关键签名**：`axis_angle_to_quat ( : : AxisX, AxisY, AxisZ, Angle : Quaternion)`
- **参数 / 取值**：AxisX,AxisY,AxisZ 单位轴 + Angle 弧度 → Quaternion
- **常见误区**：**轴必须是单位向量**，否则结果错误；轴角与四元数互转不会丢精度，但欧拉角会。

#### quat_compose

- **关键签名**：`quat_compose ( : : QuaternionLeft, QuaternionRight : QuaternionComposed)`
- **参数 / 取值**：QuaternionLeft ⊗ QuaternionRight = QuaternionComposed（四元数乘法，Hamilton 约定）
- **常见误区**：HALCON 用 Hamilton 约定（i²=j²=k²=ijk=-1），与一些游戏引擎的 JPL 约定相反，**跨引擎对接必查约定**。

#### quat_interpolate

- **关键签名**：`quat_interpolate ( : : QuaternionStart, QuaternionEnd, InterpPos : QuaternionInterpolated)`
- **参数 / 取值**：Quaternion1 + Quaternion2 + Fraction (0-1) → QuaternionInterpolated
- **常见误区**：HALCON 用 Slerp（球面线性插值），**自动取最短路径**；fraction∈[0,1]，越界需手动 normalize。

#### quat_normalize

- **关键签名**：`quat_normalize ( : : Quaternion : NormalizedQuaternion)`
- **参数 / 取值**：Quaternion → UnitQuaternion
- **常见误区**：**任何四元数复合或插值前必归一化**，否则数值漂移会导致旋转轴倾斜。

#### quat_rotate_point_3d

- **关键签名**：`quat_rotate_point_3d ( : : Quaternion, Px, Py, Pz : Qx, Qy, Qz)`
- **参数 / 取值**：Quaternion + 3D point → RotatedPoint
- **常见误区**：是 v'=q·v·q⁻¹ 的快速实现，比 quat_to_hom_mat3d + affine_trans_point_3d 快一个数量级，大批量点云优选。

#### quat_to_hom_mat3d

- **关键签名**：`quat_to_hom_mat3d ( : : Quaternion : RotationMatrix)`
- **参数 / 取值**：Quaternion → HomMat3D (3×3 旋转矩阵，无平移列)
- **常见误区**：只含旋转，不含平移；要完整刚体变换需配合 vector_to_pose 或 pose_to_hom_mat3d。

### 2.4 Misc 杂项（2 ops）

- **功能**：3D 点坐标的笛卡尔↔球坐标互换（带赤道面/零子午线参数）。
- **场景**：全向相机/激光雷达点云转经纬度、地理坐标系转换、球面分布点云生成

**算子清单**（一行速览）：

- `convert_point_3d_cart_to_spher`：3D 笛卡尔坐标→球坐标（可指定赤道面/零子午线）
- `convert_point_3d_spher_to_cart`：球坐标→3D 笛卡尔坐标（注意北极退化）

**重点算子详解**：

#### convert_point_3d_cart_to_spher

- **关键签名**：`convert_point_3d_cart_to_spher ( : : X, Y, Z, EquatPlaneNormal, ZeroMeridian : Longitude, Latitude, Radius)`
- **参数 / 取值**：X,Y,Z + EquatPlaneNormal (3 元素法向量) + ZeroMeridian (3 元素零子午线方向) → Longitude, Latitude, Radius
- **常见误区**：**赤道面和零子午线**可任意指定，适合地心→地理经纬度、自定义工作面→柱坐标等场景。

#### convert_point_3d_spher_to_cart

- **关键签名**：`convert_point_3d_spher_to_cart ( : : Longitude, Latitude, Radius, EquatPlaneNormal, ZeroMeridian : X, Y, Z)`
- **参数 / 取值**：Longitude, Latitude, Radius + EquatPlaneNormal + ZeroMeridian → X,Y,Z
- **常见误区**：是上一个的反向操作，**注意球坐标退化（北极方向未定义）需要手动处理**。

## 3. 全卷算子速查表

| 算子 | 一句话功能 | HDevelop 关键签名 |
|------|------------|------------------|
| `dual_quat_compose` | 复合两个双四元数（对偶数乘法，同时表达旋转+平移） | `dual_quat_compose ( : : DualQuaternionLeft, DualQuaternionRight : DualQuaternionComposed)` |
| `dual_quat_conjugate` | 对偶四元数共轭（实部与对偶部取反，实现旋转反向） | `dual_quat_conjugate ( : : DualQuaternion : DualQuaternionConjugate)` |
| `dual_quat_interpolate` | 双四元数线性混合插值（dual quaternion blending，动画级最短路径） | `dual_quat_interpolate ( : : DualQuaternionStart, DualQuaternionEnd, InterpPos : DualQuaternionInterpolated)` |
| `dual_quat_normalize` | 归一化双四元数以保证单位长度（复合/插值前必做） | `dual_quat_normalize ( : : DualQuaternion : DualQuaternionNormalized)` |
| `dual_quat_to_hom_mat3d` | 双四元数→4×4 同次变换矩阵（含旋转+平移） | `dual_quat_to_hom_mat3d ( : : DualQuaternion : HomMat3D)` |
| `dual_quat_to_screw` | 双四元数→螺旋轴表示（Chasles 定理：刚体=绕轴旋转+沿轴平移） | `dual_quat_to_screw ( : : DualQuaternion, ScrewFormat : AxisDirectionX, AxisDirectionY, AxisDirectionZ, AxisMomentOrPointX, AxisMomentOrPointY, AxisMomentOrPointZ, Rotation, Translation)` |
| `dual_quat_trans_line_3d` | 用双四元数变换 3D 直线（点+方向，比点云高效） | `dual_quat_trans_line_3d ( : : DualQuaternion, LineFormat, LineDirectionX, LineDirectionY, LineDirectionZ, LineMomentOrPointX, LineMomentOrPointY, LineMomentOrPointZ : TransLineDirectionX, TransLineDirectionY, TransLineDirectionZ, TransLineMomentOrPointX, TransLineMomentOrPointY, TransLineMomentOrPointZ)` |
| `screw_to_dual_quat` | 螺旋轴表示→双四元数（与 dual_quat_to_screw 互逆） | `screw_to_dual_quat ( : : ScrewFormat, AxisDirectionX, AxisDirectionY, AxisDirectionZ, AxisMomentOrPointX, AxisMomentOrPointY, AxisMomentOrPointZ, Rotation, Translation : DualQuaternion)` |
| `serialize_dual_quat` | 双四元数序列化（进程间/网络传输） | `serialize_dual_quat ( : : DualQuaternion : SerializedItemHandle)` |
| `deserialize_dual_quat` | 反序列化还原双四元数 | `deserialize_dual_quat ( : : SerializedItemHandle : DualQuaternion)` |
| `convert_pose_type` | 改变姿态变换约定（OrderOfTransform/OrderOfRotation/ViewOfTransform） | `convert_pose_type ( : : PoseIn, OrderOfTransform, OrderOfRotation, ViewOfTransform : PoseOut)` |
| `create_pose` | 从 6 自由度+约定创建 7 元姿态 Pose | `create_pose ( : : TransX, TransY, TransZ, RotX, RotY, RotZ, OrderOfTransform, OrderOfRotation, ViewOfTransform : Pose)` |
| `deserialize_pose` | 反序列化还原姿态 | `deserialize_pose ( : : SerializedItemHandle : Pose)` |
| `dual_quat_to_pose` | 双四元数→姿态（自带归一化） | `dual_quat_to_pose ( : : DualQuaternion : Pose)` |
| `get_circle_pose` | 由共圆 3D 点估计圆所在平面姿态（快速 6D 定位） | `get_circle_pose (Contour : : CameraParam, Radius, OutputType : Pose1, Pose2)` |
| `get_pose_type` | 查询姿态的变换约定 | `get_pose_type ( : : Pose : OrderOfTransform, OrderOfRotation, ViewOfTransform)` |
| `get_rectangle_pose` | 由矩形轮廓估计姿态（平面工件定位） | `get_rectangle_pose (Contour : : CameraParam, Width, Height, WeightingMode, ClippingFactor : Pose, CovPose, Error)` |
| `pose_average` | 多姿态加权平均（几何/迭代加权，重建必备） | `pose_average ( : : Poses, Weights, Mode, SigmaT, SigmaR : AveragePose, Quality)` |
| `pose_compose` | 复合两个姿态（HALCON 右乘约定） | `pose_compose ( : : PoseLeft, PoseRight : PoseCompose)` |
| `pose_invert` | 求逆姿态（旋转转置+平移取反） | `pose_invert ( : : Pose : PoseInvert)` |
| `pose_to_dual_quat` | 姿态→双四元数 | `pose_to_dual_quat ( : : Pose : DualQuaternion)` |
| `pose_to_quat` | 姿态旋转部分→单位四元数 | `pose_to_quat ( : : Pose : Quaternion)` |
| `proj_hom_mat2d_to_pose` | 2D 同次矩阵→3D 姿态（平面假设） | `proj_hom_mat2d_to_pose ( : : Homography, CameraMatrix, Method : Pose)` |
| `quat_to_pose` | 四元数→姿态旋转部分 | `quat_to_pose ( : : Quaternion : Pose)` |
| `read_pose` | 从 .pos 文件读取姿态 | `read_pose ( : : PoseFile : Pose)` |
| `serialize_pose` | 姿态序列化（进程间/网络传输） | `serialize_pose ( : : Pose : SerializedItemHandle)` |
| `set_origin_pose` | 平移偏移姿态原点（改变平移分量） | `set_origin_pose ( : : PoseIn, DX, DY, DZ : PoseNewOrigin)` |
| `vector_to_pose` | 6 元素向量→姿态 | `vector_to_pose ( : : WorldX, WorldY, WorldZ, ImageRow, ImageColumn, CameraParam, Method, QualityType : Pose, Quality)` |
| `write_pose` | 姿态写 .pos 文件 | `write_pose ( : : Pose, PoseFile : )` |
| `axis_angle_to_quat` | 轴角→单位四元数（轴必须单位向量） | `axis_angle_to_quat ( : : AxisX, AxisY, AxisZ, Angle : Quaternion)` |
| `deserialize_quat` | 反序列化还原四元数 | `deserialize_quat ( : : SerializedItemHandle : Quaternion)` |
| `quat_compose` | 复合两个四元数（Hamilton 约定，与部分引擎相反） | `quat_compose ( : : QuaternionLeft, QuaternionRight : QuaternionComposed)` |
| `quat_conjugate` | 四元数共轭（旋转反向，q⁻¹） | `quat_conjugate ( : : Quaternion : ConjugatedQuaternion)` |
| `quat_interpolate` | 四元数球面线性插值 SLERP（最短路径，fraction∈[0,1]） | `quat_interpolate ( : : QuaternionStart, QuaternionEnd, InterpPos : QuaternionInterpolated)` |
| `quat_normalize` | 归一化四元数（复合/插值前必做） | `quat_normalize ( : : Quaternion : NormalizedQuaternion)` |
| `quat_rotate_point_3d` | 用四元数旋转 3D 点（比矩阵路径快一个数量级） | `quat_rotate_point_3d ( : : Quaternion, Px, Py, Pz : Qx, Qy, Qz)` |
| `quat_to_hom_mat3d` | 四元数→3×3 旋转矩阵（无平移） | `quat_to_hom_mat3d ( : : Quaternion : RotationMatrix)` |
| `serialize_quat` | 四元数序列化（进程间/网络传输） | `serialize_quat ( : : Quaternion : SerializedItemHandle)` |
| `convert_point_3d_cart_to_spher` | 3D 笛卡尔坐标→球坐标（可指定赤道面/零子午线） | `convert_point_3d_cart_to_spher ( : : X, Y, Z, EquatPlaneNormal, ZeroMeridian : Longitude, Latitude, Radius)` |
| `convert_point_3d_spher_to_cart` | 球坐标→3D 笛卡尔坐标（注意北极退化） | `convert_point_3d_spher_to_cart ( : : Longitude, Latitude, Radius, EquatPlaneNormal, ZeroMeridian : X, Y, Z)` |

## 4. 跨算子误区 & 调试提示

- ⚠️ **ViewOfTransform 'point' vs 'coordinate_system'**：HALCON 默认 'point'（旋转作用于点），机器人学常反过来；多相机标定链对接时必须显式指定。
- ⚠️ **OrderOfRotation 三种顺序** ('RxRyRz'/'RxRzRy'/'RyRxRz' 等)：不同顺序对同一 RxRyRz 数值结果完全不同，跨系统传输必带此参数。
- ⚠️ **HALCON 四元数用 Hamilton 约定**（与 Unity/UE 不同，JPL 约定 i²=j²=k²=+1，ijk=-1），跨引擎对接必做约定归一化。
- ⚠️ **四元数/双四元数复合后必归一化**：数值漂移累积几个迭代就会让旋转矩阵行列式偏离 1。
- ⚠️ **dual_quat_interpolate 与 pose_average 区别**：前者保证最短路径 + 短弧插值（动画级），后者加权做多视图姿态平均（重建级）。
- ⚠️ **serialize_pose 与 write_pose 二选一**：前者输出序列化句柄（进程内/网络传输），后者写 .pos 文件（持久化），不能交叉。
- ⚠️ **convert_pose_type 只改约定不改数值**：从 'Rp+T' 改到 'Tb+R' 时旋转矩阵会变，但本质姿态不变。

## 5. 调用链路与组合用法

### 机器人手眼标定链路（Pose 主线）

```hdevelop
* 1. 多视角扫描 → 3D 匹配获取 N 个相机姿态
read_cam_par('cam_campar.dat', CamParam)
for F : 1 to N by 1
    find_surface_model(SurfaceModelID, ObjectModel3D, 0.05, 'find_surface_model_params', Pose, Score)
endfor
* 2. 读出 N 个姿态求平均（降噪）
pose_average(Poses, [], 'iterative', 1.0, 0.1, AveragePose, Quality)
* 3. 平均姿态取逆，得到工件坐标系姿态
pose_invert(AveragePose, WorldPose)
* 若机器人控制器需要 4x4 矩阵，可再转：
* pose_to_hom_mat3d(WorldPose, HomMat3D)
* 4. 写文件给机器人控制器
write_pose(WorldPose, 'final_target.pos')
```

### 姿态平滑插值链路（Dual Quat 动画级）

```hdevelop
* 1. 起点姿态 → DualQuat
pose_to_dual_quat(PoseStart, DQStart)
pose_to_dual_quat(PoseEnd,   DQEnd)
* 2. 插值 100 帧做平滑动画
for T : 0 to 100 by 1
    Fraction := T / 100.0
    dual_quat_interpolate(DQStart, DQEnd, Fraction, DQTmp)
    dual_quat_normalize(DQTmp, DQNorm)
    dual_quat_to_pose(DQNorm, PoseTmp)
    pose_to_hom_mat3d(PoseTmp, CamMat)
    affine_trans_point_3d(CamMat, Px, Py, Pz, Qx, Qy, Qz)
endfor
```

### 四元数旋转 + 归一化 + 序列化链路

```hdevelop
* 1. 轴角 → 四元数
axis_angle_to_quat(0.0, 0.0, 1.0, rad(45), Quat)
* 2. 旋转一个 3D 点
quat_rotate_point_3d(Quat, 1.0, 0.0, 0.0, Rx, Ry, Rz)
* 3. 复合两个旋转
quat_compose(Quat, Quat, Quat2)
quat_normalize(Quat2, QuatUnit)
* 4. 序列化为二进制串行（进程间传）
serialize_quat(QuatUnit, SerializedHandle)
deserialize_quat(SerializedHandle, QuatRecovered)
```

## 6. 与其它章节的关联

- **Ch4 Object Model 3D**：ObjectModel3D 的 set/get_pose_of_object_model_3d 直接消费 Pose，是 Pose 的最常见下游。
- **Ch3 3D Matching**：find_surface_model/deserialized_3d_match 输出 Pose，本章是其数学后端。
- **Ch6 Calibration**：camera_calibration 输出的相机位姿参数就是 Pose 元组。
- **Ch18 Matrix**：hom_mat3d_to_pose / pose_to_hom_mat3d 是 Pose↔4×4 矩阵的桥。
- **Ch5 3D Reconstruction**：SfM 重建输出的多视角姿态可直接喂给 pose_average 求全局一致性。

## 7. 一句话核心要义

**3D 位姿的所有数学表示方式 + 完整互转 + 序列化持久化，构成 3D 视觉、机器人、SLAM、动画的数学底座；核心三条流：Pose 主线（结构化、易读）+ Quat 子线（紧凑无奇点）+ Dual Quat 子线（统一旋转平移、动画级插值）。**
