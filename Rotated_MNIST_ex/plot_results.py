"""
plot_results.py
===============
Generate all presentation figures for the Rotated-MNIST Deep CORAL analysis.

Produces 5 publication-ready plots saved to ./figures/:
  1. gap_curve.png         — accuracy vs. rotation angle (3 lines)
  2. coral_gain.png        — CORAL absolute gain & gap closed (side-by-side bars)
  3. per_class_heatmap.png — per-class accuracy heatmap across angles
  4. per_class_bars.png    — grouped bar chart per digit per angle (source-only)
  5. upper_bound.png       — source-only vs upper bound ceiling

Usage
-----
python plot_results.py

All data is hardcoded from results_summary.txt files. Edit the DATA section
below if you re-run experiments with different seeds or hyperparameters.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

os.makedirs("./figures", exist_ok=True)

# =============================================================================
# DATA  — sourced directly from results_summary.txt files
# =============================================================================

ANGLES = [15, 30, 45, 60, 75]

SOURCE_ONLY = {
    15: 0.9841,
    30: 0.8953,
    45: 0.6552,
    60: 0.3807,
    75: 0.2388,
}

CORAL = {
    # 15°: not run (gap too small)
    30: 0.9035,   # lambda=1.0
    45: 0.7031,   # lambda=25.0
    60: 0.4584,   # lambda=1.0
    75: 0.2696,   # lambda=1.0
}

UPPER_BOUND = {
    # 15°: not run
    30: 0.9935,
    45: 0.9919,
    60: 0.9916,
    75: 0.9924,
}

SOURCE_ACC = 0.9948   # source test accuracy (same for all runs)

PER_CLASS_SOURCE_ONLY = {
    15: [0.997, 0.995, 0.967, 0.983, 0.987, 0.984, 0.981, 0.981, 0.989, 0.977],
    30: [0.994, 0.987, 0.846, 0.904, 0.796, 0.887, 0.932, 0.744, 0.939, 0.919],
    45: [0.988, 0.772, 0.595, 0.647, 0.327, 0.541, 0.807, 0.317, 0.784, 0.762],
    60: [0.987, 0.530, 0.162, 0.136, 0.129, 0.191, 0.418, 0.284, 0.588, 0.369],
    75: [0.960, 0.228, 0.036, 0.006, 0.065, 0.068, 0.146, 0.318, 0.459, 0.105],
}

# Derived quantities
CORAL_GAIN_PP   = {a: CORAL[a] - SOURCE_ONLY[a] for a in CORAL}
GAP             = {a: SOURCE_ACC - SOURCE_ONLY[a] for a in ANGLES}
GAP_CLOSED_PCT  = {a: CORAL_GAIN_PP[a] / GAP[a] * 100 for a in CORAL}

# =============================================================================
# STYLE
# =============================================================================

BLUE   = "#2563EB"
GREEN  = "#059669"
GRAY   = "#6B7280"
ORANGE = "#D97706"
RED    = "#DC2626"

ANGLE_COLORS = ["#93C5FD", "#3B82F6", "#1D4ED8", "#059669", "#065F46"]  # light→dark per angle

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.25,
    "grid.linestyle":    "--",
    "figure.dpi":        150,
    "savefig.dpi":       150,
})

LABEL_STYLE = dict(fontsize=9, ha="center", va="bottom")

# =============================================================================
# FIG 1 — GAP CURVE
# =============================================================================

def plot_gap_curve():
    fig, ax = plt.subplots(figsize=(7, 4.5))

    coral_angles = sorted(CORAL.keys())
    ub_angles    = sorted(UPPER_BOUND.keys())

    ax.plot(ANGLES,
            [SOURCE_ONLY[a] * 100 for a in ANGLES],
            "o-", color=BLUE, linewidth=2.2, markersize=7,
            label="Source-only baseline", zorder=3)

    ax.plot(coral_angles,
            [CORAL[a] * 100 for a in coral_angles],
            "s--", color=GREEN, linewidth=2.2, markersize=7,
            label="Deep CORAL (λ=1)", zorder=3)

    ax.plot(ub_angles,
            [UPPER_BOUND[a] * 100 for a in ub_angles],
            "^:", color=GRAY, linewidth=1.8, markersize=6,
            label="Supervised upper bound", zorder=3)

    # Shaded gap between source-only and upper bound
    ub_y  = [UPPER_BOUND[a] * 100 for a in ub_angles]
    src_y = [SOURCE_ONLY[a] * 100 for a in ub_angles]
    ax.fill_between(ub_angles, src_y, ub_y, alpha=0.07, color=BLUE, label="_nolegend_")

    # Annotate CORAL gain at 45° and 60°
    for a in [45, 60]:
        ax.annotate(
            f"+{CORAL_GAIN_PP[a]*100:.1f} pp",
            xy=(a, CORAL[a] * 100),
            xytext=(a + 2, CORAL[a] * 100 + 4),
            fontsize=8.5, color=GREEN,
            arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.8),
        )

    ax.axhline(10, color=RED, linestyle=":", linewidth=1, alpha=0.5)
    ax.text(76, 11.5, "chance (10%)", fontsize=8, color=RED, alpha=0.7)

    ax.set_xlabel("Target rotation angle (degrees)", fontsize=11)
    ax.set_ylabel("Target test accuracy (%)", fontsize=11)
    ax.set_title("Accuracy vs. domain gap — Rotated MNIST", fontsize=13, fontweight="bold", pad=10)
    ax.set_xticks(ANGLES)
    ax.set_xticklabels([f"{a}°" for a in ANGLES])
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right", fontsize=9.5, framealpha=0.9)

    fig.tight_layout()
    fig.savefig("./figures/gap_curve.png")
    plt.close(fig)
    print("Saved: ./figures/gap_curve.png")


# =============================================================================
# FIG 2 — CORAL GAIN (side-by-side)
# =============================================================================

def plot_coral_gain():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

    coral_angles = sorted(CORAL.keys())
    x = np.arange(len(coral_angles))
    w = 0.55

    bar_colors = [ANGLE_COLORS[ANGLES.index(a)] for a in coral_angles]

    # Left: absolute gain
    bars1 = ax1.bar(x, [CORAL_GAIN_PP[a] * 100 for a in coral_angles],
                    width=w, color=bar_colors, edgecolor="white", linewidth=0.5, zorder=3)
    for bar, a in zip(bars1, coral_angles):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.15,
                 f"{CORAL_GAIN_PP[a]*100:.1f} pp",
                 **LABEL_STYLE)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{a}°" for a in coral_angles])
    ax1.set_ylabel("Absolute accuracy gain (pp)", fontsize=10)
    ax1.set_title("CORAL absolute gain", fontsize=12, fontweight="bold")
    ax1.set_ylim(0, 12)

    # Right: gap closed %
    bars2 = ax2.bar(x, [GAP_CLOSED_PCT[a] for a in coral_angles],
                    width=w, color=bar_colors, edgecolor="white", linewidth=0.5, zorder=3)
    for bar, a in zip(bars2, coral_angles):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.3,
                 f"{GAP_CLOSED_PCT[a]:.1f}%",
                 **LABEL_STYLE)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{a}°" for a in coral_angles])
    ax2.set_ylabel("Percentage of gap closed (%)", fontsize=10)
    ax2.set_title("CORAL gap closed", fontsize=12, fontweight="bold")
    ax2.set_ylim(0, 22)

    fig.suptitle("Deep CORAL effectiveness across rotation angles", fontsize=13,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig("./figures/coral_gain.png")
    plt.close(fig)
    print("Saved: ./figures/coral_gain.png")


# =============================================================================
# FIG 3 — PER-CLASS HEATMAP
# =============================================================================

def plot_per_class_heatmap():
    data = np.array([PER_CLASS_SOURCE_ONLY[a] for a in ANGLES])  # (5, 10)

    cmap = LinearSegmentedColormap.from_list(
        "coral_map", ["#DC2626", "#F59E0B", "#D1FAE5", "#059669"], N=256
    )

    fig, ax = plt.subplots(figsize=(9, 4))
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(10))
    ax.set_xticklabels([f"digit {i}" for i in range(10)], fontsize=10)
    ax.set_yticks(range(len(ANGLES)))
    ax.set_yticklabels([f"{a}°" for a in ANGLES], fontsize=10)
    ax.set_xlabel("Digit class", fontsize=11)
    ax.set_ylabel("Target rotation angle", fontsize=11)
    ax.set_title("Per-class accuracy — source-only baseline", fontsize=13,
                 fontweight="bold", pad=10)

    for i in range(len(ANGLES)):
        for j in range(10):
            val = data[i, j]
            color = "white" if val < 0.45 else "#1e293b"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=8.5, color=color, fontweight="500")

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Accuracy", fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    fig.tight_layout()
    fig.savefig("./figures/per_class_heatmap.png")
    plt.close(fig)
    print("Saved: ./figures/per_class_heatmap.png")


# =============================================================================
# FIG 4 — PER-CLASS GROUPED BARS
# =============================================================================

def plot_per_class_bars():
    digits = list(range(10))
    n_angles = len(ANGLES)
    x = np.arange(10)
    total_w = 0.75
    w = total_w / n_angles

    fig, ax = plt.subplots(figsize=(12, 5))

    for i, (angle, color) in enumerate(zip(ANGLES, ANGLE_COLORS)):
        offset = (i - n_angles / 2 + 0.5) * w
        ax.bar(x + offset, PER_CLASS_SOURCE_ONLY[angle],
               width=w * 0.92, color=color,
               edgecolor="white", linewidth=0.4,
               label=f"{angle}°", zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels([f"digit {d}" for d in digits], fontsize=10)
    ax.set_ylabel("Target test accuracy", fontsize=11)
    ax.set_ylim(0, 1.08)
    ax.set_title("Per-class accuracy by rotation angle — source-only baseline",
                 fontsize=13, fontweight="bold", pad=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))

    legend_patches = [
        mpatches.Patch(color=ANGLE_COLORS[i], label=f"{a}°")
        for i, a in enumerate(ANGLES)
    ]
    ax.legend(handles=legend_patches, title="Target angle",
              fontsize=9.5, title_fontsize=9.5, loc="upper right",
              framealpha=0.9, ncol=5)

    # Highlight most degraded digits
    for d in [3, 4, 7]:
        ax.axvspan(d - 0.45, d + 0.45, alpha=0.06, color=RED, zorder=0)

    ax.text(3, 1.055, "hardest at\nlarge angles", ha="center",
            fontsize=7.5, color=RED, alpha=0.8)

    fig.tight_layout()
    fig.savefig("./figures/per_class_bars.png")
    plt.close(fig)
    print("Saved: ./figures/per_class_bars.png")


# =============================================================================
# FIG 5 — SOURCE-ONLY vs UPPER BOUND
# =============================================================================

def plot_upper_bound():
    ub_angles = sorted(UPPER_BOUND.keys())
    x = np.arange(len(ub_angles))
    w = 0.32

    fig, ax = plt.subplots(figsize=(7, 4.5))

    bars_src = ax.bar(x - w / 2,
                      [SOURCE_ONLY[a] * 100 for a in ub_angles],
                      width=w, color=BLUE, label="Source-only baseline",
                      edgecolor="white", linewidth=0.5, zorder=3)

    bars_ub = ax.bar(x + w / 2,
                     [UPPER_BOUND[a] * 100 for a in ub_angles],
                     width=w, color=GRAY, label="Supervised upper bound",
                     edgecolor="white", linewidth=0.5, zorder=3)

    for bar in bars_src:
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.8,
                f"{bar.get_height():.1f}%",
                **LABEL_STYLE)

    for bar in bars_ub:
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.8,
                f"{bar.get_height():.1f}%",
                **LABEL_STYLE, color=GRAY)

    # Draw ceiling line
    ax.axhline(99.2, color=GRAY, linestyle=":", linewidth=1.2, alpha=0.6)
    ax.text(len(ub_angles) - 0.4, 99.8, "~99% ceiling", fontsize=8.5,
            color=GRAY, alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{a}°" for a in ub_angles])
    ax.set_xlabel("Target rotation angle (degrees)", fontsize=11)
    ax.set_ylabel("Target test accuracy (%)", fontsize=11)
    ax.set_title("Architecture ceiling vs. source-only — the gap is not the model",
                 fontsize=12, fontweight="bold", pad=10)
    ax.set_ylim(0, 108)
    ax.legend(fontsize=10, framealpha=0.9)

    fig.tight_layout()
    fig.savefig("./figures/upper_bound.png")
    plt.close(fig)
    print("Saved: ./figures/upper_bound.png")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("Generating figures...")
    plot_gap_curve()
    plot_coral_gain()
    plot_per_class_heatmap()
    plot_per_class_bars()
    plot_upper_bound()
    print("\nAll figures saved to ./figures/")
    print("Files:")
    for f in sorted(os.listdir("./figures")):
        print(f"  ./figures/{f}")
