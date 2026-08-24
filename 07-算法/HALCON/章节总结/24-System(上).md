# 第 24 章 System · 上卷：本地系统资源（47 算子 · 5 子族）

> **HALCON 官方手册第 24 章 System** 全章 12 子族 133 算子，是 HALCON 的"**操作系统与硬件接口**"层——上接应用算法（Ch11~Ch23），下接物理设备（GPU/相机/PLC/磁盘/网络）。  
> **上卷 5 子族 47 算子** = 计算设备 + 数据库 + 错误处理 + I/O 设备 + 元信息——"**本地系统资源管理**"：算子怎么跑在 GPU 上、错误怎么追、PLC 怎么控制、反射元数据怎么查。  
> 一句话总结：**本卷的本质 = HALCON 与外部世界（硬件 + 数据 + 错误）打交道的"系统调用"**。

---

## 1. 全卷结构：5 子族总览

| 子族 | 算子数 | 一句话功能 | 典型场景 |
|---|---|---|---|
| **① 计算设备** | 11 | GPU/OpenCL/CPU 设备枚举、激活、参数读写、释放 | 深度学习加速、多核并行 |
| **② 数据库** | 3 | 元组关系计数、模块列表、对象库重置 | 调试、数据归档清理 |
| **③ 错误处理** | 7 | 检查模式、错误码查询、spy 调试 | 异常捕获、离线调试 |
| **④ I/O 设备** | 15 | 工业 IO（PLC/串口卡/数字 IO）的开/关/控/读写 | 触发拍照、PLC 信号交互 |
| **⑤ 元信息** | 11 | 算子/章/参数/关键字的反射元数据查询 | 动态代码生成、IDE 集成 |

**与下卷的分工**：
- **上卷** = "**本地**"资源（计算设备、错误、IO、元信息都是单机/进程内）
- **下卷**（待做） = "**分布式**"资源（Multithreading 38、Parallelization 6、Sockets 22——多线程/并行/网络）

---

## 2. 5 子族分述（详细模式）

### ① 计算设备（Compute Devices，11 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **query_available_compute_devices** | 枚举所有可用计算设备 · `query_available_compute_devices(: : : DeviceIdentifier)` |
| **open_compute_device** | 按 ID 打开指定设备 · `open_compute_device(: : DeviceIdentifier : DeviceHandle)` |
| **init_compute_device** | 初始化（预热 + 加载算子） · `init_compute_device(: : DeviceHandle, Operators :)` |
| **activate_compute_device** | 设为活动设备（之后算子走 GPU） · `activate_compute_device(: : DeviceHandle :)` |
| **get_compute_device_info** | 读设备信息（名称、内存、算力） · `get_compute_device_info(: : DeviceIdentifier, InfoName : Info)` |
| **get_compute_device_param** | 读设备参数 · `get_compute_device_param(: : DeviceHandle, GenParamName : GenParamValue)` |
| **set_compute_device_param** | 写设备参数 · `set_compute_device_param(: : DeviceHandle, GenParamName, GenParamValue :)` |
| **release_compute_device** | 释放指定设备 · `release_compute_device(: : DeviceHandle :)` |
| **deactivate_compute_device** | 停用指定设备（切回 CPU） · `deactivate_compute_device(: : DeviceHandle :)` |
| **release_all_compute_devices** | 释放所有设备 · `release_all_compute_devices(: : :)` |
| **deactivate_all_compute_devices** | 停用所有设备 · `deactivate_all_compute_devices(: : :)` |

**用途**：
- **HALCON 的 GPU 加速机制**——`open → init → activate` 三步把后续算子（深度学习、形态学、FFT）卸载到 GPU。
- **典型用户**：跑 Deep OCR、Deep Counting、3D Matching 时强制激活 GPU，CPU 上要慢 10~50 倍。
- **`query_available_compute_devices` 是入口**——返回 4 类 ID（'cpu', 'gpu', 'opencl', 'cuda'）。

**重点参数**：
- `init_compute_device` 的 `Operators` 是字符串列表，指定**预加载哪些算子**到设备——空列表只预热通用库。
- `set_compute_device_param` 的 `GenParamName` ∈ {'memory_limit', 'cache_size', 'parallelism', ...}。
- `get_compute_device_info` 的 `InfoName` ∈ {'name', 'vendor', 'version', 'memory', 'compute_capability'}。

