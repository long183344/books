# 第 26 章 Transformations（坐标变换）· 上卷

> **本章定位**：HALCON 的"几何决策算子库——齐次矩阵的全栈操作"。如果说 Ch3（3D Matching）和 Ch4（3D Object Model）是"如何识别/表达 3D"，那 Ch26 就是"识别后如何把它们对齐、转换、变换"。无论工件抓取、手眼标定、相机外参反推、序列化网络传输，根本都是几个 3×3 或 4×4 矩阵的拼接乘法。

> **本卷定位**：2D + 3D 齐次矩阵构造 + 应用层算子。共 **2 个子族，51 算子**。下卷将介绍 Dual Quaternions(10) + Misc(2) + Poses(19) + Quaternions(9) = 40 算子，覆盖旋转载体的"另一种表示法"和位姿互转。

> **一句话总结**：本卷 = "hom_mat2d"+"hom_mat3d"+"vector_to_*"+"affine_trans_*"+"projective_trans_*" 五大类算子的矩阵构造/查询/应用/序列化全栈。
## 1. 全卷结构表

| 子族 | 算子数 | 矩阵类型 | 主要场景 |
|---|---|---|---|
| 2D Transformations (二维齐次矩阵变换) | 32 | 3×3 齐次矩阵 (6 元素) | 2D 视觉对位/图像配准/畸变校正/字符摆正 |
| 3D Transformations (三维齐次矩阵变换) | 19 | 4×4 齐次矩阵 (12 元素) | 3D 对位/相机外参/手眼标定/机器人基坐标↔工具 |
| **合计** | **51** | — | — |

## 2. 子族分述

### ◆ 2D Transformations (二维齐次矩阵变换)（32 算子）

**2D 齐次矩阵（hom_mat2d，3×3 = 6 元素）** 全栈。从单位阵、复合/反演/转置/行列式这些"基础代数"，到 6 类基本局部变换（旋转/平移/缩放/斜切/镜射），再到 9 类"点对应反算矩阵"的工程实用算子，最后到对像素/点的应用 + 序列化。整个 2D 视觉的 90% 矩阵操作集中在这里。

#### 2D 几何决策——算子速查表

| # | 算子 | 一句话功能 | HDevelop 关键签名 |
|---|---|---|---|
| 1 | `affine_trans_pixel` | affine_trans_pixel applies an arbitrary affine 2D transfo... | `affine_trans_pixel( : : HomMat2D, Row, Col : RowTrans, ColTrans)` |
| 2 | `affine_trans_point_2d` | affine_trans_point_2d applies an arbitrary affine 2D tran... | `affine_trans_point_2d( : : HomMat2D, Px, Py : Qx, Qy)` |
| 3 | `deserialize_hom_mat2d` | deserialize_hom_mat2d deserializes a homogeneous 2D trans... | `deserialize_hom_mat2d( : : SerializedItemHandle : HomMat2D)` |
| 4 | `hom_mat2d_compose` | hom_mat2d_compose composes a new 2D transformation matrix... | `hom_mat2d_compose( : : HomMat2DLeft, HomMat2DRight : HomMat2DCompose)` |
| 5 | `hom_mat2d_determinant` | hom_mat2d_determinant computes the determinant of the hom... | `hom_mat2d_determinant( : : HomMat2D : Determinant)` |
| 6 | `hom_mat2d_identity` | hom_mat2d_identity generates the homogeneous transformati... | `hom_mat2d_identity( : : : HomMat2DIdentity)` |
| 7 | `hom_mat2d_invert` | hom_mat2d_invert inverts the homogeneous 2D transformatio... | `hom_mat2d_invert( : : HomMat2D : HomMat2DInvert)` |
| 8 | `hom_mat2d_reflect` | hom_mat2d_reflect adds a reflection about the axis given ... | `hom_mat2d_reflect( : : HomMat2D, Px, Py, Qx, Qy : HomMat2DReflect)` |
| 9 | `hom_mat2d_reflect_local` | hom_mat2d_reflect_local adds a reflection about the axis ... | `hom_mat2d_reflect_local( : : HomMat2D, Px, Py : HomMat2DReflect)` |
| 10 | `hom_mat2d_rotate` | hom_mat2d_rotate adds a rotation by the angle Phi to the ... | `hom_mat2d_rotate( : : HomMat2D, Phi, Px, Py : HomMat2DRotate)` |
| 11 | `hom_mat2d_rotate_local` | hom_mat2d_rotate_local adds a rotation by the angle Phi t... | `hom_mat2d_rotate_local( : : HomMat2D, Phi : HomMat2DRotate)` |
| 12 | `hom_mat2d_scale` | hom_mat2d_scale adds a scaling by the scale factors Sx an... | `hom_mat2d_scale( : : HomMat2D, Sx, Sy, Px, Py : HomMat2DScale)` |
| 13 | `hom_mat2d_scale_local` | hom_mat2d_scale_local adds a scaling by the scale factors... | `hom_mat2d_scale_local( : : HomMat2D, Sx, Sy : HomMat2DScale)` |
| 14 | `hom_mat2d_slant` | hom_mat2d_slant adds a slant by the angle Theta to the ho... | `hom_mat2d_slant( : : HomMat2D, Theta, Axis, Px, Py : HomMat2DSlant)` |
| 15 | `hom_mat2d_slant_local` | hom_mat2d_slant_local adds a slant by the angle Theta to ... | `hom_mat2d_slant_local( : : HomMat2D, Theta, Axis : HomMat2DSlant)` |
| 16 | `hom_mat2d_to_affine_par` | hom_mat2d_to_affine_par computes the affine transformatio... | `hom_mat2d_to_affine_par( : : HomMat2D : Sx, Sy, Phi, Theta, Tx, Ty)` |
| 17 | `hom_mat2d_translate` | hom_mat2d_translate adds a translation by the vector t = ... | `hom_mat2d_translate( : : HomMat2D, Tx, Ty : HomMat2DTranslate)` |
| 18 | `hom_mat2d_translate_local` | hom_mat2d_translate_local adds a translation by the vecto... | `hom_mat2d_translate_local( : : HomMat2D, Tx, Ty : HomMat2DTranslate)` |
| 19 | `hom_mat2d_transpose` | hom_mat2d_transpose transposes the homogeneous 2D transfo... | `hom_mat2d_transpose( : : HomMat2D : HomMat2DTranspose)` |
| 20 | `hom_vector_to_proj_hom_mat2d` | hom_vector_to_proj_hom_mat2d determines the homogeneous p... | `hom_vector_to_proj_hom_mat2d( : : Px, Py, Pw, Qx, Qy, Qw, Method : HomMat2D)` |
| 21 | `point_line_to_hom_mat2d` | point_line_to_hom_mat2d approximates an affine transforma... | `point_line_to_hom_mat2d( : : TransformationType, Px, Py, L1x, L1y, L2x, L2y :...` |
| 22 | `projective_trans_pixel` | projective_trans_pixel applies the homogeneous projective... | `projective_trans_pixel( : : HomMat2D, Row, Col : RowTrans, ColTrans)` |
| 23 | `projective_trans_point_2d` | projective_trans_point_2d applies the homogeneous project... | `projective_trans_point_2d( : : HomMat2D, Px, Py, Pw : Qx, Qy, Qw)` |
| 24 | `serialize_hom_mat2d` | serialize_hom_mat2d serializes the data of a homogeneous ... | `serialize_hom_mat2d( : : HomMat2D : SerializedItemHandle)` |
| 25 | `vector_angle_to_rigid` | vector_angle_to_rigid computes a rigid affine transformat... | `vector_angle_to_rigid( : : Row1, Column1, Angle1, Row2, Column2, Angle2 : Hom...` |
| 26 | `vector_field_to_hom_mat2d` | vector_field_to_hom_mat2d approximates an affine map from... | `vector_field_to_hom_mat2d(VectorField : : : HomMat2D)` |
| 27 | `vector_to_aniso` | vector_to_aniso approximates an anisotropic similarity tr... | `vector_to_aniso( : : Px, Py, Qx, Qy : HomMat2D)` |
| 28 | `vector_to_hom_mat2d` | vector_to_hom_mat2d approximates an affine transformation... | `vector_to_hom_mat2d( : : Px, Py, Qx, Qy : HomMat2D)` |
| 29 | `vector_to_proj_hom_mat2d` | vector_to_proj_hom_mat2d determines the homogeneous proje... | `vector_to_proj_hom_mat2d( : : Px, Py, Qx, Qy, Method, CovXX1, CovYY1, CovXY1,...` |
| 30 | `vector_to_proj_hom_mat2d_distortion` | vector_to_proj_hom_mat2d_distortion determines the projec... | `vector_to_proj_hom_mat2d_distortion( : : Points1Row, Points1Col, Points2Row, ...` |
| 31 | `vector_to_rigid` | vector_to_rigid approximates a rigid affine transformatio... | `vector_to_rigid( : : Px, Py, Qx, Qy : HomMat2D)` |
| 32 | `vector_to_similarity` | vector_to_similarity approximates a similarity transforma... | `vector_to_similarity( : : Px, Py, Qx, Qy : HomMat2D)` |

