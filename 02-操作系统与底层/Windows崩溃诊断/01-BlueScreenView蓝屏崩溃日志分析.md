# BlueScreenView：加载 Minidump 分析蓝屏崩溃日志

> **一句话结论**：蓝屏后 Windows 把"内核崩溃现场"写进 `C:\Windows\Minidump\*.dmp`，BlueScreenView 是 NirSoft 出品的**免费、绿色、无需符号服务器**的小工具，能一键把这些 dump 解析成"崩溃时间 / STOP 代码 / 出事驱动"，是定位"谁导致蓝屏"最快的第一步。
> **数据基准**：2026-09 ｜ **难度**：入门 ｜ **前置**：无（了解 Windows 蓝屏机制更佳，见 [02 分类规划中的"系统调用与中断"](../README.md)）

---

## 1. 为什么要搞懂这个

- 蓝屏（BSOD）本身不可怕，**可怕的是每次都复现却找不到原因**。对运维、装机、驱动调试来说，目标从来不是"消除这一次蓝屏"，而是"定位到具体驱动 / 硬件"。
- Windows 在内核崩溃时会把内存现场（崩溃栈、寄存器、加载的驱动模块）写入转储文件，**Minidump（小内存转储，约 256 KB）就是给"事后查凶"用的证据**。
- 但 `.dmp` 是二进制，裸眼看不了。WinDbg 虽强，却要配符号服务器、学习门槛高。
- **BlueScreenView 的价值**：绿色免装、打开即用、把 dump 直接翻译成"这张表 + 这个驱动嫌疑最大"，**不需要任何符号配置**——它是"先快速定性，再决定是否深挖"的最优入口工具。

---

## 2. 核心原理

### 2.1 蓝屏时发生了什么

内核态出现不可恢复错误时，Windows 调用 `KeBugCheckEx()`，按注册表 `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\CrashControl` 的设置，把现场写入转储文件，然后停 machine 显蓝屏。

```
 内核态异常 (非法访问 / 驱动 BUG / 硬件错)
        │
        ▼
 KeBugCheckEx(BugCheckCode, P1, P2, P3, P4)
        │
        ▼
 按 CrashControl 配置把内存现场写盘
        │
        ├── Small Memory Dump → C:\Windows\Minidump\MiniYYMMDD-NN.dmp   (256 KB)
        ├── Kernel Memory Dump  → C:\Windows\MEMORY.DMP
        ├── Complete Memory Dump→ C:\Windows\MEMORY.DMP (全内存)
        ├── Automatic Memory Dump (Win8+ 默认)
        └── Active Memory Dump
        │
        ▼
   系统重启 (或显示蓝屏后等待)
```

### 2.2 五种转储类型对照

| 类型 | 默认路径 | 大小 | 含什么 | BlueScreenView 能否读 |
| --- | --- | --- | --- | --- |
| Small / Minidump | `C:\Windows\Minidump\Mini*.dmp` | ~256 KB | 崩溃栈 + 加载模块 + 少量内存 | ✅ 默认读这个 |
| Kernel Memory Dump | `C:\Windows\MEMORY.DMP` | 物理内存一部分（典型数百 MB~数 GB） | 内核态全部 | ✅ 可选加载 |
| Complete Memory Dump | `C:\Windows\MEMORY.DMP` | 全部物理内存 | 内核+用户态全部 | ✅ 可选加载 |
| Automatic Memory Dump | `C:\Windows\MEMORY.DMP` | 同 Kernel | Win8+ 默认，自动规模 | ✅ |
| Active Memory Dump | `C:\Windows\MEMORY.DMP` | 剔除闲置页 | 仅活跃内存 | ✅ |

> 日常查蓝屏，**Small Minidump 就够**（BlueScreenView 默认只读它）。只有 Minidump 被关掉时，才需要指到 `MEMORY.DMP`。

### 2.3 BlueScreenView 到底做了什么

```
 枚举 C:\Windows\Minidump\*.dmp
        │
        ▼
 逐个解析 dump 头：BugCheckCode / 4 个参数 / Crash Time / 崩溃 CPU
        │
        ▼
 解析崩溃时内核栈上的"返回地址"列表
        │
        ▼
 把每个地址 ↔ 已加载驱动模块 (ntoskrnl / 某 .sys) 做映射
        │
        ▼
 栈顶模块 = "Caused By Driver"（最可疑）
 所有出现在栈里的驱动 = 高亮标粉 (Mark in Pink)
        │
        ▼
 渲染成：上 = 崩溃列表，下 = 选中项的详情/栈
```