**误区**：
- ⚠️ **必须 `open` → `init` → `activate` 顺序**——直接 `activate` 未打开的设备句柄会崩溃。
- ⚠️ **深度学习算子（Ch13）**才会真正用 GPU；**传统算子**（形态学、阈值）即使激活 GPU 也是 CPU 执行（HALCON 没优化）。
- ⚠️ 多卡系统一次只能激活一个设备为"主"——并行多卡需用 `init_compute_device` 多次初始化。
- ⚠️ `release_all_compute_devices` 强制释放**所有**设备——若其他程序正在用会卡住，慎用于生产。

### ② 数据库（Database，3 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **count_relation** | 统计指定关系名在对象数据库中的元组数 · `count_relation(: : RelationName : NumOfTuples)` |
| **get_modules** | 列出已加载的所有模块（功能包） · `get_modules(: : : UsedModules, ModuleKey)` |
| **reset_obj_db** | 重置对象数据库到默认大小 · `reset_obj_db(: : DefaultImageWidth, DefaultImageHeight, DefaultChannels :)` |

**用途**：
- **HALCON 内部维护一个"对象数据库"**——所有创建的对象（Region/XLD/Image/Handle）都在里面登记，释放时回收到池里。
- **`get_modules` 是授权检查**——列出当前 HALCON 实例加载了哪些功能包（OCR/3D/Deep Learning 等），可检测授权是否完整。
- **`reset_obj_db` 是大程序启动时的"清场"**——避免前一次运行的残留对象影响本轮。

**重点参数**：
- `reset_obj_db` 的三个参数是**对象数据库的默认参数**——新创建对象若没指定尺寸就用这组。
- `get_modules` 的 `UsedModules` 包含模块名（如 `'halcon','halcon_ocr'`），`ModuleKey` 是对应 License Key（私有）。

**误区**：
- ⚠️ `reset_obj_db` 不会**清空已创建对象**——只是重置数据库元数据；清空需 `clear_*` 各类型。
- ⚠️ `get_modules` 的 `ModuleKey` 返回值是**加密字符串**，不是 license 本身——不能直接拼接到 license 文件。
- ⚠️ `count_relation` 的 `RelationName` 必须是已注册关系名——自定义关系需用 HDevelop 的 `insert_*` 算子族（Ch21 Object）。

### ③ 错误处理（Error Handling，7 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **get_check** | 读取检查模式（'none'/'input'/'all'） · `get_check(: : : Check)` |
| **set_check** | 设置检查模式（控制参数校验严格度） · `set_check(: : Check :)` |
| **get_error_text** | 错误码 → 错误信息字符串 · `get_error_text(: : ErrorCode : ErrorMessage)` |
| **get_extended_error_info** | 取最近一次错误的扩展信息（算子名+错误码+消息） · `get_extended_error_info(: : : OperatorName, ErrorCode, ErrorMessage)` |
| **get_spy** | 读 spy 类别的当前值（调试用） · `get_spy(: : Class : Value)` |
| **query_spy** | 列出所有 spy 类别及当前值 · `query_spy(: : : Classes, Values)` |
| **set_spy** | 设置 spy 类别的值（埋点监控） · `set_spy(: : Class, Value :)` |

**用途**：
- **`set_check('all')` 是"严苛模式"**——所有算子都对输入做完整性检查，违反就抛 `HException`；生产环境关闭，调试时打开。
- **`get_extended_error_info` 是 HDevelop 异常处理的核心**——`try/catch` 块里调用它能拿到完整错误三件套（哪个算子、什么错、消息）。
- **`set_spy` / `get_spy` 是 HALCON 的"性能 profiler"**——spy 算子能监控运行时间、内存、算子调用次数等。

**重点参数**：
- `set_check` 的 `Check` ∈ {'none'（最不严）, 'input'（检查输入）, 'all'（最严）}。
- `set_spy` 的 `Class` 是 spy 类别名（如 `'moms_obj_mem_used'`, `'mom_used_time'`, `'cputime'`, `'num_proc_threads'`）——全部类别由 `query_spy` 枚举。

**误区**：
- ⚠️ `set_check('all')` 严重拖慢速度（5~30%）——**生产代码永远用 'none'**，仅调试用。
- ⚠️ `get_extended_error_info` 返回的是**最近一次错误**——若两次异常间没出错，缓存被清空，返回空字符串。
- ⚠️ `set_spy` 的 `'cputime'` 等于"自 HALCON 启动以来的总 CPU 时间"——非本次调用时长；要看"某算子耗时"需 HDevelop 的 `dev_*_time` 或 `get_check_time`。
- ⚠️ HDevelop 调试器**自己**用 `set_spy` 监控算子——你设的 spy 会和 HDevelop 冲突，记得用完 `set_spy(Class, '')` 清掉。

