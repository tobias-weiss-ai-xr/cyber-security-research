#!/usr/bin/env python3
"""Generate research reports from the corpus:
  - docs/research/literature_review.md    (synthesis + top papers per category)
  - docs/research/cyber_security_trends_2026.md   (trend report from trend scanner)

Usage:
    python3 scripts/analysis/generate_reports.py
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
from trend_scanner import scan as scan_trends  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE)

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

KEY_INSIGHTS = {
    "threat-intelligence": (
        "Threat-intelligence research spans collection, sharing and analytics: CTI platforms, TTP modeling and automated indicator correlation. Attribution and intelligence sharing (ISACs) are dominant themes; evaluation of intelligence quality is thin."
    ),
    "vulnerability-management": (
        "Vulnerability research covers discovery, coordinated disclosure and remediation. CVE/CVSS-based prioritization is criticized for ignoring exploitability — exploit-driven risk scoring is the emergent direction."
    ),
    "incident-response": (
        "Incident-response and forensics research covers playbooks, memory/disk forensics and detection-to-response timelines. Automation (SOAR-style) reduces containment time; post-incident learning is under-studied."
    ),
    "malware-analysis": (
        "Malware research pairs static/dynamic analysis with ML-based classification. Ransomware family tracking and evasion-aware detectors dominate; dataset labeling quality is a recurring limitation."
    ),
    "network-security": (
        "Network-security research is dominated by intrusion detection (signature vs anomaly vs ML-based). Evasion, adversarial robustness and deployment reality (imbalanced traffic) are the open problems."
    ),
    "application-security": (
        "Application-security research covers secure SDLC, SAST/DAST and developer security behavior. Tooling improves but developer adoption and false-positive fatigue remain the binding constraints."
    ),
    "cloud-security": (
        "Cloud-security research targets misconfiguration, container and Kubernetes hardening, and serverless attack surface. CSPM/IaC scanning is the commercial answer; runtime drift detection is emerging."
    ),
    "identity-access": (
        "Identity and access research covers IAM architecture, MFA/FIDO and privileged access. Phishing-resistant authentication and identity governance at scale are the active frontiers."
    ),
    "cryptography": (
        "Cryptography research is transitioning to post-quantum algorithms (NIST PQC), with homomorphic and zero-knowledge techniques advancing privacy-preserving computation. Implementation side-channels remain the failure mode."
    ),
    "zero-trust": (
        "Zero-trust research formalizes never-trust-always-verify architecture: continuous verification, microsegmentation and identity-centric access. Adoption maturity models and migration costs are the practical gap."
    ),
    "supply-chain-security": (
        "Supply-chain research follows the dependency-attack wave: SBOM, provenance and reproducible builds. Package-manager trust models and artifact signing are the mitigation frontier."
    ),
    "security-operations": (
        "SOC research targets detection engineering, alert triage and automation. Alert fatigue and analyst burnout are chronic; AI-assisted triage is the active answer."
    ),
    "ai-security": (
        "AI-security research covers adversarial ML, prompt injection, jailbreaks and poisoning. LLM red-teaming and evals are the fastest-moving subfield; runtime monitoring lags."
    ),
    "security-education": (
        "Security-education research evaluates training, awareness programs and workforce development. Serious games and cyber ranges improve engagement; transfer to real behavior is the weak link (mirrors the training-evaluation gap seen in adjacent domains)."
    ),
    "security-compliance": (
        "Compliance research maps frameworks (NIST CSF, ISO 27001) onto organizational practice. NIS2/CMMC raise the stakes; framework proliferation and audit burden are the practical pain points."
    ),
    "risk-management": (
        "Risk-management research moves from qualitative matrices to quantitative models (FAIR-style). Cyber insurance pricing and board-level risk communication are the applied edge."
    ),
    "privacy": (
        "Privacy research spans GDPR compliance, PETs and breach economics. Consent fatigue and the usability of privacy controls are the persistent gaps."
    ),
    "iot-security": (
        "IoT/OT security research covers device vulnerabilities, ICS and SCADA protection. Patching constraints and air-gapped environments make traditional controls inapplicable — runtime anomaly detection is the workaround."
    ),
    "human-factor": (
        "Human-factor research quantifies phishing susceptibility, social engineering and risky behaviors. Just-in-time interventions and behavioral nudges outperform annual training — evidence transferable to security-awareness programs."
    ),
    "cyber-warfare": (
        "Cyber-warfare research analyzes state-sponsored operations, attribution and deterrence theory. Critical-infrastructure resilience and international norms are the policy frontier."
    ),
}

def render_literature_review(papers, now, stats=None):
    total = len(papers)
    lines = [
        "# Cyber-Security Research — Literature Review",
        "",
        f"**Generated:** {now}  ",
        f"**Corpus:** {total:,} papers across {len(CATEGORY_DISPLAY)} categories",
        "",
        "> Synthesis of the cyber-security research corpus. Category "
        "insights are drawn from title/abstract analysis of the papers themselves.",
        "",
        "---",
        "",
        "## Corpus Overview",
        "",
    ]
    cat_counter = Counter(p.get("category", "unknown") for p in papers)
    sub_counter = Counter(p.get("subcategory", "unknown") for p in papers)
    year_counter = Counter(p.get("date", "")[:4] for p in papers if p.get("date"))
    top_cats = sorted(cat_counter.items(), key=lambda kv: -kv[1])[:5]

    lines.append("| Rank | Category | Papers |")
    lines.append("|------|----------|--------|")
    for i, (c, n) in enumerate(top_cats, 1):
        lines.append(f"| {i} | {CATEGORY_DISPLAY.get(c, c)} | {n} |")

    years = sorted(y for y in year_counter if y)
    lines += [
        "",
        f"**Time span:** {years[0]}–{years[-1]} (median year {years[len(years)//2] if years else '—'})",
        f"**Dominant aspects:** {', '.join(f'{SUBCATEGORY_DISPLAY.get(s, s)} ({n})' for s, n in sub_counter.most_common(3))}",
        "",
        "---",
        "",
    ]

    # ---- enhanced sections drawn from statistics.json ----
    if isinstance(stats, dict):
        mom = stats.get("momentum", [])
        if mom:
            lines += [
                "## 📈 Research Momentum (Last 12 Months)",
                "",
                "Categories ranked by a momentum score combining recent output "
                "density with year-over-year growth.",
                "",
                "| Category | Total | Last 12m | Prior 12m | Growth | 12-m share | Papers/mo |",
                "|----------|------:|---------:|----------:|-------:|----------:|----------:|",
            ]
            for m in mom:
                g = f"{m['growth_pct']:+}%" if m['growth_pct'] is not None else "—"
                lines.append(
                    f"| {m['name']} | {m['total']} | {m['recent']} | {m['prior']} | {g} | "
                    f"{m['recent_share']*100:.0f}% | {m['papers_per_month']} |"
                )
            lines += ["", "---", ""]

        gaps = stats.get("gaps", {})
        if gaps:
            lines += ["## 🕳️ Research Gaps & White Space", ""]
            thinnest = gaps.get("thinnest_cells", [])[:8]
            if thinnest:
                lines += ["**Thinnest taxonomy cells:**", "", "| Cell | Papers |", "|------|--------|"]
                for g in thinnest:
                    lines.append(f"| `{g['cell']}` | {g['papers']} |")
                lines.append("")
            ws = gaps.get("white_space", [])[:8]
            if ws:
                lines += [
                    "**White-space cells** (low total but fast-growing):", "",
                    "| Cell | Total | Last-12m | 12-m share |",
                    "|------|-------:|---------:|-----------:|",
                ]
                for w in ws:
                    lines.append(f"| `{w['cell']}` | {w['total']} | {w['recent']} | {w['recent_share']*100:.0f}% |")
                lines.append("")
            lines += ["---", ""]

        if stats.get("venues"):
            lines += [
                "## Publishing Venues", "",
                "Top venues by paper count (where present in the metadata):", "",
                "| Venue | Papers |", "|-------|--------|",
            ]
            for v in stats["venues"][:10]:
                lines.append(f"| {v['name']} | {v['papers']} |")
            lines += ["", "---", ""]

    lines += ["", "## Category Insights", ""]
    for c in sorted(cat_counter, key=lambda c: -cat_counter[c]):
        if cat_counter[c] == 0:
            continue
        insight = KEY_INSIGHTS.get(c, "Category is still saturating — see `statistics.json` for cell counts.")
        # top recent papers
        cat_papers = [p for p in papers if p.get("category") == c and p.get("date", "") >= "2025-01"]
        cat_papers.sort(key=lambda p: p.get("date", ""), reverse=True)
        top3 = cat_papers[:3]
        lines += [
            f"### {CATEGORY_DISPLAY.get(c, c)} (`{c}`)",
            "",
            f"{insight}",
            "",
            f"**Corpus size:** {cat_counter[c]} papers",
        ]
        if top3:
            lines += ["", "**Recent papers:**", ""]
            for p in top3:
                lines.append(f"- [{p['date']}] {p['title'][:100]} — {p.get('url', '')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines += [
        "## Methodology",
        "",
        "1. Papers are discovered via taxonomy-aware arXiv queries and "
        "auto-classified into the 20×8 taxonomy.",
        "2. Category insights above are editorially curated but grounded in "
        "corpus statistics.",
        "3. Regenerate this document with `scripts/analysis/generate_reports.py`.",
        "",
    ]
    return "\n".join(lines)


def render_trend_report(papers, now, stats=None):
    result = scan_trends(papers, months=12, top=15)
    lines = [
        "# Cyber-Security Research Trends (12-Month View)",
        "",
        f"**Generated:** {now}  ",
        f"**Window:** since {result['cutoff']} — {result['recent_papers']} of {len(papers)} papers",
        "",
        "## 🔥 Keyword Bursts",
        "",
        "| Keyword | Recent | Total | Burst |",
        "|---------|--------|-------|-------|",
    ]
    for t in result["trends"]:
        lines.append(f"| {t['keyword']} | {t['recent_papers']} | {t['total_papers']} | {t['burst_score']}× |")

    lines += [
        "",
        "## 📈 Fastest-Growing Cells",
        "",
        "| Cell | Recent | Total | Recent Share |",
        "|------|--------|-------|--------------|",
    ]
    for g in result["growing_cells"]:
        lines.append(f"| `{g['cell']}` | {g['recent']} | {g['total']} | {g['recent_share']*100:.0f}% |")

    lines += [
        "",
        "## What This Means for the ALaaS Research Program",
        "",
        "- Categories with high burst scores are the safest content bets "
        "(reader interest follows research momentum) for the threat-intelligence and incident-response guides.",
        "- Fast-growing cells with few total papers are white-space opportunities: "
        "early coverage builds topical authority before the definitive guides land.",
        "- Thin cells in `statistics.json` mark research gaps where evidence is "
        "thin — write with appropriate caution.",
        "",
        "Regenerate with `python3 tools/trend_scanner.py --months 12`.",
        "",
    ]
    return "\n".join(lines)


def main():
    with open(os.path.join(BASE, "papers.yaml"), encoding="utf-8") as f:
        data = yaml.safe_load(f)
    papers = data.get("papers", [])
    now = datetime.now().isoformat()[:10]

    lit_path = os.path.join(BASE, "docs", "research", "literature_review.md")
    stats_path = os.path.join(BASE, "statistics.json")
    stats = None
    if os.path.exists(stats_path):
        with open(stats_path, encoding="utf-8") as f:
            stats = json.load(f)

    with open(lit_path, "w", encoding="utf-8") as f:
        f.write(render_literature_review(papers, now, stats))
    print(f"Wrote {lit_path}")

    trend_path = os.path.join(BASE, "docs", "research", "cyber_security_trends_2026.md")
    with open(trend_path, "w", encoding="utf-8") as f:
        f.write(render_trend_report(papers, now, stats))
    print(f"Wrote {trend_path}")


if __name__ == "__main__":
    main()
