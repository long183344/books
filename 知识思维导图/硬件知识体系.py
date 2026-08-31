# -*- coding: utf-8 -*-
"""硬件知识体系思维导图（matplotlib 辐射布局）
主题：PLC / 开发板 / 电路板 的区别与联系，含 PLC 详细解析
依赖：matplotlib + 中文字体 SimHei
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle
import os, math

SIMHEI = r"C:/Windows/Fonts/simhei.ttf"
fm.fontManager.addfont(SIMHEI)
FPROP = fm.FontProperties(fname=SIMHEI)
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "STXihei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

# ---------- 配色 ----------
COLOR = {
    "center": "#2d3436",
    "plc":    "#e17055",   # 橙：PLC（重点）
    "dev":    "#00b894",   # 绿：开发板
    "pcb":    "#0984e3",   # 蓝：电路板
    "rel":    "#d63031",   # 红：区别与联系
    "rel2":   "#b2bec3",
    "link":   "#a29bfe",   # 紫：关联硬件
}

# ---------- 数据：5 大家族（辐射）----------
FAMILIES = [
    ("PLC 详细解析 ★", COLOR["plc"], "工业可编程逻辑控制器", [
        "本质：工业级可编程控制器",
        "原理：循环扫描 输入→执行→输出",
        "特性：确定性 / 硬实时",
        "语言：梯形图·指令表·ST·FBD·SFC",
        "I/O：数字 DI/DO · 模拟 AI/AO",
        "I/O：高速计数 · 脉冲定位",
        "三菱：FX1S / 1N / 2N · Q · L · iQ-R",
        "三菱：FX3U（第三代小型）",
        "三菱：FX5U（iQ-F 旗舰）",
        "信捷：XD / XL / XC（国产）",
        "应用：产线 · 单机 · 装备自动化",
        "优势：抗干扰 · 断电保持 · 7x24",
    ]),
    ("开发板 Dev Board", COLOR["dev"], "预焊芯片的电路板", [
        "定义：预焊接 MCU/SoC 的电路板",
        "用途：学习 / 原型验证",
        "Arduino（最易上手）",
        "STM32 Nucleo / Discovery",
        "ESP32（蓝牙 / WiFi）",
        "属于：带芯片的电路板",
        "vs PLC：无工业防护",
    ]),
    ("电路板 / PCB", COLOR["pcb"], "一切硬件的物理载体", [
        "定义：焊元器件的绝缘基板",
        "类型：刚性板 / 柔性 FPC",
        "类型：刚挠结合 / HDI",
        "层级：裸板 → 焊元件 → 板卡",
        "PCB = 未焊元件的裸板",
        "无智能，纯物理载体",
    ]),
    ("三者区别与联系", COLOR["rel"], "核心对比（重点）", [
        "电路板：无智能的物理载体",
        "开发板：有智能 · 面向开发者",
        "PLC：智能 + 工业防护 · 面向现场",
        "联系①：开发板 属于 电路板",
        "联系②：PLC 主板也是电路板",
        "联系③：都含 MCU / 逻辑器件",
        "控制力：电路板<开发板<PLC",
    ]),
    ("关联硬件", COLOR["link"], "横向坐标参照", [
        "MCU：开发板的『心脏』",
        "FPGA：并行硬件 / 加速",
        "树莓派：跑 Linux 的单板机",
        "PC：上位机 / 机器视觉",
    ]),
]

# ---------- 画布 ----------
fig, ax = plt.subplots(figsize=(34, 24), facecolor="#fafbfc")
ax.set_aspect("equal")
ax.axis("off")

bounds = {"xmin": 1e9, "xmax": -1e9, "ymin": 1e9, "ymax": -1e9}

def track(x0, y0, x1, y1):
    bounds["xmin"] = min(bounds["xmin"], x0, x1)
    bounds["xmax"] = max(bounds["xmax"], x0, x1)
    bounds["ymin"] = min(bounds["ymin"], y0, y1)
    bounds["ymax"] = max(bounds["ymax"], y0, y1)

def rbox(x, y, w, h, fc, ec=None, lw=2.0, alpha=1.0, z=3):
    p = FancyBboxPatch((x - w/2, y - h/2), w, h,
                       boxstyle="round,pad=0.02,rounding_size=0.18",
                       facecolor=fc, edgecolor=ec or fc,
                       linewidth=lw, alpha=alpha, zorder=z,
                       transform=ax.transData)
    ax.add_patch(p)
    track(x - w/2, y - h/2, x + w/2, y + h/2)
    return p

def t(x, y, s, fs=11, color="#2d3436", bold=True, fp=FPROP, z=6):
    ax.text(x, y, s, ha="center", va="center", fontsize=fs,
            color=color, fontweight="bold" if bold else "normal",
            fontproperties=fp, zorder=z)

# ---------- 中心 ----------
cx, cy = 0, 0
CW, CH = 7.2, 3.0
rbox(cx, cy, CW, CH, COLOR["center"])
t(cx, cy + 0.55, "PLC · 开发板 · 电路板", fs=15, color="white")
t(cx, cy - 0.55, "区别与联系（含 PLC 详解）", fs=12, color="#dfe6e9")

# ---------- 5 族辐射 ----------
N = len(FAMILIES)
R = 7.2
LBL_W, LBL_H = 5.4, 1.35
HDR_H = 0.55
ITEM_H = 0.62
PAD = 0.35

for i, (name, color, sub_desc, items) in enumerate(FAMILIES):
    ang = math.radians(90 - i * 360 / N)
    dx, dy = math.cos(ang), math.sin(ang)
    fx, fy = cx + R * dx, cy + R * dy

    # 中心 → 家族 连线
    ax.plot([cx + dx * 3.4, fx - dx * (LBL_W/2 + 0.2)],
            [cy + dy * 3.4, fy - dy * (LBL_H/2 + 0.2)],
            color=color, linewidth=2.2, alpha=0.8, zorder=1)

    # 家族标签框
    rbox(fx, fy, LBL_W, LBL_H, color)
    t(fx, fy, name, fs=12.5, color="white")

    # 子组 box（径向向外）
    sub_w = max(LBL_W + 0.4, 0.20 * max(len(s) for s in items) + 0.6)
    sub_h = HDR_H + ITEM_H * len(items) + PAD * 2
    sx = fx + dx * (LBL_H/2 + 0.25 + sub_w/2)
    sy = fy + dy * (LBL_H/2 + 0.25 + sub_h/2)

    # 家族 → 子组 连线
    ax.plot([fx + dx * (LBL_W/2 + 0.1), sx - dx * (sub_w/2 + 0.1)],
            [fy + dy * (LBL_H/2 + 0.1), sy - dy * (sub_h/2 + 0.1)],
            color=color, linewidth=1.6, alpha=0.6, zorder=1)

    # 子组背景
    rbox(sx, sy, sub_w, sub_h, "white", ec=color, lw=1.6, alpha=1.0, z=2)
    # 头部色条
    rbox(sx, sy + sub_h/2 - HDR_H/2, sub_w - 0.2, HDR_H, color,
         ec=color, lw=0.5, z=3)
    t(sx, sy + sub_h/2 - HDR_H/2, sub_desc, fs=10, color="white")

    # 功能项纵向列
    for j, it in enumerate(items):
        iy = sy + sub_h/2 - HDR_H - PAD - ITEM_H/2 - j * ITEM_H
        t(sx, iy, it, fs=10.5, color="#2d3436", bold=False)

# ---------- 标题 / 脚注 ----------
ax.text(cx, bounds["ymax"] + 0.6, "硬件知识体系：PLC / 开发板 / 电路板 区别与联系（详细解析 PLC）",
        ha="center", va="bottom", fontsize=17, fontweight="bold",
        color="#2d3436", fontproperties=FPROP)
ax.text(cx, bounds["ymin"] - 0.4,
        "辐射布局：①电路板=物理载体 ②开发板=带芯片的电路板 ③PLC=工业加固的控制器 ④三者联系见红框 ⑤关联硬件作坐标",
        ha="center", va="top", fontsize=10.5, color="#636e72", fontproperties=FPROP)

# ---------- 自适应边界 ----------
PADX, PADY = 1.6, 1.4
ax.set_xlim(bounds["xmin"] - PADX, bounds["xmax"] + PADX)
ax.set_ylim(bounds["ymin"] - 1.6, bounds["ymax"] + 1.2)

OUT_PNG = os.path.join(os.path.dirname(__file__), "硬件知识体系.png")
OUT_SVG = os.path.join(os.path.dirname(__file__), "硬件知识体系.svg")
plt.savefig(OUT_PNG, dpi=150, bbox_inches="tight", facecolor="#fafbfc")
plt.savefig(OUT_SVG, bbox_inches="tight", facecolor="#fafbfc")
plt.close()
print("OK ->", OUT_PNG)
print("bounds", bounds)