**关键认知**：BlueScreenView **不做符号解析**（不解析函数名），它只做"地址 → 模块文件名"的映射。好处是**完全离线、无需符号服务器**；代价是只知道"哪个 .sys"，不知道"这个 .sys 里的哪一行"。要函数级，得上 WinDbg + 微软符号服务器（见第 9 节）。

---

## 3. 工具横向对比：该用哪一个

| 工具 | 形态 | 上手难度 | 分析深度 | 是否需要符号 | 最适合 |
| --- | --- | --- | --- | --- | --- |
| **BlueScreenView** | 绿色 GUI，免装 | ⭐ 极简 | 浅层：直接给出"嫌疑驱动" | ❌ 不需要 | **快速定性、找是哪个驱动** |
| **WhoCrashed** | 安装 GUI | ⭐ 极简 | 浅层 + 中文建议文案 | ❌ 不需要 | 给不懂技术的人出报告 |
| **WinDbg / WinDbg Preview** | GUI/命令行 | 🔴 难 | 深层：完整栈、变量、源码级 | ✅ 需符号服务器 | 专业根因分析、驱动开发 |
| **可靠性监视器** (perfmon /rel) | 系统内置 | ⭐ 简单 | 仅时间线 + 错误事件 | ❌ | 把蓝屏和"装了啥/更新了啥"对时间 |
| **事件查看器** (Event Viewer) | 系统内置 | ⭐⭐ | 仅 BugCheck 事件 ID 1001 | ❌ | 确认"确实崩过 + 时间" |

**怎么选**：

- 蓝屏了，想 1 分钟内知道"是不是显卡/网卡驱动"→ **BlueScreenView**（本文主角）。
- 要写一份给老板/客户看的人话报告 → WhoCrashed。
- 蓝屏反复、BlueScreenView 指向的驱动看起来"无辜"（可能是下层硬件诱发）→ **WinDbg + 符号**深挖。
- 怀疑"是不是装了某个更新后开始的"→ 可靠性监视器按时间线对照。

---

## 4. 详细使用步骤（加载 C:\Windows\Minidump）

### 4.1 前置：确认系统会写 Minidump

很多"找不到 dump"的问题，其实是没开转储。检查 / 开启：

1. `Win + R` → 输入 `sysdm.cpl` → 回车 → **高级** 选项卡 → **启动和故障恢复** 区的"设置"。
2. **写入调试信息** 选 **"小内存转储 (256 KB)"**。
3. **转储文件** 路径默认 `%SystemRoot%\Minidump`（即 `C:\Windows\Minidump`）。
4. 确认 **"系统失败"** 下 **"将事件写入系统日志"** 已勾选（便于事件查看器佐证）。
5. 点确定 → **下次蓝屏后** 才会生成 `MiniYYMMDD-NN.dmp`。已发生的旧蓝屏若当时没开，则无 dump 可看。

> 若客户机蓝屏后没 dump：先按上面开好，等复现一次再取。或临时改成"核心内存转储"以保留更多现场。

### 4.2 获取 BlueScreenView

- 官网 NirSoft 下载 `bluescreenview.zip`（含 32/64 位 `BlueScreenView.exe`）。
- **绿色版**：解压即用，无需安装、无残留注册表。
- 也可通过包管理器（如 `winget install nirsoft.bluescreenview`，取决于源可用性）安装。
- 注意：安全软件偶尔误报 NirSoft 工具，属误报，加白名单即可。

### 4.3 首次打开与加载

1. 双击 `BlueScreenView.exe`（64 位系统用 x64 版）。
2. 程序**自动扫描**本机 `C:\Windows\Minidump\*.dmp`，把每个 dump 列成一行。
3. 若 dump 在别处（如从别的机器拷来的 `MEMORY.DMP`、或 `C:\Windows\Minidump` 被改过路径）：
   - 菜单 **File → Advanced Options**（或 `F9`）→ 在 "Load symbols from the following folder" 区上方选 **"The default Minidump folder"** 或 **"Load from the following MiniDump folder"** 指定目录；
   - 也可勾选 **"Load from MEMORY.DMP file"** 指向完整转储。
4. 加载完成后，顶部出现崩溃列表，每行一次蓝屏。

### 4.4 主界面布局

