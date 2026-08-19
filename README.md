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

1. **Corpus** — 17,026 research papers across 20 cyber-security disciplines,
   analyzed with the taxonomy → momentum → burst → gap pipeline used in
   [business-development-research](https://github.com/tobias-weiss-ai-xr/business-development-research)
   and [graph-research](https://github.com/tobias-weiss-ai-xr/graph-research).
2. **News tracker** — a rolling 786-item feed of operational
   cyber-security news (CISA advisories, NIST/NIST-IR, ENISA, BSI, NCSC, …),
   deduplicated by URL and mapped onto the same taxonomy (see `news.yaml`).

### Research Scope

| Metric | Value |
|--------|-------|
| **Papers Analyzed** | 17,026 |
| **Cyber-Security Disciplines** | 20 |
| **Time Span** | 1991-2026 |
| **Research Aspects** | 8 |
| **Taxonomy Cells** | 160 |
| **Saturation** | 100.0% (160/160 cells) |
| **News Items Tracked** | 786 |
| **KEV CVEs Tracked** | 1,670 |

### Top Evidence Areas

...
│   └── landscape_analyzer.py          # Landscape report ✨
│
├── scripts/                           # Research pipeline
│   ├── fetch/                         # OpenAlex (primary), arXiv, DBLP/CrossRef
│   ├── fetch/fetch_news.py            # News-tracker (CISA, NIST, ENISA, …)
│   ├── fetch/fetch_kev.py             # CISA KEV catalog — latest exploited CVEs
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

**CISA Known Exploited Vulnerabilities (KEV).** For security, tracking the
*latest CVEs that are actually being exploited* is the highest-value signal.
`scripts/fetch/fetch_kev.py` pulls CISA's KEV catalog — every CVE known to be
actively exploited in the wild — into `kev.yaml` (full metadata: vendor,
product, due date, CWEs, ransomware flag) and, with `--merge-news`, folds newly
added CVEs into the rolling news tracker so they surface alongside advisories.

```bash
python3 scripts/fetch/fetch_news.py [--sources cisa,nist,enisa,bsi,ncsc,thn,krebs,kev] [--days 14]
python3 scripts/fetch/fetch_news.py --check     # validate news.yaml
python3 scripts/fetch/fetch_kev.py              # build/update kev.yaml
python3 scripts/fetch/fetch_kev.py --merge-news --merge-days 14   # also push new CVEs to news.yaml
python3 scripts/fetch/fetch_kev.py --check      # validate kev.yaml
```

**Sources:** CISA news + cybersecurity advisories and the **KEV catalog** (via
CISA-accessible egress), NIST, ENISA, BSI, NCSC-UK, CERT-EU, The Hacker News,
Krebs on Security, SANS ISC.

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
   **KEV CVEs** — `python3 scripts/fetch/fetch_kev.py --merge-news`  (CISA Known Exploited Vulnerabilities)
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

**17,026 papers** across **20 categories**.  
Sources: **arXiv** 3,840 (23%) · **DOI** 12,804 (75%) · **Other** 382 (2%).  
Full paper list: [GitHub Pages site](https://tobias-weiss-ai-xr.github.io/cyber-security-research).

### Top categories

| Category | Papers | Recent | |
|----------|--------|--------|-|
| Network & Perimeter Security | **1,251** | 523 | ████████████████████ |
| Incident Response & Forensics | **1,202** | 514 | ███████████████████ |
| Vulnerability Management | **1,122** | 636 | ██████████████████ |
| Cryptography & Protocols | **1,061** | 373 | █████████████████ |
| Malware Analysis & Reverse Engineering | **980** | 399 | ████████████████ |
| AI & Adversarial ML Security | **970** | 520 | ████████████████ |
| Application Security & DevSecOps | **963** | 475 | ███████████████ |
| Identity, Access & Authentication | **956** | 407 | ███████████████ |
| Software Supply Chain Security | **931** | 462 | ███████████████ |
| Cloud & Container Security | **910** | 390 | ███████████████ |

### By year

| Year | Papers | |
|------|--------|-|
| 1991 | 1 |  |
| 1995 | 2 |  |
| 2000 | 1 |  |
| 2002 | 2 |  |
| 2003 | 3 |  |
| 2005 | 5 |  |
| 2007 | 12 |  |
| 2008 | 3 |  |
| 2009 | 1 |  |
| 2010 | 6 |  |
| 2011 | 10 |  |
| 2012 | 1 |  |
| 2013 | 11 |  |
| 2014 | 16 |  |
| 2015 | 8 |  |
| 2016 | 13 |  |
| 2017 | 13 |  |
| 2018 | 14 |  |
| 2019 | 16 |  |
| 2020 | 25 |  |
| 2021 | 537 | ██ |
| 2022 | 1,681 | ██████ |
| 2023 | 1,866 | ███████ |
| 2024 | 3,006 | ████████████ |
| 2025 | 4,460 | █████████████████ |
| 2026 | 5,176 | ████████████████████ |

### Momentum (hottest categories)

| Category | Total | Rate | Recent | Score |
|----------|-------|------|--------|-------|
| Vulnerability Management | 1,122 | 53.0/mo | 57% | 280 |
| AI & Adversarial ML Security | 970 | 43.3/mo | 54% | 193 |
| Application Security & DevSecOps | 963 | 39.6/mo | 49% | 177 |
| Software Supply Chain Security | 931 | 38.5/mo | 50% | 161 |
| Security Operations & SOC | 713 | 30.4/mo | 51% | 159 |

### Trending keywords

| Keyword | Papers | Burst |
|---------|--------|-------|
| cmmc | 3 | 2.49 |
| typosquatting | 3 | 2.49 |
| red teaming | 14 | 2.31 |
| jailbreak | 51 | 2.25 |
| detection engineering | 9 | 2.21 |
| unpacking | 7 | 2.13 |
| identity governance | 13 | 2.11 |
| sandbox | 47 | 2.07 |

### Top venues

| Venue | Papers |
|-------|--------|
| Zenodo (CERN European Organization for Nuclear Research) | 703 |
| IEEE Access | 277 |
| SSRN Electronic Journal | 212 |
| Lecture notes in computer science | 206 |
| arXiv | 166 |
| Applied Sciences | 131 |
| Sensors | 129 |
| Electronics | 127 |

### Research gaps (thinnest cells)

| Cell | Papers |
|------|--------|
| `security-compliance/evaluation` | 1 |
| `cyber-warfare/evaluation` | 1 |
| `zero-trust/evaluation` | 2 |
| `cloud-security/evaluation` | 2 |
| `risk-management/evaluation` | 3 |
| `iot-security/evaluation` | 3 |
| `risk-management/development` | 4 |
| `human-factor/development` | 5 |

*Generated 2026-08 by `scripts/standard_stats.py`.*


## 🙏 Acknowledgments

This corpus synthesizes 17,026 papers across 1991-2026 — plus a rolling
news feed — to create the evidence base for the cyber-security research
program: from academic findings to operational reality.

---

**Want to explore the corpus?**
`cd tools && python3 landscape_analyzer.py`
