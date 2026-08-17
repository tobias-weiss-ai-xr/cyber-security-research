<h1 align="center">
  <strong>Cyber-Security Research Corpus</strong>
</h1>
<h3 align="center">Evidence base for the cyber-security landscape — 20 categories × 8 research aspects</h3>

<div align="center">
  [![GitHub](https://img.shields.io/badge/GitHub-tobias-weiss-ai-xr/cyber--security--research-181717.svg?logo=github)](https://github.com/tobias-weiss-ai-xr/cyber-security-research)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![CI](https://img.shields.io/github/actions/workflow/status/tobias-weiss-ai-xr/cyber--security--research/validate.yml?label=CI&logo=github)](https://github.com/tobias-weiss-ai-xr/cyber-security-research/actions/workflows/validate.yml)
  [![DevOps](https://img.shields.io/badge/DevOps-devops--research-blue.svg?logo=github)](https://github.com/tobias-weiss-ai-xr/devops-research) [![C2-AI](https://img.shields.io/badge/C2-AI-c2--ai--research-blue.svg?logo=github)](https://github.com/tobias-weiss-ai-xr/c2-ai-research)
</div>

> 🔒 **Cyber-security research corpus:** threat intelligence, vulnerabilities,
> incident response, malware, network/cloud/application security, zero trust,
> supply chain, AI security, compliance, risk, privacy, IoT/OT, and the human factor —
> part of the family of `*-research` corpora.

<p align="center">
  <img src="https://raw.githubusercontent.com/tobias-weiss-ai-xr/cyber-security-research/main/assets/visualizations/category_distribution.png" alt="Teaser" width="600" />
</p>

---

## 🎯 Overview

This repository combines two knowledge layers:

1. **Corpus** — 14,163 research papers across 20 cyber-security disciplines,
   analyzed with the taxonomy → momentum → burst → gap pipeline used in
   [business-development-research](https://github.com/tobias-weiss-ai-xr/business-development-research)
   and [graph-research](https://github.com/tobias-weiss-ai-xr/graph-research).
2. **News tracker** — a rolling 763-item feed of operational
   cyber-security news (CISA advisories, NIST/NIST-IR, ENISA, BSI, NCSC, …),
   deduplicated by URL and mapped onto the same taxonomy (see `news.yaml`).

### Research Scope

| Metric | Value |
|--------|-------|
| **Papers Analyzed** | 14,163 |
| **Cyber-Security Disciplines** | 20 |
| **Time Span** | 1991-2026 |
| **Research Aspects** | 8 |
| **Taxonomy Cells** | 160 |
| **Saturation** | 100.0% (160/160 cells) |
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
## 📊 Corpus Statistics

**14,163 papers** across **20 categories**.  
Sources: **arXiv** 3,350 (23%) · **DOI** 10,639 (75%) · **Other** 174 (1%).  
Full paper list: [GitHub Pages site](https://tobias-weiss-ai-xr.github.io/cyber-security-research).

### Top categories

| Category | Papers | Recent | |
|----------|--------|--------|-|
| network-security | **1,088** | 0 | ████████████ |
| cryptography | **970** | 0 | ██████████░░ |
| incident-response | **869** | 0 | █████████░░░ |
| vulnerability-management | **842** | 0 | █████████░░░ |
| ai-security | **802** | 0 | ████████░░░░ |
| malware-analysis | **764** | 0 | ████████░░░░ |
| supply-chain-security | **743** | 0 | ████████░░░░ |
| threat-intelligence | **715** | 0 | ███████░░░░░ |
| cloud-security | **709** | 0 | ███████░░░░░ |
| application-security | **704** | 0 | ███████░░░░░ |
| *other* | **5,957** | | |


### By year

| Year | Papers | |
|------|--------|-|
| 2025 | 4,460 | ████████████ |
| 2026 | 2,326 | ██████░░░░░░ |
| unknown | 128 | ░░░░░░░░░░░░ |


### Momentum (hottest categories)

| Category | Total | Rate | Recent | Score |
|----------|-------|------|--------|-------|
| Vulnerability Management | 842 | 29.8/mo | 42% | 124 |
| AI & Adversarial ML Security | 802 | 29.3/mo | 44% | 106 |
| Security Operations & SOC | 590 | 20.2/mo | 41% | 78 |
| Software Supply Chain Security | 743 | 22.8/mo | 37% | 62 |
| Network & Perimeter Security | 1,088 | 30.2/mo | 33% | 48 |


### Trending keywords

| Keyword | Papers | Burst |
|---------|--------|-------|
| cmmc | 3 | 3.55 |
| typosquatting | 1 | 3.55 |
| red teaming | 11 | 3.23 |
| detection engineering | 9 | 3.16 |
| jailbreak | 37 | 3.07 |
| alert fatigue | 20 | 2.84 |
| unpacking | 5 | 2.84 |
| nis2 | 18 | 2.76 |


### Top venues

| Venue | Papers |
|-------|--------|
| IEEE Access | 277 |
| Zenodo (CERN European Organization for Nuclear Research) | 243 |
| SSRN Electronic Journal | 212 |
| Lecture notes in computer science | 166 |
| Applied Sciences | 123 |
| Electronics | 121 |
| Sensors | 120 |
| Computers & Security | 112 |


### Research gaps (thinnest cells)

| Cell | Papers |
|------|--------|
| `security-compliance/evaluation` | 1 |
| `cyber-warfare/evaluation` | 1 |
| `cloud-security/evaluation` | 1 |
| `zero-trust/evaluation` | 2 |
| `risk-management/evaluation` | 3 |



*Generated 2026-10 by `scripts/standard_stats.py`.*

## 📊 Corpus Statistics

**14,163 papers** across **20 categories**.  
Sources: **arXiv** 3,350 (23%) · **DOI** 10,639 (75%) · **Other** 174 (1%).  
Full paper list: [GitHub Pages site](https://tobias-weiss-ai-xr.github.io/cyber-security-research).

### Top categories

| Category | Papers | Recent | |
|----------|--------|--------|-|
| network-security | **1,088** | 0 | ████████████ |
| cryptography | **970** | 0 | ██████████░░ |
| incident-response | **869** | 0 | █████████░░░ |
| vulnerability-management | **842** | 0 | █████████░░░ |
| ai-security | **802** | 0 | ████████░░░░ |
| malware-analysis | **764** | 0 | ████████░░░░ |
| supply-chain-security | **743** | 0 | ████████░░░░ |
| threat-intelligence | **715** | 0 | ███████░░░░░ |
| cloud-security | **709** | 0 | ███████░░░░░ |
| application-security | **704** | 0 | ███████░░░░░ |
| *other* | **5,957** | | |


### By year

| Year | Papers | |
|------|--------|-|
| 2025 | 4,460 | ████████████ |
| 2026 | 2,326 | ██████░░░░░░ |
| unknown | 128 | ░░░░░░░░░░░░ |


### Momentum (hottest categories)

| Category | Total | Rate | Recent | Score |
|----------|-------|------|--------|-------|
| Vulnerability Management | 842 | 29.8/mo | 42% | 124 |
| AI & Adversarial ML Security | 802 | 29.3/mo | 44% | 106 |
| Security Operations & SOC | 590 | 20.2/mo | 41% | 78 |
| Software Supply Chain Security | 743 | 22.8/mo | 37% | 62 |
| Network & Perimeter Security | 1,088 | 30.2/mo | 33% | 48 |


### Trending keywords

| Keyword | Papers | Burst |
|---------|--------|-------|
| cmmc | 3 | 3.55 |
| typosquatting | 1 | 3.55 |
| red teaming | 11 | 3.23 |
| detection engineering | 9 | 3.16 |
| jailbreak | 37 | 3.07 |
| alert fatigue | 20 | 2.84 |
| unpacking | 5 | 2.84 |
| nis2 | 18 | 2.76 |


### Top venues

| Venue | Papers |
|-------|--------|
| IEEE Access | 277 |
| Zenodo (CERN European Organization for Nuclear Research) | 243 |
| SSRN Electronic Journal | 212 |
| Lecture notes in computer science | 166 |
| Applied Sciences | 123 |
| Electronics | 121 |
| Sensors | 120 |
| Computers & Security | 112 |


### Research gaps (thinnest cells)

| Cell | Papers |
|------|--------|
| `security-compliance/evaluation` | 1 |
| `cyber-warfare/evaluation` | 1 |
| `cloud-security/evaluation` | 1 |
| `zero-trust/evaluation` | 2 |
| `risk-management/evaluation` | 3 |



*Generated 2026-10 by `scripts/standard_stats.py`.*


## 🙏 Acknowledgments

This corpus synthesizes 14,163 papers across 1991-2026 — plus a rolling
news feed — to create the evidence base for the cyber-security research
program: from academic findings to operational reality.

---

**Want to explore the corpus?**
`cd tools && python3 landscape_analyzer.py`
