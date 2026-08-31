# -*- coding: utf-8 -*-
"""Modbus 通讯思维导图（matplotlib 辐射布局）
主题：Modbus 通讯协议族 —— RTU / ASCII / TCP / UDP 的区别与介绍
      覆盖 串口(Modbus RTU/ASCII) 与 网口(Modbus TCP/UDP) 全部通讯方式
依赖：matplotlib + 中文字体 SimHei
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
import os, math

SIMHEI = r"C:/Windows/Fonts/simhei.ttf"
fm.fontManager.addfont(SIMHEI)
FPROP = fm.FontProperties(fname=SIMHEI)
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "STXihei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

# ---------- 配色（6 族：鲜明区分）----------
COLOR = {
    "center":   "#2d3436",
    "overview": "#0984e3",   # 蓝：协议总览
    "rtu":      "#e17055",   # 橙：串口 RTU
    "ascii":    "#00b894",   # 绿：串口 ASCII
    "tcp":      "#6c5ce7",   # 紫：网口 TCP
    "udp":      "#d63031",   # 红：网口 UDP
    "compare":  "#e84393",   # 洋红：终极对比与选型
}

# ---------- 数据：6 大家族（六边形辐射）----------
FAMILIES = [
    ("Modbus 协议总览", COLOR["overview"], "开放主从协议 · 1979 施耐德", [
        "起源：1979 Modicon（现施耐德）为 PLC 通信发明",
        "本质：主从(Master/Slave) 请求-响应协议",
        "OSI 定位：应用层(第 7 层) 协议",
        "可承载：串行链路 或 以太网",
        "特点：开放免费 · 简单 · 跨厂商互通",
        "主从：单主多从，主站轮询从站",
        "现代叫法：TCP 端称 Client/Server",
        "三大变种：RTU / ASCII / TCP",
        "应用：工业自动化 · SCADA · 智能仪表",
    ]),
    ("串口 Modbus RTU", COLOR["rtu"], "最常用 · 二进制 · CRC", [
        "物理层：RS-232 / RS-422 / RS-485",
        "编码：二进制紧凑（传输效率最高）",
        "校验：CRC-16 循环冗余校验",
        "帧格式：地址 + 功能码 + 数据 + CRC",
        "波特率：9600 / 19200 / 115200 可配",
        "RS-485：差分·抗干扰·1200m·32+ 节点",
        "RS-232：点对点·15m·全双工",
        "RS-422：差分·全双工·点对多",
        "链路：半双工 主从轮询",
        "工业现场最主流",
    ]),
    ("串口 Modbus ASCII", COLOR["ascii"], "可读 · 易调试 · 低效", [
        "物理层：同 RTU（RS-232 / RS-485）",
        "编码：ASCII 十六进制字符（人可读）",
        "校验：LRC 纵向冗余校验",
        "帧格式：冒号 : 起始 + … + CR/LF 结束",
        "优点：肉眼可读 · 易抓包调试",
        "缺点：效率低（1 字节 → 2 字符）",
        "优点：字符间隔容错，抗误码",
        "现代应用较少",
    ]),
    ("网口 Modbus TCP", COLOR["tcp"], "可靠 · 跨网段 · 主流", [
        "物理层：以太网（RJ45 / 光纤）",
        "传输层：TCP（端口 502）",
        "封装：MBAP 头 + PDU（无地址 / 无 CRC）",
        "特点：面向连接 · 可靠 · 自动重传",
        "模型：Client / Server",
        "优势：跨网段 · 可路由 · 融入 IT 网",
        "缺点：开销略大 · 实时性略弱于串口",
        "工业以太网绝对主流",
    ]),
    ("网口 Modbus UDP", COLOR["udp"], "无连接 · 低延迟（注:ucp=UDP）", [
        "物理层：以太网",
        "传输层：UDP（端口 502）",
        "特点：无连接 · 低延迟 · 不可靠",
        "丢包：不重传 · 需应用层保障",
        "适用：局域网 · 实时优先 · 广播",
        "vs TCP：要不要握手 / 确认",
        "注：用户 'ucp' 即 UDP 笔误",
        "部分网关 / 网关协议支持",
    ]),
    ("终极对比 & 选型", COLOR["compare"], "串口/网口 · TCP/UDP 怎么选", [
        "串口 vs 网口：速率/距离/拓扑不同",
        "RTU vs ASCII：二进制高效 vs 可读",
        "TCP vs UDP：可靠 vs 低延迟",
        "短距多节点：RTU over RS-485",
        "跨楼跨网段：Modbus TCP",
        "实时低延迟：Modbus UDP",
        "调试可读：Modbus ASCII",
        "数据模型：4 表 线圈/离散/输入/保持",
        "功能码：01-06 · 15 · 16 最常用",
    ]),
]

# ---------- 画布 ----------
fig, ax = plt.subplots(figsize=(52, 44), facecolor="#fafbfc")
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
CW, CH = 8.2, 3.0
rbox(cx, cy, CW, CH, COLOR["center"])
t(cx, cy + 0.55, "Modbus 通讯协议族", fs=16, color="white")
t(cx, cy - 0.55, "RTU / ASCII / TCP / UDP 区别与介绍", fs=12, color="#dfe6e9")

# ---------- 6 族辐射 ----------
N = len(FAMILIES)
R = 8.0
LBL_W, LBL_H = 5.8, 1.45
HDR_H = 0.55
ITEM_H = 0.60
PAD = 0.35

for i, (name, color, sub_desc, items) in enumerate(FAMILIES):
    ang = math.radians(90 - i * 360 / N)
    dx, dy = math.cos(ang), math.sin(ang)
    fx, fy = cx + R * dx, cy + R * dy

    # 中心 → 家族 连线
    ax.plot([cx + dx * 3.8, fx - dx * (LBL_W/2 + 0.2)],
            [cy + dy * 3.8, fy - dy * (LBL_H/2 + 0.2)],
            color=color, linewidth=2.4, alpha=0.85, zorder=1)

    # 家族标签框
    rbox(fx, fy, LBL_W, LBL_H, color)
    t(fx, fy, name, fs=13, color="white")

    # 子组 box（径向向外）—— 限宽 ≤ 族标签 + 严格"x 与 y 都不重叠"offset
    sub_w = max(LBL_W, 0.20 * max(len(s) for s in items) + 0.6)
    sub_h = HDR_H + ITEM_H * len(items) + PAD * 2
    th = 0.35
    need_dx = ((LBL_W + sub_w) / (2 * abs(dx))) if abs(dx) > th else 0
    need_dy = ((LBL_H + sub_h) / (2 * abs(dy))) if abs(dy) > th else 0
    offset = max(need_dx, need_dy) + 0.4
    sx = fx + dx * offset
    sy = fy + dy * offset

    # 家族 → 子组 连线
    sub_half = max(sub_w, sub_h) / 2
    ax.plot([fx + dx * (LBL_W/2 + 0.1), sx - dx * (sub_half + 0.1)],
            [fy + dy * (LBL_H/2 + 0.1), sy - dy * (sub_half + 0.1)],
            color=color, linewidth=1.8, alpha=0.6, zorder=1)

    # 子组背景
    rbox(sx, sy, sub_w, sub_h, "white", ec=color, lw=1.8, alpha=1.0, z=2)
    # 头部色条
    rbox(sx, sy + sub_h/2 - HDR_H/2, sub_w - 0.2, HDR_H, color,
         ec=color, lw=0.5, z=3)
    t(sx, sy + sub_h/2 - HDR_H/2, sub_desc, fs=10, color="white")

    # 功能项纵向列
    for j, it in enumerate(items):
        iy = sy + sub_h/2 - HDR_H - PAD - ITEM_H/2 - j * ITEM_H
        t(sx, iy, it, fs=10.5, color="#2d3436", bold=False)

# ---------- 标题 / 脚注 ----------
ax.text(cx, bounds["ymax"] + 0.6,
        "Modbus 通讯协议族：Modbus RTU / ASCII / TCP / UDP 区别与介绍（串口 · 网口 · TCP · UDP）",
        ha="center", va="bottom", fontsize=18, fontweight="bold",
        color="#2d3436", fontproperties=FPROP)
ax.text(cx, bounds["ymin"] - 0.4,
        "辐射布局：①协议总览 ②串口 RTU(RS-485/232/422) ③串口 ASCII ④网口 TCP(端口502) ⑤网口 UDP（注：ucp=UDP）⑥四方式终极对比与选型",
        ha="center", va="top", fontsize=11, color="#636e72", fontproperties=FPROP)

# ---------- 自适应边界 ----------
PADX, PADY = 1.6, 1.4
ax.set_xlim(bounds["xmin"] - PADX, bounds["xmax"] + PADX)
ax.set_ylim(bounds["ymin"] - 1.6, bounds["ymax"] + 1.2)

OUT_PNG = os.path.join(os.path.dirname(__file__), "Modbus通讯.png")
OUT_SVG = os.path.join(os.path.dirname(__file__), "Modbus通讯.svg")
plt.savefig(OUT_PNG, dpi=150, bbox_inches="tight", facecolor="#fafbfc")
plt.savefig(OUT_SVG, bbox_inches="tight", facecolor="#fafbfc")
plt.close()
print("OK ->", OUT_PNG)
print("bounds", bounds)
