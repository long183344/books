# 第 24 章 System·中卷 — 多线程 + 操作系统 + 自动算子并行化 + 参数控制

> HALCON 官方 Reference 第 24 章 System 的**中卷**,覆盖**4 子族 52 算子**,主题是"**让 HALCON 用满 CPU,不出错地跑完**"——多线程同步原语、操作系统时间/调用、自动算子并行化（AOP）、算子超时控制。

---

## 📌 一、章节定位与切片逻辑

| 卷 | 子族 | ops | 主题 |
|:---:|:---|:---:|:---|
| 上卷 | 5 子族 | 47 | **本地系统资源** — 计算设备 + 数据库 + 错误处理 + IO 设备 + 元信息 |
| **中卷**(本卷) | **4 子族** | **52** | **多线程 + 操作系统 + 并行化 + 参数** — "**让 HALCON 用满 CPU 跑完不超时**" |
| 下卷 | 4 子族 | 34 | **分布式系统** — 串口 + 序列化 + 套接字 + 串口 24 ops + 序列化 9 + 串口 11(=44 待对账) |

---

## 二、本卷 4 子族 52 算子 速查矩阵

### ① Multithreading 多线程同步(38 ops)⭐⭐⭐

HALCON 程序典型架构:1 主线程 + N 工作线程。本族提供 7 大类原语:mutex / condition / event / barrier / message / message_queue / 等待查询。

#### A. 互斥锁 mutex(7 ops)

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `create_mutex` | `create_mutex( : : AttribName, AttribValue : MutexHandle)` | 创建互斥锁 |
| `lock_mutex` | `lock_mutex( : : MutexHandle : )` | 加锁(阻塞直到获得) |
| `try_lock_mutex` | `try_lock_mutex( : : MutexHandle : Busy)` | 尝试加锁(非阻塞,返回 Busy) |
| `unlock_mutex` | `unlock_mutex( : : MutexHandle : )` | 释放锁 |
| `clear_mutex` | `clear_mutex( : : MutexHandle : )` | 销毁互斥锁 |
| `get_mutex_var` 配套 | — | (Ch18 矩阵操作共享变量) |

#### B. 条件变量 condition(4 ops)

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `create_condition` | `create_condition( : : AttribName, AttribValue : ConditionHandle)` | 创建条件变量 |
| `signal_condition` | `signal_condition( : : ConditionHandle : )` | 唤醒**一个**等待者 |
| `broadcast_condition` | `broadcast_condition( : : ConditionHandle : )` | 唤醒**所有**等待者 |
| `clear_condition` | `clear_condition( : : ConditionHandle : )` | 销毁条件变量 |
| `wait_condition` | `wait_condition( : : ConditionHandle, MutexHandle : )` | 释放 mutex + 阻塞等待 + 重新锁(标准三步原子) |
| `timed_wait_condition` | `timed_wait_condition( : : ConditionHandle, MutexHandle, Timeout : TimedOut)` | 带超时的 wait_condition |

#### C. 事件 event(4 ops)

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `create_event` | `create_event( : : AttribName, AttribValue : EventHandle)` | 创建事件(可自动/手动复位) |
| `signal_event` | `signal_event( : : EventHandle : )` | 触发事件 |
| `wait_event` | `wait_event( : : EventHandle : )` | 阻塞等待事件触发 |
| `try_wait_event` | `try_wait_event( : : EventHandle : IsSet)` | 非阻塞查询是否已触发 |
| `clear_event` | `clear_event( : : EventHandle : )` | 销毁事件 |

#### D. 屏障 barrier(3 ops)

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `create_barrier` | `create_barrier( : : AttribName, AttribValue, TeamSize : BarrierHandle)` | 创建 TeamSize 人屏障 |
| `wait_barrier` | `wait_barrier( : : BarrierHandle : )` | 阻塞直到 TeamSize 个线程全部到达 |
| `clear_barrier` | `clear_barrier( : : BarrierHandle : )` | 销毁屏障 |

#### E. 单条消息 message(6 ops)

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `create_message` | `create_message( : : GenParamName, GenParamValue : MessageHandle)` | 创建消息 |
| `set_message_tuple` | `set_message_tuple( : : MessageHandle, MessageData : )` | 设元组数据 |
| `get_message_tuple` | `get_message_tuple( : : MessageHandle : MessageData)` | 取元组数据 |
| `set_message_obj` | `set_message_obj( : : MessageHandle, MessageData : )` | 设 iconic 对象(图、区域、XLD) |
| `get_message_obj` | `get_message_obj( : : MessageHandle : MessageData)` | 取 iconic 对象 |
| `set_message_param` | `set_message_param( : : MessageHandle, GenParamName, GenParamValue : )` | 设消息属性 |
| `get_message_param` | `get_message_param( : : MessageHandle, GenParamName : GenParamValue)` | 取消息属性 |
| `clear_message` | `clear_message( : : MessageHandle : )` | 销毁消息 |

