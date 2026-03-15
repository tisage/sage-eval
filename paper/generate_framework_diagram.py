"""
Generate Figure 1: SAGE Framework Architecture Diagram (sketch/draft).

Two-panel layout:
  (a) Six-Layer Hierarchy  — L1-L3 rule-based (dashed), L4-L6 LLM-based (solid)
  (b) Evaluation Pipeline  — Dual-mode → Dual-track (iterative + validator) → output
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
})

# ── Colors ────────────────────────────────────────────
RULE_BG   = "#f2f2f2"
RULE_EC   = "#aaaaaa"
LLM_BG    = ["#d5d5d5", "#c5c5c5", "#b5b5b5"]
BORDER    = "#333333"
MODE_BG   = "#e8e8e8"
TRACK_BG  = "#f0f0f0"
TRACK_OUTER = "#fafafa"
AGREE_BG  = "#e0e0e0"
WHITE     = "#ffffff"


def rbox(ax, x, y, w, h, fc="white", ec="black", lw=0.8, ls="-", rad=0.1):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={rad}",
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=2,
    )
    ax.add_patch(p)


def txt(ax, x, y, s, fs=7, fw="normal", ha="center", va="center",
        c="black", style="normal"):
    ax.text(x, y, s, fontsize=fs, fontweight=fw, ha=ha, va=va,
            color=c, fontstyle=style, zorder=3)


def arr(ax, x1, y1, x2, y2, lw=0.7, color="#333333", style="->"):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                        shrinkA=1, shrinkB=1),
        zorder=1,
    )


def main():
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    ax.set_xlim(0, 17)
    ax.set_ylim(1.8, 9.5)  # Crop bottom white space
    ax.axis("off")

    # ════════════════════════════════════════════════════
    #  (a) LEFT PANEL — Six-Layer Hierarchy  (x: 0–6)
    # ════════════════════════════════════════════════════
    txt(ax, 3.0, 9.2, "(a) Six-Layer Hierarchy", fs=9, fw="bold")

    lx, lw_ = 0.2, 5.6

    # ── L1-L3: Rule-Based (dashed borders, darker text) ──
    for i, (lab, desc) in enumerate([
        ("L1", "Lexical Quality"),
        ("L2", "Narrative Structure"),
        ("L3", "Thematic Content"),
    ]):
        y = 8.2 - i * 0.5
        rbox(ax, lx, y, lw_, 0.38, fc=RULE_BG, ec=RULE_EC, lw=0.5, ls="--")
        txt(ax, lx + 0.25, y + 0.19, lab, fs=6.5, fw="bold", ha="left",
            c="#666666")
        txt(ax, lx + 1.0, y + 0.19, desc, fs=5.5, ha="left",
            c="#777777")

    # Rule-based label
    txt(ax, lx + lw_ / 2, 6.85, "Rule-Based (Computational)",
        fs=5.5, c="#777777", style="italic")

    # Dotted separator
    ax.plot([lx + 0.5, lx + lw_ - 0.5], [6.65, 6.65],
            color="#999999", lw=0.4, ls=":", zorder=1)

    # ── L4-L6: LLM-Based (solid borders) ──
    layers_llm = [
        ("L4", "Cultural Representation", "IPD · CVP · CSP · CPC", LLM_BG[0]),
        ("L5", "Emotional-Psychological", "AC · PI · EG · ENC", LLM_BG[1]),
        ("L6", "Existential-Philosophical", "LP · MR · HC · ME", LLM_BG[2]),
    ]
    for i, (lab, focus, dims, bg) in enumerate(layers_llm):
        y = 5.85 - i * 0.78
        rbox(ax, lx, y, lw_, 0.62, fc=bg, ec=BORDER, lw=0.8)
        txt(ax, lx + 0.2, y + 0.4, f"{lab}: {focus}",
            fs=7, fw="bold", ha="left")
        txt(ax, lx + 0.2, y + 0.17, dims, fs=5.5, ha="left",
            c="#444444", style="italic")

    # LLM-based label
    txt(ax, lx + lw_ / 2, 3.72, "LLM-Based (Interpretive)",
        fs=5.5, c="#444444", style="italic")

    # ════════════════════════════════════════════════════
    #  (b) RIGHT PANEL — Evaluation Pipeline  (x: 7–17)
    # ════════════════════════════════════════════════════
    px = 7.3
    pw = 9.2
    pcx = px + pw / 2

    txt(ax, pcx, 9.2, "(b) Evaluation Pipeline", fs=9, fw="bold")

    # ── Story Corpus ──
    cy = 8.35
    rbox(ax, px + 1.0, cy, pw - 2.0, 0.55, fc=WHITE, ec=BORDER)
    txt(ax, pcx, cy + 0.35, "Story Corpus", fs=7.5, fw="bold")
    txt(ax, pcx, cy + 0.14,
        "Canonical (50)  ·  Pulp (30)  ·  LLM-Generated (20)",
        fs=5.5, c="#555555")

    # ── Dual Mode ──
    mw = 3.2
    mg = 0.8
    mx1 = px + (pw - 2 * mw - mg) / 2
    mx2 = mx1 + mw + mg
    my = 7.35

    # V-split arrows from corpus to modes
    arr(ax, pcx, cy, mx1 + mw / 2, my + 0.5, lw=0.7)
    arr(ax, pcx, cy, mx2 + mw / 2, my + 0.5, lw=0.7)

    rbox(ax, mx1, my, mw, 0.45, fc=MODE_BG, ec=BORDER, lw=0.7)
    txt(ax, mx1 + mw / 2, my + 0.3, "Content-Limit", fs=6.5, fw="bold")
    txt(ax, mx1 + mw / 2, my + 0.12, "(Text Only)", fs=5, c="#555555")

    rbox(ax, mx2, my, mw, 0.45, fc=MODE_BG, ec=BORDER, lw=0.7)
    txt(ax, mx2 + mw / 2, my + 0.3, "Title-Limit", fs=6.5, fw="bold")
    txt(ax, mx2 + mw / 2, my + 0.12, "(Title + Author)", fs=5, c="#555555")

    # V-merge lines from mode bottoms to center
    merge_y = 6.9
    ax.plot([mx1 + mw / 2, pcx], [my, merge_y], color=BORDER, lw=0.7,
            zorder=1)
    ax.plot([mx2 + mw / 2, pcx], [my, merge_y], color=BORDER, lw=0.7,
            zorder=1)

    # Label "× 3 Layers"
    txt(ax, pcx + 0.15, merge_y + 0.15, "× 3 Layers (L4, L5, L6)",
        fs=5.5, ha="left", c="#555555", style="italic")

    # Single arrow down to the dual-track container
    dt_outer_top = 6.55
    arr(ax, pcx, merge_y, pcx, dt_outer_top + 0.05, lw=0.7)

    # ── Dual-Track Architecture (container box) ──
    dt_h = 3.6  # Taller container to fit agreement properly
    dt_outer_x = px + 0.2
    dt_outer_w = pw - 0.4
    rbox(ax, dt_outer_x, dt_outer_top - dt_h, dt_outer_w, dt_h,
         fc=TRACK_OUTER, ec=BORDER, lw=0.8, rad=0.12)
    txt(ax, pcx, dt_outer_top - 0.18, "Dual-Track Architecture",
        fs=7.5, fw="bold")

    # Inner boxes: Iterative Evaluator and Independent Validator
    inner_margin = 0.3
    inner_gap = 0.4
    inner_w = (dt_outer_w - 2 * inner_margin - inner_gap) / 2
    inner_top = dt_outer_top - 0.45
    inner_h = 2.05  # Sized to fit R1-R5 content

    ie_x = dt_outer_x + inner_margin
    iv_x = ie_x + inner_w + inner_gap

    # ── Iterative Evaluator ──
    rbox(ax, ie_x, inner_top - inner_h, inner_w, inner_h,
         fc=TRACK_BG, ec=BORDER, lw=0.6)
    txt(ax, ie_x + inner_w / 2, inner_top - 0.18,
        "Iterative Evaluator", fs=6.5, fw="bold")
    txt(ax, ie_x + inner_w / 2, inner_top - 0.38,
        "(5-Round Self-Reflection)", fs=4.5, c="#555555")

    rounds = [
        ("R1", "Initial Assessment"),
        ("R2", "Projection Bias Check"),
        ("R3", "Layer Boundary"),
        ("R4", "Evidence Sufficiency"),
        ("R5", "Final Consolidation"),
    ]
    r_start = inner_top - 0.65
    r_step = 0.32
    for j, (rnum, rdesc) in enumerate(rounds):
        ry = r_start - j * r_step
        rbox(ax, ie_x + 0.15, ry - 0.07, 0.35, 0.18,
             fc="#d0d0d0", ec="#999999", lw=0.3, rad=0.04)
        txt(ax, ie_x + 0.325, ry + 0.02, rnum, fs=5, fw="bold", c="#333333")
        txt(ax, ie_x + 0.65, ry + 0.02, rdesc, fs=5, ha="left", c="#444444")

    # Small down arrows between rounds
    for j in range(4):
        ry1 = r_start - j * r_step - 0.1
        ry2 = r_start - (j + 1) * r_step + 0.1
        arr(ax, ie_x + 0.325, ry1, ie_x + 0.325, ry2,
            lw=0.35, color="#aaaaaa")

    # ── Independent Validator ──
    rbox(ax, iv_x, inner_top - inner_h, inner_w, inner_h,
         fc=TRACK_BG, ec=BORDER, lw=0.6)
    txt(ax, iv_x + inner_w / 2, inner_top - 0.18,
        "Independent Validator", fs=6.5, fw="bold")
    txt(ax, iv_x + inner_w / 2, inner_top - 0.38,
        "(Cross-Verification)", fs=4.5, c="#555555")

    val_items = [
        "Independent Scoring",
        "Projection Bias Detection",
        "Hallucination Detection",
        "Reasoning Quality",
        "Confidence Calibration",
    ]
    for j, item in enumerate(val_items):
        vy = r_start - j * r_step
        txt(ax, iv_x + 0.25, vy + 0.02, f"•  {item}",
            fs=5, ha="left", c="#444444")

    # ── Agreement Analysis (below inner boxes, inside container) ──
    inner_bottom = inner_top - inner_h
    ag_h = 0.4
    ag_gap = 0.2
    ag_margin = 0.8
    ag_y = inner_bottom - ag_gap - ag_h
    ag_w = dt_outer_w - 2 * ag_margin
    rbox(ax, dt_outer_x + ag_margin, ag_y, ag_w, ag_h,
         fc=AGREE_BG, ec="#666666", lw=0.5)
    txt(ax, pcx, ag_y + 0.25, "Agreement Analysis", fs=6, fw="bold")
    txt(ax, pcx, ag_y + 0.08, "Inter-Rater Reliability · MAD < 0.5",
        fs=4.5, c="#555555")

    # Arrows from inner boxes down to agreement
    arr(ax, ie_x + inner_w / 2, inner_bottom,
        pcx - 1.0, ag_y + ag_h + 0.02, lw=0.5, color="#666666")
    arr(ax, iv_x + inner_w / 2, inner_bottom,
        pcx + 1.0, ag_y + ag_h + 0.02, lw=0.5, color="#666666")

    # ── Single arrow from container bottom to Final Assessment ──
    container_bottom = dt_outer_top - dt_h
    out_y = container_bottom - 0.65
    arr(ax, pcx, container_bottom, pcx, out_y + 0.55, lw=0.7)

    rbox(ax, px + 2.0, out_y, pw - 4.0, 0.5, fc=WHITE, ec=BORDER, lw=0.8)
    txt(ax, pcx, out_y + 0.32, "Final Assessment", fs=7, fw="bold")
    txt(ax, pcx, out_y + 0.12,
        "12 Dimensions × 2 Modes × 100 Stories",
        fs=5, c="#555555")

    # ════════════════════════════════════════════════════
    #  CONNECTION: Left panel → Right panel
    # ════════════════════════════════════════════════════
    conn_y = 6.7
    ax.annotate(
        "", xy=(px + 0.1, conn_y), xytext=(lx + lw_ + 0.1, conn_y),
        arrowprops=dict(
            arrowstyle="-|>", color="#555555", lw=1.0,
            shrinkA=3, shrinkB=3,
        ),
        zorder=4,
    )
    txt(ax, (lx + lw_ + px + 0.1) / 2, conn_y + 0.2,
        "evaluated via", fs=5.5, c="#555555", style="italic")

    # ── Save ──
    fig.tight_layout()
    out = OUT_DIR / "framework_diagram.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
