"""
Generate figures for the SAGE framework paper.

Figure 2: Genre comparison grouped bar chart (replaces Table 3)
Figure 3: Score convergence trajectory across 5 iterative rounds
Figure 4: Effect size (Cohen's d) comparison across layers
"""

import json
from pathlib import Path
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
RESULTS = BASE / "results"
L4_CSV = RESULTS / "phase4_layer4_full_50v50" / "LAYER4_FINAL_RESULTS.csv"
L5_CSV = RESULTS / "phase4_layer5_full_50v50" / "LAYER5_FINAL_RESULTS.csv"
L4_JSON_DIR = RESULTS / "SAGE_FINAL_DATASET" / "layer4_cultural"
L5_JSON_DIR = RESULTS / "SAGE_FINAL_DATASET" / "layer5_emotional"
L6_JSON_DIR = RESULTS / "layer6_existential_parallel_20260221_200743"
OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(exist_ok=True)

# ── Style ──────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 9,
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
})

# Bar chart colors & hatching
COLOR_CANONICAL = "#1a1a1a"
COLOR_PULP      = "#808080"
COLOR_LLM       = "#d9d9d9"

CATEGORY_COLORS = {
    "canonical": COLOR_CANONICAL,
    "pulp": COLOR_PULP,
    "llm_generated": COLOR_LLM,
}
CATEGORY_HATCHES = {
    "canonical": "",
    "pulp": "",
    "llm_generated": "",
}

# Line chart styles (all dark enough to be visible)
CATEGORY_LINECOLORS = {
    "canonical": "#1a1a1a",
    "pulp": "#606060",
    "llm_generated": "#404040",
}
CATEGORY_LINESTYLES = {
    "canonical": "-",
    "pulp": "--",
    "llm_generated": "-.",
}
CATEGORY_MARKERS = {
    "canonical": "o",
    "pulp": "s",
    "llm_generated": "^",
}
CATEGORY_LABELS = {
    "canonical": "Canonical",
    "pulp": "Pulp",
    "llm_generated": "LLM-Generated",
}
LAYER_LABELS = {
    4: "L4: Cultural",
    5: "L5: Emotional",
    6: "L6: Existential",
}


# ── Helpers ────────────────────────────────────────────────────────
def build_category_map():
    df = pd.read_csv(L4_CSV)
    return dict(zip(df["story_id"], df["category"]))


def extract_round_scores(json_dir, category_map):
    data = defaultdict(lambda: defaultdict(list))
    for fpath in sorted(json_dir.glob("layer*_*.json")):
        if "batch_summary" in fpath.name or "backup" in fpath.name:
            continue
        try:
            with open(fpath) as f:
                obj = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        story_id = obj.get("story_id", "")
        cat = category_map.get(story_id)
        if cat is None:
            continue
        for r in obj.get("primary_result", {}).get("rounds", []):
            rnd = r.get("round")
            score = r.get("iterative_overall_score")
            if rnd is not None and score is not None:
                data[cat][rnd].append(score)
    return data


def save_png(fig, name):
    out = OUT_DIR / f"{name}.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[OK] {out}")


# ══════════════════════════════════════════════════════════════════
#  FIGURE 2: Genre Comparison Grouped Bar Chart
# ══════════════════════════════════════════════════════════════════

