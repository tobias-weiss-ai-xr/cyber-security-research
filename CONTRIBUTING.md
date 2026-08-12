# Contributing to ai-literacy-research

Thanks for helping build the evidence base for the AI-literacy research program!

## Ways to Contribute

### 1. Add Papers

1. Fork the repository.
2. Edit `papers.yaml` — append entries in this format:

```yaml
- title: "A great AI-literacy paper"
  date: "2026-07"
  url: https://doi.org/10.xxxx/xxxxx
  category: assessment
  subcategory: evaluation
  authors: []
  abstract: "Short abstract..."
```

3. Open a PR. Use the `paper_submission` issue template for guidance.

### Taxonomy Reference

**Categories (20):** `ai-literacy-construct`, `ai-literacy-pedagogy`,
`learning-design`, `assessment`, `workforce-upskilling`, `org-implementation`,
`sme-training`, `compliance`, `k12-education`, `higher-education`,
`professional-education`, `teacher-ai-literacy`, `critical-ai-literacy`,
`generative-ai-skills`, `attitudes-trust`, `adoption-behavior`,
`program-evaluation`, `roi-measurement`, `tooling`, `lifelong-learning`

**Aspects (8):** `theory`, `mechanism`, `method`, `application`,
`development`, `systems`, `evaluation`, `review`

### 2. Work the Research Program

The program targets two gaps: implementation (`*/development`,
`org-implementation`, `learning-design`) and evaluation (`*/evaluation`,
`program-evaluation`, `roi-measurement`, `assessment`). Evidence synthesis
goes into `docs/research/` following PROTOCOL.md.

### 3. Improve Tooling

All scripts are standard Python 3.11+ with `pyyaml`, `requests`,
`matplotlib`. Keep them dependency-light and self-contained (path resolution
relative to the repo root).

## Validation

Before merging, run:

```bash
python3 scripts/validate_papers.py --strict
python3 scripts/generate_readme.py --check
```
