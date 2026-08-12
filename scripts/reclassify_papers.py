#!/usr/bin/env python3
"""Re-run subcategory classification over the whole corpus.

Use after tuning SUBCATEGORY_RULES in scripts/fetch/fetch_new_papers.py to
redistribute papers across the 8 research aspects without refetching.

Usage:
    python3 scripts/reclassify_papers.py
    python3 scripts/reclassify_papers.py --dry-run
"""

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch"))
from fetch_new_papers import classify_subcategory  # noqa: E402

BASE = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description="Reclassify corpus subcategories")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    yaml_path = BASE / "papers.yaml"
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    papers = data.get("papers", [])

    changed = 0
    before = Counter()
    after = Counter()
    for p in papers:
        sub = p.get("subcategory", "")
        before[sub] += 1
        new_sub = classify_subcategory(p.get("title", ""), p.get("abstract", ""))
        after[new_sub] += 1
        if new_sub != sub:
            changed += 1
            p["subcategory"] = new_sub

    print(f"Reclassified {len(papers)} papers, {changed} changed")
    print("Before:", dict(before))
    print("After: ", dict(after))

    if args.dry_run:
        print("Dry run — not saved")
        return

    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("Saved papers.yaml")


if __name__ == "__main__":
    main()