def figure_genre_comparison():
    scores = {
        "canonical":     [3.96, 4.15, 3.95],
        "pulp":          [3.83, 4.04, 3.68],
        "llm_generated": [2.55, 3.36, 2.59],
    }
    stds = {
        "canonical":     [0.41, 0.31, 0.57],
        "pulp":          [0.36, 0.24, 0.56],
        "llm_generated": [0.62, 0.59, 0.57],
    }
    layers = ["Cultural\n(L4)", "Emotional\n(L5)", "Existential\n(L6)"]

    # 可以稍微加高一点画布，给顶部的图例留出空间
    fig, ax = plt.subplots(figsize=(3.5, 2.8)) 

    x = np.arange(len(layers))
    width = 0.22
    offsets = [-width, 0, width]

    for i, cat in enumerate(["canonical", "pulp", "llm_generated"]):
        bars = ax.bar(
            x + offsets[i], scores[cat], width,
            yerr=stds[cat],
            label=CATEGORY_LABELS[cat], # 假设你已在外部定义
            color=CATEGORY_COLORS[cat], # 假设你已在外部定义
            edgecolor="black",
            linewidth=0.6,
            hatch=CATEGORY_HATCHES[cat], # 假设你已在外部定义
            capsize=2,
            error_kw={"linewidth": 0.7, "capthick": 0.7},
        )
        
        # 修复 1：动态调整数字位置，避开向下延伸的误差线
        for j, (bar, val) in enumerate(zip(bars, scores[cat])):
            text_color = "white" if cat != "llm_generated" else "black"
            
            # 计算当前柱子的误差线向下延伸到了哪里
            error_down = stds[cat][j]
            # 将文字放在误差线下端再往下 0.1 的位置 (也可以直接放中间：y_pos = bar.get_height() / 2)
            y_pos = bar.get_height() - error_down - 0.1 
            
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y_pos,
                f"{val:.2f}", ha="center", va="top",
                fontsize=5.5, fontweight="bold", color=text_color,
            )

    ax.set_ylabel("Mean Score (1\u20135)", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(layers, fontsize=8)
    ax.set_ylim(0, 5.2)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 美化项：在柱子后方添加浅色的水平网格线，提升专业感和可读性
    ax.set_axisbelow(True) 
    ax.yaxis.grid(True, color='gray', linestyle='dashed', alpha=0.3)

    # 修复 2：将图例放置在图表外侧的正上方，并改为水平排列 (ncol=3)
    ax.legend(
        loc="lower center", 
        bbox_to_anchor=(0.5, 1.0), # 将图例锚点设在 X轴中心，Y轴顶端稍上
        ncol=3,                     # 改为 3 列水平排列
        frameon=False,              # 去掉图例边框，显得更清爽
        fontsize=7, 
        handlelength=1.5,
        columnspacing=1.0
    )

    fig.tight_layout()
    # plt.show() # 如果需要预览可以打开
    save_png(fig, "genre_comparison") # 假设你已在外部定义


# ══════════════════════════════════════════════════════════════════
#  FIGURE 3: Score Convergence Trajectory
# ══════════════════════════════════════════════════════════════════
def figure_convergence_trajectory():
    category_map = build_category_map()
    layer_dirs = {4: L4_JSON_DIR, 5: L5_JSON_DIR, 6: L6_JSON_DIR}

    fig, axes = plt.subplots(1, 3, figsize=(6.8, 2.2), sharey=True)

    for idx, (layer_num, json_dir) in enumerate(layer_dirs.items()):
        ax = axes[idx]
        round_data = extract_round_scores(json_dir, category_map)

        for cat in ["canonical", "pulp", "llm_generated"]:
            means, stds = [], []
            rounds_present = sorted(round_data[cat].keys())
            for rnd in rounds_present:
                vals = round_data[cat][rnd]
                means.append(np.mean(vals))
                stds.append(np.std(vals))

            means = np.array(means)
            rounds_x = np.array(rounds_present)

            ax.plot(
                rounds_x, means,
                marker=CATEGORY_MARKERS[cat],
                markersize=4, linewidth=1.5,
                linestyle=CATEGORY_LINESTYLES[cat],
                color=CATEGORY_LINECOLORS[cat],
                label=CATEGORY_LABELS[cat],
                markeredgecolor="black",
                markeredgewidth=0.5,
                markerfacecolor=CATEGORY_LINECOLORS[cat],
            )

        ax.set_title(LAYER_LABELS[layer_num], fontsize=9.5)
        ax.set_xlabel("Round")
        ax.set_xticks([1, 2, 3, 4, 5])
        ax.set_xlim(0.7, 5.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        # Horizontal grid lines instead of shaded bands
        ax.yaxis.grid(True, linestyle="--", linewidth=0.4, alpha=0.5)
        ax.set_axisbelow(True)

    axes[0].set_ylabel("Mean Score")
    axes[0].set_ylim(1.5, 5.0)
    axes[0].yaxis.set_major_locator(ticker.MultipleLocator(0.5))

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="lower center", ncol=3,
        bbox_to_anchor=(0.5, -0.02), frameon=False, fontsize=8,
    )

    fig.tight_layout(rect=[0, 0.08, 1, 1])
    save_png(fig, "convergence_trajectory")


# ══════════════════════════════════════════════════════════════════
#  FIGURE 4: Effect Size Comparison (Cohen's d)
# ══════════════════════════════════════════════════════════════════
def figure_effect_sizes():
    layers = ["L4: Cultural", "L5: Emotional", "L6: Existential"]
    cohens_d = [2.68, 1.68, 2.40]
    # Three distinct colors
    colors = ["#1a1a1a", "#999999", "#4a4a4a"]

    fig, ax = plt.subplots(figsize=(3.3, 1.6))

    y = np.arange(len(layers))
    bars = ax.barh(
        y, cohens_d, height=0.5,
        color=colors, edgecolor="black", linewidth=0.6,
    )

    # Threshold line with label above chart
    ax.axvline(x=0.8, color="#c0392b", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.text(0.82, -0.55, "large (0.8)", fontsize=6.5, color="#c0392b", va="top")

    for bar, val in zip(bars, cohens_d):
        ax.text(
            bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
            f"d = {val:.2f}", ha="left", va="center", fontsize=8, fontweight="bold",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(layers)
    ax.set_xlabel("Cohen's d (Canonical vs LLM)")
    ax.set_xlim(0, 3.3)
    ax.set_ylim(2.6, -0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    save_png(fig, "effect_sizes")


# ── Main ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating paper figures...")
    print(f"Output: {OUT_DIR}")
    print()
    figure_genre_comparison()
    figure_convergence_trajectory()
    figure_effect_sizes()
    print("\nAll figures generated.")
