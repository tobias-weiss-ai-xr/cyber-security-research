#!/usr/bin/env python3
"""Fetch full abstracts for all final-shortlist papers.

Sources: arXiv API (arxiv.org), CrossRef (api.crossref.org), Zenodo
(zenodo.org). Caches results to docs/research/extraction/abstracts.json
so re-runs only fetch missing entries.

Usage:
    python3 tools/fetch_full_abstracts.py [--sleep 2] [--force]
"""

import argparse
import json
import os
import re
import time
import urllib.request
import urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(BASE, "docs", "research", "extraction", "abstracts.json")


def fetch_arxiv(aid):
    api = f"http://export.arxiv.org/api/query?id_list={aid}"
    xml = urllib.request.urlopen(api, timeout=25).read().decode()
    m = re.search(r"<summary>(.*?)</summary>", xml, re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()


def fetch_crossref(doi):
    api = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    j = json.load(urllib.request.urlopen(api, timeout=25))
    ab = j["message"].get("abstract", "")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", ab)).strip()


def fetch_zenodo(doi):
    api = f"https://zenodo.org/api/records/{urllib.parse.quote(doi, safe='')}"
    j = json.load(urllib.request.urlopen(api, timeout=25))
    rec = j if isinstance(j, dict) and "metadata" in j else j.get("hits", {}).get("hits", [{}])[0]
    return re.sub(r"\s+", " ", rec.get("metadata", {}).get("description", "")).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    shorts = json.load(open(os.path.join(
        BASE, "docs", "research", "extraction", "final_shortlists.json"),
        encoding="utf-8"))
    cache = {}
    if os.path.exists(CACHE) and not args.force:
        cache = json.load(open(CACHE, encoding="utf-8"))

    todo = []
    for rq, items in shorts["final"].items():
        for e in items:
            key = f"{rq}|{e['title']}"
            if key not in cache:
                todo.append((key, e))
    print(f"{len(todo)} abstracts to fetch (cache has {len(cache)})")

    for key, e in todo:
        url = e.get("url", "")
        ab = ""
        try:
            if "arxiv.org/abs/" in url:
                aid = url.split("/abs/")[-1].split("v")[0]
                ab = fetch_arxiv(aid)
            elif url.startswith("https://doi.org/"):
                doi = url.replace("https://doi.org/", "")
                if doi.startswith("10.5281/"):
                    ab = fetch_zenodo(doi)
                else:
                    ab = fetch_crossref(doi)
        except Exception as ex:
            ab = f"[fetch error: {type(ex).__name__}]"
        cache[key] = {"url": url, "abstract": ab[:3000]}
        time.sleep(args.sleep)
        if len(cache) % 20 == 0:
            json.dump(cache, open(CACHE, "w", encoding="utf-8"), indent=1,
                      ensure_ascii=False)
            print(f"  ...{len(cache)} cached")

    json.dump(cache, open(CACHE, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    ok = sum(1 for v in cache.values()
             if v["abstract"] and not v["abstract"].startswith("[fetch error"))
    print(f"Done: {len(cache)} cached, {ok} with usable abstracts")


if __name__ == "__main__":
    main()
