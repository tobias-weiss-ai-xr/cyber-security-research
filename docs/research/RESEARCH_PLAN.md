# Cyber-Security Research Plan

**Status:** corpus seeded (8,606 papers) · news tracker live (39 sources, 763 items) · analysis pipeline generated

## Mission

Turn a large cyber-security corpus + live operational news into evidence-based,
practitioner-usable deliverables: landscape maps, deep-dive briefs, and an
alert→paper bridge that connects breaking advisories to the underlying
research base.

## Deliverables

| # | Deliverable | Targets | Status |
|---|-------------|---------|--------|
| 1 | Landscape mapping | all 20 categories × 8 aspects | generated (`literature_review.md`) |
| 2 | Trend report | momentum + keyword bursts | generated (`cyber_security_trends_2026.md`) |
| 3 | Deep-dive: incident response | `incident-response`, `network-security`, `threat-intelligence` | planned |
| 4 | Deep-dive: AI security | `ai-security`, `supply-chain-security` | planned |
| 5 | Alert→paper bridge | `fetch_news.py` categories ↔ corpus cells | live (news tagged) |
| 6 | White-space report | empty/thin cells (see `taxonomy.md`) | planned |

## Evidence Base

- **Corpus:** 8,606 papers (OpenAlex 6,608 · arXiv 1,466 · CrossRef/DBLP 532),
  20 categories × 8 aspects, 1991–2026.
- **News:** 763 items from 39 sources (CISA news + advisories, NIST, ENISA, BSI,
  Cloudflare, Talos, Unit 42, Check Point, Securelist, Wiz, SentinelOne, The
  Record, BleepingComputer, SecurityWeek, Dark Reading, The Register, TechCrunch
  Security, Ars Technica, CyberScoop, BankInfoSecurity, THN, Krebs, SANS ISC,
  EFF, Schneier, Troy Hunt, PortSwigger, Netskope, …), deduplicated by URL,
  classified into the same taxonomy.

## Pipeline

1. **Discover** — `python3 scripts/fetch/fetch_openalex.py` (or the distributed
   bulk fetcher across the 4 personal servers for 4× daily credit budget)
2. **News** — `python3 scripts/fetch/fetch_news.py [--via-host ...]`
3. **Validate** — `python3 scripts/validate_papers.py` + `fetch_news.py --check`
4. **Analyze** — `scripts/analysis/generate_analysis.py`
5. **Visualize** — `scripts/visualize_statistics.py`
6. **Report** — `scripts/analysis/generate_reports.py`
7. **README** — `scripts/generate_readme.py`

## Refresh Cadence

- **Corpus:** distributed OpenAlex refresh (manual, ~monthly); deep passes after
  each midnight-UTC credit reset (configs in `business-development-research/examples/`)
- **News:** manual daily fetch (one command; CISA via `--via-host`)
- **CI:** validates corpus + news on every push

## Quality Tiers (for deep-dives)

| Tier | Definition |
|------|-----------|
| A | Peer-reviewed, replicated, representative sample |
| B | Peer-reviewed, single strong study / panel |
| C | Peer-reviewed, correlational / small sample |
| D | Preprint / practitioner evidence (vendor blog, advisory) |
| E | Opinion / single case |

Claims in deep-dives must cite their tier; load-bearing recommendations should
rest on B+ evidence, with news items as leading indicators (D/E) that point to
emerging literature.
