# Cyber-Security Research Corpus

**Research program** — evidence base for the cyber-security landscape:
20 categories × 8 aspects covering threat intelligence, vulnerabilities,
incident response, malware, network/cloud/application security, zero trust,
supply chain, AI security, compliance, risk, privacy, IoT/OT and the human
factor — plus live tracking of authoritative news sources (CISA, NIST, ENISA, …).

**Author:** Tobias Weiss
**Contact:** business@tobias-weiss.org

---

## 🎯 Overview

This repository combines two knowledge layers:

1. **Corpus** — 8,606 research papers across 20 cyber-security disciplines,
   analyzed with the taxonomy → momentum → burst → gap pipeline used in
   [business-development-research](https://github.com/tobias-weiss-ai-xr/business-development-research)
   and [graph-research](https://github.com/tobias-weiss-ai-xr/graph-research).
2. **News tracker** — a rolling 763-item feed of operational
   cyber-security news (CISA advisories, NIST/NIST-IR, ENISA, BSI, NCSC, …),
   deduplicated by URL and mapped onto the same taxonomy (see `news.yaml`).

### Research Scope

| Metric | Value |
|--------|-------|
| **Papers Analyzed** | 8,606 |
| **Cyber-Security Disciplines** | 20 |
| **Time Span** | 1991-2026 |
| **Research Aspects** | 8 |
| **Taxonomy Cells** | 160 |
| **Saturation** | 99.4% (159/160 cells) |
| **News Items Tracked** | 763 |

### Top Evidence Areas

...
│   └── landscape_analyzer.py          # Landscape report ✨
│
├── scripts/                           # Research pipeline
│   ├── fetch/                         # OpenAlex (primary), arXiv, DBLP/CrossRef
│   ├── fetch/fetch_news.py            # News-tracker (CISA, NIST, ENISA, …)
│   ├── analysis/generate_analysis.py  # Statistics + visualizations
│   ├── validate_papers.py             # Corpus validation
│   └── generate_readme.py             # README generator
│
└── examples/                          # Usage examples
```

---

## 📈 News Tracker

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

## 🔥 Research Program

| Deliverable | Targets | Status |
|-------------|---------|--------|
| **Landscape mapping** | all 20 categories × 8 aspects | planned (see `docs/research/`) |
| **Deep-dive: threat intelligence** | `threat-intelligence` | planned |
| **Deep-dive: incident response** | `incident-response`, `network-security` | planned |
| **Alert-to-paper bridge** | `fetch_news.py` ↔ corpus categories | shipped |

## 🛠️ Tools

```bash
cd tools
python3 topic_planner.py --top 10               # ranked evidence areas
python3 trend_scanner.py --months 6             # keyword bursts
python3 brief_generator.py "zero trust architecture" --papers 5
python3 landscape_analyzer.py --write-doc       # full landscape
```

---

## 🔄 Research Pipeline

1. **Discover** — `python3 scripts/fetch/fetch_openalex.py --months 3`
2. **News** — `python3 scripts/fetch/fetch_news.py`
3. **Validate** — `python3 scripts/validate_papers.py`
4. **Analyze** — `python3 scripts/analysis/generate_analysis.py`
5. **Visualize** — `python3 scripts/visualize_statistics.py`
6. **Report** — `python3 scripts/analysis/generate_reports.py`
7. **Generate** — `python3 scripts/generate_readme.py`

CI (`.github/workflows/validate.yml`) validates and regenerates on every push;
a weekly scheduled job opens a PR with newly discovered papers.

---

## 🔗 Related Repositories

- **Adjacent corpus:** [business-development-research](https://github.com/tobias-weiss-ai-xr/business-development-research)
- **Adjacent corpus:** [learning-research](https://github.com/tobias-weiss-ai-xr/learning-research)
- **Adjacent corpus:** [graph-research](https://github.com/tobias-weiss-ai-xr/graph-research)
- **Adjacent corpus:** [devops-research](https://github.com/tobias-weiss-ai-xr/devops-research)

---

## 📄 License

**© 2026 Tobias Weiss**

- **Research corpus:** Proprietary
- **Tools:** MIT License

---

## 🙏 Acknowledgments

This corpus synthesizes 8,606 papers across 1991-2026 — plus a rolling
news feed — to create the evidence base for the cyber-security research
program: from academic findings to operational reality.

---

**Want to explore the corpus?**
`cd tools && python3 landscape_analyzer.py`