### ④ I/O 设备（I/O Devices，15 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **open_io_device** | 打开 IO 设备（PLC/串口卡/数字 IO 板） · `open_io_device(: : IOInterfaceName, IODeviceName, GenParamName, GenParamValue : IODeviceHandle)` |
| **close_io_device** | 关闭 IO 设备 · `close_io_device(: : IODeviceHandle :)` |
| **query_io_interface** | 枚举 IO 接口（'modbus', 'opc_ua', 'digital_io'...） · `query_io_interface(: : IOInterfaceName, Query : Result)` |
| **query_io_device** | 枚举指定接口的设备 · `query_io_device(: : IODeviceHandle, IOChannelName, Query : Result)` |
| **open_io_channel** | 打开 IO 通道（设备内的子地址） · `open_io_channel(: : IODeviceHandle, IOChannelName, GenParamName, GenParamValue : IOChannelHandle)` |
| **close_io_channel** | 关闭 IO 通道 · `close_io_channel(: : IOChannelHandle :)` |
| **read_io_channel** | 读通道（位/字节/字） · `read_io_channel(: : IOChannelHandle : Value, Status)` |
| **write_io_channel** | 写通道 · `write_io_channel(: : IOChannelHandle, Value : Status)` |
| **control_io_device** | 设备级控制（启动/停止/复位） · `control_io_device(: : IODeviceHandle, Action, Argument : Result)` |
| **control_io_channel** | 通道级控制 · `control_io_channel(: : IOChannelHandle, ParamAction, ParamArgument : GenParamValue)` |
| **control_io_interface** | 接口级控制 · `control_io_interface(: : IOInterfaceName, Action, Argument : Result)` |
| **get_io_device_param** | 读设备参数 · `get_io_device_param(: : IODeviceHandle, GenParamName : GenParamValue)` |
| **set_io_device_param** | 写设备参数 · `set_io_device_param(: : IODeviceHandle, GenParamName, GenParamValue :)` |
| **get_io_channel_param** | 读通道参数 · `get_io_channel_param(: : IOChannelHandle, GenParamName : GenParamValue)` |
| **set_io_channel_param** | 写通道参数 · `set_io_channel_param(: : IOChannelHandle, GenParamName, GenParamValue :)` |

**用途**：
- **HALCON 的 IO 设备是"工业 4.0 的瑞士军刀"**——支持 Modbus TCP/RTU、OPC UA、EtherCAT、Profibus、数字 IO 卡、串口卡等 20+ 协议。
- **典型工业流程**：
  1. **触发拍照**：相机发 trigger 信号 → PLC 接收 → 触发 HALCON 拍照（用 `read_io_channel` 检测 trigger 线）
  2. **结果输出**：HALCON 检测完成 → `write_io_channel` 给 PLC 发 OK/NG 信号
  3. **配方切换**：`set_io_channel_param` 把新配方号写到 PLC
- **三层架构**：`Interface`（协议）→ `Device`（物理设备）→ `Channel`（设备内的子地址）——一个 Device 可有多个 Channel。

**重点参数**：
- `open_io_device` 的 `IOInterfaceName` ∈ {'modbus', 'modbus_tcp', 'opc_ua', 'ethernetip', 'profinet', 'digital_io', 'serial', ...}。
- `write_io_channel` 的 `Value` 类型随 `GenParamName('io_direction')` 而定——`'output'` 才能写。
- `control_io_*` 的 `Action` 是字符串指令（设备/接口特定）——具体看 HALCON 文档的 IO 协议表。

**误区**：
- ⚠️ **必须 `open_io_device` 后才能 `open_io_channel`**——channel 是 device 的子资源。
- ⚠️ `read_io_channel` 的 `Status` 是**硬件状态**（如 'success', 'timeout', 'crc_error'）——**不是值**。
- ⚠️ **Modbus 地址 HALCON 用 1-based**（`ModbusAddr=1` 是协议里 0 那个）——与 PLC 工程师约定 0-based 时会差 1。
- ⚠️ `set_io_channel_param` 的 `GenParamName` ≠ 物理信号名——是 HALCON 抽象（'baud_rate', 'parity', 'timeout_ms'）。
- ⚠️ **`control_io_device` 的 `Action` 各协议不同**——Modbus 没 Action，OPC UA 的 'subscribe'/'unsubscribe' 仅 OPC UA 有。

### ⑤ 元信息（Information，11 算子）

