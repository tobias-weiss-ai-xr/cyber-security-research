#!/usr/bin/env python3
"""fetch_kev.py — track CISA's Known Exploited Vulnerabilities (KEV) catalog.

The KEV catalog is CISA's authoritative, living list of vulnerabilities that
are *known to be actively exploited in the wild* — i.e. the latest CVEs that
actually matter operationally. For a security corpus this is the single most
relevant "latest CVEs" feed: every entry is a real CVE with a vendor, product,
required remediation action, due date and (often) ransomware involvement.

This script mirrors the fetch_news.py / fetch_openalex.py pattern:

  * pulls the public KEV JSON feed (no API key required),
  * normalizes each CVE into a rich `kev.yaml` catalog (full metadata
    preserved: CVE id, vendor, product, due date, CWEs, ransomware flag, …),
  * maps every CVE onto the same 20-category taxonomy used by the corpus,
  * optionally folds *newly added* CVEs into `news.yaml` so they surface in
    the rolling operational news tracker (deduplicated by CVE/NVD url).

CISA HTML pages are 403-blocked from some egress IPs; the JSON feed used here
is generally reachable. Use --via-host HOST to pull through an allowed SSH host
if needed (same workaround as fetch_news.py for CISA).

Usage:
    python3 scripts/fetch/fetch_kev.py                  # build/update kev.yaml
    python3 scripts/fetch/fetch_kev.py --merge-news     # also push recent CVEs to news.yaml
    python3 scripts/fetch/fetch_kev.py --check          # validate kev.yaml only
    python3 scripts/fetch/fetch_kev.py --via-host weiss@192.168.42.11
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

import requests
import yaml

BASE = Path(__file__).resolve().parent.parent.parent
KEV_PATH = BASE / "kev.yaml"
NEWS_PATH = BASE / "news.yaml"
KEV_JSON_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}

# CISA KEV entries are all actively-exploited vulnerabilities. Default taxonomy
# bucket is vulnerability-management; specific product families can override it.
DEFAULT_CATEGORY = "vulnerability-management"
CATEGORY_RULES = [
    (["ransomware", "lockbit", "cl0p", "data extortion"], "malware-analysis"),
    (["iot", "ot ", "scada", "ics", "industrial", "firmware", "embedded"], "iot-security"),
    (["cloud", "kubernetes", "container", "aws", "azure", "gcp", "saas"], "cloud-security"),
    (["identity", "authentication", "mfa", "credential", "password", "fido", "access"], "identity-access"),
    (["supply chain", "sbom", "dependency", "provenance"], "supply-chain-security"),
    (["zerotrust", "zero trust", "ztna", "microsegmentation"], "zero-trust"),
    (["post-quantum", "cryptograph", "encryption", "tls", "certificate"], "cryptography"),
    (["web application", "owasp", "sdlc", "devsecops"], "application-security"),
    (["phishing", "social engineering", "vishing", "smishing"], "human-factor"),
    (["intrusion detection", "firewall", "network"], "network-security"),
    (["privacy", "gdpr", "personal data"], "privacy"),
    (["machine learning", "llm", "litellm", "prompt injection", "adversarial",
      "genai", "generative ai", " \bai\b"], "ai-security"),
]


def classify(title: str) -> str:
    t = (title or "").lower()
    for keywords, cat in CATEGORY_RULES:
        if any(re.search(k, t) for k in keywords):
            return cat
    return DEFAULT_CATEGORY


def fetch_kev_raw(via_host: str | None = None) -> dict | None:
    """Download the raw KEV catalog (dict with 'vulnerabilities' list)."""
    if via_host:
        out = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=8", via_host,
             f"curl -s --max-time 30 -A 'Mozilla/5.0' {KEV_JSON_URL!r}"],
            capture_output=True, text=True, timeout=60).stdout
        if not out.strip():
            return None
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            return None
    try:
        r = requests.get(KEV_JSON_URL, headers=UA, timeout=30)
        if r.status_code == 403 and via_host is None:
            # Some egress IPs are blocked; surface the hint.
            print("  kev: HTTP 403 (egress blocked) — retry with --via-host HOST", flush=True)
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  kev: fetch error: {e}", flush=True)
        return None


def best_url(vuln: dict) -> str:
    """Pick the best deep-link for a KEV entry (prefer NVD per-CVE page)."""
    cve = vuln.get("cveID", "")
    notes = vuln.get("notes", "") or ""
    urls = [u.rstrip(";").strip() for u in re.findall(r"https?://\S+", notes)]
    for u in urls:
        if "nvd.nist.gov" in u:
            return u
    for u in urls:
        if cve.lower() in u.lower():
            return u
    if urls:
        return urls[0]
    return "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"


def raw_to_catalog_entries(raw: dict) -> list[dict]:
    """Normalize the raw KEV JSON into rich, taxonomy-mapped catalog entries."""
    out = []
    for v in raw.get("vulnerabilities", []):
        cve = v.get("cveID", "")
        if not cve:
            continue
        title = v.get("vulnerabilityName") or cve
        entry = {
            "cveID": cve,
            "vendor": v.get("vendorProject", ""),
            "product": v.get("product", ""),
            "title": title,
            "dateAdded": v.get("dateAdded", ""),
            "dueDate": v.get("dueDate", ""),
            "ransomware": v.get("knownRansomwareCampaignUse", "Unknown"),
            "cwes": v.get("cwes", []) or [],
            "category": classify(f"{title} {v.get('product', '')}"),
            "url": best_url(v),
            "shortDescription": (v.get("shortDescription", "") or "").strip(),
            "requiredAction": (v.get("requiredAction", "") or "").strip(),
            "notes": (v.get("notes", "") or "").strip(),
        }
        # Keep newest dateAdded when a CVE appears more than once.
        out.append(entry)
    return out


def raw_to_news_items(raw: dict, cutoff: dt.date) -> list[dict]:
    """Build news-tracker-shaped items for KEV entries added on/after cutoff."""
    items = []
    for v in raw.get("vulnerabilities", []):
        cve = v.get("cveID", "")
        date_added = v.get("dateAdded", "")
        if not cve or not date_added:
            continue
        try:
            d = dt.datetime.strptime(date_added, "%Y-%m-%d").date()
        except Exception:
            d = dt.date.today()
        if d < cutoff:
            continue
        items.append({
            "title": v.get("vulnerabilityName") or cve,
            "url": best_url(v),
            "date": date_added,
            "source": "kev",
            "category": classify(f"{v.get('vulnerabilityName','')} {v.get('product','')}"),
            "summary": (v.get("shortDescription", "") or "").strip(),
            "cve": cve,
        })
    return items


# ── kev.yaml persistence ────────────────────────────────────────────────

def load_existing_catalog() -> dict[str, dict]:
    if not KEV_PATH.exists():
        return {}
    data = yaml.safe_load(KEV_PATH.read_text()) or {}
    return {e.get("cveID", ""): e for e in data.get("kev", []) if e.get("cveID")}


def write_catalog(entries: list[dict]) -> int:
    existing = load_existing_catalog()
    added = 0
    for e in entries:
        cve = e["cveID"]
        if cve in existing:
            # Refresh in place (KEV fields like dueDate/ransomware can change).
            existing[cve].update(e)
        else:
            existing[cve] = e
            added += 1
    ordered = sorted(existing.values(), key=lambda e: e.get("dateAdded", ""), reverse=True)
    KEV_PATH.write_text(
        yaml.safe_dump({"kev": ordered}, allow_unicode=True, sort_keys=False, width=1000)
    )
    return added


# ── news.yaml merge (used directly and by fetch_news.py) ─────────────────

def merge_into_news(news_path: Path, items: list[dict]) -> int:
    """Append new KEV items into news.yaml (dedup by url/cve). Returns #added.

    Already-merged KEV CVEs have their taxonomy category refreshed in place
    (KEV fields such as due date / ransomware flag can change over time).
    """
    if not news_path.exists():
        news = []
    else:
        news = list((yaml.safe_load(news_path.read_text()) or {}).get("news", []))
    by_url = {e.get("url"): e for e in news if e.get("url")}
    by_cve = {e.get("cve"): e for e in news if e.get("cve")}
    added = 0
    refreshed = 0
    for it in items:
        existing = by_url.get(it["url"]) or by_cve.get(it.get("cve"))
        if existing is not None:
            # Refresh taxonomy mapping for an already-tracked KEV CVE.
            if existing.get("category") != it["category"]:
                existing["category"] = it["category"]
                refreshed += 1
            continue
        news.append(it)
        by_url[it["url"]] = it
        added += 1
    if added or refreshed:
        news_sorted = sorted(news, key=lambda e: e.get("date", ""), reverse=True)
        news_path.write_text(
            yaml.safe_dump({"news": news_sorted}, allow_unicode=True, sort_keys=False, width=1000)
        )
    return added


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--merge-news", action="store_true",
                    help="also push KEV CVEs added in the last --merge-days into news.yaml")
    ap.add_argument("--merge-days", type=int, default=14,
                    help="window for --merge-news (default 14, matches news tracker)")
    ap.add_argument("--via-host", default=None, help="SSH host for egress-blocked fetch")
    ap.add_argument("--check", action="store_true", help="validate kev.yaml only")
    args = ap.parse_args()

    if args.check:
        data = yaml.safe_load(KEV_PATH.read_text()) if KEV_PATH.exists() else {}
        entries = data.get("kev", [])
        cves = {e.get("cveID") for e in entries}
        required = ("cveID", "title", "dateAdded", "category", "url")
        errors = [e for e in entries if not all(e.get(k) for k in required)]
        print(f"kev.yaml: {len(entries)} CVEs, {len(errors)} incomplete, "
              f"{len(entries)-len(cves)} dup cveIDs")
        sys.exit(1 if errors or len(cves) != len(entries) else 0)

    raw = fetch_kev_raw(args.via_host)
    if not raw or "vulnerabilities" not in raw:
        print("kev: no data fetched — aborting", flush=True)
        sys.exit(1)

    print(f"kev: fetched catalogVersion={raw.get('catalogVersion')} "
          f"count={raw.get('count')}", flush=True)

    catalog = raw_to_catalog_entries(raw)
    added_cat = write_catalog(catalog)
    print(f"kev.yaml: {len(catalog)} total CVEs (+{added_cat} new)", flush=True)

    if args.merge_news:
        cutoff = dt.date.today() - dt.timedelta(days=args.merge_days)
        items = raw_to_news_items(raw, cutoff)
        added_news = merge_into_news(NEWS_PATH, items)
        print(f"news.yaml: +{added_news} KEV CVEs (last {args.merge_days}d) merged", flush=True)


if __name__ == "__main__":
    main()