#### F. 消息队列 message_queue(10 ops)⭐

线程间异步通信:**生产者 enqueue → 消费者 dequeue**,可装任意 Htuple 或 iconic。

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `create_message_queue` | `create_message_queue( : : QueueName : QueueHandle)` | 创建命名消息队列 |
| `enqueue_message` | `enqueue_message( : : QueueHandle, MessageHandle, IsMessageCopy : )` | 入队(可拷贝或不拷贝消息) |
| `dequeue_message` | `dequeue_message( : : QueueHandle : MessageHandle)` | 出队(阻塞) |
| `read_message` | `read_message( : : QueueHandle, MessageHandle, IsMessageCopy : )` | 不出队只读队首 |
| `write_message` | `write_message( : : QueueHandle, MessageHandle, IsMessageCopy : )` | 写入队尾(等价于 enqueue) |
| `set_message_queue_param` | `set_message_queue_param( : : QueueHandle, GenParamName, GenParamValue : )` | 设队列属性(max_size/timeout) |
| `get_message_queue_param` | `get_message_queue_param( : : QueueHandle, GenParamName : GenParamValue)` | 取队列属性 |
| `set_message_param` | `set_message_queue_param`(同上) | — |
| `get_message_param` | — | — |
| `clear_message_queue` | `clear_message_queue( : : QueueHandle : )` | 销毁消息队列 |

#### G. 等待与线程查询(3 ops)

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `wait_condition` | (见 B) | — |
| `timed_wait_condition` | (见 B) | — |
| `get_current_hthread_id` | `get_current_hthread_id( : : : HthreadId)` | 拿当前 HDevelop 内置线程 ID |
| `get_threading_attrib` | `get_threading_attrib( : : Name : Value)` | 读线程属性(thread_num/max_threads 等) |
| `interrupt_operator` | `interrupt_operator( : : OpName : )` | 中断另一个线程中正在执行的某算子(用于超时保护) |

> **关键经验**:`wait_condition` 是"**释放 mutex + 阻塞 + 重新加锁**"三步原子操作,**永远不要**手写这三步(无法原子),HALCON 系统保证原子性。

### ② Operating System 操作系统(4 ops)

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `count_seconds` | `count_seconds( : : : Seconds)` | 自纪元以来的秒数(real,Unix 时间戳) |
| `get_system_time` | `get_system_time( : : : MSecond, Second, Minute, Hour, Day, Month, Year)` | 拆解年月日时分秒 |
| `wait_seconds` | `wait_seconds( : : Seconds : )` | 阻塞当前线程 N 秒 |
| `system_call` | `system_call( : : Command : Output)` | 调外部 shell 并捕获 stdout |

### ③ Parallelization 自动算子并行化 AOP(6 ops)⭐⭐

HALCON 19.11+ 引入 **Automatic Operator Parallelization**:对数组合规算子(`find_shape_model`/`find_text`等)自动并行。

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `query_aop_info` | `query_aop_info( : : : ParallelOperators, DefaultIsParallel, CurrentIsParallel)` | 询问 AOP 当前状态 |
| `set_aop_info` | `set_aop_info( : : OperatorName, IsParallel : )` | **运行时开关**指定算子的并行化 |
| `get_aop_info` | `get_aop_info( : : OperatorName : IsParallel)` | 读取某算子当前 AOP 开关 |
| `optimize_aop` | `optimize_aop( : : : AllResults)` | 在样本数据上**离线评测**各算子的并行收益 |
| `read_aop_knowledge` | `read_aop_knowledge( : : FileName : )` | 从文件载入离线评测结果 |
| `write_aop_knowledge` | `write_aop_knowledge( : : FileName : )` | 把优化结果存盘 |

### ④ Parameters 算子超时控制(4 ops)

| 算子 | 签名 | 一句话功能 |
|---|---|---|
| `set_system` | `set_system( : : SystemParameter, Value : )` | 改全局系统参数(timeout/thread_num 等) |
| `get_system` | `get_system( : : Query : Information)` | 读全局系统参数 |
| `set_operator_timeout` | `set_operator_timeout( : : OperatorName, Timeout, Mode : )` | **单算子粒度**超时控制(生产救星) |
| `get_system_info` | `get_system_info( : : Query : Information)` | 读详细系统信息(GPU/内存/线程数) |

