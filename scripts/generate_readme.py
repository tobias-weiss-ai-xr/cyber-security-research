#!/usr/bin/env python3
"""Generate README.md from statistics.json (cyber-security-research edition).

Usage:
    python3 scripts/generate_readme.py          # write README.md
    python3 scripts/generate_readme.py --check  # verify README is up to date (CI)
"""

STATS_ONLY = False  # Set True to skip full paper list generation
import argparse
import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

CATEGORY_DISPLAY = {
    "threat-intelligence": "Threat Intelligence & Analysis",
    "vulnerability-management": "Vulnerability Management",
    "incident-response": "Incident Response & Forensics",
    "malware-analysis": "Malware Analysis & Reverse Engineering",
    "network-security": "Network & Perimeter Security",
    "application-security": "Application Security & DevSecOps",
    "cloud-security": "Cloud & Container Security",
    "identity-access": "Identity, Access & Authentication",
    "cryptography": "Cryptography & Protocols",
    "zero-trust": "Zero Trust Architecture",
    "supply-chain-security": "Software Supply Chain Security",
    "security-operations": "Security Operations & SOC",
    "ai-security": "AI & Adversarial ML Security",
    "security-education": "Security Education & Workforce",
    "security-compliance": "Compliance, Regulation & Standards",
    "risk-management": "Cyber Risk Management",
    "privacy": "Privacy & Data Protection",
    "iot-security": "IoT, OT & ICS Security",
    "human-factor": "Human Factor & Social Engineering",
    "cyber-warfare": "Cyber Warfare & State Threats",
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


def render_readme(stats):
    meta = stats["metadata"]
    total = meta["total_papers"]
    saturation = meta["taxonomy"]["saturation"]
    filled = meta["taxonomy"]["filled_cells"]
    total_cells = meta["taxonomy"]["total_cells"]
    by_cat = stats["by_category"]
    by_sub = stats["by_subcategory"]
    by_year = stats["by_year"]
    news_total = 0
    news_path = BASE / "news.yaml"
    if news_path.exists():
        import yaml as _y
        try:
            news_total = len(_y.safe_load(news_path.read_text()).get("news", []))
        except Exception:
            news_total = 0
    by_cell = stats["by_cell"]
    themes = stats.get("emerging_themes_12m", [])

    years = [y for y in by_year if y != "unknown"]
    ymin = min(years, default="—")
    ymax = max(years, default="—")

    top_cats = sorted(by_cat.items(), key=lambda kv: -kv[1])[:6]
    top_cats_rows = "\n".join(
        f"{i+1}. **{CATEGORY_DISPLAY[c]}** — {n} papers" for i, (c, n) in enumerate(top_cats)
    )

    theme_rows = "\n".join(
        f"{i+1}. **{t['keyword']}** — {t['papers']} papers" for i, t in enumerate(themes[:6])
    )

    momentum = stats.get("momentum", [])[:6]
    mom_rows = "\n".join(
        f"| {m['name']} | {m['total']} | {m['recent']} | "
        + (f"{m['growth_pct']:+}%" if m['growth_pct'] is not None else "—")
        + f" | {m['recent_share']*100:.0f}% |"
        for m in momentum
    )

    thin = sorted(by_cell.items(), key=lambda kv: kv[1])[:8]
    gap_rows = "\n".join(f"- `{c}` — {n} papers" for c, n in thin)

    cat_table = "\n".join(
        f"| {CATEGORY_DISPLAY[c]} | {by_cat.get(c, 0)} |"
        for c in CATEGORY_DISPLAY
    )
    sub_table = "\n".join(
        f"| {SUBCATEGORY_DISPLAY[s]} | {by_sub.get(s, 0)} |"
        for s in SUBCATEGORY_DISPLAY
    )

    return f"""# Cyber-Security Research Corpus

**Research program** — evidence base for the cyber-security landscape:
20 categories \u00d7 8 aspects covering threat intelligence, vulnerabilities,
incident response, malware, network/cloud/application security, zero trust,
supply chain, AI security, compliance, risk, privacy, IoT/OT and the human
factor \u2014 plus live tracking of authoritative news sources (CISA, NIST, ENISA, \u2026).

**Author:** Tobias Weiss
**Contact:** business@tobias-weiss.org

---

## \U0001F3AF Overview

This repository combines two knowledge layers:

1. **Corpus** \u2014 {total:,} research papers across 20 cyber-security disciplines,
   analyzed with the taxonomy \u2192 momentum \u2192 burst \u2192 gap pipeline used in
   [business-development-research](https://github.com/tobias-weiss-ai-xr/business-development-research)
   and [graph-research](https://github.com/tobias-weiss-ai-xr/graph-research).
2. **News tracker** \u2014 a rolling {news_total:,}-item feed of operational
   cyber-security news (CISA advisories, NIST/NIST-IR, ENISA, BSI, NCSC, \u2026),
   deduplicated by URL and mapped onto the same taxonomy (see `news.yaml`).

### Research Scope

| Metric | Value |
|--------|-------|
| **Papers Analyzed** | {total:,} |
| **Cyber-Security Disciplines** | {len(CATEGORY_DISPLAY)} |
| **Time Span** | {ymin}-{ymax} |
| **Research Aspects** | {len(SUBCATEGORY_DISPLAY)} |
| **Taxonomy Cells** | {total_cells} |
| **Saturation** | {saturation}% ({filled}/{total_cells} cells) |
| **News Items Tracked** | {news_total:,} |

### Top Evidence Areas

...
│   └── landscape_analyzer.py          # Landscape report ✨
│
├── scripts/                           # Research pipeline
│   ├── fetch/                         # OpenAlex (primary), arXiv, DBLP/CrossRef
│   ├── fetch/fetch_news.py            # News-tracker (CISA, NIST, ENISA, \u2026)
│   ├── analysis/generate_analysis.py  # Statistics + visualizations
│   ├── validate_papers.py             # Corpus validation
│   └── generate_readme.py             # README generator
│
└── examples/                          # Usage examples
```

---

## \U0001F4C8 News Tracker

Operational news (advisories, alerts, breach reports, policy changes) moves
faster than the literature. `scripts/fetch/fetch_news.py` pulls RSS/HTML from
authoritative sources, normalizes and deduplicates entries into `news.yaml`,
tagged with the same 20-category taxonomy so news can be cross-referenced
against the research corpus.

```bash
python3 scripts/fetch/fetch_news.py [--sources cisa,nist,enisa,bsi,ncsc,thn,krebs] [--days 14]
python3 scripts/fetch/fetch_news.py --check     # validate news.yaml
```

**Sources:** CISA news + cybersecurity advisories (via CISA-accessible egress),
NIST, ENISA, BSI, NCSC-UK, CERT-EU, The Hacker News, Krebs on Security, SANS ISC.

---

## \U0001F525 Research Program

| Deliverable | Targets | Status |
|-------------|---------|--------|
| **Landscape mapping** | all 20 categories \u00d7 8 aspects | planned (see `docs/research/`) |
| **Deep-dive: threat intelligence** | `threat-intelligence` | planned |
| **Deep-dive: incident response** | `incident-response`, `network-security` | planned |
| **Alert-to-paper bridge** | `fetch_news.py` \u2194 corpus categories | shipped |

## \U0001F6E0\uFE0F Tools

```bash
cd tools
python3 topic_planner.py --top 10               # ranked evidence areas
python3 trend_scanner.py --months 6             # keyword bursts
python3 brief_generator.py "zero trust architecture" --papers 5
python3 landscape_analyzer.py --write-doc       # full landscape
```

---

## \U0001F504 Research Pipeline

1. **Discover** \u2014 `python3 scripts/fetch/fetch_openalex.py --months 3`
2. **News** \u2014 `python3 scripts/fetch/fetch_news.py`
3. **Validate** \u2014 `python3 scripts/validate_papers.py`
4. **Analyze** \u2014 `python3 scripts/analysis/generate_analysis.py`
5. **Visualize** \u2014 `python3 scripts/visualize_statistics.py`
6. **Report** \u2014 `python3 scripts/analysis/generate_reports.py`
7. **Generate** \u2014 `python3 scripts/generate_readme.py`

CI (`.github/workflows/validate.yml`) validates and regenerates on every push;
a weekly scheduled job opens a PR with newly discovered papers.

---

## \U0001F517 Related Repositories

- **Adjacent corpus:** [business-development-research](https://github.com/tobias-weiss-ai-xr/business-development-research)
- **Adjacent corpus:** [learning-research](https://github.com/tobias-weiss-ai-xr/learning-research)
- **Adjacent corpus:** [graph-research](https://github.com/tobias-weiss-ai-xr/graph-research)
- **Adjacent corpus:** [devops-research](https://github.com/tobias-weiss-ai-xr/devops-research)

---

## \U0001F4C4 License

**\u00A9 2026 Tobias Weiss**

- **Research corpus:** Proprietary
- **Tools:** MIT License

---

## \U0001F64F Acknowledgments

This corpus synthesizes {total:,} papers across {ymin}-{ymax} \u2014 plus a rolling
news feed \u2014 to create the evidence base for the cyber-security research
program: from academic findings to operational reality.

---

**Want to explore the corpus?**
`cd tools && python3 landscape_analyzer.py`
"""

def main():
    parser = argparse.ArgumentParser(description="Generate README.md")
    parser.add_argument("--check", action="store_true", help="Verify README is current")
    args = parser.parse_args()

    stats_path = BASE / "statistics.json"
    if not stats_path.exists():
        print("ERROR: statistics.json not found — run scripts/analysis/generate_analysis.py first")
        sys.exit(1)

    with open(stats_path, encoding="utf-8") as f:
        stats = json.load(f)

    readme = render_readme(stats)
    readme_path = BASE / "README.md"

    if args.check:
        if readme_path.exists() and readme_path.read_text(encoding="utf-8") == readme:
            print("README.md is up to date")
        else:
            print("README.md is OUT OF DATE — run scripts/generate_readme.py")
            sys.exit(1)
    else:
        readme_path.write_text(readme, encoding="utf-8")
        print(f"Wrote README.md ({len(readme)} chars)")


if __name__ == "__main__":
    main()