#### 重点算子详解（29 个）

##### `affine_trans_pixel`

**功能**：affine_trans_pixel applies an arbitrary affine 2D transformation, i.e., scaling, rotation, translation, and slant (skewing), to the input pixels ( Row , Col ) and returns the resulting pixels in ( RowTrans , ColTrans ); the input and output pixels are subpixel precise coordinates. The affine transformation is described by the homogeneous transformation matrix given in HomMat2D . In contrast to affine_trans_point_2d , affine_trans_pixel first converts the input coordinates from HALCON's standard coordinate system (with the origin in the center of the upper left pixel) to a coordinate system with the origin in the upper left corner of the upper left pixel. After the transformation with HomMat2D the result is converted back to the standard coordinate system. This way, affine_trans_pixel is compatible with affine_trans_image , affine_trans_image_size , affine_trans_region , affine_trans_contour_xld , and affine_trans_polygon_xld .

**签名**：`affine_trans_pixel( : : HomMat2D, Row, Col : RowTrans, ColTrans)`

**参数说明**：对单个像素坐标 (Row, Col) 应用仿射变换；用于点位变换查询

**常见误区**："pixel"是图像坐标系(y,x)，与 (X,Y) 列行不同；批量改坐标应用 projective_trans_pixel

##### `affine_trans_point_2d`

**功能**：affine_trans_point_2d applies an arbitrary affine 2D transformation, i.e., scaling, rotation, translation, and slant (skewing), to the input points ( Px , Py ) and returns the resulting points in ( Qx , Qy ). The affine transformation is described by the homogeneous transformation matrix given in HomMat2D . This corresponds to the following equation (input and output points as homogeneous vectors): If the points to transform are specified in standard image coordinates, their row coordinates must be passed in Px and their column coordinates in Py . This is necessary to obtain a right-handed coordinate system for the image. In particular, this assures that rotations are performed in the correct direction. Note that the (x,y) order of the matrices quite naturally corresponds to the usual (row,column) order for coordinates in the image.

**签名**：`affine_trans_point_2d( : : HomMat2D, Px, Py : Qx, Qy)`

**参数说明**：对多个点坐标应用仿射变换

**常见误区**：与 affine_trans_pixel 区别：pixel 用 (Row,Col)，point 用 (X,Y)；混淆出现 x/y 翻转

##### `deserialize_hom_mat2d`

**功能**：deserialize_hom_mat2d deserializes a homogeneous 2D transformation matrix, that was serialized by serialize_hom_mat2d (see fwrite_serialized_item for an introduction of the basic principle of serialization). The serialized transformation matrix is defined by the handle SerializedItemHandle . The deserialized values are stored in an automatically created transformation matrix with the handle HomMat2D .

**签名**：`deserialize_hom_mat2d( : : SerializedItemHandle : HomMat2D)`

**参数说明**：从 SerializedItemHandle 还原矩阵；与 serialize_hom_mat2d 配套

**常见误区**：文件读出建议搭配 fread_serialized_item；本算子只接内存 handle

##### `hom_mat2d_compose`

**功能**：hom_mat2d_compose composes a new 2D transformation matrix by multiplying the two input matrices: For example, if the two input matrices correspond to rigid transformations, i.e., to transformations consisting of a rotation and a translation, the resulting matrix is calculated as follows:

**签名**：`hom_mat2d_compose( : : HomMat2DLeft, HomMat2DRight : HomMat2DCompose)`

**参数说明**：左乘矩阵 HomMat2DLeft + 右乘矩阵 HomMat2DRight；返回 HomMat2DCompose = Left × Right

**常见误区**：HALCON 中矩阵乘法是"先应用 Right，再应用 Left"（与传统数学相反），常导致视觉错位；调试时先画坐标轴

##### `hom_mat2d_determinant`

**功能**：hom_mat2d_determinant computes the determinant of the homogeneous 2D transformation matrix given by HomMat2D and returns it in Determinant .

**签名**：`hom_mat2d_determinant( : : HomMat2D : Determinant)`

**参数说明**：返回 6 参数矩阵的等效行列式；用于判断矩阵可逆性（≠0）、退化、镜射（<0）

**常见误区**：det < 0 表示镜射（手性反转），3D 重建里这会破坏法线方向；视觉里感觉"上下颠倒"

##### `hom_mat2d_identity`

**功能**：hom_mat2d_identity generates the homogeneous transformation matrix HomMat2DIdentity describing the identical 2D transformation:

**签名**：`hom_mat2d_identity( : : : HomMat2DIdentity)`

**参数说明**：无参数：调一次即返回 6 参数单位矩阵

**常见误区**：hom_mat2d 句柄类型不能直接 print；要用 vector_to_* 系列从点对应构造

##### `hom_mat2d_invert`

**功能**：hom_mat2d_invert inverts the homogeneous 2D transformation matrix given by HomMat2D . The resulting matrix is returned in HomMat2DInvert .

**签名**：`hom_mat2d_invert( : : HomMat2D : HomMat2DInvert)`

**参数说明**：接受任意 2D 齐次矩阵返回其逆；对奇异矩阵（det=0）会报错

**常见误区**：矩阵不可逆常见场景：纯平移 + 缩放=0、镜射 + 平移退化、齐次最后一行[0,0,0]；先 get_determinant 检查

##### `hom_mat2d_reflect`

**功能**：hom_mat2d_reflect adds a reflection about the axis given by the two points ( Px , Py ) and ( Qx , Qy ) to the homogeneous 2D transformation matrix HomMat2D and returns the resulting matrix in HomMat2DReflect . The reflection is described by a 2×2 reflection matrix M. It is performed relative to the global (i.e., fixed) coordinate system; this corresponds to the following chain of transformation matrices: The axis ( Px , Py )-( Qx , Qy ) is fixed in the transformation, i.e., the points on the axis remain unchanged when transformed using HomMat2DReflect . To obtain this behavior, first a translation is added to the input transformation matrix that moves the axis onto the origin of the global coordinate system. Then, the reflection is added, and finally a translation that moves the axis back to its original position. This corresponds to the following chain of transformations:

**签名**：`hom_mat2d_reflect( : : HomMat2D, Px, Py, Qx, Qy : HomMat2DReflect)`

**参数说明**：沿(穿过指定点的)任意轴镜射；Axis=x 或 y 或任意两点 Px,Py

**常见误区**：镜射会让左手系变右手系（det<0）：OCR/字符识别可能反向

##### `hom_mat2d_reflect_local`

**功能**：hom_mat2d_reflect_local adds a reflection about the axis given by the two points (0,0) and ( Px , Py ) to the homogeneous 2D transformation matrix HomMat2D and returns the resulting matrix in HomMat2DReflect . The reflection is described by a 2×2 reflection matrix M. In contrast to hom_mat2d_reflect , it is performed relative to the local coordinate system, i.e., the coordinate system described by HomMat2D ; this corresponds to the following chain of transformation matrices: The axis (0,0)-( Px , Py ) is fixed in the transformation, i.e., the points on the axis remain unchanged when transformed using HomMat2DReflect .

**签名**：`hom_mat2d_reflect_local( : : HomMat2D, Px, Py : HomMat2DReflect)`

**参数说明**：过原点的镜射；等价于 hom_mat2d_reflect(0,0)

**常见误区**：与全图镜射直接画区别；_local 没有指定中心点参数

##### `hom_mat2d_rotate`

**功能**：hom_mat2d_rotate adds a rotation by the angle Phi to the homogeneous 2D transformation matrix HomMat2D and returns the resulting matrix in HomMat2DRotate . The rotation is described by a 2×2 rotation matrix R. It is performed relative to the global (i.e., fixed) coordinate system; this corresponds to the following chain of transformation matrices: The point ( Px , Py ) is the fixed point of the transformation, i.e., this point remains unchanged when transformed using HomMat2DRotate . To obtain this behavior, first a translation is added to the input transformation matrix that moves the fixed point onto the origin of the global coordinate system. Then, the rotation is added, and finally a translation that moves the fixed point back to its original position. This corresponds to the following chain of transformations:

**签名**：`hom_mat2d_rotate( : : HomMat2D, Phi, Px, Py : HomMat2DRotate)`

**参数说明**：hom_mat2d_rotate(原矩阵, 角度Phi, 旋转中心Px, Py)：以 (Px,Py) 为中心追加旋转

**常见误区**："_local 变种"以原点为中心，"普通"以 (Px,Py) 为中心；混用导致工件绕偏旋转中心偏转

##### `hom_mat2d_rotate_local`

