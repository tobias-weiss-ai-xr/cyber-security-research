#!/usr/bin/env python3
"""Generate statistics.json, papers.json and D3.js visualization data from papers.yaml.

Enhancements over the baseline counts:
  - category momentum (12-month velocity, YoY growth, recent share + score)
  - category trajectories (per-year counts)
  - keyword bursts (recent share vs corpus share)
  - venue & source analytics (arXiv / DOI / other, top publishing venues)
  - research gaps (thinnest cells + white-space "fast-growing, thin" cells)
  - top authors
"""

import json
import os
import re
import yaml
from collections import Counter, defaultdict
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

CATEGORY_ORDER = list(CATEGORY_DISPLAY.keys())

SUBCATEGORY_ORDER = [
    "theory",
    "mechanism",
    "method",
    "application",
    "development",
    "systems",
    "evaluation",
    "review",
]

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

CAT_COLORS = [
    "#58a6ff", "#3fb950", "#d29922", "#f0883e", "#db6d8a",
    "#7ee787", "#a5d6ff", "#79c0ff", "#ffa657", "#ff7b72",
    "#d2a8ff", "#79c0ff", "#56d4dd", "#b392f0", "#ffc680",
    "#85e89d", "#f778ba", "#68a4ff", "#ffdf5d", "#a371f7",
]

# Keywords tracked for emerging-theme analysis (recent-vs-corpus burst).
BURST_KEYWORDS = [
    "adversarial",
    "alert fatigue",
    "anomaly detection",
    "anonymization",
    "attribution",
    "capture the flag",
    "certification",
    "cmmc",
    "consent",
    "container",
    "coordinated disclosure",
    "critical infrastructure",
    "cspm",
    "cti",
    "cve",
    "cyber insurance",
    "cyber range",
    "cyber risk",
    "cyber warfare",
    "cybersecurity education",
    "dast",
    "data breach",
    "data poisoning",
    "dependency",
    "detection engineering",
    "deterrence",
    "devsecops",
    "dfir",
    "digital forensics",
    "dns tunneling",
    "embedded",
    "emulation",
    "evidence",
    "exploit",
    "fido",
    "firmware",
    "gdpr",
    "homomorphic",
    "human factor",
    "iam",
    "ics",
    "identity governance",
    "ids",
    "incident response",
    "indicator of compromise",
    "insider threat",
    "ioc",
    "iot",
    "ips",
    "iso 27001",
    "jailbreak",
    "key management",
    "kubernetes",
    "lattice",
    "least privilege",
    "malware",
    "memory forensics",
    "mfa",
    "microsegmentation",
    "misconfiguration",
    "misdelivery",
    "model poisoning",
    "nis2",
    "nist csf",
    "ot",
    "owasp",
    "passkey",
    "patching",
    "pet",
    "phishing",
    "post-quantum",
    "pqc",
    "privacy",
    "privileged access",
    "prompt injection",
    "provenance",
    "quantification",
    "ransomware",
    "red teaming",
    "reproducible builds",
    "reverse engineering",
    "risk register",
    "sandbox",
    "sast",
    "sbom",
    "scada",
    "secure coding",
    "security awareness",
    "serious games",
    "serverless",
    "siem",
    "soar",
    "soc",
    "social engineering",
    "state-sponsored",
    "static analysis",
    "supply chain",
    "threat actor",
    "threat hunting",
    "threat intelligence",
    "traffic analysis",
    "ttps",
    "typosquatting",
    "unpacking",
    "var",
    "zero standing privileges",
    "zero trust",
    "zero-day",
    "zero-knowledge",
    "ztna"
]

# Cutoff for "last 12 months" relative to today.
def _twelve_months_ago(now):
    y, m = now.year, now.month - 12
    while m <= 0:
        y -= 1
        m += 12
    return (y, m)


def _date_in(datestring, lo, end):
    """Return True if lo <= date < end (tuple cutoffs)."""
    if not datestring:
        return False
    try:
        y, m = int(datestring[:4]), int(datestring[5:7])
        return (y, m) >= lo and (y, m) < end
    except (ValueError, AttributeError):
        return False


