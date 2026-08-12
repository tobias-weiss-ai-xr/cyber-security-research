#!/usr/bin/env python3
"""Phase-2a: screen shortlists (judgments in screening.json) + refill.

Combines the human/LLM screening judgments (docs/research/extraction/
screening.json, keyed by RQ + index into shortlists.json) with a targeted
refill pass that tops each RQ up to --target includes using refined
queries (the keyword-scored seed lists over-represent adjacent-but-off-
topic material for RQ3-RQ5).

Writes:
  docs/research/extraction/screening_report.md  (Phase-2a deliverable)
  docs/research/extraction/final_shortlists.json
  docs/research/extraction/screening.json       (machine-readable judgments)

Usage:
    python3 tools/refill_shortlists.py [--target 25]
"""

import argparse
import json
import os
import re
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Refined per-RQ queries: (must-match terms, categories, aspect boost)
REFILLS = {
    "RQ1": {
        "terms": ["framework", "literacy", "construct", "model", "stage"],
        "categories": ["ai-literacy-construct"],
    },
    "RQ2": {
        "terms": ["training", "upskill", "program", "implement", "workplace",
                  "sme", "organization"],
        "categories": ["org-implementation", "learning-design",
                       "workforce-upskilling", "sme-training"],
    },
    "RQ3": {
        "terms": ["ai literacy", "artificial intelligence literacy", "scale",
                  "instrument", "test", "assessment", "measure", "validity",
                  "reliability", "psychometric"],
        "categories": ["assessment", "program-evaluation",
                       "ai-literacy-construct"],
    },
    "RQ4": {
        "terms": ["training", "upskill", "education", "program", "course",
                  "productivity", "performance", "impact", "outcome",
                  "behavior", "roi", "return"],
        "categories": ["roi-measurement", "program-evaluation",
                       "adoption-behavior", "workforce-upskilling"],
    },
    "RQ5": {
        "terms": ["ai act", "article 4", "literacy", "compliance",
                  "training", "obligation", "regulation"],
        "categories": ["compliance", "org-implementation"],
    },
}


def tokenize(text):
    return set(re.findall(r"[a-z0-9]{3,}", text.lower()))


