"""Generates publication-quality charts for the project report using Matplotlib."""

from pathlib import Path
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import numpy as np

# UI matching Midnight Indigo palette
BG_COLOR = "#0B1020"
PANEL_COLOR = "#121A2F"
TEXT_COLOR = "#E6EAF5"
TEXT_MUTED = "#94A0BF"
GRID_COLOR = "#1F2B4A"
BRAND_COLOR = "#6C8CFF"  # Periwinkle
ACCENT_COLOR = "#22D3EE"  # Cyan
SUCCESS_COLOR = "#34D399"  # Emerald
WARN_COLOR = "#FBBF24"  # Amber
DANGER_COLOR = "#F87171"  # Coral Red


def _apply_dark_style(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_facecolor(PANEL_COLOR)
    ax.set_title(title, color=TEXT_COLOR, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, color=TEXT_MUTED, fontsize=10, labelpad=8)
    ax.set_ylabel(ylabel, color=TEXT_MUTED, fontsize=10, labelpad=8)
    ax.tick_params(colors=TEXT_MUTED, labelsize=9)
    ax.grid(True, linestyle="--", linewidth=0.5, color=GRID_COLOR, alpha=0.7)
    for spine in ax.spines.values():
        spine.set_color("#2F3F8F")
        spine.set_linewidth(0.8)


def generate_all_plots(
    detection_data: List[Dict[str, Any]],
    strategies_data: List[Dict[str, Any]],
    models_data: Dict[str, Any],
    scalability_data: List[Dict[str, Any]],
    output_dir: Path,
) -> None:
    """Renders and saves all 5 report figures at 200 DPI."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("dark_background")

    # 1. Detection vs Budget
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=BG_COLOR, dpi=200)
    budgets = [d["budgetSec"] for d in detection_data]
    ours = [d["ours"] for d in detection_data]
    risk = [d["riskBased"] for d in detection_data]
    dep = [d["dependencyOnly"] for d in detection_data]
    rand = [d["random"] for d in detection_data]

    ax.plot(budgets, ours, label="Ours (SetCover + DP)", color=ACCENT_COLOR, linewidth=2.5, marker="o")
    ax.plot(budgets, risk, label="Risk-Based", color=BRAND_COLOR, linewidth=1.8, linestyle="--")
    ax.plot(budgets, dep, label="Dependency-Only", color=WARN_COLOR, linewidth=1.5, linestyle=":")
    ax.plot(budgets, rand, label="Random (Baseline)", color="#94A3B8", linewidth=1.2, linestyle="-.")
    ax.axhline(100.0, label="Run All Suite", color=SUCCESS_COLOR, linewidth=1.5, linestyle="--")

    _apply_dark_style(ax, "Bug Detection Rate vs Time Budget", "Execution Budget (seconds)", "Bugs Caught (%)")
    ax.set_ylim(-5, 105)
    ax.legend(facecolor=PANEL_COLOR, edgecolor="#2F3F8F", labelcolor=TEXT_COLOR, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "detection_vs_budget.png")
    plt.close(fig)

    # 2. Strategy Comparison (Time & Caught %)
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=BG_COLOR, dpi=200)
    names = [s["name"] for s in strategies_data]
    caught = [s["bugsCaughtPct"] for s in strategies_data]
    times = [s["timeSec"] for s in strategies_data]

    x = np.arange(len(names))
    width = 0.35

    rects1 = ax.bar(x - width / 2, caught, width, label="Bugs Caught (%)", color=ACCENT_COLOR)
    rects2 = ax.bar(x + width / 2, times, width, label="Time Spent (s)", color=BRAND_COLOR)

    _apply_dark_style(ax, "Strategy Comparison at 30s Reference Budget", "Strategy", "Value")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha="right")
    ax.legend(facecolor=PANEL_COLOR, edgecolor="#2F3F8F", labelcolor=TEXT_COLOR, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "strategy_comparison.png")
    plt.close(fig)

    # 3. Model Comparison
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=BG_COLOR, dpi=200)
    m_list = models_data.get("models", [])
    m_names = [m["name"] for m in m_list]
    pr_aucs = [m.get("prAuc", 0) for m in m_list]
    roc_aucs = [m.get("rocAuc", 0) for m in m_list]
    f1s = [m.get("f1", 0) for m in m_list]

    mx = np.arange(len(m_names))
    m_width = 0.25

    ax.bar(mx - m_width, pr_aucs, m_width, label="PR-AUC (Selection Metric)", color=ACCENT_COLOR)
    ax.bar(mx, roc_aucs, m_width, label="ROC-AUC", color=BRAND_COLOR)
    ax.bar(mx + m_width, f1s, m_width, label="F1 Score", color=WARN_COLOR)

    _apply_dark_style(ax, "Supervised Model Performance on Holdout Mutants", "Model Architecture", "Score [0.0 - 1.0]")
    ax.set_xticks(mx)
    ax.set_xticklabels(m_names)
    ax.set_ylim(0, 1.05)
    ax.legend(facecolor=PANEL_COLOR, edgecolor="#2F3F8F", labelcolor=TEXT_COLOR, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "model_comparison.png")
    plt.close(fig)

    # 4. Feature Importance
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=BG_COLOR, dpi=200)
    feat_items = models_data.get("featureImportance", [])[:8]
    feat_names = [f["feature"] for f in reversed(feat_items)]
    feat_vals = [f["importance"] for f in reversed(feat_items)]

    y_pos = np.arange(len(feat_names))
    ax.barh(y_pos, feat_vals, color=BRAND_COLOR, edgecolor=ACCENT_COLOR, height=0.6)

    _apply_dark_style(ax, "Permutation Feature Importance (Holdout Set)", "Normalized Importance", "")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(feat_names)
    fig.tight_layout()
    fig.savefig(output_dir / "feature_importance.png")
    plt.close(fig)

    # 5. Scalability (Log Scale)
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=BG_COLOR, dpi=200)
    ns = [s["n"] for s in scalability_data]
    g_ms = [s["greedyMs"] for s in scalability_data]
    dp_ms = [s["dpMs"] for s in scalability_data]
    bnb_ms = [s["bnbMs"] for s in scalability_data]

    ax.plot(ns, g_ms, label="Greedy Heuristic O(n log n)", color=SUCCESS_COLOR, linewidth=2, marker="o")
    ax.plot(ns, dp_ms, label="DP Knapsack O(n W)", color=ACCENT_COLOR, linewidth=2, marker="s")
    ax.plot(ns, bnb_ms, label="Branch & Bound (Pruned DFS)", color=DANGER_COLOR, linewidth=2, marker="^")

    ax.set_xscale("log")
    ax.set_yscale("log")
    _apply_dark_style(ax, "Algorithm Execution Time vs Problem Scale (n)", "Test Suite Size (n)", "Runtime (ms - log scale)")
    ax.legend(facecolor=PANEL_COLOR, edgecolor="#2F3F8F", labelcolor=TEXT_COLOR, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "scalability.png")
    plt.close(fig)