**功能**：hom_mat2d_rotate_local adds a rotation by the angle Phi to the homogeneous 2D transformation matrix HomMat2D and returns the resulting matrix in HomMat2DRotate . The rotation is described by a 2×2 rotation matrix R. In contrast to hom_mat2d_rotate , it is performed relative to the local coordinate system, i.e., the coordinate system described by HomMat2D ; this corresponds to the following chain of transformation matrices: The fixed point of the transformation is the origin of the local coordinate system, i.e., this point remains unchanged when transformed using HomMat2DRotate .

**签名**：`hom_mat2d_rotate_local( : : HomMat2D, Phi : HomMat2DRotate)`

**参数说明**：追加"以原点为中心"的旋转；与 hom_mat2d_rotate(0,0) 等价但更明确

**常见误区**：多次 _local 拼接顺序"先平移到中心再旋转再平移回"——必须放对顺序：T(-px,-py) × R × T(px,py)

##### `hom_mat2d_scale_local`

**功能**：hom_mat2d_scale_local adds a scaling by the scale factors Sx and Sy to the homogeneous 2D transformation matrix HomMat2D and returns the resulting matrix in HomMat2DScale . The scaling is described by a 2×2 scaling matrix S. In contrast to hom_mat2d_scale , it is performed relative to the local coordinate system, i.e., the coordinate system described by HomMat2D ; this corresponds to the following chain of transformation matrices: The fixed point of the transformation is the origin of the local coordinate system, i.e., this point remains unchanged when transformed using HomMat2DScale .

**签名**：`hom_mat2d_scale_local( : : HomMat2D, Sx, Sy : HomMat2DScale)`

**参数说明**：以原点为中心的等比/异比缩放 (sx, sy)；HALCON 的标量参数是按 (sx, sy) tuple

**常见误区**：单参 sx= 不代表等比缩放！HALCON 会自动同步 sy=sx；但 0 缩放会让矩阵奇异

##### `hom_mat2d_slant`

**功能**：hom_mat2d_slant adds a slant by the angle Theta to the homogeneous 2D transformation matrix HomMat2D and returns the resulting matrix in HomMat2DSlant . A slant is an affine transformation in which one coordinate axis remains fixed, while the other coordinate axis is rotated counterclockwise by an angle Theta . The parameter Axis determines which coordinate axis is slanted. For Axis = 'x' , the x-axis is slanted and the y-axis remains fixed, while for Axis = 'y' the y-axis is slanted and the x-axis remains fixed. The slanting is performed relative to the global (i.e., fixed) coordinate system; this corresponds to the following chains of transformation matrices: The point ( Px , Py ) is the fixed point of the transformation, i.e., this point remains unchanged when transformed using HomMat2DSlant . To obtain this behavior, first a translation is added to the input transformation matrix that moves the fixed point onto the origin of the global coordinate system. Then, the slant is added, and finally a translation that moves the fixed point back to its original position. This corresponds to the following chain of transformations for Axis = 'x' :

**签名**：`hom_mat2d_slant( : : HomMat2D, Theta, Axis, Px, Py : HomMat2DSlant)`

**参数说明**：追加斜切(skew)：Theta 倾斜角 + Axis (0=x-轴/1=y-轴) + 中心点

**常见误区**：Slant 是"剪切变换"不是"旋转"——矩形变平行四边形但边长不变；用得少，多用于"摆正文本"

##### `hom_mat2d_to_affine_par`

**功能**：hom_mat2d_to_affine_par computes the affine transformation parameters corresponding to the homogeneous 2D transformation matrix HomMat2D . The parameters Sx and Sy determine how the transformation scales the original x- and y-axes, respectively. The two scaling factors are always positive. The angle Theta describes whether the transformed coordinate axes are orthogonal ( Theta = 0) or slanted. If , the transformation contains a reflection. The angle Phi determines the rotation of the transformed x-axis with respect to the original x-axis. The parameters Tx and Ty determine the translation of the two coordinate systems. The matrix HomMat2D can be constructed from the six transformation parameters by the following operator sequence:

**签名**：`hom_mat2d_to_affine_par( : : HomMat2D : Sx, Sy, Phi, Theta, Tx, Ty)`

**参数说明**：从齐次矩阵反算 6 仿射参数：Sx, Sy, Phi, Theta, Tx, Ty —— 用于"已知矩阵想看参数"

**常见误区**：若矩阵是"投影矩阵"（9 参数非 0/1），此算子失败；先 hom_mat2d_invert + 检查 det≠0

##### `hom_mat2d_translate_local`

**功能**：hom_mat2d_translate_local adds a translation by the vector t = ( Tx , Ty ) to the homogeneous 2D transformation matrix HomMat2D and returns the resulting matrix in HomMat2DTranslate . In contrast to hom_mat2d_translate , the translation is performed relative to the local coordinate system, i.e., the coordinate system described by HomMat2D ; this corresponds to the following chain of transformation matrices:

**签名**：`hom_mat2d_translate_local( : : HomMat2D, Tx, Ty : HomMat2DTranslate)`

**参数说明**：以原点为中心的平移；常用于"局部坐标系内平移"

**常见误区**：不是"全图位移"！要以全图为参照，用普通 hom_mat2d_translate(图像, dx, dy)

##### `hom_mat2d_transpose`

**功能**：hom_mat2d_transpose transposes the homogeneous 2D transformation matrix given by HomMat2D . The result matrix HomMat2DTranspose is always a 3×3 matrix, even if the input matrix is represented by a 2×3 matrix.

**签名**：`hom_mat2d_transpose( : : HomMat2D : HomMat2DTranspose)`

**参数说明**：调换原矩阵的前两行；常用于仿射矩阵的"反转坐标基"

**常见误区**：不是"共轭转置"也不是"逆"；真正的转置只交换 a/b/c 与 d/e/f；不能等同 matrix_transpose

##### `hom_vector_to_proj_hom_mat2d`

**功能**：hom_vector_to_proj_hom_mat2d determines the homogeneous projective transformation matrix HomMat2D that optimally fulfills the following equations given by at least 4 point correspondences If fewer than 4 pairs of points ( Px , Py , Pw ), ( Qx , Qy , Qw ) are given, there exists no unique solution, if exactly 4 pairs are supplied the matrix HomMat2D transforms them in exactly the desired way, and if there are more than 4 point pairs given, hom_vector_to_proj_hom_mat2d seeks to minimize the transformation error. To achieve such a minimization, two different algorithms are available. The algorithm to use can be chosen using the parameter Method . For conventional geometric problems Method = 'normalized_dlt' usually yields better results. However, if one of the coordinates Qw or Pw equals 0, Method = 'dlt' must be chosen.

**签名**：`hom_vector_to_proj_hom_mat2d( : : Px, Py, Pw, Qx, Qy, Qw, Method : HomMat2D)`

**参数说明**："齐次点-齐次点对应"(Px,Py,Pw)>(Qx,Qy,Qw) 反算投影矩阵

**常见误区**：与 vector_to_proj_hom_mat2d 区别：输入是齐次坐标（带 Pw）；非齐次会失败

##### `point_line_to_hom_mat2d`

**功能**：point_line_to_hom_mat2d approximates an affine transformation from point-to-line correspondences and returns it as the homogeneous transformation matrix HomMat2D (see hom_mat2d_to_affine_par for the content of the homogeneous transformation matrix). The points are passed in the tuples ( Px , Py ). Their corresponding lines are specified as two points on the line, which are passed in ( L1x , L1y ) and ( L2x , L2y ). Corresponding points and lines must be at the same index positions in these tuples.

**签名**：`point_line_to_hom_mat2d( : : TransformationType, Px, Py, L1x, L1y, L2x, L2y : HomMat2D)`

**参数说明**："点-线对应"反算仿射矩阵：点 P 应落在直线 L（两点决定的）上；适用于"已知标志对到模板"

**常见误区**：每对"点-线"提供 2 个约束 = 1 个点对；至少要 3 对

##### `projective_trans_pixel`

**功能**：projective_trans_pixel applies the homogeneous projective transformation matrix HomMat2D to all input pixels ( Row , Col ) and returns an array of output pixels ( RowTrans , ColTrans ). The transformation is described by the homogeneous transformation matrix given in HomMat2D . The difference between projective_trans_pixel and projective_trans_point_2d lies in the used coordinate system: projective_trans_pixel uses a coordinate system with origin in the upper left corner of the image, while projective_trans_point_2d uses the standard image coordinate system, whose origin lies in the middle of the upper left pixel and which is also used by operators like area_center .

**签名**：`projective_trans_pixel( : : HomMat2D, Row, Col : RowTrans, ColTrans)`

**参数说明**：对像素坐标应用投影变换（8 参数含透视）

**常见误区**：投影可能让原本在内部的点跑到无穷远（w=0），需检查返回 Qw

##### `projective_trans_point_2d`

**功能**：projective_trans_point_2d applies the homogeneous projective transformation matrix HomMat2D to all homogeneous input points ( Px , Py , Pw ) and returns an array of homogeneous output points ( Qx , Qy , Qw ). The transformation is described by the homogeneous transformation matrix given in HomMat2D . This corresponds to the following equation (input and output points as homogeneous vectors): To transform the homogeneous coordinates to Euclidean coordinates, they have to be divided by Qw :

