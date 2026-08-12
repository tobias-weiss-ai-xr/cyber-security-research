#!/usr/bin/env python3
"""fetch_news.py — fetch operational cyber-security news into news.yaml.

Sources: RSS where available (The Hacker News, SANS ISC, Krebs, NIST, BSI,
ENISA, NCSC) and HTML pages (CISA news + cybersecurity advisories) parsed
with stdlib only. CISA blocks some egress IPs with 403 — run with
--via-host HOST to pull the CISA pages through an SSH host whose IP is
allowed (verified: tobias-weiss.org, tobi-yoga).

Usage:
    python3 scripts/fetch/fetch_news.py                  # all sources, last 14 days
    python3 scripts/fetch/fetch_news.py --days 30
    python3 scripts/fetch/fetch_news.py --sources cisa,krebs
    python3 scripts/fetch/fetch_news.py --via-host weiss@192.168.42.11
    python3 scripts/fetch/fetch_news.py --check          # validate news.yaml only
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

import requests
import yaml

BASE = Path(__file__).resolve().parent.parent.parent
NEWS_PATH = BASE / "news.yaml"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}

# (name, kind, url, category-hint) — kind: rss | html
SOURCES = {
    "cisa":        ("html", "https://www.cisa.gov/news-events/news", "/news-events/news/", None),
    "cisa-advisories": ("html", "https://www.cisa.gov/news-events/cybersecurity-advisories",
                        "/news-events/cybersecurity-advisories/", None),
    "nist":        ("rss", "https://www.nist.gov/news-events/news", None, None),
    "enisa":       ("html", "https://www.enisa.europa.eu/news", "/news/", None),
    "bsi":         ("html", "https://www.bsi.bund.de/DE/Service-Navi/Presse/Pressemitteilungen",
                    "/Pressemitteilungen/", None),
    "ncsc":        ("html", "https://www.ncsc.gov.uk/news", "/news/", None),
    "thn":         ("rss", "https://feeds.feedburner.com/TheHackersNews", None, None),
    "krebs":       ("rss", "https://krebsonsecurity.com/feed/", None, None),
    "sans":        ("rss", "https://isc.sans.edu/rssfeed.xml", None, None),
}

# keyword -> taxonomy category (first match wins, checked in order of specificity)
CATEGORY_RULES = [
    (["ransomware", "lockbit", "cl0p", "data extortion"], "malware-analysis"),
    (["malware", "botnet", "trojan", "backdoor", "infostealer", "loader"], "malware-analysis"),
    (["zero trust", "ztna", "microsegmentation"], "zero-trust"),
    (["supply chain", "sbom", "dependency", "typosquatting", "provenance"], "supply-chain-security"),
    (["phishing", "social engineering", "misdelivery", "vishing", "smishing"], "human-factor"),
    (["incident response", "containment", "forensics", "dfir"], "incident-response"),
    (["vulnerability", "cve", "zero-day", "patch", "exploit", "disclosure"], "vulnerability-management"),
    (["ai", "machine learning", "llm", "adversarial", "prompt injection", "jailbreak", "model"], "ai-security"),
    (["cloud", "kubernetes", "container", "aws", "azure", "gcp", "misconfiguration"], "cloud-security"),
    (["identity", "authentication", "mfa", "credential", "password", "fido", "access"], "identity-access"),
    (["iot", "ot ", "scada", "ics", "industrial", "firmware", "embedded"], "iot-security"),
    (["cryptography", "encryption", "quantum", "tls", "certificate", "key"], "cryptography"),
    (["intrusion detection", "network", "firewall", "traffic", "dns"], "network-security"),
    (["threat intelligence", "ttps", "attribution", "nation state", "apt", "spyware"], "threat-intelligence"),
    (["soc", "siem", "detection engineering", "threat hunting", "alert"], "security-operations"),
    (["gdpr", "privacy", "data breach", "consent", "personal data"], "privacy"),
    (["regulation", "compliance", "nist", "iso", "audit", "certification", "nis2"], "security-compliance"),
    (["risk", "insurance", "quantification"], "risk-management"),
    (["training", "awareness", "education", "workforce", "skills"], "security-education"),
    (["warfare", "critical infrastructure", "deterrence", "state-sponsored"], "cyber-warfare"),
    (["application security", "web", "owasp", "devsecops", "sdlc"], "application-security"),
]
DEFAULT_CATEGORY = "vulnerability-management"


class LinkParser(HTMLParser):
    """Collect (href, title) for anchors matching a slug prefix (e.g. /news-events/news/)."""

    def __init__(self, slug):
        super().__init__(convert_charrefs=True)
        self.slug = slug
        self._in_a = False
        self._href = None
        self._text = []
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if self.slug in href:
                self._in_a = True
                self._href = href
                self._text = []

    def handle_data(self, data):
        if self._in_a:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._in_a:
            title = " ".join("".join(self._text).split())
            if title and len(title) > 15:
                self.items.append((self._href, title))
            self._in_a = False


def fetch_url(url: str, via_host: str | None = None) -> str | None:
    if via_host:
        # curl on the remote host (verified egress: tobias-weiss.org, tobi-yoga)
        out = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=8", via_host,
             f"curl -s --max-time 25 -A 'Mozilla/5.0' {url!r}"],
            capture_output=True, text=True, timeout=60).stdout
        return out if out.strip() else None
    try:
        r = requests.get(url, headers=UA, timeout=25)
        if r.status_code != 200:
            return None
        return r.text
    except Exception:
        return None


def parse_rss(text: str, source: str, cutoff: dt.date, limit: int = 60) -> list[dict]:
    items = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return items
    for item in root.iter():
        if item.tag.endswith("item"):
            title = pub = link = ""
            for child in item:
                tag = child.tag.split("}")[-1]
                if tag == "title":
                    title = (child.text or "").strip()
                elif tag == "pubDate" or tag == "pubdate":
                    pub = (child.text or "").strip()
                elif tag == "link":
                    link = (child.text or "").strip()
            if not title:
                continue
            try:
                d = dt.datetime.strptime(pub[:25].strip(), "%a, %d %b %Y %H:%M:%S %z").date()
            except Exception:
                d = dt.date.today()
            if d < cutoff:
                continue
            items.append({"title": html.unescape(title), "url": link, "date": d.isoformat(),
                          "source": source})
            if len(items) >= limit:
                break
    return items


def parse_html(text: str, slug: str, source: str, cutoff: dt.date, limit: int = 60) -> list[dict]:
    p = LinkParser(slug)
    try:
        p.feed(text)
    except Exception:
        return []
    items = []
    for href, title in p.items:
        url = href if href.startswith("http") else "https://www.cisa.gov" + href
        items.append({"title": title, "url": url, "date": dt.date.today().isoformat(), "source": source})
        if len(items) >= limit:
            break
    return items


def classify(title: str) -> str:
    t = title.lower()
    for keywords, cat in CATEGORY_RULES:
        if any(k in t for k in keywords):
            return cat
    return DEFAULT_CATEGORY


def load_existing() -> dict[str, dict]:
    if not NEWS_PATH.exists():
        return {}
    data = yaml.safe_load(NEWS_PATH.read_text()) or {}
    return {e.get("url", ""): e for e in data.get("news", []) if e.get("url")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=14, help="only items newer than N days (RSS; HTML pages are today)")
    ap.add_argument("--sources", default=None, help="comma-separated subset of source names")
    ap.add_argument("--via-host", default=None, help="SSH host for CISA (403-blocked egress workaround)")
    ap.add_argument("--check", action="store_true", help="validate news.yaml only")
    args = ap.parse_args()

    if args.check:
        data = yaml.safe_load(NEWS_PATH.read_text()) if NEWS_PATH.exists() else {}
        entries = data.get("news", [])
        errors = [e for e in entries if not all(e.get(k) for k in ("title", "url", "date", "source", "category"))]
        urls = {e.get("url") for e in entries}
        print(f"news.yaml: {len(entries)} items, {len(errors)} incomplete, {len(entries)-len(urls)} dup urls")
        sys.exit(1 if errors or len(urls) != len(entries) else 0)

    existing = load_existing()
    wanted = {s.strip() for s in (args.sources or "").split(",") if s.strip()} if args.sources else None
    cutoff = dt.date.today() - dt.timedelta(days=args.days)
    new_entries = []
    per_source = {}

    for name, (kind, url, slug, _hint) in SOURCES.items():
        if wanted and name not in wanted:
            continue
        via = args.via_host if name.startswith("cisa") else None
        text = fetch_url(url, via)
        if not text:
            print(f"  {name}: fetch failed (blocked?) — {'use --via-host' if name.startswith('cisa') else 'skip'}")
            continue
        items = parse_rss(text, name, cutoff) if kind == "rss" else parse_html(text, slug, name, cutoff)
        fresh = 0
        for it in items:
            if it["url"] in existing:
                continue
            it["category"] = classify(it["title"])
            it["summary"] = ""
            existing[it["url"]] = it
            new_entries.append(it)
            fresh += 1
        per_source[name] = len(items)
        print(f"  {name}: {len(items)} items ({fresh} new)")

    if new_entries:
        entries = sorted(existing.values(), key=lambda e: e.get("date", ""), reverse=True)
        NEWS_PATH.write_text(yaml.safe_dump({"news": entries}, allow_unicode=True, sort_keys=False, width=1000))
    print(f"news.yaml: {len(existing)} total items (+{len(new_entries)} new)")


if __name__ == "__main__":
    main()