---

## 三、本卷 7 大技术深度

### 1. ⭐ Producer-Consumer 异步队列五件套

经典多线程模板,主线程生产图数据,工作线程消费算法:

```
create_message_queue → loop: enqueue_message → 所有工作线程:dequeue_message → get_message_obj → 算法 → clear
```

**性能要点**:
- 生产速度 >> 消费速度 → `set_message_queue_param(..., 'max_size', 50)` 限流,生产者 enqueue 阻塞
- 队列清零:`clear_message_queue` + 重建更安全(`clear_message` 残留)
- 单个消息生命周期:`create_message → set_* → enqueue → 消费者 get_* → clear_message`

### 2. ⭐ mutex + condition 同步范式(三步原子)

```
* 临界区外
lock_mutex(M)
* 临界区内 共享数据修改
signal_condition(C)  * 唤醒 waiter
unlock_mutex(M)

* Waiter 端
lock_mutex(M)
while not condition_predicate():
    wait_condition(C, M)   * 自动 release_mutex + 阻塞 + re-lock
* 此时 已锁 且 条件成立
unlock_mutex(M)
```

**关键陷阱**:
- `wait_condition` 是**唯一**合法的"放弃 mutex 阻塞"路径;`lock_mutex + while + unlock + wait` 不原子
- `signal_condition` 只唤醒**一个** waiter,若多 waiter 必须用 `broadcast_condition`
- **永远先 lock,再 wait**(wait 内部帮你 unlock);**永远先 signal,再 unlock**(避免唤醒者再拿不到锁)

### 3. ⭐ barrier 三方同步(罕见但精妙)

`create_barrier(..., TeamSize=3, ...)`:
- T1 `wait_barrier` → 阻塞
- T2 `wait_barrier` → 阻塞
- T3 `wait_barrier` → **T1/T2/T3 同时通过**,可启动下一阶段并行

应用场景:**多相机同步采集**(3 个相机线程都采完一帧才一起做后续处理)。一次性的,不可重用。

### 4. ⭐ AOP 自动算子并行化三大决定

**算子能否 AOP** 由 HALCON 内部写死(查询 `query_aop_info.ParallelOperators` 拿名单);**是否真正开启**取决于 3 个开关的**与运算**:

```
最终状态 = 'parallelize_operators'(system) AND get_aop_info(op) AND set_system('parallelize_operators', 'true')
```

- `system('parallelize_operators', 'true')` ← 全局开关
- `set_aop_info(op, 'true')` ← 单算子开关
- **false 默认值问题**:HDevelop IDE 单步调试/算子独立窗口 → AOP 自动关

**生产部署关键 4 步**(确保 100% 发挥算力):
1. `set_system('parallelize_operators', 'true')`
2. 启动批处理(`dev_inspect_ctrl` 必须 OFF)
3. `optimize_aop` 用样本跑一遍,把结果 `write_aop_knowledge` 固化为 `aop_knowledge.ini`
4. `read_aop_knowledge` 在程序入口加载,新会话直接受益

**生态对比**:
- HALCON AOP = 编译器级自动向量化,无需写多线程代码
- 对手 OpenCV = openmp(`cv::setNumThreads`)手动选,粒度粗
- 对手 PCL/Kornia = 不自动并行,GPU 走 CUDA 流

### 5. ⭐ 单算子超时(生产救星)

`set_operator_timeout(OperatorName, Timeout, Mode)` 三参数:
- `OperatorName`:`'*'`(所有算子)/ `'find_shape_model'`(单算子)
- `Timeout`:毫秒,如 5000
- `Mode`:`'cancel'`(取消)/ `'break'`(抛异常)

**生产环境必配**:
```
set_operator_timeout('*', 10000, 'cancel')  * 全局 10 秒熔断
```

**与 `try_*` 配套**:通常配合 `try / catch / endtry` 使用,捕 HDevEngine 抛的 exception。

### 6. ⭐ system_call 谨慎使用

`system_call` 风险:
- **阻塞主线程**(等子进程退出)→ 拖垮 HALCON 实时性
- **无 shell escape** → `'dir; del /f /q'` 类命令注入
- **大输出爆炸** → 内存溢出

**安全用法**:
- `system_call('cmd /c dir "E:\\halcon"', stdout)` 短命令
- 加超时:`wait_seconds` 前切片(粗)
- 真要稳,用 `read_image` + `call_external` 调 DLL,完全绕过 shell