**签名**：`projective_trans_point_2d( : : HomMat2D, Px, Py, Pw : Qx, Qy, Qw)`

**参数说明**：对多个点坐标应用投影变换（返回 Qx,Qy,Qw）

**常见误区**：与 projective_trans_pixel 区别同 affine_trans_pixel — 坐标系不同

##### `serialize_hom_mat2d`

**功能**：serialize_hom_mat2d serializes the data of a homogeneous 2D transformation matrix (see fwrite_serialized_item for an introduction of the basic principle of serialization). The transformation matrix is defined by the handle HomMat2D . The serialized transformation matrix is returned by the handle SerializedItemHandle and can be deserialized by deserialize_hom_mat2d .

**签名**：`serialize_hom_mat2d( : : HomMat2D : SerializedItemHandle)`

**参数说明**：把矩阵序列化为 SerializedItemHandle；用于跨进程/网络传输

**常见误区**：序列化格式是 HALCON 私有；不能给 OpenCV 用；要 OpenCV 用 vector_to_* 反算 6 数值

##### `vector_angle_to_rigid`

**功能**：vector_angle_to_rigid computes a rigid affine transformation, i.e., a transformation consisting of a rotation and a translation, from a point correspondence and two corresponding angles and returns it as the homogeneous transformation matrix HomMat2D . The matrix consists of 2 components: a rotation matrix R and a translation vector t (also see hom_mat2d_rotate and hom_mat2d_translate ): The coordinates of the original point are passed in ( Row1 , Column1 ), while the corresponding angle is passed in Angle1 . The coordinates of the transformed point are passed in ( Row2 , Column2 ), while the corresponding angle is passed in Angle2 . The following equation describes the transformation of the point using homogeneous vectors:

**签名**：`vector_angle_to_rigid( : : Row1, Column1, Angle1, Row2, Column2, Angle2 : HomMat2D)`

**参数说明**：输入"(Row1,Column1,Angle1)→(Row2,Column2,Angle2)"两个位姿：直接构造刚体变换

**常见误区**：比 vector_to_rigid 少 4 个参数；用在"已知旋转+平移"对位（如工件贴附对位）

##### `vector_field_to_hom_mat2d`

**功能**：vector_field_to_hom_mat2d approximates an affine map from the displacement vector field VectorField . The affine map is returned in HomMat2D . If the displacement vector field has been computed from the original image

**签名**：`vector_field_to_hom_mat2d(VectorField : : : HomMat2D)`

**参数说明**：从"向量场"(每点 Row, Col 位移)估计最佳单一全局仿射矩阵

**常见误区**：本质是"最小二乘拟合"——整个区域用一个矩阵表达；非刚性变形需用 vector_fields

##### `vector_to_aniso`

**功能**：vector_to_aniso approximates an anisotropic similarity transformation, i.e., a transformation consisting of a rotation, a non-uniform scaling, and a translation, from at least three point correspondences and returns it as the homogeneous transformation matrix HomMat2D . The matrix consists of 3 components: a scaling matrix S with non-identical scaling in the x and y directions, a rotation matrix R, and a translation vector t (also see hom_mat2d_scale , hom_mat2d_rotate , and hom_mat2d_translate ): The point correspondences are passed in the tuples ( Px , Py ) and ( Qx , Qy ), where corresponding points must be at the same index positions in the tuples. The transformation is always overdetermined. Therefore, the returned transformation is the transformation that minimizes the distances between the original points ( Px , Py ) and the transformed points ( Qx , Qy ), as described in the following equation (points as homogeneous vectors):

**签名**：`vector_to_aniso( : : Px, Py, Qx, Qy : HomMat2D)`

**参数说明**：至少 2 组点对应：返回"各向异性相似变换"（旋转+异比缩放+平移）；保留角度

**常见误区**："各向异性"=两个方向缩放不同；sx=2, sy=1 让圆形变椭圆。视觉里不要用，除非你明确想要

##### `vector_to_hom_mat2d`

**功能**：vector_to_hom_mat2d approximates an affine transformation from at least three point correspondences and returns it as the homogeneous transformation matrix HomMat2D (see hom_mat2d_to_affine_par for the content of the homogeneous transformation matrix). The point correspondences are passed in the tuples ( Px , Py ) and ( Qx , Qy ), where corresponding points must be at the same index positions in the tuples. If more than three point correspondences are passed, the transformation is overdetermined. In this case, the returned transformation is the transformation that minimizes the distances between the input points ( Px , Py ) and the transformed points ( Qx , Qy ), as described in the following equation (points as homogeneous vectors):

**签名**：`vector_to_hom_mat2d( : : Px, Py, Qx, Qy : HomMat2D)`

**参数说明**：至少 3 组点对应(P,Q)：返回"全仿射"变换（含剪切）

**常见误区**：2 个点不够！HALCON 必须 ≥ 3 才能解 6 仿射参数；少于会报 H8010

##### `vector_to_proj_hom_mat2d`

**功能**：vector_to_proj_hom_mat2d determines the homogeneous projective transformation matrix HomMat2D that optimally fulfills the following equations given by at least 4 point correspondences If fewer than 4 pairs of points ( Px , Py ), ( Qx , Qy ) are given, there exists no unique solution, if exactly 4 pairs are supplied the matrix HomMat2D transforms them in exactly the desired way, and if there are more than 4 point pairs given, vector_to_proj_hom_mat2d seeks to minimize the transformation error. To achieve such a minimization, several different algorithms are available. The algorithm to use can be chosen using the parameter Method . Method = 'dlt' uses a fast and simple, but also rather inaccurate error estimation algorithm while Method = 'normalized_dlt' offers a good compromise between speed and accuracy. Finally, Method = 'gold_standard' performs a mathematically optimal but slower optimization.

**签名**：`vector_to_proj_hom_mat2d( : : Px, Py, Qx, Qy, Method, CovXX1, CovYY1, CovXY1, CovXX2, CovYY2, CovXY2 : HomMat2D, Covariance)`

**参数说明**：至少 4 组点对应：返回"投影变换"（8 参数含透视效果）

**常见误区**：仿射 6 参数不够解"透视"（如斜拍文档变形）必须用投影；混淆会出现"四角对不齐"

##### `vector_to_proj_hom_mat2d_distortion`

**功能**：vector_to_proj_hom_mat2d_distortion determines the projective transformation matrix HomMat2D and the radial distortion coefficient Kappa from given point correspondences ( Points1Row , Points1Col ), ( Points2Row , Points2Col ) that optimally fulfill the following equation:

**签名**：`vector_to_proj_hom_mat2d_distortion( : : Points1Row, Points1Col, Points2Row, Points2Col, CovRR1, CovRC1, CovCC1, CovRR2, CovRC2, CovCC2, ImageWidth, ImageHeight, Method : HomMat2D, Kappa, Error)`

**参数说明**：≥ 4 组点对应 + 协方差 CovRR1/2 CovRC1/2 CovCC1/2：同时反算径向畸变系数 Kappa

**常见误区**：工业相机去畸变通常用 calibrate 章节的 calibration 算子，本算子用于"粗略无标定板"场景

##### `vector_to_rigid`

**功能**：vector_to_rigid approximates a rigid affine transformation, i.e., a transformation consisting of a rotation and a translation, from at least two point correspondences and returns it as the homogeneous transformation matrix HomMat2D . The matrix consists of 2 components: a rotation matrix R and a translation vector t (also see hom_mat2d_rotate and hom_mat2d_translate ): The point correspondences are passed in the tuples ( Px , Py ) and ( Qx , Qy ), where corresponding points must be at the same index positions in the tuples. The transformation is always overdetermined. Therefore, the returned transformation is the transformation that minimizes the distances between the original points ( Px , Py ) and the transformed points ( Qx , Qy ), as described in the following equation (points as homogeneous vectors):

**签名**：`vector_to_rigid( : : Px, Py, Qx, Qy : HomMat2D)`

**参数说明**：2 组点对应(P,Q) ≥ 2 个：返回"刚体变换"（旋转+平移，不缩放不剪切）；HALCON 中 "刚性同构"

**常见误区**：与 vector_to_hom_mat2d 区别：rigid 不允许缩放；刚性 6 参数 vs 仿射 6 参数同样 6 参数但自由度不同

##### `vector_to_similarity`

**功能**：vector_to_similarity approximates a similarity transformation, i.e., a transformation consisting of a uniform scaling, a rotation, and a translation, from at least two point correspondences and returns it as the homogeneous transformation matrix HomMat2D . The matrix consists of 3 components: a scaling matrix S with identical scaling in the x and y directions, a rotation matrix R, and a translation vector t (also see hom_mat2d_scale , hom_mat2d_rotate , and hom_mat2d_translate ): The point correspondences are passed in the tuples ( Px , Py ) and ( Qx , Qy ), where corresponding points must be at the same index positions in the tuples. If more than two point correspondences are passed, the transformation is overdetermined. In this case, the returned transformation is the transformation that minimizes the distances between the original points ( Px , Py ) and the transformed points ( Qx , Qy ), as described in the following equation (points as homogeneous vectors):

