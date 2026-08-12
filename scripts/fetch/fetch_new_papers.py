#!/usr/bin/env python3
"""Discover cyber-security research papers from the arXiv API across all 20 taxonomy categories.

Runs 160+ queries spanning cyber-security constructs, threat intelligence, malware-analysis,
workforce upskilling, org implementation, identity-access, education sectors,
program evaluation and all other categories in the taxonomy. Each query carries a category (and keyword-derived subcategory)
so new papers are auto-classified into the 20x8 taxonomy on discovery.

Usage:
    python3 scripts/fetch/fetch_new_papers.py --months 3 --dry-run
    python3 scripts/fetch/fetch_new_papers.py --months 1 --create-pr
"""

import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
import yaml

ARXIV_ID_PATTERN = re.compile(r"(\d{4}\.\d{4,5})")
ARXIV_SEARCH_API = (
    "https://export.arxiv.org/api/query?search_query={}&start={}&max_results={}"
)

# (query, category, subcategory-hint). Subcategory is refined by keyword scoring
# on title/abstract; the hint is used as a fallback when nothing matches.
QUERIES = [
    ('abs:"threat intelligence" AND abs:"analysis"', 'threat-intelligence', 'theory'),
    ('abs:"threat intelligence" AND abs:"sharing"', 'threat-intelligence', 'mechanism'),
    ('abs:"threat actor" AND abs:"profiling"', 'threat-intelligence', 'method'),
    ('abs:"cyber threat" AND abs:"intelligence" AND abs:"platform"', 'threat-intelligence', 'systems'),
    ('abs:"vulnerability" AND abs:"disclosure" AND abs:"coordinated"', 'vulnerability-management', 'mechanism'),
    ('abs:"vulnerability" AND abs:"management"', 'vulnerability-management', 'method'),
    ('abs:"CVE" AND abs:"vulnerability"', 'vulnerability-management', 'systems'),
    ('abs:"patching" AND abs:"prioritization"', 'vulnerability-management', 'method'),
    ('abs:"incident response" AND abs:"forensics"', 'incident-response', 'method'),
    ('abs:"digital forensics" AND abs:"investigation"', 'incident-response', 'method'),
    ('abs:"incident" AND abs:"handling"', 'incident-response', 'mechanism'),
    ('abs:"digital evidence" AND abs:"analysis"', 'incident-response', 'method'),
    ('abs:"malware" AND abs:"reverse engineering"', 'malware-analysis', 'method'),
    ('abs:"ransomware" AND abs:"detection"', 'malware-analysis', 'method'),
    ('abs:"malware" AND abs:"classification" AND abs:"machine learning"', 'malware-analysis', 'method'),
    ('abs:"binary" AND abs:"analysis" AND abs:"malicious"', 'malware-analysis', 'method'),
    ('abs:"intrusion detection" AND abs:"network"', 'network-security', 'method'),
    ('abs:"network" AND abs:"anomaly detection"', 'network-security', 'method'),
    ('abs:"traffic" AND abs:"analysis" AND abs:"security"', 'network-security', 'method'),
    ('abs:"intrusion detection" AND abs:"deep learning"', 'network-security', 'systems'),
    ('abs:"application security" AND abs:"vulnerabilities"', 'application-security', 'mechanism'),
    ('abs:"static analysis" AND abs:"security"', 'application-security', 'method'),
    ('abs:"secure software development"', 'application-security', 'method'),
    ('abs:"web application" AND abs:"security"', 'application-security', 'application'),
    ('abs:"cloud" AND abs:"misconfiguration"', 'cloud-security', 'mechanism'),
    ('abs:"container" AND abs:"security" AND abs:"kubernetes"', 'cloud-security', 'systems'),
    ('abs:"cloud security" AND abs:"configuration"', 'cloud-security', 'method'),
    ('abs:"serverless" AND abs:"security"', 'cloud-security', 'systems'),
    ('abs:"identity" AND abs:"access management"', 'identity-access', 'systems'),
    ('abs:"multi-factor authentication"', 'identity-access', 'method'),
    ('abs:"privileged access" AND abs:"security"', 'identity-access', 'systems'),
    ('abs:"single sign-on" AND abs:"security"', 'identity-access', 'application'),
    ('abs:"post-quantum" AND abs:"cryptography"', 'cryptography', 'mechanism'),
    ('abs:"homomorphic encryption"', 'cryptography', 'mechanism'),
    ('abs:"key management" AND abs:"security"', 'cryptography', 'systems'),
    ('abs:"cryptographic protocols" AND abs:"analysis"', 'cryptography', 'mechanism'),
    ('abs:"zero trust" AND abs:"architecture"', 'zero-trust', 'theory'),
    ('abs:"zero trust" AND abs:"network access"', 'zero-trust', 'systems'),
    ('abs:"zero trust" AND abs:"model"', 'zero-trust', 'theory'),
    ('abs:"least privilege" AND abs:"microsegmentation"', 'zero-trust', 'mechanism'),
    ('abs:"supply chain" AND abs:"software" AND abs:"security"', 'supply-chain-security', 'mechanism'),
    ('abs:"software bill of materials"', 'supply-chain-security', 'systems'),
    ('abs:"dependency" AND abs:"vulnerability" AND abs:"software"', 'supply-chain-security', 'mechanism'),
    ('abs:"third-party" AND abs:"component" AND abs:"security"', 'supply-chain-security', 'application'),
    ('abs:"security operations center"', 'security-operations', 'systems'),
    ('abs:"detection engineering" AND abs:"SIEM"', 'security-operations', 'systems'),
    ('abs:"threat hunting"', 'security-operations', 'method'),
    ('abs:"security orchestration" AND abs:"automation"', 'security-operations', 'systems'),
    ('abs:"adversarial" AND abs:"machine learning"', 'ai-security', 'mechanism'),
    ('abs:"prompt injection" AND abs:"LLM"', 'ai-security', 'mechanism'),
    ('abs:"model poisoning" AND abs:"AI"', 'ai-security', 'mechanism'),
    ('abs:"adversarial examples" AND abs:"defense"', 'ai-security', 'method'),
    ('abs:"cybersecurity" AND abs:"education" AND abs:"training"', 'security-education', 'method'),
    ('abs:"security awareness" AND abs:"program"', 'security-education', 'application'),
    ('abs:"cybersecurity" AND abs:"workforce" AND abs:"skills"', 'security-education', 'method'),
    ('abs:"security training" AND abs:"effectiveness"', 'security-education', 'evaluation'),
    ('abs:"NIST" AND abs:"cybersecurity framework"', 'security-compliance', 'application'),
    ('abs:"ISO 27001" AND abs:"implementation"', 'security-compliance', 'application'),
    ('abs:"cybersecurity" AND abs:"regulation" AND abs:"compliance"', 'security-compliance', 'theory'),
    ('abs:"cybersecurity" AND abs:"certification"', 'security-compliance', 'application'),
    ('abs:"cyber risk" AND abs:"management"', 'risk-management', 'theory'),
    ('abs:"cyber risk" AND abs:"quantification"', 'risk-management', 'method'),
    ('abs:"risk assessment" AND abs:"cybersecurity"', 'risk-management', 'method'),
    ('abs:"cyber insurance" AND abs:"risk"', 'risk-management', 'application'),
    ('abs:"GDPR" AND abs:"data protection"', 'privacy', 'theory'),
    ('abs:"privacy enhancing technologies"', 'privacy', 'mechanism'),
    ('abs:"data breach" AND abs:"notification"', 'privacy', 'application'),
    ('abs:"privacy impact assessment"', 'privacy', 'application'),
    ('abs:"IoT" AND abs:"security" AND abs:"vulnerabilities"', 'iot-security', 'mechanism'),
    ('abs:"industrial control" AND abs:"security"', 'iot-security', 'systems'),
    ('abs:"SCADA" AND abs:"security"', 'iot-security', 'systems'),
    ('abs:"firmware" AND abs:"security" AND abs:"embedded"', 'iot-security', 'method'),
    ('abs:"phishing" AND abs:"detection" AND abs:"users"', 'human-factor', 'mechanism'),
    ('abs:"social engineering" AND abs:"attacks"', 'human-factor', 'mechanism'),
    ('abs:"human factor" AND abs:"security"', 'human-factor', 'theory'),
    ('abs:"cybersecurity" AND abs:"behavior" AND abs:"employees"', 'human-factor', 'application'),
    ('abs:"cyber warfare" AND abs:"nation state"', 'cyber-warfare', 'theory'),
    ('abs:"critical infrastructure" AND abs:"cyberattack"', 'cyber-warfare', 'application'),
    ('abs:"cyber deterrence"', 'cyber-warfare', 'theory'),
    ('abs:"state-sponsored" AND abs:"cyber"', 'cyber-warfare', 'application'),
]
# Subcategory keyword rules, applied in order. First match wins.
# Each rule: (subcategory, keywords, title_only?) — title_only restricts
# matching to the paper title (for strong signals like "survey").
SUBCATEGORY_RULES = [
    ("review", ["survey", "systematic review", "state-of-the-art", "sota", "overview of"], True),
    ("review", ["a survey of", "review of", "bibliographic review"], False),
    ("theory", ["expressivity", "expressiveness", "theoretical", "complexity of", "bounds", "fundamental limits", "axiomat", "computational complexity", "approximation guarantees"], False),
    ("application", ["application to", "application of", "case study", "real-world", "in practice", "production", "clinical", "medical", "fraud detection", "drug discovery", "recommender", "supply chain", "bioinformatics", "proteomics", "genomics", "diagnosis", "osint", "cybersecurity", "deployment"], False),
    ("development", ["open-source", "library", "toolkit", "implementation of", "software package", "benchmarking tool", "api for", "python library"], False),
    ("mechanism", ["interpretab", "explainab", "understanding why", "analysis of", "inner workings", "attention analysis", "probing", "mechanism", "why graph"], False),
    ("systems", ["system", "engine", "platform", "infrastructure", "architecture", "pipeline", "distributed", "scalable", "indexing", "storage", "gpu", "parallel"], False),
    ("evaluation", ["benchmark", "empirical study", "empirical comparison", "experimental evaluation", "evaluating", "comparative analysis", "dataset"], False),
]