def main():
    with open(os.path.join(BASE, "papers.yaml"), encoding="utf-8") as f:
        data = yaml.safe_load(f)
    entries = data.get("papers", [])
    print(f"Parsed {len(entries)} papers")

    cat_counter = Counter()
    subcat_counter = Counter()
    cell_counter = Counter()
    year_counter = Counter()
    pub_dates = []

    for e in entries:
        cat = e.get("category", "unknown")
        sub = e.get("subcategory", "unknown")
        cat_counter[cat] += 1
        subcat_counter[sub] += 1
        cell = f"{cat}/{sub}"
        cell_counter[cell] += 1
        d = e.get("date", "")
        if d and len(d) >= 7:
            year_counter[d[:4]] += 1
            pub_dates.append((d[:7], cat, sub))
        else:
            year_counter["unknown"] += 1

    total = len(entries)
    total_cells = len(CATEGORY_ORDER) * len(SUBCATEGORY_ORDER)
    filled_cells = len(cell_counter)
    saturation = round(filled_cells / total_cells * 100, 1)

    # ---- Enhanced analysis -------------------------------------------------
    now = datetime.now()
    cur_lo = _twelve_months_ago(now)  # start of current 12-month window
    # previous 12-month window is [prev_lo, cur_lo)
    py, pm = cur_lo[0], cur_lo[1] - 12
    while pm <= 0:
        py -= 1
        pm += 12
    prev_lo = (py, pm)

    def is_recent(p):
        return _date_in(p.get("date", ""), cur_lo, (9999, 1))

    def is_prior(p):
        return _date_in(p.get("date", ""), prev_lo, cur_lo)

    # category momentum
    cat_traj = {c: Counter() for c in CATEGORY_ORDER}
    cat_recent = Counter()
    cat_total = Counter()
    for e in entries:
        c = e.get("category", "unknown")
        if c not in cat_traj:
            continue
        d = e.get("date", "")
        y = d[:4] if d and len(d) >= 4 else "unknown"
        cat_traj[c][y] += 1
        cat_total[c] += 1
        if is_recent(e):
            cat_recent[c] += 1

    momentum = []
    for c in CATEGORY_ORDER:
        t = cat_total[c]
        r = cat_recent[c]
        prior = sum(1 for e in entries if e.get("category") == c and is_prior(e))
        growth_pct = round((r - prior) / prior * 100, 1) if prior > 0 else None
        recent_share = round(r / t, 3) if t else 0
        velocity = round(r / 12.0, 1)  # papers per month in current window
        momentum.append({
            "id": c,
            "name": CATEGORY_DISPLAY[c],
            "total": t,
            "recent": r,
            "prior": prior,
            "growth_pct": growth_pct,
            "recent_share": recent_share,
            "papers_per_month": velocity,
            "score": round(recent_share * 100 + (growth_pct or 0), 1),
        })
    momentum.sort(key=lambda m: -m["score"])

    # category trajectories (per year)
    trajectory = {
        c: {y: cat_traj[c][y] for y in sorted(y for y in cat_traj[c] if y != "unknown")}
        for c in CATEGORY_ORDER
    }

    # --- keyword bursts (12-month recent vs corpus share) ---
    def text(p):
        return f"{p.get('title','')} {p.get('abstract','')}".lower()

    kw_total = Counter()
    kw_recent = Counter()
    for e in entries:
        t = text(e)
        for kw in BURST_KEYWORDS:
            if kw in t:
                kw_total[kw] += 1
                if is_recent(e):
                    kw_recent[kw] += 1
    recent_n = sum(1 for e in entries if is_recent(e))
    bursts = []
    for kw in BURST_KEYWORDS:
        r = kw_recent[kw]
        if r == 0:
            continue
        corpus_share = kw_total[kw] / total if total else 0
        recent_share = r / recent_n if recent_n else 0
        burst = round(recent_share / corpus_share, 2) if corpus_share > 0 else 99
        bursts.append({
            "keyword": kw, "recent": r, "total": kw_total[kw],
            "burst_score": burst, "recent_share": round(recent_share, 4),
        })
    bursts.sort(key=lambda b: (-b["burst_score"], -b["recent"]))

    # --- venue & source analytics ---
    venue_counter = Counter()
    for e in entries:
        v = _url_venue(e.get("venue", ""))
        if v:
            venue_counter[v] += 1
    top_venues = [
        {"name": v, "papers": n}
        for v, n in venue_counter.most_common(15)
    ]
    arxiv_n = sum(1 for e in entries if "arxiv" in e.get("url", ""))
    doi_n = sum(1 for e in entries if "doi.org" in e.get("url", "") or e.get("url", "").startswith("10."))
    other_n = total - arxiv_n - doi_n
    source_breakdown = {"arxiv": arxiv_n, "doi": doi_n, "other": other_n}

    # --- research gaps ---
    thin = sorted(cell_counter.items(), key=lambda kv: kv[1])[:10]
    # white space: thin but fast-growing (recent-ish share among low-total cells)
    cell_recent = Counter()
    for e in entries:
        cell = f"{e.get('category','')}/{e.get('subcategory','')}"
        if is_recent(e):
            cell_recent[cell] += 1
    whitespace = []
    for cell, ct in cell_counter.items():
        rc = cell_recent[cell]
        if ct <= 25 and rc >= 3:      # low total but clear near-term signal
            whitespace.append({
                "cell": cell, "total": ct, "recent": rc,
                "recent_share": round(rc / ct, 2),
            })
    whitespace.sort(key=lambda w: (-w["recent_share"], -w["recent"]))

    # --- top authors ---
    author_counter = Counter()
    for e in entries:
        for a in e.get("authors", []) or []:
            if a:
                author_counter[a] += 1
    top_authors = [
        {"name": a, "papers": n}
        for a, n in author_counter.most_common(15)
    ]

    # ---- statistics.json ---------------------------------------------------
    stats = {
        "metadata": {
            "total_papers": total,
            "generated_date": max((e.get("date", "") for e in entries if e.get("date")), default=""),
            "taxonomy": {
                "categories": len(CATEGORY_ORDER),
                "subcategories": len(SUBCATEGORY_ORDER),
                "total_cells": total_cells,
                "filled_cells": filled_cells,
                "saturation": saturation,
                "empty_cells": total_cells - filled_cells,
            },
            "analysis_window": {"last_12m_start": f"{cur_lo[0]:04d}-{cur_lo[1]:02d}"},
        },
        "by_category": {c: cat_counter.get(c, 0) for c in CATEGORY_ORDER},
        "by_subcategory": {s: subcat_counter.get(s, 0) for s in SUBCATEGORY_ORDER},
        "by_year": {y: year_counter[y] for y in sorted(year_counter, key=lambda x: (x == "unknown", x))},
        "by_cell": {cell: cell_counter[cell] for cell in sorted(cell_counter, key=lambda c: -cell_counter[c])},
        "emerging_themes_12m": [{"keyword": b["keyword"], "papers": b["recent"]} for b in bursts[:10]],
        "momentum": momentum,
        "category_trajectory": trajectory,
        "keyword_bursts": bursts[:15],
        "source_breakdown": source_breakdown,
        "venues": top_venues,
        "gaps": {
            "thinnest_cells": [{"cell": c, "papers": n} for c, n in thin],
            "white_space": whitespace[:10],
        },
        "top_authors": top_authors,
    }

    with open(os.path.join(BASE, "statistics.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Wrote statistics.json ({total} papers, {saturation}% saturation)")

    # ---- papers.json export (newest first) ---------------------------------
    export = []
    for e in entries:
        export.append({
            "title": e.get("title", ""),
            "date": e.get("date", ""),
            "url": e.get("url", ""),
            "category": e.get("category", ""),
            "subcategory": e.get("subcategory", ""),
            "authors": e.get("authors", []),
            "abstract": e.get("abstract", ""),
            "tags": e.get("tags", []),
            "venue": e.get("venue", ""),
        })
    export.sort(key=lambda p: p.get("date", ""), reverse=True)
    with open(os.path.join(BASE, "papers.json"), "w", encoding="utf-8") as f:
        json.dump(export, f, indent=1)
    print(f"Wrote papers.json ({len(export)} papers)")

    # ---- D3 visualization data ----------------------------------------------
    cir = defaultdict(int)
    for date_s, cat, sub in pub_dates:
        cir[(cat, sub)] += 1
    viz = {
        "categories": [
            {
                "id": c,
                "name": CATEGORY_DISPLAY[c],
                "color": CAT_COLORS[i % len(CAT_COLORS)],
                "count": cat_counter.get(c, 0),
                "subcategories": [
                    {"id": s, "name": SUBCATEGORY_DISPLAY[s], "count": cell_counter.get(f"{c}/{s}", 0)}
                    for s in SUBCATEGORY_ORDER
                ],
                "trajectory": trajectory.get(c, {}),
                "momentum": next((m for m in momentum if m["id"] == c), None),
            }
            for i, c in enumerate(CATEGORY_ORDER)
        ],
        "subcategories": [
            {"id": s, "name": SUBCATEGORY_DISPLAY[s], "count": subcat_counter.get(s, 0)}
            for s in SUBCATEGORY_ORDER
        ],
        "timeline": sorted(pub_dates),
        "venues": top_venues,
        "source_breakdown": source_breakdown,
        "keyword_bursts": bursts[:15],
    }
    os.makedirs(os.path.join(BASE, "assets"), exist_ok=True)
    with open(os.path.join(BASE, "assets", "cyber_security_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(viz, f, indent=1)
    print("Wrote assets/cyber_security_analysis.json")


def _url_venue(name):
    """Normalise a venue string for grouping."""
    if not name:
        return ""
    if isinstance(name, list):
        name = ", ".join(str(x) for x in name)
    s = re.sub(r" \(Cornell University\)| CERN European Organization for Nuclear", "", name.strip())
    return s


if __name__ == "__main__":
    main()