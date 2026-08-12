# AI-Literacy Research Tools — API Reference

Tools that turn the corpus into research priorities and content plans for the
AI-literacy research program.

| Tool | Purpose |
|------|---------|
| `topic_planner.py` | Evidence-ranked research/content topics (density × velocity) |
| `trend_scanner.py` | Emerging trend detection (keyword bursts, growing cells) |
| `brief_generator.py` | Full briefs for guides (title, outline, key papers) |
| `landscape_analyzer.py` | Full corpus landscape report |

All tools read `papers.yaml` at the repository root. Run them from anywhere —
they resolve paths relative to the repo.

---

## 1. Topic Planner (`topic_planner.py`)

Ranks research areas by corpus density × 12-month research velocity and writes
`docs/topics/ARTICLE_TOPICS.md`.

```bash
python3 tools/topic_planner.py                # top 10 topics
python3 tools/topic_planner.py --top 20
python3 tools/topic_planner.py --json         # machine-readable output
```

**How ranking works:**
- **Density:** number of papers in the category
- **Velocity:** share of category papers published in the last 12 months
- **Score:** density + recency-weighted component

---

## 2. Trend Scanner (`trend_scanner.py`)

Detects research trends via keyword-burst analysis: a keyword is a *burst* if
its share of recent papers exceeds its share of the whole corpus.

```bash
python3 tools/trend_scanner.py --months 6
python3 tools/trend_scanner.py --months 12 --json
```

**Output:**
- 🔥 Top keyword bursts (recent share vs corpus share)
- 📈 Fastest-growing taxonomy cells (share of papers in look-back window)

**Customisation:** extend `TREND_KEYWORDS` in the script with domain terms
(e.g. `agentic`, `prompt engineering`, `eu ai act`).

---

## 3. Brief Generator (`brief_generator.py`)

Builds a write-ready brief for a topic by matching corpus papers
(keyword overlap + phrase bonus + recency).

```bash
python3 tools/brief_generator.py "EU AI Act literacy obligations" --papers 5
python3 tools/brief_generator.py "AI literacy assessment" --json
```

**Output:** title candidates, angle, 7-section outline, key papers
(title/date/url/category), open questions.

---

## 4. Landscape Analyzer (`landscape_analyzer.py`)

Produces a structured picture of the corpus — category growth/velocity,
research aspects, year trends, venue mix, top authors, hot & thin cells,
and emerging themes.

```bash
python3 tools/landscape_analyzer.py               # terminal report
python3 tools/landscape_analyzer.py --json        # machine-readable
python3 tools/landscape_analyzer.py --write-doc   # docs/research/landscape_report.md
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `papers.yaml not found` | Run from repo root or `cd ~/git/ai-literacy-research` |
| Empty results | Corpus not fetched yet — run `scripts/fetch/fetch_openalex.py` |
| Wrong categories in output | Taxonomy assignments are auto-tagged; refine in `papers.yaml` |

## Configuration

All tools are zero-config — the only dependency is `pyyaml`:

```bash
pip install -r requirements.txt
```