| 算子 | 一句话功能 · HDevelop 关键签名 |
|---|---|
| **get_chapter_info** | 查章号（按算子名） · `get_chapter_info(: : Chapter : Info)` |
| **get_operator_name** | 模糊匹配算子名（支持通配符） · `get_operator_name(: : Pattern : OperatorNames)` |
| **get_operator_info** | 查算子文档片段 · `get_operator_info(: : OperatorName, Slot : Information)` |
| **search_operator** | 按关键字搜索算子 · `search_operator(: : Keyword : OperatorNames)` |
| **get_param_names** | 查算子的参数名（4 类：输入/输出对象/控制参数） · `get_param_names(: : OperatorName : InpObjPar, OutpObjPar, InpCtrlPar, OutpCtrlPar)` |
| **get_param_num** | 查算子参数数量 · `get_param_num(: : OperatorName : CName, InpObjPar, OutpObjPar, InpCtrlPar, OutpCtrlPar)` |
| **get_param_info** | 查参数信息（类型/含义/默认值） · `get_param_info(: : OperatorName, ParamName, Slot : Information)` |
| **get_param_types** | 查控制参数类型 · `get_param_types(: : OperatorName : InpCtrlParType, OutpCtrlParType)` |
| **get_keywords** | 查算子的关键字（用于搜索） · `get_keywords(: : OperatorName : Keywords)` |
| **query_operator_info** | 查算子可查询信息字段列表 · `query_operator_info(: : : Slots)` |
| **query_param_info** | 查参数可查询信息字段列表 · `query_param_info(: : : Slots)` |

**用途**：
- **HALCON 的反射元数据（Reflection）是 IDE 和代码生成器的基础**——HDevelop 的算子帮助面板、Python/.NET binding 自动生成、ML 选算子，全靠这 11 个算子。
- **`get_operator_name('threshold*')`** 返回所有 threshold 开头的算子——`'*'` 通配符支持 `?`（单字符）和 `*`（任意）。
- **`get_param_info(op, 'MinGray', 'default')`** 查默认参数值——动态生成调用代码的利器。
- **`get_chapter_info('Region')`** 知道 'Region' 在第 22 章。

**重点参数**：
- `get_operator_name` 的 `Pattern` 支持通配符 `*`/`?`——`'*threshold*'` 匹配所有含 threshold 的算子。
- `get_param_info` 的 `Slot` ∈ {'description', 'type', 'default', 'range', 'multivalued', 'optional', 'value_list'}。
- `get_param_names` 的 4 类参数对应 HALCON 签名四列：`(Input Objects : Output Objects : Input Control : Output Control)`。
- `search_operator` 的 `Keyword` 不区分大小写，支持中文（HALCON 算子关键字含英中对照）。

**误区**：
- ⚠️ `get_param_names` 返回的**不是签名字符串**——是 4 个独立元组（每个参数名一个）。
- ⚠️ `get_param_info` 的 `Slot='default'` 对**必填参数**返回空字符串（HALCON 无默认）。
- ⚠️ `get_operator_name('*')` 一次返回**全部 1900+ 算子**——内存可能占 100+MB，慎用。
- ⚠️ `query_operator_info` 返回的 Slots 列表是**整章一致的**——所有算子都用同一套 Slot 名。

---

## 3. 关键技术要点

### 3.1 GPU 加速的"3+1 步套路"

```
query_available_compute_devices(: DeviceIdentifier)        * 查设备
open_compute_device(: DeviceIdentifier : DeviceHandle)     * 打开
init_compute_device(: DeviceHandle, 'all' :)                * 初始化（预热所有算子）
activate_compute_device(: DeviceHandle :)                   * 激活（之后算子走 GPU）
```

**释放时反向**：`deactivate → release → close`（或用 `release_all_compute_devices` 一键全释放）。

### 3.2 PLC 交互的"5 步套路"

```
open_io_device('modbus', '192.168.1.10:502', [], [] : DeviceHandle)   * 开设备
open_io_channel(DeviceHandle, 'ModbusAddr=0', 'io_direction', 'output' : ChHandle) * 开通道
* 业务循环
read_io_channel(TriggerCh : TriggerValue, Status)        * 监听 trigger
if (TriggerValue == 1)
    grab_image(Image, AcqHandle)
    * ... 检测 ...
    write_io_channel(ResultCh, 1 : Status)                * 输出 OK
endif
close_io_channel(ChHandle)
close_io_device(DeviceHandle)
```

### 3.3 错误处理的"3 段式"

