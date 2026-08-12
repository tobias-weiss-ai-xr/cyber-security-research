#!/usr/bin/env python3
"""Full landscape analysis of the AI-literacy research corpus.

Produces a structured picture of the current paper landscape:
category growth/velocity, research aspects, year trends, venue mix,
top authors, hot & thin cells, and emerging themes.

Usage:
    python3 tools/landscape_analyzer.py                 # terminal report
    python3 tools/landscape_analyzer.py --json          # machine-readable
    python3 tools/landscape_analyzer.py --write-doc     # docs/research/landscape_report.md
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATEGORY_DISPLAY = {
    "ai-literacy-construct": "AI Literacy Constructs & Models",
    "ai-literacy-pedagogy": "AI Literacy Pedagogy",
    "learning-design": "Learning Design & Curriculum",
    "assessment": "Assessment & Measurement",
    "workforce-upskilling": "Workforce Upskilling",
    "org-implementation": "Org Implementation & Change",
    "sme-training": "SME Training & Adoption",
    "compliance": "Compliance & AI Act",
    "k12-education": "K-12 Education",
    "higher-education": "Higher Education",
    "professional-education": "Professional & Executive Ed",
    "teacher-ai-literacy": "Teacher AI Literacy",
    "critical-ai-literacy": "Critical & Ethical AI Literacy",
    "generative-ai-skills": "Generative AI Skills",
    "attitudes-trust": "Attitudes, Trust & Acceptance",
    "adoption-behavior": "Adoption Behavior & Engagement",
    "program-evaluation": "Program Evaluation & Outcomes",
    "roi-measurement": "ROI & Business Impact",
    "tooling": "Tools, Platforms & AI Tutors",
    "lifelong-learning": "Lifelong & Self-Directed Learning",
}

SUBCATEGORY_DISPLAY = {
    "theory": "Theory",
    "mechanism": "Mechanism",
    "method": "Method",
    "application": "Application",
    "development": "Development",
    "systems": "Systems & Technology",
    "evaluation": "Evaluation & Benchmarks",
    "review": "Reviews & Surveys",
}


def load_papers():
    with open(os.path.join(BASE, "papers.yaml"), encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("papers", [])


def analyze(papers):
    now = datetime.now()
    cur_year = now.year
    prev_year = cur_year - 1
    two_prev = cur_year - 2

    n = len(papers)

    def is_in(p, year):
        return p.get("date", "")[:4] == str(year)

    cat_total = Counter(p["category"] for p in papers)
    cat_prev = Counter(p["category"] for p in papers if is_in(p, prev_year))
    cat_2prev = Counter(p["category"] for p in papers if is_in(p, two_prev))
    cat_cur = Counter(p["category"] for p in papers if is_in(p, cur_year))

    # 12-month velocity
    cutoff = f"{prev_year}-{now.month:02d}"
    recent_by_cat = Counter(
        p["category"] for p in papers if p.get("date", "") >= cutoff
    )

    sub_total = Counter(p["subcategory"] for p in papers)
    year_total = Counter(p["date"][:4] for p in papers if p.get("date"))

    # venue mix (OpenAlex entries carry venue; arXiv entries empty)
    venue = Counter((", ".join(p.get("venue")) if isinstance(p.get("venue"), list) else (p.get("venue") or "")).strip() for p in papers)
    venue.pop("", None)
    arxiv_count = sum(1 for p in papers if "arxiv.org" in p.get("url", ""))
    journal_count = n - arxiv_count

    # authors
    author_counter = Counter()
    for p in papers:
        for a in p.get("authors", []):
            if a:
                author_counter[a] += 1

    # themes: keyword bursts (last 12 months vs corpus)
        theme_kw = [
        "generative ai", "genai", "llm", "large language model", "chatgpt",
        "agent", "agentic", "ai literacy", "ai competence", "upskilling",
        "reskilling", "workforce", "employee", "sme", "eu ai act", "article 4",
        "compliance", "regulation", "prompt engineering", "prompting",
        "critical thinking", "self-efficacy", "trust", "acceptance", "readiness",
        "assessment", "evaluation", "kirkpatrick", "outcome", "measurement",
        "framework", "taxonomy", "continuum", "persona", "reliance",
        "training", "course", "workshop", "curriculum", "pedagogy", "k-12",
        "higher education", "university", "teachers", "lifelong learning",
        "tutor", "chatbot", "productivity", "transfer", "spaced repetition",
    ]
    recent_text = Counter()
    all_text = Counter()
    recent_papers = [p for p in papers if p.get("date", "") >= cutoff]
    for p in papers:
        text = (p.get("title", "") + " " + p.get("abstract", "")).lower()
        for kw in theme_kw:
            if kw in text:
                all_text[kw] += 1
    for p in recent_papers:
        text = (p.get("title", "") + " " + p.get("abstract", "")).lower()
        for kw in theme_kw:
            if kw in text:
                recent_text[kw] += 1
    themes = []
    rn = max(len(recent_papers), 1)
    for kw in theme_kw:
        r = recent_text.get(kw, 0)
        t = all_text.get(kw, 0)
        if r == 0:
            continue
        corpus_share = t / n
        recent_share = r / rn
        themes.append({
            "keyword": kw, "recent": r, "total": t,
            "burst": round(recent_share / corpus_share, 2) if corpus_share else 99,
        })
    themes.sort(key=lambda x: (-x["burst"], -x["recent"]))

    # cells
    cell_counter = Counter(f"{p['category']}/{p['subcategory']}" for p in papers)

    # category landscape with growth
    cats = []
    for c in CATEGORY_DISPLAY:
        t = cat_total.get(c, 0)
        if t == 0:
            continue
        cur = cat_cur.get(c, 0)
        prev = cat_prev.get(c, 0)
        prev2 = cat_2prev.get(c, 0)
        yoy = (cur - prev) / prev if prev else 0
        share_12m = recent_by_cat.get(c, 0) / max(len(recent_papers), 1)
        cats.append({
            "category": c,
            "name": CATEGORY_DISPLAY[c],
            "total": t,
            f"y{two_prev}": prev2,
            f"y{prev_year}": prev,
            f"y{cur_year}": cur,
            "yoy": round(yoy, 2),
            "recent_12m_share": round(share_12m, 3),
        })
    cats.sort(key=lambda x: -x["total"])

    return {
        "generated": now.isoformat()[:10],
        "total_papers": n,
        "arxiv_papers": arxiv_count,
        "journal_papers": journal_count,
        "year_span": f"{min(year_total)}-{max(year_total)}",
        "years": {y: year_total[y] for y in sorted(year_total)},
        "categories": cats,
        "aspects": {s: sub_total.get(s, 0) for s in SUBCATEGORY_DISPLAY},
        "themes": themes[:15],
        "top_authors": author_counter.most_common(15),
        "top_venues": venue.most_common(10),
        "hottest_cells": sorted(cell_counter.items(), key=lambda kv: -kv[1])[:10],
        "thin_cells": sorted(cell_counter.items(), key=lambda kv: kv[1])[:10],
    }


def render_markdown(res):
    L = []
    L.append("# AI-Literacy Paper Landscape Report")
    L.append("")
    L.append(f"**Generated:** {res['generated']}  ")
    L.append(f"**Corpus:** {res['total_papers']:,} papers ({res['year_span']}) | "
             f"{res['arxiv_papers']:,} arXiv preprints · {res['journal_papers']:,} journal/publisher records")
    L.append("")
    L.append("## Category Landscape")
    L.append("")
    L.append("| Category | Total | Prev Yr | This Yr | YoY | 12m Share |")
    L.append("|----------|------:|--------:|--------:|----:|----------:|")
    cur_year = res["generated"][:4]
    prev_year = str(int(cur_year) - 1)
    for c in res["categories"]:
        L.append(f"| {c['name']} | {c['total']} | {c[f'y{prev_year}']} | {c[f'y{cur_year}']} | "
                 f"{c['yoy']*100:+.0f}% | {c['recent_12m_share']*100:.0f}% |")
    L.append("")
    L.append("## Research Aspects")
    L.append("")
    for s, v in res["aspects"].items():
        share = v / res["total_papers"] * 100
        bar = "#" * int(share / 2)
        L.append(f"- **{SUBCATEGORY_DISPLAY[s]}** ({s}): {v} papers ({share:.0f}%) {bar}")
    L.append("")
    L.append("## Year Trend")
    L.append("")
    L.append("| Year | Papers |")
    L.append("|------|-------:|")
    for y, v in res["years"].items():
        L.append(f"| {y} | {v} |")
    L.append("")
    L.append("## Emerging Themes (12-Month Bursts)")
    L.append("")
    L.append("| Keyword | Recent | Total | Burst |")
    L.append("|---------|-------:|------:|------:|")
    for t in res["themes"][:12]:
        L.append(f"| {t['keyword']} | {t['recent']} | {t['total']} | {t['burst']}× |")
    L.append("")
    L.append("## Venue Landscape (Top Publishers)")
    L.append("")
    L.append("| Venue | Papers |")
    L.append("|-------|-------:|")
    for v, c in res["top_venues"]:
        L.append(f"| {v} | {c} |")
    L.append("")
    L.append("## Top Authors")
    L.append("")
    L.append("| Author | Papers |")
    L.append("|--------|-------:|")
    for a, c in res["top_authors"][:10]:
        L.append(f"| {a} | {c} |")
    L.append("")
    L.append("## Hottest Cells")
    L.append("")
    for cell, v in res["hottest_cells"]:
        L.append(f"- `{cell}` — {v}")
    L.append("")
    L.append("## Thin Cells (White Space)")
    L.append("")
    for cell, v in res["thin_cells"]:
        L.append(f"- `{cell}` — {v}")
    L.append("")
    return "\n".join(L)


def main():
    parser = argparse.ArgumentParser(description="Graph paper landscape analyzer")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-doc", action="store_true", help="Write docs/research/landscape_report.md")
    args = parser.parse_args()

    papers = load_papers()
    res = analyze(papers)

    if args.json:
        print(json.dumps(res, indent=2, default=str))
        return

    md = render_markdown(res)
    if args.write_doc:
        path = os.path.join(BASE, "docs", "research", "landscape_report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Wrote {path}\n")

    print(md)


if __name__ == "__main__":
    main()
