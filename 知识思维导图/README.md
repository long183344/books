# 知识思维导图

> 用 **PlantUML `mindmap` 语法** + **kroki.io 渲染** 维护的跨主题可视化笔记。
> 每个主题一份 `.puml` 源文件 + 自动渲染的 `.svg` / `.png` + 一份配套 `.md`。

## 目录约定

```
知识思维导图/
├── README.md                  ← 本说明
└── <主题名>/
    ├── <主题>.puml           ← PlantUML 源（结构化、可编辑）
    ├── <主题>.svg            ← 矢量图（首选查看）
    ├── <主题>.png            ← 栅格图（kroki 渲染）
    └── <主题>.md             ← 含关系速览表 + 内嵌 plantuml 代码块
```

> 当前为第一批内容，未做主题子目录，所有文件平铺。

## 已收录

| 主题 | 主入口 | 节点数（约） | 说明 |
| --- | --- | --- | --- |
| 硬件知识体系 | [`硬件知识体系.md`](./硬件知识体系.md) | 8 大族 / 50+ 节点 | PLC（三菱/信捷/3U/5U）·MCU·FPGA·开发板·树莓派·电路板·PC·关系 |

## 工具链

| 环节 | 工具 | 备注 |
| --- | --- | --- |
| 编辑 | 手写 PlantUML `mindmap` | 语法见 <https://plantuml.com/mindmap-diagram> |
| 渲染 | [kroki.io](https://kroki.io) | 公共 PlantUML 服务，无需本地装 Java |
| 查看 | SVG 优先（浏览器放大无失真）；PNG 备查 | — |

## 新增主题模板

1. `知识思维导图/<主题>.puml`
2. 用 kroki 渲染：把 `.puml` 文本 POST 到 `https://kroki.io/plantuml/{svg|png}`，保存为同名的 `.svg` / `.png`
3. 写一份 `.md`：含「一句话核心」+「关系速览表」+「内嵌 plantuml 代码块」+「文件清单」
4. 更新本 README 的「已收录」表格

> PlantUML mindmap 节点层级：`*` 根 → `**` 一级 → `***` 二级 → `****` 三级，最多建议到 4 级；
> 用 `left side` 把后续分支切换到根节点左侧，可显著降低横向宽度（适合 6+ 个一级分支时）。