**签名**：`vector_to_similarity( : : Px, Py, Qx, Qy : HomMat2D)`

**参数说明**：至少 2 组点对应：返回"等比相似变换"（旋转+等比缩放+平移）；保持形状（边长比例）

**常见误区**："等比缩放" sx=sy；若输入点不等比，对应矩阵是最佳拟合实际并非完美相似

### ◆ 3D Transformations (三维齐次矩阵变换)（19 算子）

**3D 齐次矩阵（hom_mat3d，4×4 = 12 元素）** 全栈。结构是 `[R(3×3) | t(3×1); 0 0 0 1]`，包含全部 3D 旋转(用 3×3 矩阵存储)+ 3D 平移 + 透视(可选)。它是相机外参、机器人基坐标系↔工具坐标系、工件坐标系等所有 3D 对齐问题的数学基础。

#### 3D 几何决策——算子速查表

| # | 算子 | 一句话功能 | HDevelop 关键签名 |
|---|---|---|---|
| 1 | `affine_trans_point_3d` | affine_trans_point_3d applies an arbitrary affine 3D tran... | `affine_trans_point_3d( : : HomMat3D, Px, Py, Pz : Qx, Qy, Qz)` |
| 2 | `deserialize_hom_mat3d` | deserialize_hom_mat3d deserializes a homogeneous 3D trans... | `deserialize_hom_mat3d( : : SerializedItemHandle : HomMat3D)` |
| 3 | `hom_mat3d_compose` | hom_mat3d_compose composes a new 3D transformation matrix... | `hom_mat3d_compose( : : HomMat3DLeft, HomMat3DRight : HomMat3DCompose)` |
| 4 | `hom_mat3d_determinant` | hom_mat3d_determinant computes the determinant of the hom... | `hom_mat3d_determinant( : : HomMat3D : Determinant)` |
| 5 | `hom_mat3d_identity` | hom_mat3d_identity generates the homogeneous transformati... | `hom_mat3d_identity( : : : HomMat3DIdentity)` |
| 6 | `hom_mat3d_invert` | hom_mat3d_invert inverts the homogeneous 3D transformatio... | `hom_mat3d_invert( : : HomMat3D : HomMat3DInvert)` |
| 7 | `hom_mat3d_rotate` | hom_mat3d_rotate adds a rotation by the angle Phi around ... | `hom_mat3d_rotate( : : HomMat3D, Phi, Axis, Px, Py, Pz : HomMat3DRotate)` |
| 8 | `hom_mat3d_rotate_local` | hom_mat3d_rotate_local adds a rotation by the angle Phi a... | `hom_mat3d_rotate_local( : : HomMat3D, Phi, Axis : HomMat3DRotate)` |
| 9 | `hom_mat3d_scale` | hom_mat3d_scale adds a scaling by the scale factors Sx , ... | `hom_mat3d_scale( : : HomMat3D, Sx, Sy, Sz, Px, Py, Pz : HomMat3DScale)` |
| 10 | `hom_mat3d_scale_local` | hom_mat3d_scale_local adds a scaling by the scale factors... | `hom_mat3d_scale_local( : : HomMat3D, Sx, Sy, Sz : HomMat3DScale)` |
| 11 | `hom_mat3d_to_pose` | hom_mat3d_to_pose converts a homogeneous transformation m... | `hom_mat3d_to_pose( : : HomMat3D : Pose)` |
| 12 | `hom_mat3d_translate` | hom_mat3d_translate adds a translation by the vector t = ... | `hom_mat3d_translate( : : HomMat3D, Tx, Ty, Tz : HomMat3DTranslate)` |
| 13 | `hom_mat3d_translate_local` | hom_mat3d_translate_local adds a translation by the vecto... | `hom_mat3d_translate_local( : : HomMat3D, Tx, Ty, Tz : HomMat3DTranslate)` |
| 14 | `hom_mat3d_transpose` | hom_mat3d_transpose transposes the homogeneous 3D transfo... | `hom_mat3d_transpose( : : HomMat3D : HomMat3DTranspose)` |
| 15 | `pose_to_hom_mat3d` | pose_to_hom_mat3d converts a 3D pose Pose , e | `pose_to_hom_mat3d( : : Pose : HomMat3D)` |
| 16 | `projective_trans_hom_point_3d` | projective_trans_hom_point_3d applies the homogeneous pro... | `projective_trans_hom_point_3d( : : HomMat3D, Px, Py, Pz, Pw : Qx, Qy, Qz, Qw)` |
| 17 | `projective_trans_point_3d` | projective_trans_point_3d applies the homogeneous project... | `projective_trans_point_3d( : : HomMat3D, Px, Py, Pz : Qx, Qy, Qz)` |
| 18 | `serialize_hom_mat3d` | serialize_hom_mat3d serializes the data of a homogeneous ... | `serialize_hom_mat3d( : : HomMat3D : SerializedItemHandle)` |
| 19 | `vector_to_hom_mat3d` | vector_to_hom_mat3d approximates an affine or projective ... | `vector_to_hom_mat3d( : : TransformationType, Px, Py, Pz, Qx, Qy, Qz : HomMat3D)` |

#### 重点算子详解（19 个）

##### `affine_trans_point_3d`

**功能**：affine_trans_point_3d applies an arbitrary affine 3D transformation, i.e., scaling, rotation, and translation, to the input points ( Px , Py , Pz ) and returns the resulting points in ( Qx , Qy , Qz ). The affine transformation is described by the homogeneous transformation matrix given in HomMat3D . This corresponds to the following equation (input and output points as homogeneous vectors): The transformation matrix can be created using the operators hom_mat3d_identity , hom_mat3d_scale , hom_mat3d_rotate , hom_mat3d_translate , etc., or be the result of pose_to_hom_mat3d .

**签名**：`affine_trans_point_3d( : : HomMat3D, Px, Py, Pz : Qx, Qy, Qz)`

**参数说明**：3D 仿射变换对多点 (X,Y,Z) → (X,Y,Z)

**常见误区**：与 affine_trans_point_2d 区别：3D；批量变换高效

##### `deserialize_hom_mat3d`

**功能**：deserialize_hom_mat3d deserializes a homogeneous 3D transformation matrix, that was serialized by serialize_hom_mat3d (see fwrite_serialized_item for an introduction of the basic principle of serialization). The serialized transformation matrix is defined by the handle SerializedItemHandle . The deserialized values are stored in an automatically created transformation matrix with the handle HomMat3D .

**签名**：`deserialize_hom_mat3d( : : SerializedItemHandle : HomMat3D)`

**参数说明**：从 SerializedItemHandle 还原 3D 矩阵

**常见误区**：只接 serialize_hom_mat3d 的产物；不能用 deserialize_hom_mat2d 解析

##### `hom_mat3d_compose`

**功能**：hom_mat3d_compose composes a new 3D transformation matrix by multiplying the two input matrices: For example, if the two input matrices correspond to rigid transformations, i.e., to transformations consisting of a rotation and a translation, the resulting matrix is calculated as follows:

**签名**：`hom_mat3d_compose( : : HomMat3DLeft, HomMat3DRight : HomMat3DCompose)`

**参数说明**：左乘矩阵 + 右乘矩阵：3D 版同 2D 版的"先 Right 再 Left"规则

**常见误区**：3D 顺序敏感得多！旋转顺序 R1→R2→R3 用 hom_mat3d_compose(Compose(Compose(R1,R2),R3), mult)，不可换序

##### `hom_mat3d_determinant`

**功能**：hom_mat3d_determinant computes the determinant of the homogeneous 3D transformation matrix given by HomMat3D and returns it in Determinant .

**签名**：`hom_mat3d_determinant( : : HomMat3D : Determinant)`

**参数说明**：返回 3D 矩阵的 det；用于判断可逆 + 镜射（det<0）

**常见误区**：镜射破坏法向量方向：3D 重建里若两次 det<0 抵消，最终模型正常

##### `hom_mat3d_identity`

**功能**：hom_mat3d_identity generates the homogeneous transformation matrix HomMat3DIdentity describing the identical 3D transformation:

**签名**：`hom_mat3d_identity( : : : HomMat3DIdentity)`

**参数说明**：无参；返回 12 参数 4×4 单位齐次矩阵

**常见误区**：4×4 矩阵存的是 [R(3×3) | t(3×1); 0 0 0 1] 共 12 个数；不能直接当 3×3 用

##### `hom_mat3d_invert`

**功能**：hom_mat3d_invert inverts the homogeneous 3D transformation matrix given by HomMat3D . The resulting matrix is returned in HomMat3DInvert .

