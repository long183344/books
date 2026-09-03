# 02 · 操作系统与底层

> 硬件之上的第一层抽象。硬件笔记里那些「CPU 有几个核」「缓存多大」，最终都要靠这一层调度出来才有意义。

## 已收录主题

### Windows 崩溃诊断（BlueScreenView / Minidump 实战）

- [01 · BlueScreenView 加载 Minidump 分析蓝屏崩溃日志](./Windows崩溃诊断/01-BlueScreenView蓝屏崩溃日志分析.md) — 工具原理（地址→驱动映射、无需符号）、5 种转储类型对照、加载 `C:\Windows\Minidump` 的详细步骤、命令行批量导出、8 步蓝屏原因检测法、STOP 代码速查表、3 个实战案例、6 条常见误区

---

## 规划中的主题

- [ ] 进程与线程：调度器、上下文切换成本、大小核调度（与 [CPU 前沿技术](../01-计算机硬件/CPU/03-CPU前沿技术.md) 的 Thread Director 呼应）
- [ ] 虚拟内存：页表、TLB、缺页处理、大页
- [ ] 内存管理：分配器、NUMA、内存回收（与 [CXL 内存池化](../01-计算机硬件/总线/03-前沿互连-CXL-UCIe-NVLink.md) 联动）
- [ ] 文件系统：ext4 / NTFS / ZFS / Btrfs 对比
- [ ] I/O 模型：阻塞 / 非阻塞 / io_uring
- [ ] 启动流程：BIOS → UEFI → bootloader → 内核（与主板笔记衔接）
- [ ] 系统调用与中断

## 与硬件分类的衔接点

| 硬件概念 | 对应的 OS 概念 |
| --- | --- |
| 缓存层级 L1/L2/L3 | 缓存亲和性调度、伪共享 |
| 大核 / 小核 | 调度器提示（Intel Thread Director、EAS） |
| NUMA 节点 | 内存本地性、`numactl` |
| PCIe 设备 | 设备枚举、MMIO、DMA、IOMMU |
| CXL 内存 | 作为无 CPU 的 NUMA 节点暴露给内核 |
