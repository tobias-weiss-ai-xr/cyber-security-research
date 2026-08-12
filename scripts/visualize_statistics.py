#!/usr/bin/env python3
"""Generate PNG chart visualizations from papers.yaml.

Outputs to assets/visualizations/:
  - category_distribution.png     bar chart per category
  - papers_by_year.png            papers per year
  - taxonomy_heatmap.png          category x subcategory heatmap
  - top_categories.png            horizontal bars of top categories
"""

import os
import sys

import yaml
from collections import Counter

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("matplotlib is required: pip install matplotlib")
    sys.exit(1)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "assets", "visualizations")
os.makedirs(OUT, exist_ok=True)

CATEGORY_ORDER = [
    "threat-intelligence",
    "vulnerability-management",
    "incident-response",
    "malware-analysis",
    "network-security",
    "application-security",
    "cloud-security",
    "identity-access",
    "cryptography",
    "zero-trust",
    "supply-chain-security",
    "security-operations",
    "ai-security",
    "security-education",
    "security-compliance",
    "risk-management",
    "privacy",
    "iot-security",
    "human-factor",
    "cyber-warfare",
]

SUBCATEGORY_ORDER = [
    "theory", "mechanism", "method", "application",
    "development", "systems", "evaluation", "review",
]

BG = "#0d1117"
FG = "#e6edf3"
ACCENT = "#58a6ff"


def load():
    with open(os.path.join(BASE, "papers.yaml"), encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("papers", [])


def style_ax(ax):
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_color("#30363d")
    ax.tick_params(colors=FG)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)


def plot_category_distribution(papers):
    counter = Counter(p.get("category", "unknown") for p in papers)
    cats = [c for c in CATEGORY_ORDER if counter.get(c, 0) > 0]
    counts = [counter.get(c, 0) for c in cats]
    fig, ax = plt.subplots(figsize=(12, 6), facecolor=BG)
    bars = ax.bar(cats, counts, color=ACCENT, edgecolor="#30363d")
    for bar, v in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, v + max(counts) * 0.01,
                str(v), ha="center", va="bottom", color=FG, fontsize=8, rotation=0)
    ax.set_title("Cyber-Security Research Papers by Category", fontsize=14)
    ax.set_ylabel("Papers")
    ax.set_xticklabels(cats, rotation=45, ha="right", fontsize=8)
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "category_distribution.png"), dpi=150)
    plt.close(fig)
    print("  category_distribution.png")


def plot_papers_by_year(papers):
    counter = Counter(p.get("date", "")[:4] for p in papers)
    years = sorted(y for y in counter if y != "")
    counts = [counter[y] for y in years]
    fig, ax = plt.subplots(figsize=(12, 5), facecolor=BG)
    ax.plot(years, counts, color=ACCENT, marker="o", markersize=3, linewidth=1.5)
    ax.fill_between(years, counts, color=ACCENT, alpha=0.2)
    ax.set_title("Papers by Year", fontsize=14)
    ax.set_ylabel("Papers")
    ax.set_xlabel("Year")
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "papers_by_year.png"), dpi=150)
    plt.close(fig)
    print("  papers_by_year.png")


def plot_taxonomy_heatmap(papers):
    matrix = np.zeros((len(CATEGORY_ORDER), len(SUBCATEGORY_ORDER)))
    for p in papers:
        cat = p.get("category", "")
        sub = p.get("subcategory", "")
        if cat in CATEGORY_ORDER and sub in SUBCATEGORY_ORDER:
            matrix[CATEGORY_ORDER.index(cat)][SUBCATEGORY_ORDER.index(sub)] += 1
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=BG)
    im = ax.imshow(matrix, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(SUBCATEGORY_ORDER)))
    ax.set_xticklabels(SUBCATEGORY_ORDER, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(CATEGORY_ORDER)))
    ax.set_yticklabels([c.replace("-", "\n") for c in CATEGORY_ORDER], fontsize=7)
    for i in range(len(CATEGORY_ORDER)):
        for j in range(len(SUBCATEGORY_ORDER)):
            v = int(matrix[i][j])
            if v > 0:
                ax.text(j, i, str(v), ha="center", va="center", fontsize=7,
                        color="white" if v > matrix.max() / 2 else "#0d1117")
    ax.set_title("Taxonomy Heatmap: Category × Subcategory", fontsize=14)
    cbar = fig.colorbar(im, ax=ax, shrink=0.7)
    cbar.ax.tick_params(colors=FG)
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "taxonomy_heatmap.png"), dpi=150)
    plt.close(fig)
    print("  taxonomy_heatmap.png")


def plot_top_categories(papers):
    counter = Counter(p.get("category", "unknown") for p in papers)
    top = sorted(counter.items(), key=lambda kv: -kv[1])[:10]
    top = top[::-1]
    names = [c.replace("-", " ").title() for c, _ in top]
    counts = [v for _, v in top]
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
    ax.barh(names, counts, color=ACCENT, edgecolor="#30363d")
    for y, v in enumerate(counts):
        ax.text(v + max(counts) * 0.01, y, str(v), va="center", color=FG, fontsize=9)
    ax.set_title("Top 10 Cyber-Security Research Categories", fontsize=14)
    ax.set_xlabel("Papers")
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "top_categories.png"), dpi=150)
    plt.close(fig)
    print("  top_categories.png")


def main():
    papers = load()
    print(f"Loaded {len(papers)} papers")
    plot_category_distribution(papers)
    plot_papers_by_year(papers)
    plot_taxonomy_heatmap(papers)
    plot_top_categories(papers)
    print(f"Done — charts written to {OUT}")


if __name__ == "__main__":
    main()
