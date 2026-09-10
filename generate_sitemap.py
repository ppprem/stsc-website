from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET


SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
DEFAULT_SITE_ROOT = "https://www.stsc.at/"
DEFAULT_OUTPUT = Path(__file__).with_name("sitemap.xml")
DEFAULT_EXCLUDES = {
    "google7d855735e969ce4c.html",
    "seo_report.html",
    "visitenkarte.html",
}


@dataclass(frozen=True, slots=True)
class SitemapEntry:
    url: str
    lastmod: datetime
    priority: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sitemap.xml from local HTML file mtimes.")
    parser.add_argument("--site-root", default=DEFAULT_SITE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_url(site_root: str, relative_path: str) -> str:
    site_root = site_root.rstrip("/")
    if relative_path == "index.html":
        return f"{site_root}/"
    return f"{site_root}/{quote(relative_path, safe='/')}"


def iter_html_files(root: Path) -> list[Path]:
    candidates = []
    for path in root.glob("*.html"):
        if path.name in DEFAULT_EXCLUDES:
            continue
        candidates.append(path)
    return sorted(candidates, key=lambda item: (0 if item.name == "index.html" else 1, item.name.lower()))


def build_entries(root: Path, site_root: str) -> list[SitemapEntry]:
    entries: list[SitemapEntry] = []
    for html_file in iter_html_files(root):
        mtime = datetime.fromtimestamp(html_file.stat().st_mtime, tz=timezone.utc).replace(microsecond=0)
        entries.append(
            SitemapEntry(
                url=file_url(site_root, html_file.name),
                lastmod=mtime,
                priority=1.0,
            )
        )
    return entries


def render_sitemap(entries: list[SitemapEntry]) -> str:
    ET.register_namespace("", SITEMAP_NAMESPACE)
    urlset = ET.Element(f"{{{SITEMAP_NAMESPACE}}}urlset")

    for entry in entries:
        url = ET.SubElement(urlset, f"{{{SITEMAP_NAMESPACE}}}url")
        loc = ET.SubElement(url, f"{{{SITEMAP_NAMESPACE}}}loc")
        loc.text = entry.url
        lastmod = ET.SubElement(url, f"{{{SITEMAP_NAMESPACE}}}lastmod")
        lastmod.text = format_timestamp(entry.lastmod)
        priority = ET.SubElement(url, f"{{{SITEMAP_NAMESPACE}}}priority")
        priority.text = f"{entry.priority:.1f}"

    tree = ET.ElementTree(urlset)
    indent = getattr(ET, "indent", None)
    if callable(indent):
        indent(tree, space="  ")

    return "<?xml version='1.0' encoding='utf-8'?>\n" + ET.tostring(urlset, encoding="unicode") + "\n"


def main() -> int:
    args = parse_args()
    entries = build_entries(args.root, args.site_root)

    if not entries:
        raise SystemExit("No HTML files found to include in sitemap.")

    sitemap_xml = render_sitemap(entries)

    if args.dry_run:
        print(sitemap_xml, end="")
        return 0

    args.output.write_text(sitemap_xml, encoding="utf-8")
    print(f"Wrote {args.output} with {len(entries)} URL(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())