```
set_check('none')                                         * 生产：关检查
dev_set_check('~input')                                   * HDevelop 调试开 'input'
try
    * 业务
catch (Exception)
    get_extended_error_info(: : OpName, ErrCode, ErrMsg)
    * 记日志 / 上报
endtry
```

**核心**：`get_extended_error_info` 是 `catch` 块里的"主战武器"。

### 3.4 反射元数据的"4 层查询"

| 需求 | 用什么 |
|---|---|
| 列算子 | `get_operator_name('*')` |
| 找算子 | `search_operator('threshold')` |
| 查算子元数据 | `get_operator_info(op, 'purpose')` |
| 查参数元数据 | `get_param_info(op, param, 'type')` |
| 算子在第几章 | `get_chapter_info(op)` |

### 3.5 spy 调试的"3 件套"

| spy 类 | 用途 |
|---|---|
| `'cputime'` | 累计 CPU 时间 |
| `'moms_obj_mem_used'` | 内存占用 |
| `'num_proc_threads'` | 进程线程数 |

**用法**：`set_spy('cputime', '') → 跑一段 → get_spy('cputime' : Time)` 测时间。

### 3.6 IO 设备的三层架构

```
Interface (协议层)        Device (物理设备)        Channel (子地址)
├── Modbus                ├── 192.168.1.10:502     ├── ModbusAddr=0 (输入 register)
├── OPC UA                ├── 192.168.1.20:4840    ├── ModbusAddr=100 (输出线圈)
├── EtherNet/IP           ├── /dev/ttyUSB0          ├── ...
└── digital_io            └── PCI card #1
```

**一个 Device = 一个物理/逻辑设备**；**一个 Channel = 该设备上的一个数据点**（PLC 的一个 register/coil、串口的一个端点）。

---

## 4. 流水线定位

```
[应用层] → [Ch11~Ch23 算法算子] → 【本卷:本地系统资源管理】
                                      ↓
        ┌──────────────────────┬──────────────────┬──────────────────┐
        ↓                      ↓                  ↓                  ↓
[硬件层] GPU/PLC/触发线    [调试层] spy/检查    [元数据层] 反射    [存储层] 数据库
```

**本卷是 HALCON 的"**系统调用层**"**——是算法与物理世界（硬件 + 错误 + 元数据）打交道的"最后一公里"。

---

## 5. 与其它章节的关联

- **Ch13 Deep Learning**：`activate_compute_device` 后，深度学习推理会自动走 GPU，CPU 慢 10~50x。
- **Ch20 OCR**：`read_io_channel` 监听相机 trigger；`write_io_channel` 输出 OK/NG 到 PLC。
- **Ch16 Inspection**：`set_check('all')` 仅在 HDevelop 调试时开，生产的 C++/Python 绑定全是 'none'。
- **Ch21 Object**：`count_relation`/`get_modules` 与 Ch21 `count_obj`/`get_obj_class` 是不同层级——前者管元数据，后者管对象。
- **Ch25 Calibration**：相机的工业接口配置常需 `set_io_device_param` 设硬件触发模式。
- **下卷 Multithreading/Sockets**：本卷 IO 设备是"单进程序列交互"，下卷网络 IO 才是"分布式通信"。

---

## 6. 5 子族算子速查表

| 子族 | 算子（按功能顺序） |
|---|---|
| ① 计算设备 | query_available_compute_devices、open_compute_device、init_compute_device、activate_compute_device、get_compute_device_info、get_compute_device_param、set_compute_device_param、release_compute_device、deactivate_compute_device、release_all_compute_devices、deactivate_all_compute_devices |
| ② 数据库 | count_relation、get_modules、reset_obj_db |
| ③ 错误处理 | get_check、set_check、get_error_text、get_extended_error_info、get_spy、query_spy、set_spy |
| ④ I/O 设备 | open_io_device、close_io_device、query_io_interface、query_io_device、open_io_channel、close_io_channel、read_io_channel、write_io_channel、control_io_device、control_io_channel、control_io_interface、get_io_device_param、set_io_device_param、get_io_channel_param、set_io_channel_param |
| ⑤ 元信息 | get_chapter_info、get_operator_name、get_operator_info、search_operator、get_param_names、get_param_num、get_param_info、get_param_types、get_keywords、query_operator_info、query_param_info |

> **下卷预告**：第 24 章 System **下卷** = 7 子族 86 算子（Multithreading 38 + Operating System 4 + Parallelization 6 + Parameters 4 + Serial 7 + Serialized Item 5 + Sockets 22）——主题"**多线程/并行化/网络通信**"，HALCON 的"分布式系统"层。
