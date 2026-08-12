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

1. **Corpus** — research papers across 20 cyber-security disciplines, analyzed
   with the taxonomy → momentum → burst → gap pipeline used in
   [business-development-research](https://github.com/tobias-weiss-ai-xr/business-development-research)
   and [graph-research](https://github.com/tobias-weiss-ai-xr/graph-research).

**News feed:** 472 items from 27 sources — CISA news + advisories, NIST, ENISA, BSI, Cloudflare, Google Security, Talos, Unit 42, Qualys, Sucuri, The Record, BleepingComputer, SecurityWeek, Threatpost, Dark Reading, The Register, CSO Online, Infosecurity Magazine, Help Net Security, The Hacker News, Krebs, SANS ISC, EFF, Schneier.
2. **News tracker** — a rolling feed of operational cyber-security news
   (CISA advisories, ENISA, BSI, NCSC, The Hacker News, Krebs on Security,
   SANS ISC, …), deduplicated by URL and mapped onto the same taxonomy
   (see `news.yaml`).

### Research Scope

| Metric | Value |
|--------|-------|
| **Cyber-Security Disciplines** | 20 |
| **Research Aspects** | 8 (theory · mechanism · method · application · development · systems · evaluation · review) |
| **Taxonomy Cells** | 160 |
| **News Sources Tracked** | 27 |

## 📰 News Tracker

Operational news (advisories, alerts, breach reports, policy changes) moves
faster than the literature. `scripts/fetch/fetch_news.py` pulls RSS/HTML from
authoritative sources, normalizes and deduplicates entries into `news.yaml`,
tagged with the same 20-category taxonomy so news can be cross-referenced
against the research corpus.

```bash
python3 scripts/fetch/fetch_news.py                       # all sources, last 14 days
python3 scripts/fetch/fetch_news.py --sources cisa,thn    # subset
python3 scripts/fetch/fetch_news.py --via-host weiss@192.168.42.11   # CISA via allowed egress
python3 scripts/fetch/fetch_news.py --check               # validate news.yaml
```

**Note on CISA:** cisa.gov returns 403 from some egress IPs; fetch it through
`--via-host` on a server with allowed egress (verified: tobias-weiss.org, tobi-yoga).

## 🔄 Pipeline

1. **Discover** — `python3 scripts/fetch/fetch_openalex.py --months 3` (or the distributed bulk fetcher)
2. **News** — `python3 scripts/fetch/fetch_news.py`
3. **Validate** — `python3 scripts/validate_papers.py`
4. **Analyze** — `python3 scripts/analysis/generate_analysis.py`
5. **Visualize** — `python3 scripts/visualize_statistics.py`
6. **Report** — `python3 scripts/analysis/generate_reports.py`
7. **Generate** — `python3 scripts/generate_readme.py`

CI (`.github/workflows/validate.yml`) validates the corpus and news on every push.

## 🔗 Related Repositories

- [business-development-research](https://github.com/tobias-weiss-ai-xr/business-development-research)
- [learning-research](https://github.com/tobias-weiss-ai-xr/learning-research)
- [graph-research](https://github.com/tobias-weiss-ai-xr/graph-research)
- [devops-research](https://github.com/tobias-weiss-ai-xr/devops-research)

## 📄 License

**© 2026 Tobias Weiss** — Research corpus: Proprietary · Tools: MIT License