SUBCATEGORY_FALLBACK = "method"


def classify_subcategory(title, abstract):
    """Assign a subcategory using keyword rules against title + abstract."""
    t_lower = title.lower()
    text = f"{title} {abstract}".lower()
    for subcat, keywords, title_only in SUBCATEGORY_RULES:
        haystack = t_lower if title_only else text
        for kw in keywords:
            if kw in haystack:
                return subcat
    return SUBCATEGORY_FALLBACK


def load_existing_papers(yaml_path):
    if not yaml_path.exists():
        return {}, []
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f) or {}
    papers = data.get("papers", [])
    by_id = {}
    titles_lower = []
    for p in papers:
        url = p.get("url", "")
        match = ARXIV_ID_PATTERN.search(url)
        if match:
            by_id[match.group(1)] = p
        titles_lower.append(p.get("title", "").lower().strip())
    return by_id, titles_lower


def search_arxiv(query, months, start=0, max_results=100, max_retries=4):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff = now - timedelta(days=months * 30)
    date_start = cutoff.strftime("%Y%m%d0000")
    date_end = now.strftime("%Y%m%d") + "2359"

    full_query = f"({query}) AND submittedDate:[{date_start} TO {date_end}]"
    try:
        resp = None
        for attempt in range(max_retries):
            resp = requests.get(
                ARXIV_SEARCH_API.format(
                    requests.utils.quote(full_query), start, max_results
                ),
                timeout=30,
            )
            if resp.status_code == 429:
                wait = 8 * (attempt + 1)
                print(f"    rate-limited (429), waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            break
        if resp is None:
            return []
        if resp.status_code != 200:
            print(f"  WARNING: arXiv returned HTTP {resp.status_code}", flush=True)
            return []
        entries = []
        root = resp.text
        for match in re.finditer(r"<entry>(.*?)</entry>", root, re.DOTALL):
            entry_xml = match.group(1)
            entry = {}
            title_m = re.search(r"<title>(.*?)</title>", entry_xml, re.DOTALL)
            if title_m:
                entry["title"] = re.sub(r"\s+", " ", title_m.group(1).strip())
            id_m = re.search(r"<id>(.*?)</id>", entry_xml)
            if id_m:
                entry["url"] = id_m.group(1).strip().replace("http://", "https://")
            published_m = re.search(r"<published>(.*?)</published>", entry_xml)
            if published_m:
                entry["date"] = published_m.group(1).strip()[:7]
            summary_m = re.search(r"<summary>(.*?)</summary>", entry_xml, re.DOTALL)
            if summary_m:
                entry["abstract"] = re.sub(r"\s+", " ", summary_m.group(1).strip())
            authors_m = re.findall(r"<name>(.*?)</name>", entry_xml)
            if authors_m:
                entry["authors"] = [a.strip() for a in authors_m][:3]
            if entry.get("title") and entry.get("url"):
                entries.append(entry)
        return entries
    except Exception as e:
        print(f"  WARNING: arXiv search error: {e}", flush=True)
        return []


def format_yaml_entry(entry, category, subcategory):
    title = entry["title"].replace('"', '\\"')
    authors = ", ".join(entry.get("authors", [])[:3])
    lines = [
        f'  - title: "{title}"',
        f'    date: "{entry.get("date", "")}"',
        f'    url: "{entry.get("url", "")}"',
        f"    category: {category}",
        f"    subcategory: {subcategory}",
        f"    authors: [{authors}]",
    ]
    if entry.get("abstract"):
        abstract = entry["abstract"][:200].replace('"', '\\"')
        lines.append(f'    abstract: "{abstract}..."')
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Discover cyber-security research papers from arXiv"
    )
    parser.add_argument(
        "--months",
        type=int,
        default=3,
        help="Search papers from the last N months (default: 3)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without creating anything"
    )
    parser.add_argument(
        "--create-pr", action="store_true", help="Create a GitHub PR with new papers"
    )
    parser.add_argument(
        "--sleep", type=float, default=2.0, help="Seconds between queries"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="Max results per arXiv query (default: 100)",
    )
    parser.add_argument(
        "--from",
        dest="from_idx",
        type=int,
        default=0,
        help="Start at query index (0-based, inclusive)",
    )
    parser.add_argument(
        "--to",
        dest="to_idx",
        type=int,
        default=None,
        help="Stop at query index (0-based, inclusive)",
    )
    args = parser.parse_args()

    yaml_path = Path(__file__).resolve().parent.parent.parent / "papers.yaml"
    by_id, titles_lower = load_existing_papers(yaml_path)

    print(f"Loaded {len(by_id)} existing papers from papers.yaml", flush=True)
    print(
        f"Searching arXiv ({len(QUERIES)} queries) for papers from the last {args.months} month(s)...",
        flush=True,
    )

    all_new = []
    CHECKPOINT_EVERY = 10
    to_idx = args.to_idx if args.to_idx is not None else len(QUERIES) - 1
    for qi, qdef in enumerate(QUERIES[args.from_idx:to_idx + 1], start=args.from_idx):
        if len(qdef) == 4:
            query, category, hint, force_sub = qdef
        else:
            query, category, hint = qdef
            force_sub = None
        print(f"Query {qi + 1}/{len(QUERIES)} [{category}] {query[:70]}", flush=True)
        entries = search_arxiv(query, args.months, max_results=args.max_results)
        for entry in entries:
            arxiv_id_match = ARXIV_ID_PATTERN.search(entry.get("url", ""))
            arxiv_id = arxiv_id_match.group(1) if arxiv_id_match else None

            if arxiv_id and arxiv_id in by_id:
                continue

            title_lower = entry.get("title", "").lower().strip()
            if any(title_lower == t for t in titles_lower):
                continue

            if arxiv_id and any(e.get("url", "") == entry["url"] for e in all_new):
                continue

            entry["category"] = category
            entry["subcategory"] = force_sub or classify_subcategory(
                entry.get("title", ""), entry.get("abstract", "")
            )
            all_new.append(entry)
            by_id[arxiv_id] = entry
            titles_lower.append(title_lower)

        # Incremental checkpoint so partial runs are never lost
        if not args.dry_run and all_new and (qi + 1) % CHECKPOINT_EVERY == 0:
            append_papers(yaml_path, all_new)
            print(f"  [checkpoint] saved {len(all_new)} papers so far", flush=True)
            all_new = []
            by_id, titles_lower = load_existing_papers(yaml_path)

        time.sleep(args.sleep)

    print(
        f"\nFound {len(all_new)} new papers ({len(by_id)} already in list)", flush=True
    )

    if not all_new:
        print("No new papers to add.", flush=True)
        return

    print("\n--- New Papers (first 10) ---", flush=True)
    for entry in all_new[:10]:
        print(format_yaml_entry(entry, entry["category"], entry["subcategory"]), flush=True)
        print(flush=True)
    print(f"... and {max(0, len(all_new) - 10)} more", flush=True)

    if args.dry_run:
        print("\nDry run complete — no files modified", flush=True)
        return

    if args.create_pr:
        branch_name = f"add-new-papers-{datetime.now().strftime('%Y%m%d')}"
        print(f"\nCreating branch '{branch_name}' and PR...", flush=True)
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name], check=True, cwd=yaml_path.parent
            )
            append_papers(yaml_path, all_new)
            subprocess.run(["git", "add", "papers.yaml"], check=True, cwd=yaml_path.parent)
            subprocess.run(
                ["git", "commit", "-m", f"Add {len(all_new)} new papers from arXiv discovery"],
                check=True,
                cwd=yaml_path.parent,
            )
            subprocess.run(
                ["git", "push", "origin", branch_name], check=True, cwd=yaml_path.parent
            )
            subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", f"Add {len(all_new)} new papers from arXiv discovery",
                    "--body", "Automatically discovered papers.\n\n**Please review taxonomy assignments.**",
                ],
                check=True,
                cwd=yaml_path.parent,
            )
            print("PR created successfully!", flush=True)
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to create PR: {e}", flush=True)
            sys.exit(1)
    else:
        append_papers(yaml_path, all_new)
        print(f"\nAppended {len(all_new)} papers to papers.yaml", flush=True)
        print(
            "\nNext: run scripts/analysis/generate_analysis.py and scripts/generate_readme.py",
            flush=True,
        )


def append_papers(yaml_path, new_papers):
    """Append new papers to papers.yaml in stable format."""
    if yaml_path.exists():
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}
    papers = data.get("papers", [])
    for entry in new_papers:
        papers.append(
            {
                "title": entry.get("title", ""),
                "date": entry.get("date", ""),
                "url": entry.get("url", ""),
                "category": entry.get("category", ""),
                "subcategory": entry.get("subcategory", ""),
                "authors": entry.get("authors", []),
                "abstract": entry.get("abstract", ""),
            }
        )
    data["papers"] = papers
    with open(yaml_path, "w") as f:
        yaml.dump(
            data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )


if __name__ == "__main__":
    main()
