#!/usr/bin/env python3
"""Static checks for the site: run from the repo root with `python3 scripts/check_site.py`.

- every JSON-LD block parses as JSON and never carries aggregateRating
- each landing page has the Smart App Banner, App Store link, SoftwareApplication
  and FAQPage JSON-LD (4-6 questions, matching the visible FAQ)
- every internal href/src resolves to a real file
- every sitemap URL resolves to a real file, and every page is in the sitemap
- robots.txt names OAI-SearchBot and ChatGPT-User and points at the sitemap
- no page makes a claim the apps can't back (ratings, "best", iCloud sync, ...)
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://dangquan1402.github.io"
SKIP_DIRS = {".git", ".github", ".claude", "scripts", "node_modules"}
# The root page is a redirect owned by the captain, not part of the app pages.
NOT_IN_SITEMAP = {"index.html"}
# Paths on this host that are served by other repos' project pages.
OTHER_REPOS = ("/llm-engineering-notes/",)
BANNED = [
    (re.compile(r"aggregateRating", re.IGNORECASE), "aggregateRating"),
    (re.compile(r"iCloud sync", re.IGNORECASE), "iCloud sync claim"),
    (
        re.compile(r"\bbest\b(?! quality)", re.IGNORECASE),
        '"best"',
    ),  # "best quality" describes a preset
    (re.compile(r"#1\b"), '"#1"'),
    (
        re.compile(
            r"\b(\d[\d,.]*\s*(k|m)?\+?\s*(downloads|ratings|reviews))\b", re.IGNORECASE
        ),
        "download/rating count",
    ),
    (re.compile(r"\baward", re.IGNORECASE), "award claim"),
    (re.compile(r"6760960875"), "competitor app id"),
]
LANDING = {
    "pdf-compressor/index.html": (
        "6757997785",
        "https://apps.apple.com/us/app/smart-pdf-compressor-reduce/id6757997785",
    ),
    "img2pdf/index.html": (
        "6762545311",
        "https://apps.apple.com/us/app/img2pdf-image-to-pdf-maker/id6762545311",
    ),
}


def check_landing(rel, text, blocks, errors):
    app_id, store_url = LANDING[rel]
    for needle in (
        f'<meta name="apple-itunes-app" content="app-id={app_id}">',
        '<meta name="description"',
        '<link rel="canonical"',
        '<meta property="og:title"',
        f'href="{store_url}"',
        "Quan Dang",
    ):
        if needle not in text:
            errors.append(f"{rel}: missing {needle!r}")
    types = {b.get("@type"): b for b in blocks}
    app = types.get("SoftwareApplication")
    if not app:
        errors.append(f"{rel}: no SoftwareApplication JSON-LD")
    else:
        offer = app.get("offers", {})
        if (
            app.get("operatingSystem") != "iOS"
            or not app.get("applicationCategory")
            or offer.get("price") != "0"
            or offer.get("priceCurrency") != "USD"
            or app.get("author", {}).get("name") != "Quan Dang"
            or store_url not in (app.get("installUrl"), offer.get("url"))
        ):
            errors.append(
                f"{rel}: SoftwareApplication JSON-LD is missing a required field"
            )
    faq = types.get("FAQPage")
    visible = text.count('class="faq-item"')
    if not faq:
        errors.append(f"{rel}: no FAQPage JSON-LD")
    elif (
        not 4 <= len(faq.get("mainEntity", [])) <= 6
        or len(faq["mainEntity"]) != visible
    ):
        errors.append(
            f"{rel}: FAQPage has {len(faq.get('mainEntity', []))} questions, page shows {visible}"
        )


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.jsonld = []
        self._in_jsonld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._buf = []

    def handle_data(self, data):
        if self._in_jsonld:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._buf))
            self._in_jsonld = False


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts):
            yield p


def resolve(target: str, page: Path):
    """Map a link to a file in the repo, or None if it is external."""
    u = urlparse(target)
    if u.scheme in ("mailto", "tel"):
        return None
    if (u.scheme or u.netloc) and u.netloc != urlparse(SITE).netloc:
        return None
    path = u.path
    if path.startswith(OTHER_REPOS):
        return None
    if not path:
        return None  # pure fragment
    base = ROOT if path.startswith("/") else page.parent
    f = (base / path.lstrip("/")).resolve()
    if path.endswith("/") or f.is_dir():
        f = f / "index.html"
    return f


def main() -> int:
    errors = []
    all_pages = list(pages())

    for page in all_pages:
        rel = page.relative_to(ROOT)
        text = page.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(text)

        blocks = []
        for i, block in enumerate(parser.jsonld):
            try:
                blocks.append(json.loads(block))
            except json.JSONDecodeError as e:
                errors.append(f"{rel}: JSON-LD block {i + 1} does not parse: {e}")
        if str(rel) in LANDING:
            check_landing(str(rel), text, blocks, errors)

        for link in parser.links:
            f = resolve(link, page)
            if f is not None and not f.is_file():
                errors.append(f"{rel}: broken internal link {link!r}")

        for pattern, label in BANNED:
            if pattern.search(text):
                errors.append(f"{rel}: banned claim ({label})")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    listed = set()
    for loc in locs:
        f = resolve(loc, ROOT / "index.html")
        if f is None or not f.is_file():
            errors.append(f"sitemap.xml: {loc} has no matching file")
        else:
            listed.add(f)
    for page in all_pages:
        rel = str(page.relative_to(ROOT))
        if rel not in NOT_IN_SITEMAP and page.resolve() not in listed:
            errors.append(f"sitemap.xml: missing {rel}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    for needle in (
        "User-agent: OAI-SearchBot",
        "User-agent: ChatGPT-User",
        f"Sitemap: {SITE}/sitemap.xml",
    ):
        if needle not in robots:
            errors.append(f"robots.txt: missing {needle!r}")
    if re.search(r"^Disallow:\s*/\s*$", robots, re.MULTILINE):
        errors.append("robots.txt: disallows the whole site")

    for e in errors:
        print(f"FAIL {e}")
    print(
        f"checked {len(all_pages)} pages, {len(locs)} sitemap URLs: {len(errors)} problem(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
