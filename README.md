# 物理笔记

用 Markdown 写的物理读书笔记：**公式全部 LaTeX**（GitHub 直接渲染），**插图全部由脚本生成**，不手敲字符画。

## 目录

| 笔记 | 主题 | 插图 | 复现脚本 |
|---|---|---|---|
| [麦克斯韦速率分布](notes/maxwell-distribution.md) | 从玻尔兹曼因子到 $v_p$、$\bar v$、$v_{\mathrm{rms}}$，含 1D/2D/3D 分布对比 | 2 张 | `scripts/plot_maxwell.py` |

## 复现

```bash
pip install pillow

python scripts/plot_maxwell.py --check   # 数值自检：归一化、峰值、一阶矩、二阶矩
python scripts/plot_maxwell.py           # 重新生成图片到 notes/assets/
```

环境：Python 3.10+，Pillow。图以 2 倍超采样绘制再缩放，线条和文字不会发毛。

`--check` 的输出应当类似：

```
归一化 ∫f3 dv        = 1.000000000
峰值 v_peak          = 421.99 m/s   （解析 v_p = 421.99）
∫v f3 dv             = 476.17 m/s   （解析 v_mean = 476.17）
√(∫v² f3 dv)         = 516.83 m/s   （解析 v_rms = 516.83）
```

## 排版约定

1. **公式**：行内 `$…$`，独立公式 `$$…$$` 单独成段。GitHub 的 Markdown 渲染器支持 LaTeX（MathJax），
   但要注意：表格单元格里别写 `|`，用 `\vert`；中文放 `\text{…}` 里。
2. **图**：脚本生成 PNG，不提交手绘字符图；每张图配一行斜体图注。
3. **表格**：GFM 表格，不用代码块靠空格对齐。
4. **结构**：笔记在 `notes/`，图在 `notes/assets/`，脚本在 `scripts/`，相对路径互相引用即可。

理由是这些笔记会被反复改：公式改一次就全篇重排，字符画改一次就得手工挪几百个空格；
交给 LaTeX 和脚本，改动只落在源头。

## 许可

暂未指定。如果要让别人引用，建议补一个 `LICENSE`：文字部分用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，
脚本用 MIT，是比较省心的组合。