**签名**：`hom_mat3d_invert( : : HomMat3D : HomMat3DInvert)`

**参数说明**：4×4 矩阵求逆；返回新 HomMat3D

**常见误区**：平移矩阵求逆等于反方向平移；旋转矩阵求逆等于转置(R⁻¹=Rᵀ)；奇异矩阵报错

##### `hom_mat3d_rotate`

**功能**：hom_mat3d_rotate adds a rotation by the angle Phi around the axis passed in the parameter Axis to the homogeneous 3D transformation matrix HomMat3D and returns the resulting matrix in HomMat3DRotate . The axis can be specified by passing the strings 'x', 'y', or 'z', or by passing a vector [x,y,z] as a tuple. The rotation is described by a 3×3 rotation matrix R. It is performed relative to the global (i.e., fixed) coordinate system; this corresponds to the following chain of transformation matrices:

**签名**：`hom_mat3d_rotate( : : HomMat3D, Phi, Axis, Px, Py, Pz : HomMat3DRotate)`

**参数说明**：追加"绕任意轴旋转"——AxisX/Y/Z + Angle + 中心点 Px,Py,Pz

**常见误区**：与 _local 区别同 2D；Axis 是"过中心点的单位方向向量"，不是 world-frame 方向

##### `hom_mat3d_rotate_local`

**功能**：hom_mat3d_rotate_local adds a rotation by the angle Phi around the axis passed in the parameter Axis to the homogeneous 3D transformation matrix HomMat3D and returns the resulting matrix in HomMat3DRotate . The axis can be specified by passing the strings 'x', 'y', or 'z', or by passing a vector [x,y,z] as a tuple. The rotation is described by a 3×3 rotation matrix R. In contrast to hom_mat3d_rotate , it is performed relative to the local coordinate system, i.e., the coordinate system described by HomMat3D ; this corresponds to the following chain of transformation matrices:

**签名**：`hom_mat3d_rotate_local( : : HomMat3D, Phi, Axis : HomMat3DRotate)`

**参数说明**：以原点为中心的旋转；不指定中心点参数

**常见误区**：多次 _local 拼接：T⁻¹ × R × T 三明治式才能"绕指定中心旋转"

##### `hom_mat3d_scale`

**功能**：hom_mat3d_scale adds a scaling by the scale factors Sx , Sy , and Sz to the homogeneous 3D transformation matrix HomMat3D and returns the resulting matrix in HomMat3DScale . The scaling is described by a 3×3 scaling matrix S. It is performed relative to the global (i.e., fixed) coordinate system; this corresponds to the following chain of transformation matrices: The point ( Px , Py , Pz ) is the fixed point of the transformation, i.e., this point remains unchanged when transformed using HomMat3DScale . To obtain this behavior, first a translation is added to the input transformation matrix that moves the fixed point onto the origin of the global coordinate system. Then, the scaling is added, and finally a translation that moves the fixed point back to its original position. This corresponds to the following chain of transformations:

**签名**：`hom_mat3d_scale( : : HomMat3D, Sx, Sy, Sz, Px, Py, Pz : HomMat3DScale)`

**参数说明**：(Sx, Sy, Sz, Px, Py, Pz)：各向异性缩放 + 固定点

**常见误区**：Sx,Sy,Sz 不能为 0；矩阵奇异不可逆

##### `hom_mat3d_scale_local`

**功能**：hom_mat3d_scale_local adds a scaling by the scale factors Sx , Sy , and Sz to the homogeneous 3D transformation matrix HomMat3D and returns the resulting matrix in HomMat3DScale . The scaling is described by a 3×3 scaling matrix S. In contrast to hom_mat3d_scale , it is performed relative to the local coordinate system, i.e., the coordinate system described by HomMat3D ; this corresponds to the following chain of transformation matrices: The fixed point of the transformation is the origin of the local coordinate system, i.e., this point remains unchanged when transformed using HomMat3DScale .

**签名**：`hom_mat3d_scale_local( : : HomMat3D, Sx, Sy, Sz : HomMat3DScale)`

**参数说明**：(Sx, Sy, Sz) 三轴异比缩放，无中心点

**常见误区**：与普通 hom_mat3d_scale 区别同 2D；3D 里负值缩放等价于镜射

##### `hom_mat3d_to_pose`

**功能**：hom_mat3d_to_pose converts a homogeneous transformation matrix into the corresponding 3D pose with type code 0. For details about 3D poses and the corresponding transformation matrices please refer to create_pose . A typical application of hom_mat3d_to_pose is that a 3D pose was converted into a homogeneous transformation matrix to further transform it, e.g., with hom_mat3d_rotate or hom_mat3d_translate , and now must be converted back into a pose to use it as input for operators like image_points_to_world_plane .

**签名**：`hom_mat3d_to_pose( : : HomMat3D : Pose)`

**参数说明**：齐次矩阵 → Pose（type code 0 的 6D 位姿 XYZ + αβγ）

**常见误区**：Pose 比矩阵少 6 个自由度约束（旋转以 ZYX 顺序）；多次互转会有数值精度损失

##### `hom_mat3d_translate`

**功能**：hom_mat3d_translate adds a translation by the vector t = ( Tx , Ty , Tz ) to the homogeneous 3D transformation matrix HomMat3D and returns the resulting matrix in HomMat3DTranslate . The translation is performed relative to the global (i.e., fixed) coordinate system; this corresponds to the following chain of transformation matrices: To perform the transformation in the local coordinate system, i.e., the one described by HomMat3D , use hom_mat3d_translate_local .

**签名**：`hom_mat3d_translate( : : HomMat3D, Tx, Ty, Tz : HomMat3DTranslate)`

**参数说明**：(Tx, Ty, Tz)：3D 平移向量追加

**常见误区**：HALCON 用行主序存储(12 个值)，TX 对应 [a13] 位；视觉混淆常把 (X,Y,Z) 写成 (Row,Col,Z)

##### `hom_mat3d_translate_local`

**功能**：hom_mat3d_translate_local adds a translation by the vector t = ( Tx , Ty , Tz ) to the homogeneous 3D transformation matrix HomMat3D and returns the resulting matrix in HomMat3DTranslate . In contrast to hom_mat3d_translate , the translation is performed relative to the local coordinate system, i.e., the coordinate system described by HomMat3D ; this corresponds to the following chain of transformation matrices:

**签名**：`hom_mat3d_translate_local( : : HomMat3D, Tx, Ty, Tz : HomMat3DTranslate)`

**参数说明**：以原点为中心的平移；与普通版区别同 2D

**常见误区**：当机器人坐标系变换时，"tool 中心"为原点——用 _local；"世界坐标系"用普通版

##### `hom_mat3d_transpose`

**功能**：hom_mat3d_transpose transposes the homogeneous 3D transformation matrix given by HomMat3D . The result matrix HomMat3DTranspose is always a 4×4 matrix, even if the input matrix is represented by a 3×4 matrix.

**签名**：`hom_mat3d_transpose( : : HomMat3D : HomMat3DTranspose)`

**参数说明**：3D 版的"互换原矩阵行列"；不是矩阵转置也不是逆

**常见误区**：纯函数变化，并不是矩阵转置 conj_transpose；hom_mat3d_invert 才是真正的"几何反变换"

##### `pose_to_hom_mat3d`

**功能**：pose_to_hom_mat3d converts a 3D pose Pose , e.g., the external camera parameters, into the equivalent homogeneous transformation matrix HomMat3D . For details about 3D poses and the corresponding transformation matrices please refer to create_pose . A typical application of pose_to_hom_mat3d is that you want to further transform the pose, e.g., rotate or translate it using hom_mat3d_rotate or hom_mat3d_translate . In case of the external camera parameters, this can be necessary if the calibration plate cannot be placed such that its coordinate system coincides with the desired world coordinate system.

**签名**：`pose_to_hom_mat3d( : : Pose : HomMat3D)`

**参数说明**：Pose → 齐次矩阵；Pose 数据格式 [X,Y,Z,α,β,γ,Code]

**常见误区**：与 hom_mat3d_to_pose 配对使用；位姿 Code 不同(0/1/2)对应不同旋转顺序

##### `projective_trans_hom_point_3d`

**功能**：projective_trans_hom_point_3d applies the homogeneous projective transformation matrix HomMat3D to all homogeneous input points ( Px , Py , Pz , Pw ) and returns an array of homogeneous output points ( Qx , Qy , Qz , Qw ). The transformation is described by the homogeneous transformation matrix given in HomMat3D . This corresponds to the following equation (input and output points as homogeneous vectors): To transform the homogeneous coordinates to Euclidean coordinates, they must be divided by Qw :

**签名**：`projective_trans_hom_point_3d( : : HomMat3D, Px, Py, Pz, Pw : Qx, Qy, Qz, Qw)`

**参数说明**：齐次 3D 点应用投影变换；返回齐次结果（带 Pw）

