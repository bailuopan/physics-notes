# 这套笔记怎么排版

三条约定，理由是同一个：**笔记会被反复改，改动应该落在源头，而不是散落在几百个空格里。**

## 1. 公式用 LaTeX，不用字符拼

字符拼出来的分式，换个字体、换个屏幕宽度就散架：

```text
            4 p̄² S₀²
P_tr = ────────────────── · R₀
        |2Z₀ + jωM|²
```

同一件事写成 LaTeX，改分子分母只改一个参数：

$$
P_{tr}=\frac{4\bar{p}^{2}S_{0}^{2}}{\left|2Z_{0}+\mathrm{j}\omega M\right|^{2}}\,R_{0}
$$

GitHub 的 Markdown 渲染器支持 LaTeX（MathJax），所以仓库里的 `.md` 直接打开就有公式。
本地预览建议用 Typora、Obsidian 或 VS Code + Markdown Preview Enhanced。

## 2. 图由脚本生成，不手绘字符画

字符画（`┌─┐│▓`）有三个硬伤：对齐脆弱、无法缩放、改一个数字要手工挪几十个空格。

这里的做法是：**脚本里写坐标和函数，图是编译产物。**

```bash
python scripts/plot_maxwell.py --check   # 先验数学，再画图
python scripts/plot_maxwell.py
```

好处：

- 参数改了重跑一遍即可，不用手工排版；
- 图里每个数字都能追到公式；
- `--check` 保证画出来的是对的曲线，而不是"看起来像"的曲线。

出图用 Pillow 手绘坐标系，2 倍超采样后缩放，不依赖 matplotlib（免去装包和中文字体的坑）。
如果以后要画更复杂的图，换成 matplotlib 也可以，`f(v)` 那一层函数不用改。

## 3. 表格用 GFM，不用代码块对齐

```markdown
| 气体 | 温度 | v_p |
|---|---|---|
| N₂ | 300 K | 422 |
```

代码块里的表格在手机上会折行，在窄窗口里会错位；GFM 表格由渲染器负责排版。

## 目录约定

```
notes/          笔记正文（每篇一个 .md）
notes/assets/   图片（脚本输出，文件名用 ASCII）
scripts/        出图与自检脚本
docs/           说明文档
```