### 7. ⭐ HDevelop 调试与多线程的互不兼容

|HDevelop 状态|AOP|多线程|
|---|---|---|
|IDE 算子窗口|❌|❌|
|IDE 步进 F6|❌|❌|
|`dev_open_window` 一个窗口|✅ 但简化|✅|
|`dev_close_window` + 批处理|✅ 全力|✅|

**生产部署检查清单**(任一不满足 AOP 失效):
- ❌ **HDevelop IDE 不能开**(单步/步进/监视)
- ❌ **不能有打开的算子窗口/变量窗口**
- ✅ **必须** `set_system('parallelize_operators', 'true')`

---

## 四、上中下三卷对照路径图

```
┌─────────────────────────────┐
│  HALCON 视觉处理流水线(简化) │
└──────────────┬──────────────┘
               ▼
        ┌─────────────┐
        │ Ch14/15/17 算法│  ← 训练/特征/匹配
        └──────┬──────┘
               ▼
        ┌─────────────────────────┐
        │ Ch24 System 三卷:       │
        │  上卷:本地资源(本题)     │ ← GPU/DB/IO/Error/Spy
        │  ★中卷:CPU/并行(本卷)   │ ← 线程/AOP/超时
        │  下卷:分布式            │ ← 串口/Socket/序列化
        └─────────────────────────┘
```

**与上卷关联**:
- `set_aop_info` 的算子列表 = `query_available_compute_devices`(GPU)+ `get_threading_attrib`(CPU)
- `set_check`(上卷) + `set_operator_timeout`(本卷) = 两套独立容错机制(参数校验 vs 运行时熔断)

**与下卷预告**:
- `socket_*`(下卷) = 把多线程 + 队列 + AOP 推到网络上的另一台机器
- `serialize_*`(下卷) = 跨 HALCON 版本/跨进程的"算子结果打包"

---

## 五、最佳实践速查

### 多线程三大铁律

1. **同一算子不得在两线程并发**:HALCON 多数算子线程不安全,要么带 mutex 排队,要么用并行版(数据切片多线程独立算)
2. **iconic 对象跨线程**:创建线程 A,`set_message_obj` → `enqueue_message`(`'copy'`)`→ 线程 B dequeue;**严禁共享 Region/XLD 句柄**
3. **销毁顺序严格反向**:先 `clear_mutex` 后 `clear_condition`,先 `clear_message` 后 `clear_message_queue`,先子后父

### AOP 部署 5 步法

```
1) optimize_aop → 全算力分析
2) write_aop_knowledge → 固化结果
3) set_system('parallelize_operators', 'true')  ← 系统层
4) set_aop_info('find_shape_model', 'true')     ← 单算子
5) read_aop_knowledge → 加载回内存
```

### 算子超时 5 步法

```
1) set_operator_timeout('*', 10000, 'cancel')  ← 全局 10s
2) set_operator_timeout('find_shape_model', 30000, 'break')  ← 单算子 30s
3) try
4)   * 业务代码
5) catch (Exception)  * HDevEngine 捕异常
    dev_disp_error(...)
endtry
```

---

## 六、本卷算子使用频率 Top10

| 排序 | 算子 | 频率 | 典型场景 |
|:---:|:---|:---:|:---|
| 1 | `enqueue_message` / `dequeue_message` | ⭐⭐⭐⭐⭐ | 生产-消费异步框架 |
| 2 | `set_system('parallelize_operators','true')` | ⭐⭐⭐⭐⭐ | 生产部署首要 |
| 3 | `set_operator_timeout` | ⭐⭐⭐⭐ | 工业现场熔断 |
| 4 | `lock_mutex` / `unlock_mutex` | ⭐⭐⭐⭐ | 共享资源保护 |
| 5 | `optimize_aop` / `read_aop_knowledge` | ⭐⭐⭐ | 性能调优 |
| 6 | `wait_condition` | ⭐⭐⭐ | 条件同步 |
| 7 | `count_seconds` | ⭐⭐⭐ | 时间戳、计时 |
| 8 | `create_message` / `set_message_tuple` | ⭐⭐⭐ | 跨线程数据传输 |
| 9 | `signal_condition` / `broadcast_condition` | ⭐⭐ | 任务分派 |
| 10 | `get_current_hthread_id` | ⭐ | 调试日志 |

---

> 本卷到此结束。HALCON 视觉基础设施的 CPU 资源层已经讲完;下卷 进入"**跨机器**"的分布式系统:Socket 通信 + 串口协议 + 序列化打包。
