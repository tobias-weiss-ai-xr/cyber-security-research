#!/usr/bin/env python3
"""Phase-1 mapping tool: build per-RQ shortlists + mapping review.

Scores every corpus paper against the five research questions
(see docs/research/RESEARCH_PLAN.md), weighting recency and the
thin development/evaluation aspects, and writes:

  docs/research/extraction/shortlists.json  (machine-readable)
  docs/research/mapping_review.md           (Phase-1 deliverable)

Usage:
    python3 tools/build_shortlists.py [--papers 30]
"""

import argparse
import json
import os
import re
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASPECTS = ["theory", "mechanism", "method", "application",
           "development", "systems", "evaluation", "review"]

# RQ definitions: primary categories + weighted aspect boost + query terms
RQS = {
    "RQ1": {
        "question": ("Which conceptualizations and stage models of AI "
                     "literacy exist, and which have empirical support?"),
        "categories": ["ai-literacy-construct", "assessment"],
        "aspect_boost": {"theory": 2, "review": 1.5, "evaluation": 0.5},
        "terms": ["conceptual", "framework", "stage", "model", "dimension",
                  "construct", "competence", "taxonomy", "continuum"],
    },
    "RQ2": {
        "question": ("Which implementation strategies for organization-level "
                     "AI-literacy programs are evidenced, and under which "
                     "conditions do they work?"),
        "categories": ["org-implementation", "learning-design",
                       "workforce-upskilling", "sme-training"],
        "aspect_boost": {"development": 3, "method": 1.5, "application": 1.2},
        "terms": ["implement", "program", "workplace", "training",
                  "upskilling", "organization", "course", "curriculum",
                  "intervention", "adoption"],
    },
    "RQ3": {
        "question": ("How is AI literacy measured — which instruments exist, "
                     "with what validity — and which evaluation frameworks "
                     "apply to programs?"),
        "categories": ["assessment", "program-evaluation"],
        "aspect_boost": {"evaluation": 3, "method": 1.5, "development": 1.5},
        "terms": ["instrument", "measure", "assessment", "scale",
                  "validity", "reliability", "test", "evaluation",
                  "psychometric", "questionnaire"],
    },
    "RQ4": {
        "question": ("What evidence links AI-literacy training to behavior "
                     "change, productivity and firm performance?"),
        "categories": ["roi-measurement", "program-evaluation",
                       "adoption-behavior"],
        "aspect_boost": {"evaluation": 2, "mechanism": 1.5, "development": 1},
        "terms": ["productivity", "performance", "roi", "return",
                  "firm", "panel", "econometric", "behavior", "impact",
                  "outcome", "adoption"],
    },
    "RQ5": {
        "question": ("How do organizations operationalize EU AI Act Art. 4 "
                     "literacy obligations in practice?"),
        "categories": ["compliance", "org-implementation"],
        "aspect_boost": {"development": 3, "application": 1.5, "evaluation": 1},
        "terms": ["eu ai act", "article 4", "compliance", "regulation",
                  "literacy", "obligation", "governance", "risk",
                  "ai act", "policy"],
    },
}


def tokenize(text):
    return set(re.findall(r"[a-z0-9]{3,}", text.lower()))


def score_paper(p, cfg, aspects):
    """Keyword overlap + recency + aspect-weighting."""
    text = f"{p.get('title', '')} {p.get('abstract', '')}".lower()
    tokens = tokenize(text)
    q = set(cfg["terms"])
    overlap = len(q & tokens)
    phrase_bonus = 0
    for t in cfg["terms"]:
        if " " in t and t in text:
            phrase_bonus += 3
    date = p.get("date", "0000-00")
    try:
        yr = int(date[:4]); mo = int(date[5:7])
        recency = 1.0 if (yr, mo) >= (2025, 1) else 0.6
    except ValueError:
        recency = 0.5
    aspect = p.get("subcategory", "application")
    boost = cfg["aspect_boost"].get(aspect, 1.0)
    return (overlap + phrase_bonus) * boost + recency