**常见误区**："齐次 4 元"=(Xw,Yw,Zw,Ww)；W=1 是常规点，W=0 代表无穷远点（消失点）

##### `projective_trans_point_3d`

**功能**：projective_trans_point_3d applies the homogeneous projective transformation matrix HomMat3D to all input points ( Px , Py , Pz ) and returns an array of output points ( Qx , Qy , Qz ). The transformation is described by the homogeneous transformation matrix given in HomMat3D . This corresponds to the following equations (input and output points as homogeneous vectors): projective_trans_point_3d then transforms the homogeneous coordinates to Euclidean coordinates by dividing them by Tw:

**签名**：`projective_trans_point_3d( : : HomMat3D, Px, Py, Pz : Qx, Qy, Qz)`

**参数说明**：非齐次 3D 点应用投影变换；返回非齐次结果

**常见误区**：3D 投影变换会让透视相机看的 3D 点映射到 2D 像平面——通常直接用相机模型算子

##### `serialize_hom_mat3d`

**功能**：serialize_hom_mat3d serializes the data of a homogeneous 3D transformation matrix (see fwrite_serialized_item for an introduction of the basic principle of serialization). The transformation matrix is defined by the handle HomMat3D . The serialized transformation matrix is returned by the handle SerializedItemHandle and can be deserialized by deserialize_hom_mat3d .

**签名**：`serialize_hom_mat3d( : : HomMat3D : SerializedItemHandle)`

**参数说明**：3D 矩阵序列化为 SerializedItemHandle

**常见误区**：与 serialize_hom_mat2d 区别只 12 vs 6 参数；不可混解析——serde 是反向同族算子

##### `vector_to_hom_mat3d`

**功能**：vector_to_hom_mat3d approximates an affine or projective 3D transformation from point correspondences and returns it as the homogeneous transformation matrix HomMat3D . The type of the 3D transformation to compute is specified with TransformationType . For TransformationType = 'rigid' , a rigid 3D transformation (a rotation and a translation), for TransformationType = 'similarity' , a 3D similarity transformation (a uniform scaling, a rotation, and a translation), for TransformationType = 'affine' a general affine 3D transformation, and for TransformationType = 'projective' a projective 3D transformation is computed.

**签名**：`vector_to_hom_mat3d( : : TransformationType, Px, Py, Pz, Qx, Qy, Qz : HomMat3D)`

**参数说明**：≥ 4 组 3D 点对应(P,Q) + TransformationType：构造 3D 仿射/投影齐次矩阵

**常见误区**：Type 选错：affine 6 自由度 vs projective 12 自由度；点对数不够会报错

## 3. 全卷算子速查表