```
┌──────────────────────────────────────────────────────────────┐
│ 上方面板：崩溃列表（每次蓝屏一行）                               │
│ Crash Time │ Bug Check String      │ Bug Check Code │ Caused By Driver │ ... │
│ 2026-09-01 │ DRIVER_IRQL_NOT_LESS  │ 0x000000D1     │ nvlddmkm.sys      │ ... │
│ 2026-08-28 │ PAGE_FAULT_IN_NONPAGED│ 0x00000050     │ ntoskrnl.exe      │ ... │
├──────────────────────────────────────────────────────────────┤
│ 下方面板：选中那次崩溃的详情（可在 Options → Lower Pane Mode 切换）│
│  · Crash Addresses（崩溃地址）                                  │
│  · Stack Addresses（崩溃栈——谁调用了谁，最有用）                │
│  · Modules/Drivers List（涉及的模块）                           │
│  · Blue Screen in XP Style（伪蓝屏画面）                        │
│  · All Threads（全部线程）                                      │
└──────────────────────────────────────────────────────────────┘
```

### 4.5 关键列解读（上方面板）

| 列名 | 含义 | 怎么用 |
| --- | --- | --- |
| **Crash Time** | 蓝屏发生时间 | 按时间排序，定位"最近一次 / 某个时间段集中爆发" |
| **Bug Check String** | 蓝屏原因字符串，如 `DRIVER_IRQL_NOT_LESS_OR_EQUAL` | 一眼看懂大致性质（驱动 / 内存 / 文件系统） |
| **Bug Check Code** | STOP 代码十六进制，如 `0x000000D1` | 对照第 6 节速查表 |
| **Parameter 1~4** | 崩溃附加参数 | 专业分析用（如 0x50 的 P1 是出错地址），一般看前 2 个 |
| **Caused By Driver** | **栈顶驱动文件名**（最可疑） | 第一怀疑对象：`nvlddmkm.sys`=NVIDIA 显卡驱动 |
| **Caused By Address** | 该驱动内出事的偏移地址 | 配合版本可定位具体功能 |
| **Crash Address** | 崩溃指令地址 | 辅助判断是内核还是某驱动 |
| **Processor / # of processors** | 第几颗 CPU 核崩的 | 多核调度相关问题时参考 |
| **Major / Minor Bug Check** | 内部版本细分 | 一般忽略 |

> **粉红高亮**：在 `Options → Mark Drivers in Pink` 开启后，凡是"出现在崩溃栈里的驱动"都会被标粉。这意味着它**当时确实在执行**，是比"Caused By Driver"更可靠的范围——栈里所有粉红驱动都该怀疑。

### 4.6 命令行与批量导出（运维 / 取证利器）

BlueScreenView 支持无界面批量导出，适合脚本化、远程取证：

```bat
:: 导出为 CSV（逗号分隔），可用 Excel / Python 分析
BlueScreenView.exe /scomma "C:\logs\bsod.csv"

:: 导出为 Tab 分隔文本
BlueScreenView.exe /stab "C:\logs\bsod.txt"

:: 导出为 HTML 报告
BlueScreenView.exe /shtml "C:\logs\bsod.html"

:: 导出为 XML
BlueScreenView.exe /sxml "C:\logs\bsod.xml"
```

