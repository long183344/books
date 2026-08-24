# 第 24 章 System · 下卷 — 4 子族 36 算子 (Parameters + Serial + SerializedItem + Sockets)

> **全章速览**：Ch24 System 是 HALCON 与外部世界对话的总接口，分两卷。上卷（本地资源 47 ops：`Ch24-System(上).md`）覆盖计算设备/数据库/错误处理/IO/元信息，本卷聚焦**分布式系统**——算子超时控制 + RS-232 串口 + 序列化持久化 + TCP/UDP 套接字联机。

> 上卷：47 ops；中卷：52 ops；下卷：36 ops；**全章 12 子族 133 算子**全部讲完。

---

## 0. 全章索引（点击跳转）

| 子族族名 | ops | 主题 | 文档位置 |
| --- | --- | --- | --- |
| ① Parameters | 4 | 算子超时控制与系统参数查询/设置 | [↓ 第 1 节](#1-parameters--4-ops) |
| ② Serial | 7 | RS-232 串口通信 | [↓ 第 2 节](#2-serial--7-ops) |
| ③ SerializedItem | 5 | 任意 HALCON 对象的序列化持久化 | [↓ 第 3 节](#3-serializeditem--5-ops) |
| ④ Sockets | 20 | TCP/UDP 联网通信 | [↓ 第 4 节](#4-sockets--20-ops) |
| 附录 A | — | 整章技术深度 | [↓ 附录 A](#附录-a技术深度) |
| 附录 B | — | 与其它章节的关联映射 | [↓ 附录 B](#附录-b与其它章节的关联映射) |

---

## 1. Parameters · 4 ops

> 主题：**算子超时控制与系统参数查询/设置**。本子族是 HALCON 全局行为调节的瑞士军刀，`set_operator_timeout` 是生产环境的"算子熔断器"，`get_system`/`set_system` 是调试期的"全局钥匙"。

### ① get_system

- **一句话功能**：查询当前激活的 HALCON 系统参数值。
- **HDevelop 关键签名**：`get_system( : : Query : Information)`
- **典型用途**：在 HDevelop 控制台输入 `get_system('*')` 一次返回所有系统参数当前值——调试期必备。
- **重点参数**：
  - `Query`（string）参数名。常用 `'cpu_num'` / `'parallelize_operators'` / `'thread_pool'` / `'tsp_path'`。
  - `'*'` 通配一次返回所有参数列表（≈100 个），适合做静态检查/迁移脚本。

### ② get_system_info

- **一句话功能**：返回与 `get_system` 相似的系统参数信息，但**无需合法 license**——离线诊断必备。
- **HDevelop 关键签名**：`get_system_info( : : Query : Information)`
- **典型用途**：客户机器没装 license 也能跑出 HALCON 全部配置——售后诊断首选。

### ③ set_operator_timeout

- **一句话功能**：给指定算子设置运行时超时时间（秒），超时熔断后抛出 `H_ERR_TIMEOUT`。
- **HDevelop 关键签名**：`set_operator_timeout( : : OperatorName, Timeout, Mode : )`
- **典型用途**：生产产线网络抖动/相机断线时算子卡死——`set_operator_timeout('read_image', 3, 'cancel')` 3 秒熔断。
- **重点参数**：
  - `OperatorName`（string）支持 `'*'` 通配代表所有算子。
  - `Timeout`（number）秒数，**不是毫秒**。
  - `Mode`（enum）`'cancel'` 熔断抛错 / `'auto'` HALCON 决定是否熔断。
- **三类适用场景**：网络阻塞算子（`read_image` / `recv_image`）/ 大图像算子（`find_shape_model`）/ 训练算子（`train_dl_model` 几百小时）。
- **注意**：与上卷 `set_check` 完全不同：`set_check` 校验参数合法性（开发期），`set_operator_timeout` 熔断运行时长（生产期），两者**正交**。

### ④ set_system

- **一句话功能**：修改 HALCON 系统参数（核心全局开关）。
- **HDevelop 关键签名**：`set_system( : : SystemParameter, Value : )`
- **典型用途**：AOP 部署第一步 ——`set_system('parallelize_operators', 'true')`。
- **重点参数**：25+ 个可设置项，常用四大件：
  - `'parallelize_operators'('true'/'false')` — AOP 总开关（中卷详解）
  - `'thread_num'`(`'auto'`/`'4'` 等) — 全局线程池大小
  - `'tsp_path'`(`'default'`/`'C:\\halcon'`) — 永久缓存路径（OCR/PX 词典/disp 模型都存这）
  - `'operator_call_timeout'`(`<number>`) — 算子调用的总超时（与 `set_operator_timeout` 的算子级超时叠加）

---

## 2. Serial · 7 ops

> 主题：**HALCON 调 RS-232 串口**。工业现场最古老但极度稳定的通信介质——相机/激光器/扫码枪/光栅尺多走 232。本子族 7 算子分四组：开/关 + 读/写 + 设置参数/查询参数 + 清除缓冲。

### ① open_serial

- **一句话功能**：按设备名（操作系统相关）打开 RS-232 串口，返回句柄。
- **HDevelop 关键签名**：`open_serial( : : PortName : SerialHandle)`
- **典型用途**：`open_serial('COM1')`(Win) / `open_serial('/dev/ttyS0')`(Linux)。
- **重点参数**：`PortName` Windows 是 `'COM1'..'COM256'`，Linux 是 `'/dev/ttyS0'`/`'/dev/ttyUSB0'`(USB 串口线)。
- **注意**：必须 `set_serial_param` 后才能通信；不同操作系统的 PortName 写法差异很大。

### ② close_serial

- **一句话功能**：关闭已打开的串口释放资源。
- **HDevelop 关键签名**：`close_serial( : : SerialHandle : )`

### ③ set_serial_param

- **一句话功能**：设置串口的 7 项参数（波特率/数据位/流控/奇偶/停止位/超时/字符间超时）。
- **HDevelop 关键签名**：`set_serial_param( : : SerialHandle, BaudRate, DataBits, FlowControl, Parity, StopBits, TotalTimeOut, InterCharTimeOut : )`
- **典型用途**：扫码器/光栅仪通信前必调 —— `set_serial_param(SH, 115200, 8, 'none', 'none', 1, 1000, 50)`。
- **重点参数**：
  - `BaudRate`(9600/19200/38400/57600/115200 等)；
  - `FlowControl`(`'none'` / `'rts_cts'` / `'xon_xoff'`)；
  - `Parity`(`'none'`/`'odd'`/`'even'`)；
  - `StopBits`(1/2)；
  - `TotalTimeOut`(读数据总超时 ms)；
  - `InterCharTimeOut`(字符间超时 ms,识别消息边界)。

### ④ get_serial_param

- **一句话功能**：查询串口的 7 项当前参数值。
- **HDevelop 关键签名**：`get_serial_param( : : SerialHandle : BaudRate, DataBits, FlowControl, Parity, StopBits, TotalTimeOut, InterCharTimeOut)`

### ⑤ read_serial

- **一句话功能**：从串口读 N 个字符(整数元组形式)，阻塞等待。
- **HDevelop 关键签名**：`read_serial( : : SerialHandle, NumCharacters : Data)`
- **典型用途**：`read_serial(SH, 16, Data)` 读 16 字节响应。
- **重点参数**：`NumCharacters` 是预期字节数,实际可能读到 `< NumCharacters`(超时)或 0(失败)。

### ⑥ write_serial

- **一句话功能**：向串口写一串字符(整数元组形式)。
- **HDevelop 关键签名**：`write_serial( : : SerialHandle, Data : )`
- **典型用途**：`write_serial(SH, [0xAA, 0x01, 0x02])` 写三字节。整数需要 0~255(8-bit)。
- **注意**：数据长度受串口缓冲区大小限制；写带超时时(`set_serial_param` 配 `TotalTimeOut`)会自动重试。

### ⑦ clear_serial

- **一句话功能**：清空串口指定通道(`'input'`/`'output'`/`'in_out'`)的内部缓冲区,丢弃未发送或未读数据。
- **HDevelop 关键签名**：`clear_serial( : : SerialHandle, Channel : )`
- **典型用途**：通信错位恢复 —— 协议 A 出现误码不清,协议 B 开始前必须 `clear_serial(SH, 'in_out')` 防止污染。
- **重点参数**：`Channel` 是枚举值，**只清发送**(`'output'`)、**只清接收**(`'input'`)、或两边都清(`'in_out'`)。

---

## 3. SerializedItem · 5 ops

> 主题：**任意 HALCON 对象的二进制序列化/反序列化**——完美解决"开发机调好的模型拿到产线""训练结果跨进程传递"两大场景。HALCON 内部把 serialized item 当成"字节流 + 句柄"，跨进程/跨语言/跨设备都有通用序列化能力。

### ① create_serialized_item_ptr

- **一句话功能**：从外部 C/C++ 数据指针 + 长度创建 HALCON 序列化项。
- **HDevelop 关键签名**：`create_serialized_item_ptr( : : Pointer, Size, Copy : SerializedItemHandle)`
- **典型用途**：把第三方 C 库(OpenCV/Infer引擎)的输出 byte[] 转 HALCON 序列化项。
- **重点参数**：
  - `Pointer`(整数)外部内存指针(由 `tuple_addressing` 获取)；
  - `Size`(整数)字节长度；
  - `Copy`(`'true'`深拷/'false'浅拷)= HALCON 是否接管该内存；
- **注意**：浅拷(`'false'`)模式下底层内存生命周期由调用方管理,HALCON 销毁时不释放。

### ② clear_serialized_item

- **一句话功能**：删除序列化项,释放句柄持有资源。
- **HDevelop 关键签名**：`clear_serialized_item( : : SerializedItemHandle : )`
- **典型用途**：模型/字典/嵌套元组使用完后必清,否则句柄泄漏。

### ③ fwrite_serialized_item

- **一句话功能**：把序列化项写入到已打开的文件句柄位置。
- **HDevelop 关键签名**：`fwrite_serialized_item( : : FileHandle, SerializedItemHandle : )`
- **典型用途**：模型持久化 —— `open_file` → `fwrite_serialized_item` → `close_file`。**关键用途：把 OCR 训练结果/MVTec DL 模型序列化项写到磁盘**。
- **注意**：写入是**裸二进制**,必须经过 `create_serialized_item_ptr` 在内存组装包装; 或者 `serialize_tuple`/`serialize_object` 等高级接口得到句柄后用这个写文件。

### ④ fread_serialized_item

- **一句话功能**：从已打开的文件句柄位置读取序列化项。
- **HDevelop 关键签名**：`fread_serialized_item( : : FileHandle : SerializedItemHandle)`
- **典型用途**：模型的反持久化 ——`open_file` → `fread_serialized_item` → `deserialize_*`。
- **注意**：读出的是包装好的句柄,**不是裸的 HALCON Object**; 需要再调 `deserialize_region`/`deserialize_tuple`/`deserialize_object` 等反序列化算子(跨章节)复原。

### ⑤ get_serialized_item_ptr

- **一句话功能**：获取序列化项底层数据指针 + 长度,用于接入 C/C++ 互操作。
- **HDevelop 关键签名**：`get_serialized_item_ptr( : : SerializedItemHandle : Pointer, Size)`
- **典型用途**：把 HALCON 数据传给 OpenCV/CPP 接口。
- **注意**：只读指针;不要尝试修改(HALCON 可能缓存头部)。

### SerializedItem 5 步配对速记法

```
  ① 序列化 packaging：
  create_serialized_item_ptr(C_ptr, len, 'true')  -- 或 deserialize_pack 模块包装
         ↓ SerializedItemHandle
  ② 写文件持久化：
  fwrite_serialized_item(FH, H)
         ↓ 文件二进制
  ③ 读文件反持久化：
  fread_serialized_item(FH)
         ↓ SerializedItemHandle
  ④ 解 packaging 还原对象：
  deserialize_region / deserialize_tuple / deserialize_object 等
         ↓ 原始 HALCON 数据
  ⑤ 清理：
  clear_serialized_item(H)
```

---

## 4. Sockets · 20 ops

> 主题：**基于 TCP/UDP 的网络通信**。HALCON 的 socket 算子封装了 Berkeley Sockets,可轻松在两台机器间同步图像/Region/参数/任何序列化项——多机器视觉产线、HALCON 子组件 + Python/OpenCV 主控、Cloud Vision 边缘计算的统一接口。

### ② 4.1 生命周期(2 ops)

#### ① close_socket

- **一句话功能**：关闭 `open_socket_*` / `socket_accept_connect` 开启的套接字。
- **HDevelop 关键签名**：`close_socket( : : Socket : )`

#### ② socket_accept_connect — **3 合 1 超级算子**

- **一句话功能**：单次调用同时打开并连接到一个 socket(服务器接受客户端连接 / 客户端连接到服务器)，支持 TCP/UDP 自动探测。
- **HDevelop 关键签名**：`socket_accept_connect( : : WaitFor, Host, Port, Type, Timeout : Socket)`
- **典型用途**：**最常用的 socket 算子**——`socket_accept_connect('accept', '192.168.1.10', 8080, 'TCP', 30)` 服务器端接受 30s 内任意客户端。
- **重点参数**：
  - `WaitFor`(`'accept'`服务器接受 / `'connect'`客户端连接)；
  - `Host`(服务器 IP / 客户端写服务器 IP)；
  - `Port`(1-65535 端口号)；
  - `Type`(`'TCP'`可靠连接 / `'UDP'`无连接报);
  - `Timeout`(秒) — DNS 查询 + 握手总超时。
- **注意**：它替代了 `open_socket_accept` + `open_socket_connect` 两个,推荐任意场景上**默认用它**。

### ③ 4.2 服务端/客户端分别模式(2 ops，已被 ② 取代)

#### ① open_socket_accept — 服务端专用

- **一句话功能**：服务端被动接受客户端 socket 连接(主战版,`socket_accept_connect` 内部调用它)。
- **HDevelop 关键签名**：`open_socket_accept( : : Host, Port, Type, Timeout : Socket)`
- **使用建议**：能调 `socket_accept_connect` 就不要用这一个(后者代码更繁而不安全)。

#### ② open_socket_connect — 客户端专用

- **一句话功能**：客户端主动向远端服务器发起 socket 连接(主战版,`socket_accept_connect` 内部调用它)。
- **HDevelop 关键签名**：`open_socket_connect( : : Host, Port, Type, Timeout : Socket)`
- **使用建议**：同上,用 `socket_accept_connect` 代替。

### ④ 4.3 参数调节(2 ops)

#### ① set_socket_param

- **一句话功能**：设置 socket 泛型参数(`'timeout'`/`'address_info'`/`'SO_SNDBUF'`/`'SO_RCVBUF'`/`'SO_BROADCAST'`/`'TCP_NODELAY'`)。
- **HDevelop 关键签名**：`set_socket_param( : : Socket, GenParamName, GenParamValue : )`
- **典型用途**：解决粘包 —— `set_socket_param(S, 'TCP_NODELAY', 'true')` 关 Nagle 算法; 调整 buffer —— `set_socket_param(S, 'SO_RCVBUF', 1048576)`。

#### ② get_socket_param

- **一句话功能**：查询 socket 当前参数值。
- **HDevelop 关键签名**：`get_socket_param( : : Socket, GenParamName : GenParamValue)`

### ⑤ 4.4 OS 级集成(2 ops)

#### ① get_socket_descriptor

- **一句话功能**：返回底层 OS socket 描述符(int 整数)——用于接入系统调用如 `select`/`poll`。
- **HDevelop 关键签名**：`get_socket_descriptor( : : Socket : SocketDescriptor)`
- **典型用途**：**HDevelop `try/catch` + Python 协同** ——PYTHON 拿到 fd 后用 `selectors`/第三方服务接入。

#### ② get_next_socket_data_type

- **一句话功能**：预查询 socket 上**下一条数据的数据类型**而不真读。
- **HDevelop 关键签名**：`get_next_socket_data_type( : : Socket : DataType)`
- **返回值**：`'image'` / `'region'` / `'xld'` / `'tuple'` / `'serialized_item'` 等。
- **典型用途**：处理多类型交互协议 —— 远端发来混合数据时,先 `get_next_socket_data_type` 判断类型再选对的 `receive_*`。

### ⑥ 4.5 发送算子 (5 ops)

#### ① send_data

- **一句话功能**：发送 tuple of int(字节流)到 socket 另一端。
- **HDevelop 关键签名**：`send_data( : : Socket, Data : )`
- **典型用途**：发送控制指令字节流 —— `send_data(S, [0x01, 0x02, 0x03])`。

#### ② send_image

- **一句话功能**：发送 Image 对象(HALCON 三种像素任意)到 socket。
- **HDevelop 关键签名**：`send_image( : : Image : Socket)`
- **典型用途**：相机流分发到云端,边缘计算上传图像。
- **注意**：网络带宽杀手 — 800×600 单字节图像单帧 480KB,1s 30 帧 = 14MB/s;双字节 28MB/s。

#### ③ send_region

- **一句话功能**：发送 Region 到 socket(对应 Python/HDevelop 远端 `receive_region`)。
- **HDevelop 关键签名**：`send_region( : : Region : Socket)`

#### ④ send_xld

- **一句话功能**：发送 XLD 轮廓到 socket(亚像素边缘/线条/圆环)。
- **HDevelop 关键签名**：`send_xld( : : XLD : Socket)`

#### ⑤ send_tuple

- **一句话功能**：发送任意 tuple(string/number/整数组)到 socket。
- **HDevelop 关键签名**：`send_tuple( : : Tuple : Socket)`

### ⑦ 4.6 发送序列化项 (1 op)

#### ① send_serialized_item

- **一句话功能**：发送 SerializedItemHandle 到 socket(本质送带型号的二进制)。
- **HDevelop 关键签名**：`send_serialized_item( : : Socket, SerializedItemHandle : )`
- **典型用途**：**把整个 OCR 训练模型/MVTec DL 模型打包串送到远端**, 这个是`fread/fwrite_serialized_item`（文件）的网络版。

### ⑧ 4.7 接收算子(7 ops 与上面发送对称)

| 接收 | 类型 | 对应发送 |
| --- | --- | --- |
| ① receive_data | 字节 | send_data |
| ② receive_image | Image | send_image |
| ③ receive_region | Region | send_region |
| ④ receive_serialized_item | 序列化项 | send_serialized_item |
| ⑤ receive_tuple | 任意 tuple | send_tuple |
| ⑥ receive_xld | XLD | send_xld |
| ⑦ socket_accept_connect | 3 合 1 启连接 | — |

所有 receive 共享同一签名模板：`receive_X( : : Socket : X)`，**socket 参数在输入侧**(发送则在输出侧,不要写反!)

---

## 附录 A:技术深度

### A1. TCP/UDP 本质差异表

| 维度 | TCP | UDP |
| --- | --- | --- |
| 连接 | 三次握手 ✓ | 无连接 ✗ |
| 可靠性 | 确认 + 重传 ✓ | 丢包 ✗ |
| 顺序 | 保证 ✓ | 不保证 ✗ |
| 拥塞控制 | 有 ✓ | 无 ✗ |
| 适用场景 | 图像同步 | 实时视频流/直播/命令 |
| HALCON 中 `'Type'` | `'TCP'` | `'UDP'` |
| data 粒度 | 流式 / 报文式 | 仅报文式 |

### A2. socket 与串口选择指南

| 需求 | 选什么 | HALCON 算子路径 |
| --- | --- | --- |
| 与相机/扫码枪(RS232) 通信 | 串口 | `open_serial` + `read/write` + `set/get_serial_param` |
| 工控机交互(PLC Modbus TCP) | socket | `socket_accept_connect` + `send_data/receive_data` |
| 两机共享图像(300MB 批处理) | socket + TCP | `send_image/receive_image`(考虑压缩 4x) |
| 多机协同训练 OCR 模型 | socket + Serialized | `serialize_*` + `send/receive_serialized_item` |
| 实时视频/主观质量 | socket + UDP | `socket_accept_connect(..., 'UDP')` + send/receive_image |

### A3. socket_param 六参数详解

| 参数 | 类型 | 默认 | 作用 |
| --- | --- | --- | --- |
| `'timeout'` | int ms | 5000 | IO 超时 |
| `'address_info'` | tuple | — | 远端地址(只读) |
| `'SO_SNDBUF'` | int byte | 8192 | 发送缓冲区 |
| `'SO_RCVBUF'` | int byte | 8192 | 接收缓冲区 |
| `'SO_BROADCAST'` | bool | false | 允许广播(UDP 必需) |
| `'TCP_NODELAY'` | bool | false | 关 Nagle 算法 |

### A4. SerIt 与 send 组合 5 大妙用

| 妙用 | 路径 |
| --- | --- |
| 跨机同步训练模型 | `train_class_*` → `serialize_*_handle` → `send_serialized_item` |
| 训练库跨网络同步 | `create_class_*` + `add_sample_*` → `serialize_*` → `send_serialized_item` |
| 推断结果拼包上行 | `(ok, score) → tuple` → `create_serialized_item_ptr` → `send_serialized_item` |
| 实时指令下行 | `send_data(S, [cmd, arg1, arg2])` |
| 实时状态上行 | `serialize_*` → `send_serialized_item` |

### A5. 生产部署 "网络三大铁律"

| 铁律 | 详情 |
| --- | --- |
| 1) TCP 必关 Nagle | `set_socket_param(S, 'TCP_NODELAY', 'true')` |
| 2) UDP 必开广播 | `set_socket_param(S, 'SO_BROADCAST', 'true')` |
| 3) 错位协议专清 | `read_serial` 后换发送协议必 `clear_serial` |

### A6. 调试 6 步套路

| 步骤 | 操作 |
| --- | --- |
| 1 | `socket_accept_connect('connect', '127.0.0.1', 8080, 'TCP', 30)` |
| 2 | `set_socket_param(S, 'timeout', 5000)` |
| 3 | 试 `send_data(S, [1,2,3])` 发包 |
| 4 | `receive_data(S, data)` 接包 |
| 5 | `set_check('all')` + `set_operator_timeout('receive_data', 3, 'cancel')` 抓错 |
| 6 | 看 `get_socket_descriptor(S)` 是 fd 拿系统调用看网络环 |

---

## 附录 B:与其它章节的关联映射

| 关联章节 | 关系 | 例子 |
| --- | --- | --- |
| Ch13 Deep Learning | 同用 `send_serialized_item` 傳送训练后的 DL model | Ch13 `train_dl_model` → 下行 到负责面 CLIP/CNN |
| Ch15/16/17/18/19/20 | 跨机推理结果集 | Ch16 测量后 `serialize_*` → `send_serialized_item` |
| Ch22 Regions | 上卷 `set_system` 并行数量会影响本卷所有多路 socket 性能 | 16 socket 同时接 16 个 region,开 CPU=8 · socket_num=16 AOP |
| Ch23 Segmentation | 本类使用同 1 个 socket 接 + 1 个 CH13 DL-CNN 模型接 | main sys or edge classifier same socket 上 stream |
| Ch24 上卷 | `set_system`总开关 加上本下卷 `set_operator_timeout` 是生产的2个安全阀 | 所有 socket/serial 必须搭配 set_operator_timeout + set_check('none') |
| 其它语言 | socket 同一 socket 可以远端接 Python `socket.recv/send` | 限 `receive_data` 发 byte stream |

---

## 总计与上下文

- **总计算子**:36
- **所在章节**:第 24 章 System  下卷
- **业务主线**:**分布式系统篇 (HALCON 与外界通信的所有面:算子超时+串口+序列化+套接字)**
- **前言**:HALCON 中用于联机通信的四种完全对外接口,补上这个卷, HALCON 能与 Python/C++/PHP/Java 进 C89 socket 收发
- **全文总计**:从 Ch01 累计跨章总计 17 卷 728 ops
- **下期预告**:Ch25 Tools / Image Acquisitation 跟其它半天这一卷三都接上
