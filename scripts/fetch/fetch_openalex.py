#!/usr/bin/env python3
"""Discover cyber-security research papers from the OpenAlex API (fallback/primary source).

OpenAlex (api.openalex.org) has generous rate limits and rich metadata.
Search terms are derived automatically from the taxonomy-aware arXiv query
list in fetch_new_papers.py, so both sources share the same coverage and
classify into the same 20x8 taxonomy.

Usage:
    python3 scripts/fetch/fetch_openalex.py --months 36 --sleep 2
    python3 scripts/fetch/fetch_openalex.py --months 6 --dry-run
    python3 scripts/fetch/fetch_openalex.py --months 3 --create-pr
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_new_papers import (  # noqa: E402
    ARXIV_ID_PATTERN,
    QUERIES,
    classify_subcategory,
    load_existing_papers,
)

OPENALEX_API = "https://api.openalex.org/works"
MAILTO = os.environ.get("OPENALEX_MAILTO", "business@tobias-weiss.org")


def arxiv_query_to_terms(query):
    """Extract plain search terms from an arXiv query string."""
    phrases = re.findall(r'abs:"([^"]+)"', query)
    bare = re.findall(r'all:"([^"]+)"', query)
    terms = " ".join(phrases + bare)
    if not terms:
        # fall back: keep non-cat tokens
        terms = query
    return terms


def reconstruct_abstract(inverted):
    """OpenAlex stores abstracts as an inverted index -> plain text."""
    if not inverted:
        return ""
    pos = {}
    for word, positions in inverted.items():
        for p in positions:
            pos[p] = word
    return " ".join(pos[i] for i in sorted(pos))


def sanitize_date(date_str):
    """Normalize a date to YYYY-MM, clamping future dates to today."""
    if not date_str:
        return ""
    y = date_str[:4]
    m = date_str[5:7] if len(date_str) >= 7 else "01"
    if not y.isdigit() or not m.isdigit():
        return ""
    now = datetime.now(timezone.utc)
    if (int(y), int(m)) > (now.year, now.month):
        return now.strftime("%Y-%m")
    return f"{y}-{m}"


def openalex_date_filter(months):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=months * 30)
    return cutoff.strftime("%Y-%m-%d")


def search_openalex(terms, months, per_page=25, max_retries=3):
    params = {
        "search": terms,
        "filter": f"from_publication_date:{openalex_date_filter(months)}",
        "per-page": per_page,
        "mailto": MAILTO,
        "sort": "publication_date:desc",
    }
    for attempt in range(max_retries):
        try:
            resp = requests.get(OPENALEX_API, params=params, timeout=30)
            if resp.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"    rate-limited (429), waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception as e:
            print(f"  WARNING: OpenAlex search error: {e}", flush=True)
            return []
    return []


def to_entry(work, category, subcategory_hint):
    """Map an OpenAlex work to the papers.yaml entry format."""
    title = work.get("title") or ""
    if not title:
        return None

    # Prefer arXiv location, else primary location
    url = ""
    for loc in work.get("locations", []):
        src = (loc.get("source") or {}).get("id", "")
        lurl = loc.get("landing_page_url") or ""
        if "arxiv" in src or "arxiv" in lurl:
            url = lurl.replace("http://", "https://")
            break
    if not url:
        primary = work.get("primary_location") or {}
        url = (primary.get("landing_page_url") or "").replace("http://", "https://")
    if not url:
        url = work.get("doi") or ""
    if not url:
        return None

    date = sanitize_date(work.get("publication_date") or "")
    if not date:
        date = sanitize_date(str(work.get("publication_year") or ""))
    authors = [a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])][:3]

    entry = {
        "title": title,
        "date": date,
        "url": url,
        "category": category,
        "subcategory": classify_subcategory(title, reconstruct_abstract(work.get("abstract_inverted_index"))),
        "authors": authors,
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index"))[:200],
        "venue": ((work.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
    }
    return entry


def append_papers(yaml_path, new_papers):
    if yaml_path.exists():
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}
    papers = data.get("papers", [])
    for entry in new_papers:
        papers.append(entry)
    data["papers"] = papers
    with open(yaml_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(description="Discover cyber-security research papers from OpenAlex")
    parser.add_argument("--months", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--create-pr", action="store_true")
    parser.add_argument("--sleep", type=float, default=2.0)
    parser.add_argument("--per-page", type=int, default=25)
    parser.add_argument("--from", dest="from_idx", type=int, default=0, help="Start at query index (0-based, inclusive)")
    parser.add_argument("--to", dest="to_idx", type=int, default=None, help="Stop at query index (0-based, inclusive)")
    args = parser.parse_args()

    yaml_path = Path(__file__).resolve().parent.parent.parent / "papers.yaml"
    by_id, titles_lower = load_existing_papers(yaml_path)
    print(f"Loaded {len(by_id)} existing papers from papers.yaml", flush=True)

    all_new = []
    CHECKPOINT_EVERY = 10
    queries = list(enumerate(QUERIES))
    to_idx = args.to_idx if args.to_idx is not None else len(queries) - 1
    for qi, qdef in queries[args.from_idx:to_idx + 1]:
        if len(qdef) == 4:
            arxiv_query, category, hint, force_sub = qdef
        else:
            arxiv_query, category, hint = qdef
            force_sub = None
        terms = arxiv_query_to_terms(arxiv_query)
        print(f"Query {qi + 1}/{len(QUERIES)} [{category}] {terms[:70]}", flush=True)
        results = search_openalex(terms, args.months, per_page=args.per_page)
        for work in results:
            entry = to_entry(work, category, hint)
            if not entry:
                continue
            if force_sub:
                entry["subcategory"] = force_sub
            arxiv_id_m = ARXIV_ID_PATTERN.search(entry.get("url", ""))
            arxiv_id = arxiv_id_m.group(1) if arxiv_id_m else None
            key = arxiv_id or entry.get("url")
            if key and key in by_id:
                continue
            t_lower = entry["title"].lower().strip()
            if any(t_lower == t for t in titles_lower):
                continue
            if key and any(e.get("url") == entry["url"] for e in all_new):
                continue
            all_new.append(entry)
            by_id[key] = entry
            titles_lower.append(t_lower)

        if not args.dry_run and all_new and (qi + 1) % CHECKPOINT_EVERY == 0:
            append_papers(yaml_path, all_new)
            print(f"  [checkpoint] saved {len(all_new)} papers so far", flush=True)
            all_new = []
            by_id, titles_lower = load_existing_papers(yaml_path)

        time.sleep(args.sleep)

    print(f"\nFound {len(all_new)} new papers total (post-checkpoint)", flush=True)
    if not all_new and not args.dry_run:
        print("No remaining papers to append.", flush=True)
        return

    if args.dry_run:
        print(f"\nDry run — {len(all_new)} papers would be added", flush=True)
        for e in all_new[:5]:
            print(f"  - [{e['date']}] {e['title'][:70]} -> {e['category']}/{e['subcategory']}", flush=True)
        return

    if args.create_pr:
        branch = f"add-new-papers-{datetime.now().strftime('%Y%m%d')}"
        try:
            subprocess.run(["git", "checkout", "-b", branch], check=True, cwd=yaml_path.parent)
            append_papers(yaml_path, all_new)
            subprocess.run(["git", "add", "papers.yaml"], check=True, cwd=yaml_path.parent)
            subprocess.run(["git", "commit", "-m", f"Add {len(all_new)} new papers via OpenAlex discovery"], check=True, cwd=yaml_path.parent)
            subprocess.run(["git", "push", "origin", branch], check=True, cwd=yaml_path.parent)
            subprocess.run(["gh", "pr", "create", "--title", f"Add {len(all_new)} new papers via OpenAlex discovery",
                            "--body", "Automatically discovered papers. **Please review taxonomy assignments.**"],
                           check=True, cwd=yaml_path.parent)
            print("PR created successfully!", flush=True)
        except subprocess.CalledProcessError as e:
            print(f"ERROR: {e}", flush=True)
            sys.exit(1)
    else:
        append_papers(yaml_path, all_new)
        print(f"Appended {len(all_new)} papers to papers.yaml", flush=True)


if __name__ == "__main__":
    main()
