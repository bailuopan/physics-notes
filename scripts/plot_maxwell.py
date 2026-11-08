# -*- coding: utf-8 -*-
"""麦克斯韦速率分布：数值自检 + 出图（Pillow，2 倍超采样）。

    python plot_maxwell.py            # 画图
    python plot_maxwell.py --check    # 只做数值自检，打印数字

自检内容（对应 math-verify 的「多点采样 + 量纲/形状自查」）：
  1. ∫f(v)dv 是否为 1（数值积分 vs 解析归一化）
  2. 峰值位置是否等于 v_p = √(2kT/m)
  3. ∫v f dv、∫v² f dv 是否等于 √(8kT/πm)、√(3kT/m)
  4. 1D / 2D / 3D 三种分布是否都归一化到 1
"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "notes" / "assets"  # 图片统一落到 notes/assets/

R_GAS = 8.314462618
K_B = 1.380649e-23
N_A = 6.02214076e23

M_N2 = 28.014e-3
M_H2 = 2.016e-3

FONT = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"

INK = (31, 41, 55)
MUTED = (107, 114, 128)
GRID = (229, 231, 235)
AXIS = (55, 65, 81)
WHITE = (255, 255, 255)
C100 = (43, 108, 176)
C300 = (47, 133, 90)
C1000 = (192, 86, 33)
C1D = (107, 114, 128)
C2D = (47, 133, 90)
C3D = (43, 108, 176)


# ----------------------------------------------------------------- 物理
def vp(T, M):
    return math.sqrt(2 * R_GAS * T / M)


def v_mean(T, M):
    return math.sqrt(8 * R_GAS * T / (math.pi * M))


def v_rms(T, M):
    return math.sqrt(3 * R_GAS * T / M)


def f3(v, T, M):
    """3D 速率分布 f(v)，单位 s/m，∫₀^∞ f dv = 1。"""
    a = M / (2 * R_GAS * T)  # 注意：用摩尔质量时 a = M/(2RT)
    return 4 * math.pi * (a / math.pi) ** 1.5 * v * v * math.exp(-a * v * v)


def f2(v, T, M):
    """2D 速率分布（瑞利），∫₀^∞ f dv = 1。"""
    a = M / (2 * R_GAS * T)
    return 2 * a * v * math.exp(-a * v * v)


def f1(v, T, M):
    """1D 速度分量分布（高斯，v 可正可负），∫_{-∞}^{∞} f dv = 1。"""
    a = M / (2 * R_GAS * T)
    return math.sqrt(a / math.pi) * math.exp(-a * v * v)


def trapz(fn, lo, hi, n=200000):
    h = (hi - lo) / n
    s = 0.5 * (fn(lo) + fn(hi))
    for i in range(1, n):
        s += fn(lo + i * h)
    return s * h


# ----------------------------------------------------------------- 自检
def check():
    T, M = 300.0, M_N2
    vp_exact = vp(T, M)

    norm = trapz(lambda v: f3(v, T, M), 0, 12 * vp_exact)
    m1 = trapz(lambda v: v * f3(v, T, M), 0, 12 * vp_exact)
    m2 = trapz(lambda v: v * v * f3(v, T, M), 0, 12 * vp_exact)

    # 峰值：先在粗网格里找，再用抛物线细化
    best, best_v, step = -1.0, 0.0, vp_exact / 400
    v = 0.0
    while v < 6 * vp_exact:
        y = f3(v, T, M)
        if y > best:
            best, best_v = y, v
        v += step

    n2 = trapz(lambda v: f2(v, T, M), 0, 12 * vp_exact)
    n1 = trapz(lambda v: f1(v, T, M), -12 * vp_exact, 12 * vp_exact)

    print(f"T = {T} K, N2")
    print(f"  归一化 ∫f3 dv        = {norm:.9f}")
    print(f"  峰值 v_peak          = {best_v:.2f} m/s   （解析 v_p = {vp_exact:.2f}）")
    print(f"  ∫v f3 dv             = {m1:.2f} m/s   （解析 v_mean = {v_mean(T, M):.2f}）")
    print(f"  √(∫v² f3 dv)         = {math.sqrt(m2):.2f} m/s   （解析 v_rms = {v_rms(T, M):.2f}）")
    print(f"  归一化 2D / 1D       = {n2:.9f} / {n1:.9f}")

    for name, MM in (("N2", M_N2), ("H2", M_H2)):
        for TT in (100, 300, 1000):
            print(f"  {name} {TT:>5} K : v_p={vp(TT, MM):7.1f}  v_mean={v_mean(TT, MM):7.1f}  "
                  f"v_rms={v_rms(TT, MM):7.1f}  比值 1:{v_mean(TT, MM)/vp(TT, MM):.4f}:{v_rms(TT, MM)/vp(TT, MM):.4f}")


# ----------------------------------------------------------------- 画图工具
def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, int(size * S))


def text(d, xy, s, size=16, fill=INK, bold=False, anchor="mm"):
    d.text((xy[0] * S, xy[1] * S), s, font=font(size, bold), fill=fill, anchor=anchor)


def rich(d, xy, parts, size=16, fill=INK, bold=False, anchor="lm"):
    """带上下标的拼接文本（中文字体缺下标字形，只能自己拼）。"""
    widths = [d.textlength(s, font=font(size * sc, bold)) / S for s, sc, _ in parts]
    x = xy[0]
    if anchor == "mm":
        x -= sum(widths) / 2
    elif anchor == "rm":
        x -= sum(widths)
    for (s, sc, dy), w in zip(parts, widths):
        d.text((x * S, (xy[1] + dy) * S), s, font=font(size * sc, bold), fill=fill, anchor="lm")
        x += w


def line(d, p1, p2, fill=AXIS, width=1.5, dash=None):
    if dash is None:
        d.line([p1[0] * S, p1[1] * S, p2[0] * S, p2[1] * S], fill=fill, width=int(width * S))
        return
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    t = 0.0
    on, off = dash
    while t < length:
        e = min(t + on, length)
        d.line([(x1 + ux * t) * S, (y1 + uy * t) * S, (x1 + ux * e) * S, (y1 + uy * e) * S],
               fill=fill, width=int(width * S))
        t = e + off


class Plot:
    """很朴素的坐标系：世界坐标 → 像素坐标。"""

    def __init__(self, w, h, box, xlim, ylim):
        self.img = Image.new("RGB", (int(w * S), int(h * S)), WHITE)
        self.d = ImageDraw.Draw(self.img)
        self.w, self.h = w, h
        self.l, self.t, self.r, self.b = box
        self.xmin, self.xmax = xlim
        self.ymin, self.ymax = ylim

    def X(self, x):
        return self.l + (x - self.xmin) / (self.xmax - self.xmin) * (self.r - self.l)

    def Y(self, y):
        return self.b - (y - self.ymin) / (self.ymax - self.ymin) * (self.b - self.t)

    def frame(self, xticks, yticks, xfmt=str, yfmt=str, grid=True):
        d = self.d
        if grid:
            for x in xticks:
                line(d, (self.X(x), self.t), (self.X(x), self.b), GRID, 1)
            for y in yticks:
                line(d, (self.l, self.Y(y)), (self.r, self.Y(y)), GRID, 1)
        line(d, (self.l, self.b), (self.r, self.b), AXIS, 1.5)
        line(d, (self.l, self.t), (self.l, self.b), AXIS, 1.5)
        for x in xticks:
            line(d, (self.X(x), self.b), (self.X(x), self.b + 6), AXIS, 1.5)
            text(d, (self.X(x), self.b + 22), xfmt(x), 15, MUTED)
        for y in yticks:
            line(d, (self.l - 6, self.Y(y)), (self.l, self.Y(y)), AXIS, 1.5)
            text(d, (self.l - 12, self.Y(y)), yfmt(y), 15, MUTED, anchor="rm")

    def curve(self, fn, color, xs, width=2.6):
        pts = [(self.X(x) * S, self.Y(fn(x)) * S) for x in xs]
        self.d.line(pts, fill=color, width=int(width * S), joint="curve")

    def dot(self, x, y, color, r=5):
        self.d.ellipse([(self.X(x) - r) * S, (self.Y(y) - r) * S,
                        (self.X(x) + r) * S, (self.Y(y) + r) * S], fill=color)

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        out = OUT / name
        self.img.resize((int(self.w), int(self.h)), Image.LANCZOS).save(out, optimize=True)
        print("written", out)


def sample(lo, hi, n=500):
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


# ----------------------------------------------------------------- 图 1
def fig_speed():
    T = 300.0
    M = M_N2
    p = Plot(1000, 620, (95, 55, 955, 520), (0, 1600), (0, 4.0))
    d = p.d

    ticks_x = list(range(0, 1601, 200))
    ticks_y = [0, 1, 2, 3, 4]
    p.frame(ticks_x, ticks_y, yfmt=lambda y: f"{y:g}")

    for temp, color in ((100, C100), (300, C300), (1000, C1000)):
        p.curve(lambda v, temp=temp: f3(v, temp, M) * 1e3, color, sample(0, 1600, 800))
        peak_v = vp(temp, M)
        peak_y = f3(peak_v, temp, M) * 1e3
        p.dot(peak_v, peak_y, color)

    # 峰值标注
    for temp, color, dx, dy in ((100, C100, 18, -14), (300, C300, 20, -14), (1000, C1000, 22, -14)):
        pv = vp(temp, M)
        py = f3(pv, temp, M) * 1e3
        rich(d, (p.X(pv) + dx, p.Y(py) + dy), [("v", 1, 0), ("p", 0.7, 3)], 14, color, anchor="lm")

    # 图例
    lx, ly = 640, 95
    for i, (temp, color) in enumerate(((100, C100), (300, C300), (1000, C1000))):
        y = ly + i * 34
        line(d, (lx, y), (lx + 44, y), color, 3)
        text(d, (lx + 56, y), f"T = {temp} K", 16, INK, anchor="lm")

    # 轴标题
    rich(d, (p.X(800), 590), [("速率 v /（m·s", 1, 0), ("−1", 0.7, -6), ("）", 1, 0)], 17, INK, anchor="mm")
    rich(d, (28, 90), [("f", 1, 0), ("v", 0.72, 4)], 17, INK, anchor="lm")
    rich(d, (44, 92), [("(v) /（10", 1, 0), ("−3", 0.7, -6), (" s·m", 1, 0), ("−1", 0.7, -6), ("）", 1, 0)], 15, MUTED, anchor="lm")

    rich(d, (640, 202), [("N", 1, 0), ("2", 0.7, 3.5), ("，M = 28 g/mol", 1, 0)], 13, MUTED, anchor="lm")
    text(d, (640, 224), "每条曲线下面积 = 1", 13, MUTED, anchor="lm")
    p.save("fig-maxwell.png")


# ----------------------------------------------------------------- 图 2
def fig_compare():
    T = 300.0
    M = M_N2
    v_p = vp(T, M)
    p = Plot(1000, 560, (95, 50, 940, 455), (0, 3.0), (0, 0.95))
    d = p.d

    p.frame([0, 0.5, 1, 1.5, 2, 2.5, 3], [0, 0.2, 0.4, 0.6, 0.8],
            xfmt=lambda x: f"{x:g}", yfmt=lambda y: f"{y:g}")

    xs = sample(0, 3, 700)
    p.curve(lambda x: math.sqrt(1 / math.pi) * math.exp(-x * x), C1D, xs)
    p.curve(lambda x: 2 * x * math.exp(-x * x), C2D, xs)
    p.curve(lambda x: 4 / math.sqrt(math.pi) * x * x * math.exp(-x * x), C3D, xs)

    line(d, (p.X(1), p.t + 8), (p.X(1), p.b), MUTED, 1.4, dash=(7, 6))
    rich(d, (p.X(1) + 8, p.t + 22), [("x = v / v", 1, 0), ("p", 0.7, 3), (" = 1", 1, 0)], 14, MUTED, anchor="lm")

    ly = 70
    for i, (c, s) in enumerate(((C1D, "1D 速度分量（高斯）"),
                                (C2D, "2D 速率（瑞利）"),
                                (C3D, "3D 速率（麦克斯韦）"))):
        y = ly + i * 32
        line(d, (640, y), (684, y), c, 3)
        text(d, (696, y), s, 15, INK, anchor="lm")

    rich(d, (p.X(1.5), 528), [("横轴以最概然速率为单位：x = v / v", 1, 0), ("p", 0.7, 3.5)], 15, INK, anchor="mm")
    rich(d, (28, 80), [("f", 1, 0), ("x", 0.72, 4), ("（x）", 1, 0)], 17, INK, anchor="lm")
    p.save("fig-1d2d3d.png")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        fig_speed()
        fig_compare()