def build_shortlists(n_per_rq, papers):
    shortlists = {}
    stats = {}
    for rq, cfg in RQS.items():
        cats = cfg["categories"]
        pool = [p for p in papers if p.get("category") in cats]
        scored = [(score_paper(p, cfg, ASPECTS), p) for p in pool]
        scored.sort(key=lambda x: (-x[0], x[1].get("date", ""), x[1].get("title", "")))
        picked = [p for _, p in scored[:n_per_rq]]
        # dedupe by title, keep the rest if short
        seen, out = set(), []
        for p in picked:
            t = p.get("title", "").lower().strip()
            if t not in seen:
                seen.add(t)
                out.append(p)
        # fill up to n_per_rq from the remaining pool
        for _, p in scored[n_per_rq:]:
            if len(out) >= n_per_rq:
                break
            t = p.get("title", "").lower().strip()
            if t not in seen:
                seen.add(t)
                out.append(p)
        shortlists[rq] = out
        stats[rq] = {
            "categories": cats,
            "pool": len(pool),
            "shortlisted": len(out),
            "cat_counts": dict(Counter(p.get("category") for p in out)),
            "aspect_counts": dict(Counter(p.get("subcategory") for p in out)),
            "latest": max((p.get("date", "") for p in out), default="n/a"),
        }
    return shortlists, stats


def cell_map(papers, cats):
    """category x aspect counts for the given categories."""
    rows = []
    for c in cats:
        row = {}
        for a in ASPECTS:
            row[a] = sum(1 for p in papers
                         if p.get("category") == c and p.get("subcategory") == a)
        rows.append((c, row))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--papers", type=int, default=30)
    args = ap.parse_args()

    papers = json.load(open(os.path.join(BASE, "papers.json"), encoding="utf-8"))
    shortlists, stats = build_shortlists(args.papers, papers)

    out_path = os.path.join(BASE, "docs", "research", "extraction", "shortlists.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump({"generated": "2026-08-12", "per_rq": args.papers,
               "rqs": RQS, "stats": stats, "shortlists": shortlists},
              open(out_path, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False, sort_keys=False)

    # ---- mapping review document ----
    all_cats = sorted({p.get("category") for p in papers})
    cells = cell_map(papers, all_cats)
    lines = []
    lines.append("# Mapping Review — AI-Literacy Implementation & Evaluation")
    lines.append("")
    lines.append("**Phase 1 deliverable** · generated by `tools/build_shortlists.py` · "
                 "2026-08-12 · corpus: 4,414 papers (100% saturation)")
    lines.append("")
    lines.append("## 1. Cell-level map (target categories × aspects)")
    lines.append("")
    lines.append("| Category | " + " | ".join(a.capitalize() for a in ASPECTS) + " | Σ |")
    lines.append("|---|" + "---|" * len(ASPECTS) + "---|")
    for c, row in cells:
        if c in {p for rq in RQS.values() for p in rq["categories"]}:
            tot = sum(row.values())
            lines.append(f"| {c} | " + " | ".join(str(row[a]) for a in ASPECTS)
                         + f" | **{tot}** |")
    lines.append("")
    lines.append("**Reading:** the `development` (how to build) and `evaluation` "
                 "(how to measure) aspects are the thinnest across all ten target "
                 "categories — `org-implementation/evaluation` has a single paper. "
                 "This is the white space the research program targets.")
    lines.append("")

    for rq, cfg in RQS.items():
        st = stats[rq]
        lines.append(f"## {rq}: {cfg['question']}")
        lines.append("")
        lines.append(f"Pool: {st['pool']} papers in "
                     f"{', '.join(st['categories'])} · shortlist: {st['shortlisted']} "
                     f"(top {args.papers}) · latest: {st['latest']}")
        lines.append("")
        lines.append(f"Composition — categories: "
                     + ", ".join(f"{k}={v}" for k, v in st["cat_counts"].items())
                     + " · aspects: "
                     + ", ".join(f"{k}={v}" for k, v in st["aspect_counts"].items()))
        lines.append("")
        lines.append("| # | Title | Date | Category/Aspect | URL |")
        lines.append("|---|-------|------|-----------------|-----|")
        for i, p in enumerate(shortlists[rq], 1):
            title = p.get("title", "")[:95]
            lines.append(f"| {i} | {title} | {p.get('date','')} | "
                         f"{p.get('category','')}/{p.get('subcategory','')} | "
                         f"{p.get('url','')} |")
        lines.append("")

    lines.append("## Next: Phase 2 — Extraction")
    lines.append("")
    lines.append("For each RQ shortlist: fetch full text via URL, screen against "
                 "PROTOCOL.md inclusion criteria, extract into "
                 "`docs/research/extraction/` evidence tables (one row per study, "
                 "quality tier A–E). Target: ≥ 80% of the shortlist extracted.")
    lines.append("")

    doc_path = os.path.join(BASE, "docs", "research", "mapping_review.md")
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {doc_path} ({len(lines)} lines)")
    print(f"Wrote {out_path}")
    for rq, st in stats.items():
        print(f"  {rq}: pool={st['pool']} shortlist={st['shortlisted']} "
              f"latest={st['latest']}")


if __name__ == "__main__":
    main()
