#!/usr/bin/env python3
"""Validate papers.yaml structure, taxonomy values and URL/date formats.

Usage:
    python3 scripts/validate_papers.py
    python3 scripts/validate_papers.py --strict
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

TODAY = datetime.now()

BASE = Path(__file__).resolve().parent.parent

CATEGORIES = {
    "threat-intelligence",
    "vulnerability-management",
    "incident-response",
    "malware-analysis",
    "network-security",
    "application-security",
    "cloud-security",
    "identity-access",
    "cryptography",
    "zero-trust",
    "supply-chain-security",
    "security-operations",
    "ai-security",
    "security-education",
    "security-compliance",
    "risk-management",
    "privacy",
    "iot-security",
    "human-factor",
    "cyber-warfare",
}

SUBCATEGORIES = {
    "theory", "mechanism", "method", "application",
    "development", "systems", "evaluation", "review",
}

ARXIV_RE = re.compile(r"https?://arxiv\.org/abs/(\d{4}\.\d{4,5})")
DATE_RE = re.compile(r"^\d{4}-\d{2}$")


def main():
    parser = argparse.ArgumentParser(description="Validate papers.yaml")
    parser.add_argument("--strict", action="store_true", help="Fail on any warning")
    args = parser.parse_args()

    yaml_path = BASE / "papers.yaml"
    if not yaml_path.exists():
        print("ERROR: papers.yaml not found")
        sys.exit(1)

    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    papers = data.get("papers", []) if data else []

    errors = []
    warnings = []
    seen_ids = set()
    seen_titles = set()

    for i, p in enumerate(papers):
        idx = i + 1
        title = p.get("title", "")
        url = p.get("url", "")

        if not title:
            errors.append(f"[{idx}] missing title")
        t_lower = title.lower().strip()
        if t_lower in seen_titles:
            errors.append(f"[{idx}] duplicate title: {title[:60]}")
        seen_titles.add(t_lower)

        if not url:
            errors.append(f"[{idx}] missing url: {title[:60]}")
        m = ARXIV_RE.search(url)
        if m:
            arxiv_id = m.group(1)
            if arxiv_id in seen_ids:
                errors.append(f"[{idx}] duplicate arXiv id: {arxiv_id}")
            seen_ids.add(arxiv_id)
        elif url:
            warnings.append(f"[{idx}] non-arXiv url: {url[:80]}")

        date = p.get("date", "")
        if not date:
            warnings.append(f"[{idx}] missing date: {title[:60]}")
        elif not DATE_RE.match(date):
            warnings.append(f"[{idx}] invalid date format '{date}': {title[:60]}")
        else:
            # QUALITY GATE: no future dates
            _y, _m = int(date[:4]), int(date[5:7])
            if (_y, _m) > (TODAY.year, TODAY.month):
                errors.append(
                    f"[{idx}] future date '{date}': papers cannot be dated after today ({TODAY:%Y-%m})"
                )

        cat = p.get("category", "")
        if not cat:
            warnings.append(f"[{idx}] missing category: {title[:60]}")
        elif cat not in CATEGORIES:
            errors.append(f"[{idx}] invalid category '{cat}': {title[:60]}")

        sub = p.get("subcategory", "")
        if not sub:
            warnings.append(f"[{idx}] missing subcategory: {title[:60]}")
        elif sub not in SUBCATEGORIES:
            errors.append(f"[{idx}] invalid subcategory '{sub}': {title[:60]}")

    print(f"Validated {len(papers)} papers")
    print(f"Errors: {len(errors)} | Warnings: {len(warnings)}")

    for e in errors:
        print(f"  ERROR: {e}")
    for w in warnings:
        print(f"  WARN:  {w}")

    if errors or (args.strict and warnings):
        print("\nValidation FAILED")
        sys.exit(1)
    print("\nValidation PASSED")


if __name__ == "__main__":
    main()
