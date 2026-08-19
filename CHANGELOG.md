# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-19

### Added
- **CISA Known Exploited Vulnerabilities (KEV) catalog as a new info source.**
  `scripts/fetch/fetch_kev.py` pulls CISA's authoritative list of *actively
  exploited* CVEs into `kev.yaml` (1,670 CVEs, full metadata: vendor, product,
  due date, CWEs, ransomware flag) and maps every CVE onto the 20-category
  taxonomy. `--merge-news` folds newly-added CVEs into the rolling news
  tracker; `fetch_news.py` now includes `kev` as a first-class source.
- README generator renders the full `## 📊 Corpus Statistics` section from
  `statistics.json` (top categories, by year, momentum, trending keywords,
  top venues, research gaps) and reports `KEV CVEs Tracked`.
- CI now validates `kev.yaml` (`python3 scripts/fetch/fetch_kev.py --check`).

### Changed
- Corpus extended to **17,026 papers** (+1,295) via OpenAlex, arXiv and
  DBLP/CrossRef/EuropePMC discovery runs.

### Fixed
- `scripts/fetch/fetch_other_sources.py` crashed on a missing `--local` flag
  (referenced but never declared in the argument parser).

## [0.1.0] - 2026-08-11

### Added
- Research program repository targeting the AI-adoption white space
  (`ai-adoption/development` and `ai-adoption/evaluation`)
- 20-category AI-literacy taxonomy (constructs, pedagogy, assessment,
  workforce upskilling, org implementation, compliance, program evaluation)
- Fetch, analysis, validation and visualization scripts (OpenAlex primary,
  arXiv secondary, DBLP/CrossRef/EuropePMC multi-source)
- Research planning tools (topic planner, trend scanner, brief generator,
  landscape analyzer)
- CI validation workflow (validate papers + README freshness)
- Research program documentation (RESEARCH_PLAN.md, PROTOCOL.md, taxonomy)