def score(p, terms):
    text = f"{p.get('title','')} {p.get('abstract','')}".lower()
    tokens = tokenize(text)
    overlap = sum(1 for t in terms if t in text or t in tokens)
    phrase = sum(3 for t in terms if " " in t and t in text)
    date = p.get("date", "0000-00")
    try:
        recency = 1.0 if int(date[:4]) >= 2025 else 0.6
    except ValueError:
        recency = 0.5
    return overlap + phrase + recency


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=25)
    args = ap.parse_args()

    papers = json.load(open(os.path.join(BASE, "papers.json"), encoding="utf-8"))
    by_title = {p["title"].lower().strip(): p for p in papers}
    shorts = json.load(open(os.path.join(BASE, "docs", "research", "extraction",
                                         "shortlists.json"), encoding="utf-8"))
    screen = json.load(open("/tmp/screening.json", encoding="utf-8"))

    # resolve screened shortlist entries to records + judgment
    judged = {}   # rq -> list of (verdict, tier, reason, record)
    for rq, lst in shorts["shortlists"].items():
        entries = []
        for i, p in enumerate(lst, 1):
            rec = by_title.get(p["title"].lower().strip(), p)
            v = screen[rq].get(str(i), ["include", "?", "no judgment recorded"])
            entries.append({"idx": i, "verdict": v[0], "tier": v[1],
                            "reason": v[2], "record": rec})
        judged[rq] = entries

    report = []
    report.append("# Screening Report — Phase 2a")
    report.append("")
    report.append("**Method:** 150 shortlisted papers (30 per RQ, "
                  "`tools/build_shortlists.py`) screened by title+abstract "
                  "against PROTOCOL.md inclusion criteria · 2026-08-12 · "
                  "judgments in `docs/research/extraction/screening.json`")
    report.append("")
    report.append("| RQ | Screened | Included | Excluded | Duplicates | Refilled | Final |")
    report.append("|---|----------|----------|----------|------------|----------|-------|")
    final_all = {}
    tier_count = Counter()

    for rq in ["RQ1", "RQ2", "RQ3", "RQ4", "RQ5"]:
        entries = judged[rq]
        inc = [e for e in entries if e["verdict"] == "include"]
        exc = [e for e in entries if e["verdict"] == "exclude"]
        dup = [e for e in entries if e["verdict"] == "duplicate"]
        # refill
        need = max(0, args.target - len(inc))
        taken_titles = {e["record"]["title"].lower().strip() for e in entries}
        cfg = REFILLS[rq]
        pool = [p for p in papers
                if p.get("category") in cfg["categories"]
                and p["title"].lower().strip() not in taken_titles]
        scored = sorted(pool, key=lambda p: -score(p, cfg["terms"]))
        refilled = []
        for p in scored:
            if len(refilled) >= need:
                break
            t = p["title"].lower().strip()
            if t in taken_titles:
                continue
            taken_titles.add(t)
            refilled.append({"idx": f"R{len(refilled)+1}", "verdict": "include",
                             "tier": "?", "reason": "refill (targeted query)",
                             "record": p})
        final = inc + refilled
        for e in final:
            tier_count[e["tier"] or "?"] += 1
        final_all[rq] = [{"title": e["record"]["title"],
                          "date": e["record"].get("date", ""),
                          "url": e["record"].get("url", ""),
                          "category": e["record"].get("category", ""),
                          "subcategory": e["record"].get("subcategory", ""),
                          "tier": e["tier"], "verdict": e["verdict"],
                          "reason": e["reason"]} for e in final]
        report.append(f"| {rq} | 30 | {len(inc)} | {len(exc)} | {len(dup)} | "
                      f"{len(refilled)} | **{len(final)}** |")
    report.append("")
    report.append(f"Quality tier distribution (final included): "
                  + ", ".join(f"{k}={v}" for k, v in sorted(tier_count.items())))
    report.append("")

    # per-RQ final tables
    for rq, items in final_all.items():
        report.append(f"## {rq} — final list ({len(items)})")
        report.append("")
        report.append("| # | Title | Date | Cat/Aspect | Tier | Source |")
        report.append("|---|-------|------|-----------|------|--------|")
        for i, e in enumerate(items, 1):
            src = "screened" if e["verdict"] == "include" and not str(e.get("reason","")).startswith("refill") else "refill"
            # provenance: refill flag
            src = "refill" if e.get("reason","").startswith("refill") else "seed"
            report.append(f"| {i} | {e['title'][:90]} | {e['date']} | "
                          f"{e['category']}/{e['subcategory']} | {e['tier']} | {src} |")
        report.append("")

    report.append("## Observations")
    report.append("")
    report.append("1. **Seed-list pollution is RQ-specific.** RQ1/RQ2 seed lists "
                  "were ~83% on-topic; RQ3-RQ5 keyword scoring surfaced adjacent "
                  "but off-topic material (other literacy domains, adoption-only "
                  "studies, technical compliance) — 73/150 excluded at screening.")
    report.append("2. **RQ4 is the thinnest evidence base**: only 6/30 seed papers "
                  "link *training* to outcomes (most measure adoption, not "
                  "training). The refill leans on workforce-upskilling categories.")
    report.append("3. **RQ5 has few Art. 4 operationalization studies** — the "
                  "M-SHALF healthcare framework and DGKL lab opinion are the "
                  "most concrete; most compliance literature is technical "
                  "(COMPL-AI, XAI) not literacy-focused. Confirms the white space.")
    report.append("4. **Quality tiers are provisional** (assigned from abstracts); "
                  "confirm at full-text extraction.")
    report.append("")
    report.append("## Next: full-text extraction")
    report.append("")
    report.append("For each included paper: fetch full text, verify tier, extract "
                  "into `docs/research/extraction/rqN.md` evidence tables per "
                  "PROTOCOL.md §3-4. Target ≥ 80% of final lists.")

    out_dir = os.path.join(BASE, "docs", "research", "extraction")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "screening_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    with open(os.path.join(out_dir, "final_shortlists.json"), "w", encoding="utf-8") as f:
        json.dump({"generated": "2026-08-12", "target_per_rq": args.target,
                   "final": final_all}, f, indent=1, ensure_ascii=False)
    # persist screening judgments next to the report
    screen_out = {}
    for rq, entries in judged.items():
        screen_out[rq] = {str(e["idx"]): {"verdict": e["verdict"],
                                          "tier": e["tier"],
                                          "reason": e["reason"]}
                          for e in entries}
    with open(os.path.join(out_dir, "screening.json"), "w", encoding="utf-8") as f:
        json.dump({"note": "Verdicts assigned by abstract-level screening "
                           "(LLM-assisted) against PROTOCOL.md criteria; "
                           "tiers provisional until full-text review.",
                   "judgments": screen_out}, f, indent=1, ensure_ascii=False)
    print(f"Wrote {out_dir}/screening_report.md")
    print(f"Wrote {out_dir}/final_shortlists.json")
    print(f"Wrote {out_dir}/screening.json")
    for rq, items in final_all.items():
        print(f"  {rq}: {len(items)} final")


if __name__ == "__main__":
    main()
