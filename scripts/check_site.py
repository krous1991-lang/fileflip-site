#!/usr/bin/env python3
"""Lightweight static checks for FileFlip's standalone HTML site."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors = []

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.canonicals = []
        self.h1_count = 0
        self.inline_script = None
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            value = attrs["id"]
            if value in self.ids:
                errors.append(f"duplicate id: {value}")
            self.ids.add(value)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "link" and attrs.get("rel", "").lower() == "canonical":
            self.canonicals.append(attrs.get("href", ""))
        if tag == "h1":
            self.h1_count += 1
        if tag == "script":
            self.inline_script = [] if "src" not in attrs else None

    def handle_data(self, data):
        if self.inline_script is not None:
            self.inline_script.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.inline_script is not None:
            self.scripts.append("".join(self.inline_script))
            self.inline_script = None

pages = sorted(ROOT.glob("*.html"))
if not pages:
    errors.append("no HTML pages found")

parsed = {}
for page in pages:
    parser = PageParser()
    parser.feed(page.read_text(encoding="utf-8"))
    parser.close()
    parsed[page.name] = parser
    if parser.h1_count != 1:
        errors.append(f"{page.name}: expected exactly one h1, found {parser.h1_count}")
    if len(parser.canonicals) != 1:
        errors.append(f"{page.name}: expected exactly one canonical URL")
    for number, source in enumerate(parser.scripts, 1):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as tmp:
            tmp.write(source)
            tmp.flush()
            check = subprocess.run(["node", "--check", tmp.name], capture_output=True, text=True)
        if check.returncode:
            errors.append(f"{page.name}: inline script {number} has a syntax error: {check.stderr.strip()}")

for page in pages:
    parser = parsed[page.name]
    for href in parser.links:
        parts = urlsplit(href)
        if parts.scheme or parts.netloc or href.startswith(("data:", "javascript:")):
            continue
        path = parts.path
        if not path:
            target = page
        elif path.startswith("/"):
            clean = path.lstrip("/")
            target = ROOT / (clean or "index.html")
            if not target.exists() and not target.suffix:
                html_target = ROOT / (clean + ".html")
                if html_target.exists():
                    target = html_target
        else:
            target = (ROOT / page.parent / path).resolve()
        if not target.exists() or not target.is_file():
            errors.append(f"{page.name}: broken local link {href}")
            continue
        if parts.fragment and target.suffix == ".html":
            fragment_parser = parsed.get(target.name)
            if fragment_parser and parts.fragment not in fragment_parser.ids:
                errors.append(f"{page.name}: missing anchor {href}")

sitemap = ROOT / "sitemap.xml"
if sitemap.exists():
    try:
        tree = ET.parse(sitemap)
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for node in tree.findall(".//sm:loc", namespace):
            url = node.text or ""
            path = urlsplit(url).path
            route = path.strip("/")
            target = ROOT / (route + ".html" if route else "index.html")
            if not target.exists():
                errors.append(f"sitemap URL has no matching page: {url}")
    except ET.ParseError as exc:
        errors.append(f"sitemap.xml is invalid: {exc}")

if errors:
    print("FileFlip quality checks failed:")
    for error in errors:
        print(" - " + error)
    raise SystemExit(1)

print(f"FileFlip quality checks passed: {len(pages)} HTML pages, unique IDs, local links, sitemap routes, one H1 and inline JavaScript syntax.")