| 算子 | 家族 | 类别 | 一句话功能 |
|---|---|---|---|
| `affine_trans_pixel` | 2D Transformations | 矩阵变换 | affine_trans_pixel applies an arbitrary affine 2D transforma |
| `affine_trans_point_2d` | 2D Transformations | 矩阵变换 | affine_trans_point_2d applies an arbitrary affine 2D transfo |
| `deserialize_hom_mat2d` | 2D Transformations | 矩阵变换 | deserialize_hom_mat2d deserializes a homogeneous 2D transfor |
| `hom_mat2d_compose` | 2D Transformations | 矩阵变换 | hom_mat2d_compose composes a new 2D transformation matrix by |
| `hom_mat2d_determinant` | 2D Transformations | 矩阵变换 | hom_mat2d_determinant computes the determinant of the homoge |
| `hom_mat2d_identity` | 2D Transformations | 矩阵变换 | hom_mat2d_identity generates the homogeneous transformation  |
| `hom_mat2d_invert` | 2D Transformations | 矩阵变换 | hom_mat2d_invert inverts the homogeneous 2D transformation m |
| `hom_mat2d_reflect` | 2D Transformations | 矩阵变换 | hom_mat2d_reflect adds a reflection about the axis given by  |
| `hom_mat2d_reflect_local` | 2D Transformations | 矩阵变换 | hom_mat2d_reflect_local adds a reflection about the axis giv |
| `hom_mat2d_rotate` | 2D Transformations | 矩阵变换 | hom_mat2d_rotate adds a rotation by the angle Phi to the hom |
| `hom_mat2d_rotate_local` | 2D Transformations | 矩阵变换 | hom_mat2d_rotate_local adds a rotation by the angle Phi to t |
| `hom_mat2d_scale` | 2D Transformations | 矩阵变换 | hom_mat2d_scale adds a scaling by the scale factors Sx and S |
| `hom_mat2d_scale_local` | 2D Transformations | 矩阵变换 | hom_mat2d_scale_local adds a scaling by the scale factors Sx |
| `hom_mat2d_slant` | 2D Transformations | 矩阵变换 | hom_mat2d_slant adds a slant by the angle Theta to the homog |
| `hom_mat2d_slant_local` | 2D Transformations | 矩阵变换 | hom_mat2d_slant_local adds a slant by the angle Theta to the |
| `hom_mat2d_to_affine_par` | 2D Transformations | 矩阵变换 | hom_mat2d_to_affine_par computes the affine transformation p |
| `hom_mat2d_translate` | 2D Transformations | 矩阵变换 | hom_mat2d_translate adds a translation by the vector t = ( T |
| `hom_mat2d_translate_local` | 2D Transformations | 矩阵变换 | hom_mat2d_translate_local adds a translation by the vector t |
| `hom_mat2d_transpose` | 2D Transformations | 矩阵变换 | hom_mat2d_transpose transposes the homogeneous 2D transforma |
| `hom_vector_to_proj_hom_mat2d` | 2D Transformations | 矩阵变换 | hom_vector_to_proj_hom_mat2d determines the homogeneous proj |
| `point_line_to_hom_mat2d` | 2D Transformations | 矩阵变换 | point_line_to_hom_mat2d approximates an affine transformatio |
| `projective_trans_pixel` | 2D Transformations | 矩阵变换 | projective_trans_pixel applies the homogeneous projective tr |
| `projective_trans_point_2d` | 2D Transformations | 矩阵变换 | projective_trans_point_2d applies the homogeneous projective |
| `serialize_hom_mat2d` | 2D Transformations | 矩阵变换 | serialize_hom_mat2d serializes the data of a homogeneous 2D  |
| `vector_angle_to_rigid` | 2D Transformations | 矩阵变换 | vector_angle_to_rigid computes a rigid affine transformation |
| `vector_field_to_hom_mat2d` | 2D Transformations | 矩阵变换 | vector_field_to_hom_mat2d approximates an affine map from th |
| `vector_to_aniso` | 2D Transformations | 矩阵变换 | vector_to_aniso approximates an anisotropic similarity trans |
| `vector_to_hom_mat2d` | 2D Transformations | 矩阵变换 | vector_to_hom_mat2d approximates an affine transformation fr |
| `vector_to_proj_hom_mat2d` | 2D Transformations | 矩阵变换 | vector_to_proj_hom_mat2d determines the homogeneous projecti |
| `vector_to_proj_hom_mat2d_distortion` | 2D Transformations | 矩阵变换 | vector_to_proj_hom_mat2d_distortion determines the projectiv |
| `vector_to_rigid` | 2D Transformations | 矩阵变换 | vector_to_rigid approximates a rigid affine transformation,  |
| `vector_to_similarity` | 2D Transformations | 矩阵变换 | vector_to_similarity approximates a similarity transformatio |
| `affine_trans_point_3d` | 3D Transformations | 矩阵变换 | affine_trans_point_3d applies an arbitrary affine 3D transfo |
| `deserialize_hom_mat3d` | 3D Transformations | 矩阵变换 | deserialize_hom_mat3d deserializes a homogeneous 3D transfor |
| `hom_mat3d_compose` | 3D Transformations | 矩阵变换 | hom_mat3d_compose composes a new 3D transformation matrix by |
| `hom_mat3d_determinant` | 3D Transformations | 矩阵变换 | hom_mat3d_determinant computes the determinant of the homoge |
| `hom_mat3d_identity` | 3D Transformations | 矩阵变换 | hom_mat3d_identity generates the homogeneous transformation  |
| `hom_mat3d_invert` | 3D Transformations | 矩阵变换 | hom_mat3d_invert inverts the homogeneous 3D transformation m |
| `hom_mat3d_rotate` | 3D Transformations | 矩阵变换 | hom_mat3d_rotate adds a rotation by the angle Phi around the |
| `hom_mat3d_rotate_local` | 3D Transformations | 矩阵变换 | hom_mat3d_rotate_local adds a rotation by the angle Phi arou |
| `hom_mat3d_scale` | 3D Transformations | 矩阵变换 | hom_mat3d_scale adds a scaling by the scale factors Sx , Sy  |
| `hom_mat3d_scale_local` | 3D Transformations | 矩阵变换 | hom_mat3d_scale_local adds a scaling by the scale factors Sx |
| `hom_mat3d_to_pose` | 3D Transformations | 矩阵变换 | hom_mat3d_to_pose converts a homogeneous transformation matr |
| `hom_mat3d_translate` | 3D Transformations | 矩阵变换 | hom_mat3d_translate adds a translation by the vector t = ( T |
| `hom_mat3d_translate_local` | 3D Transformations | 矩阵变换 | hom_mat3d_translate_local adds a translation by the vector t |
| `hom_mat3d_transpose` | 3D Transformations | 矩阵变换 | hom_mat3d_transpose transposes the homogeneous 3D transforma |
| `pose_to_hom_mat3d` | 3D Transformations | 矩阵变换 | pose_to_hom_mat3d converts a 3D pose Pose , e |
| `projective_trans_hom_point_3d` | 3D Transformations | 矩阵变换 | projective_trans_hom_point_3d applies the homogeneous projec |
| `projective_trans_point_3d` | 3D Transformations | 矩阵变换 | projective_trans_point_3d applies the homogeneous projective |
| `serialize_hom_mat3d` | 3D Transformations | 矩阵变换 | serialize_hom_mat3d serializes the data of a homogeneous 3D  |
| `vector_to_hom_mat3d` | 3D Transformations | 矩阵变换 | vector_to_hom_mat3d approximates an affine or projective 3D  |

## 4. 跨算子误区 & 调试提示

1. **`hom_mat2d_compose` 是"先 Right 再 Left"**：HALCON 矩阵乘法约定与传统相反——A→B 后视觉里的变换应用顺序是 `Right × Left`（即"先子后父"）。视觉应用时取 `apply_transform = T_left × T_right`。调试错位时先画坐标轴而非盲调顺序。
2. **`_local` 变种 = 中心点是原点**：所有 `hom_mat2d_rotate/_translate/_scale/_slant/_reflect_local` 都"以原点为不动点"。要绕任意点 P 旋转要三明治式：`T(-P) × R × T(P)`，分别用 `hom_mat2d_translate` + `hom_mat2d_rotate` + `hom_mat2d_translate` 三次 compose。
3. **`det < 0` 是镜射**：齐次矩阵 det<0 表示手性反转（左右颠倒 / 法线指向反侧）。2D 视觉里感觉"上下颠倒"；3D 重建里破坏法线方向（会让光线方向反转）。可用 `hom_mat2d_determinant` 检查，多次镜射可能抵消但不保证。
4. **`vector_to_*` 反算的点对数量决定变换类型**：rigid ≥ 2、similarity ≥ 2、aniso ≥ 2、affine ≥ 3、projective ≥ 4。每多一对提高鲁棒性（最小二乘抗噪）；少了报错 H8010。
5. **`serialize_*_mat2d` 不可跨类型**：`serialize_hom_mat2d` 只能用 `deserialize_hom_mat2d` 还原；3D 版同理。SerializedItem 是私有协议，不能给 OpenCV 用，要 OpenCV 兼容要用 `vector_to_*` 反算 6/12 数值。
6. **`affine_trans_pixel` vs `affine_trans_point_2d`**：pixel 用 `(Row,Col)=(y,x)` 图像坐标系，point 用 `(X,Y)` 数学坐标系。两者 6 参数刚好对调。混淆出现 x/y 翻转错位。
7. **3D Pose 互转损失**：`hom_mat3d_to_pose` 与 `pose_to_hom_mat3d` 多次互转会累积数值误差（ZYX/ZXY/YZX 等旋转顺序强加 6 DOF 约束）。批量循环里要保留矩阵句柄避免反复转换。
8. **`affine_trans_*` 大批量元素应用效率**：对 ROI/XLD 类型的批量变换有 `affine_trans_image/region/xld` 等系列算子（不同章节）；本卷对点/像素应用算子用于"少量点的坐标查询"。

## 5. 调用链路与组合用法（HDevelop 实战代码）

### 5.1 2D 刚体对位——vector_angle_to_rigid 三步流水线

```hdevelop
* 已知模板在 (R1,C1,A1) 处，现在图像中在 (R2,C2,A2) 处出现
* 一行代码构造"绕指定点旋转+平移"仿射矩阵（最常见标定/对齐流水线）
vector_angle_to_rigid (R1, C1, A1, R2, C2, A2, HomMat2D)
affine_trans_image (Image, ImageAligned, HomMat2D, "constant", "false")
* 与 find_shape_model 返回的 HomMat2D 配合——后者直接对接本算子

* ROI 也跟着对齐（RegionOfInterest 跟着目标走）
affine_trans_region (RegionROI, RegionAligned, HomMat2D, "nearest_neighbor")
```

### 5.2 2D 透视校正——vector_to_proj_hom_mat2d_distortion + 反算畸变

```hdevelop
* 已知 4 个 (P,Q) 世界→图像点对应 + 观测噪声协方差
* 同时反算"投影变换 + 径向畸变系数"，适合"无标定板粗对位"
vector_to_proj_hom_mat2d_distortion (Rows1, Cols1, Rows2, Cols2, \
                               CovRR1, CovRC1, CovCC1, \
                               CovRR2, CovRC2, CovCC2, \
                               HomMat2D, Kappa)
* 之后对所有点应用变换（含畸变补偿）
projective_trans_pixel (HomMat2D, Row, Col, RowT, ColT)
```

### 5.3 3D 手眼标定——hom_mat3d_to_pose + cam_pose 反推

```hdevelop
* HALCON 标准手眼标定流水线：相机外参 + 机器人基→工具矩阵 = 相机→工具变换
* 先反推相机外参
camera_calibration (CalibDataID, ErrorEstimate, CameraPoseOut)
* 矩阵转位姿便于机器人控制器读取
hom_mat3d_to_pose (CameraPoseOut, Pose)
* 反向：把机器人位姿转矩阵便于 3D 数学计算
pose_to_hom_mat3d (ToolInBasePose, ToolInBaseMat)
* 矩阵复合：相机→基工具坐标系
hom_mat3d_compose (CameraInTool, ToolInBaseMat, CamInBaseMat)
```

### 5.4 3D 任意轴旋转——T⁻¹ × R × T 三明治式（绕任意点旋转）

```hdevelop
* hom_mat3d_rotate_local 是"绕原点旋转"，要绕任意点 (Cx,Cy,Cz) 旋转需三明治：
hom_mat3d_translate (HomMat3D, -Cx, -Cy, -Cz, HomMat3DPre)
hom_mat3d_rotate (HomMat3DPre, AxisX, AxisY, AxisZ, AngleRad, 0, 0, 0, HomMat3DMid)
* 注意：上面 _rotate 之后已经内置了"绕原点"语义——再 compose 上"反向平移即可回到 Cx,Cy,Cz"
hom_mat3d_translate (HomMat3DMid, Cx, Cy, Cz, HomMat3DFinal)
* 更简洁：让 hom_mat3d_rotate 直接以 (Cx,Cy,Cz) 为中心（这是 _rotate(非local)的标准用法）
hom_mat3d_rotate (HomMat3D, AxisX, AxisY, AxisZ, AngleRad, Cx, Cy, Cz, HomMat3DRotate)
```

## 6. 与其它章节的关联

- **Ch3 3D Matching**：模板匹配返回的 `HomMat3D` 直接对接本卷 `affine_trans_point_3d` / `hom_mat3d_invert` 等；
- **Ch4 3D Object Model**：3D 对象模型的所有变换（旋转/平移/缩放）本质上都是 `hom_mat3d` 系列算子组合；
- **Ch8 Control**：标定助手 `calibrate_hand_eye` 内部就用 `hom_mat3d_compose`/`hom_mat3d_invert` 链；
- **Ch9 Deep Learning**：3D 推理结果的位姿常用 `pose_to_hom_mat3d` + 反向变换对齐到场景；
- **Ch17 Matching**：find_shape_model 直接返回 hom_mat2d，可直接用于 affine_trans_image；
- **Ch18 Matrix**：HALCON 元组层对矩阵的逐元素操作 vs 本卷的"几何语义层"互转；
- **Ch20 OCR**：印刷/手写字符的"倾斜校正"核心就是 hom_mat2d_rotate；
- **Ch24 System**：序列化 (serialize/deserialize) 属于 Ch24 算子，但矩阵的序列化版本就在 Ch26；
- **Ch25 Tools**：图像拼接 Mosaicking 的所有估计变换矩阵 + warp_image 都是 hom_mat2d 应用。

> 本卷算子常作为"接收方"——Ch3/Ch4/Ch17 返回的矩阵直接喂给本卷应用算子，避免反复构造中间句柄。

## 7. 一句话核心要义

> **HALCON 的矩阵操作抽象成 3 层：(1) 构造（hom_mat2d_identity / vector_to_*）→ (2) 变换复合（hom_mat2d_compose / _rotate / _translate / _scale / _slant / _reflect）→ (3) 应用（affine_trans_pixel/point_2d/3d + projective_trans_*）+ 序列化（serialize/deserialize）。**