> 取证流程：把目标机的 `C:\Windows\Minidump\` 整个目录拷到 U 盘 → 在本机用上述命令导出 CSV → 跨多台机器汇总比对"是不是同一个驱动在作妖"。

### 4.7 常用高级选项

- **Options → Lower Pane Mode**：切换下方面板内容，最常用 **Stack Addresses**（看完整崩溃调用链）。
- **Options → Mark Drivers in Pink**：开启栈内驱动高亮（强烈建议常开）。
- **View → Choose Columns**：加列，如 `Full Path`、`File Version`、`Product Name`，便于确认"这个 .sys 属于哪个厂商 / 版本"。
- **File → Save Selected Items**（或 `Ctrl+C` 复制）：把某次崩溃摘要贴到工单 / 聊天里。
- **File → Advanced Options → 指定 Minidump 文件夹**：分析别的机器的 dump。

---

## 5. 蓝屏原因检测步骤（方法论）

按下面 8 步走，从"快速定性"到"验证根因"：

**步骤 1 · 打开 BlueScreenView，按 Crash Time 排序**
找最近一次崩溃，先解决"最新的那次"（往往和当前症状最相关）。

**步骤 2 · 读 Bug Check String / Code**
结合第 6 节速查表，判断大类：驱动类 / 内存类 / 文件系统类 / 硬件类。

**步骤 3 · 看 Caused By Driver（栈顶嫌疑）**
记下文件名 → 百度/厂商官网查它属于哪个驱动（如 `nvlddmkm.sys` = NVIDIA 显示驱动，`atikmdag.sys` = AMD，`ndis.sys` = 网络栈，`ntoskrnl.exe` = 内核自身）。

**步骤 4 · 看下方面板的 Stack Addresses（关键）**
确认栈顶驱动是否"真的在执行"，以及**它下面还压着谁**。例如栈是 `ntoskrnl → myav.sys → (崩溃)`，那 `myav.sys`（某杀软驱动）可能才是真凶，而非内核。

**步骤 5 · 核对粉红高亮驱动**
所有标粉驱动都在崩溃现场，把它们都列出来，缩小嫌疑圈。

**步骤 6 · 跨多次崩溃找"共性驱动"（最重要的一步）**
如果列表里有 3~5 次蓝屏，**Caused By Driver 都是同一个 .sys** → 基本坐实就是它。BlueScreenView 天然适合这种"重复犯罪"模式。
> 技巧：先按 Caused By Driver 排序，看同一驱动出现几次。

**步骤 7 · 对嫌疑驱动采取行动**
- 第三方驱动（显卡/网卡/声卡/杀软/虚拟网卡）→ **更新到最新版**，或回滚到上一个稳定版（设备管理器 → 该设备 → 回滚驱动）。
- 若是刚装/刚更新后出现 → 卸载最近装的软件/驱动。
- 若是 `ntoskrnl.exe` 单独背锅、无其他粉红驱动 → 往往不是内核真 bug，而是**硬件（内存/CPU/供电）或某个没被识别的下层组件**，转入步骤 8。

**步骤 8 · 怀疑硬件时**
- `0x00000124 WHEA_UNCORRECTABLE_ERROR`、`0x00000101 CLOCK_WATCHDOG_TIMEOUT`、`0x0000003B` 伴随机箱异响 → 跑 **MemTest86（内存）**、看 CPU/显卡温度、检查超频/降频、更新 BIOS。
- `0x00000050 / 0x0000001A` 反复 → 内存或硬盘坏道嫌疑，跑 `chkdsk` / 厂商诊断。

---

## 6. 常见 STOP 代码速查表

| STOP 代码 | 字符串 | 大类 | 第一怀疑 |
| --- | --- | --- | --- |
| `0x0000000A` | IRQL_NOT_LESS_OR_EQUAL | 驱动/中断 | 驱动在错误 IRQL 访问分页内存 |
| `0x0000001E` | KMODE_EXCEPTION_NOT_HANDLED | 驱动 | 内核态未处理异常 |
| `0x0000003B` | SYSTEM_SERVICE_EXCEPTION | 驱动/系统 | 系统服务调用出错（常伴硬件） |
| `0x00000050` | PAGE_FAULT_IN_NONPAGED_AREA | 内存/驱动 | 访问了不该访问的地址（坏内存/坏驱动） |
| `0x0000007E` | SYSTEM_THREAD_EXCEPTION_NOT_HANDLED | 驱动 | 系统线程抛异常 |
| `0x0000007F` | UNEXPECTED_KERNEL_MODE_TRAP | 硬件/CPU | CPU 陷阱（超频/过热/内存） |
| `0x0000000D1` | DRIVER_IRQL_NOT_LESS_OR_EQUAL | 驱动 | 驱动在 DISPATCH 级碰了分页内存 |
| `0x00000019` | BAD_POOL_HEADER | 驱动/内存 | 内核池损坏 |
| `0x0000001A` | MEMORY_MANAGEMENT | 内存 | 物理内存/页表损坏 |
| `0x00000024` | NTFS_FILE_SYSTEM | 磁盘/驱动 | NTFS 驱动或硬盘坏道 |
| `0x000000C2` | BAD_POOL_CALLER | 驱动 | 驱动错误地释放/分配池 |
| `0x000000C4` | DRIVER_VERIFIER_DETECTED_VIOLATION | 驱动 | **开了驱动验证器抓到的违规** |
| `0x000000BE` | ATTEMPTED_WRITE_TO_READONLY_MEMORY | 驱动 | 写了只读页（常是坏驱动/rootkit） |
| `0x000000EF` | CRITICAL_PROCESS_DIED | 系统/磁盘 | 关键系统进程挂掉 |
| `0x000000F4` | CRITICAL_OBJECT_TERMINATION | 磁盘/系统 | 关键对象被终止（常因硬盘/电源） |
| `0x00000124` | WHEA_UNCORRECTABLE_ERROR | **硬件** | CPU/RAM/PCIe 不可纠正硬件错 |
| `0x00000139` | KERNEL_MODE_HEAP_CORRUPTION | 驱动/内存 | 内核堆损坏 |
| `0xC000021A` | WINLOGON_FATAL_ERROR | 系统/账户 | 登录相关关键进程失败 |

> 详细大全见微软官方 "Bug Check Code Reference"（见第 9 节）。

---

## 7. 实战案例

### 案例 A：显卡驱动背锅（最常见）
- **现象**：玩游戏 / 切分辨率时随机蓝屏。
- **BlueScreenView 显示**：`Bug Check = 0xD1 DRIVER_IRQL_NOT_LESS_OR_EQUAL`，`Caused By Driver = nvlddmkm.sys`，栈里 `dxgkrnl.sys → nvlddmkm.sys`。
- **判断**：NVIDIA 显示驱动在过高 IRQL 访问了分页内存。
- **动作**：更新 NVIDIA 驱动到最新 Studio/Game Ready 版；若刚更新才出 → 回滚驱动；顺带检查显卡是否超频，降频试试。

### 案例 B：杀软驱动诱发的"内核背锅"
- **现象**：开机不久蓝屏，Caused By 显示 `ntoskrnl.exe`，无其他粉红驱动——看似内核 bug。
- **深看 Stack Addresses**：栈底其实是 `xxxav.sys`（某杀软/安全软件驱动）→ 它在内核里干了非法操作，把锅甩给内核。
- **动作**：更新 / 卸载该安全软件，或临时禁用其内核驱动验证是否不再蓝屏。

### 案例 C：硬件（内存）作妖
- **现象**：`0x00000050` / `0x0000001A` 反复，Caused By 每次都不同（有时 ntoskrnl，有时随机 .sys）。
- **判断**：没有"固定嫌疑驱动"，且错误地址随机 → 偏向物理内存损坏。
- **动作**：MemTest86 跑一轮，发现报错 → 换内存条；或先拔掉一条内存交叉验证。

---

## 8. 常见误区

- ❌ **"BlueScreenView 说 xxx.sys 坏了，就是它的问题"**
  → ✅ 它只报"栈顶模块"。栈顶可能是被下层驱动 / 硬件诱发的替罪羊。务必看完整 Stack Addresses 和粉红驱动集合。
- ❌ **"蓝屏一定是软件/驱动问题"**
  → ✅ `0x124 WHEA`、`0x7F`、随机地址的 `0x50/0x1A` 多为**硬件**（内存、CPU、供电、过热、超频）。
- ❌ **"Minidump 一定存在"**
  → ✅ 只有开了"小内存转储"且**那次崩溃确实写了盘**才有；若是突然断电/卡死未必生成。先按 4.1 确认设置。
- ❌ **"BlueScreenView 不需要符号，所以不如 WinDbg"**
  → ✅ 两者定位不同：BlueScreenView 做**分钟级定性**；WinDbg 做**函数级深挖**。先用前者定性，必要时再上后者。
- ❌ **"同一个 .sys 出现一次就该卸载它"**
  → ✅ 看**频次**：单次可能是偶发；多次崩溃都指向它才是高置信证据（步骤 6）。
- ❌ **"开了驱动验证器（Driver Verifier）能自动修好"**
  → ✅ 验证器是用来**抓**违规驱动的（会故意触发 `0xC4`），不是修复工具；抓到后要去更新/卸载那个驱动。

---

## 9. 延伸阅读

- [02 操作系统与底层 · 分类规划](../README.md) — 本分类的进程/内存/中断等主题地图
- [微软官方 Bug Check Code Reference](https://learn.microsoft.com/windows-hardware/drivers/debugger/bug-check-code-reference2) — 全部 STOP 代码的权威解释
- [WinDbg 入门（微软 Learn）](https://learn.microsoft.com/windows-hardware/drivers/debugger/debugger-download-tools) — 当 BlueScreenView 不够用时，升级到符号级分析
- [NirSoft BlueScreenView 官网](https://www.nirsoft.net/utils/blue_screen_view.html) — 工具下载、命令行参数、更新日志
- 站内联动：[CPU 前沿技术](../01-计算机硬件/CPU/03-CPU前沿技术.md)（超频/过热与 `0x7F`/`0x124` 蓝屏的关联）、[主板结构与供电](../01-计算机硬件/主板/01-主板结构与芯片组.md)（供电不稳诱发随机蓝屏）

---

<!-- 修订记录 -->
<!-- 2026-09-03 初稿：BlueScreenView 加载 Minidump 的详细使用日志 + 蓝屏原因检测 8 步法 + STOP 代码速查 + 实战案例 + 误区 -->
