# 06 · 工具与效率

> 让重复劳动消失的那些东西。

## 规划中的主题

- [ ] Shell 与命令行：管道思维、常用组合技
- [ ] Git 进阶：rebase / reflog / bisect / worktree
- [ ] 编辑器配置与快捷键肌肉记忆
- [ ] 正则表达式实战速查
- [ ] 自动化脚本模式：幂等、可重试、可观测
- [ ] 硬件诊断工具箱：CPU-Z / HWiNFO / lscpu / lspci / dmidecode / MemTest86
- [ ] 基准测试方法论：怎么测才不自欺欺人

## 硬件诊断速查（配合 01 分类使用）

| 想知道什么 | Windows | Linux |
| --- | --- | --- |
| CPU 型号 / 缓存 / 微架构 | CPU-Z | `lscpu` |
| 主板型号 / BIOS 版本 | `wmic baseboard get product,manufacturer` | `dmidecode -t baseboard` |
| 内存条型号 / 频率 / 通道 | CPU-Z → SPD 页 | `dmidecode -t memory` |
| PCIe 设备与链路速率 | HWiNFO64 | `lspci -vv \| grep LnkSta` |
| NVMe 实际跑在几代 | CrystalDiskInfo | `nvme list` + `lspci` |
| 温度 / 功耗墙 | HWiNFO64 | `sensors`、`turbostat` |
