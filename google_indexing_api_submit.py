"""Submit project URLs to the Google Indexing API.

This script reads URLs from sitemap.xml by default, authenticates with the
service-account JSON in this repository, and sends URL_UPDATED notifications
to the Google Indexing API.

Important: the Google Indexing API is officially intended for eligible
content types such as JobPosting and BroadcastEvent pages. If you submit
general web pages, Google may ignore the notifications.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account


DEFAULT_CREDENTIALS = Path(__file__).with_name("stsc-490212-be6879d57ad0.json")
DEFAULT_SITEMAP = Path(__file__).with_name("sitemap.xml")
INDEXING_SCOPE = "https://www.googleapis.com/auth/indexing"
INDEXING_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send URLs from a sitemap to the Google Indexing API."
    )
    parser.add_argument(
        "--credentials",
        type=Path,
        default=DEFAULT_CREDENTIALS,
        help="Path to the service-account JSON file.",
    )
    parser.add_argument(
        "--sitemap",
        type=Path,
        default=DEFAULT_SITEMAP,
        help="Path to sitemap.xml.",
    )
    parser.add_argument(
        "--site-root",
        default="https://www.stsc.at/",
        help="Only send URLs that belong to this site root.",
    )
    parser.add_argument(
        "--type",
        choices=("URL_UPDATED", "URL_DELETED"),
        default="URL_UPDATED",
        help="Notification type to send.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maximum number of URLs to send. 0 means no limit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and print URLs without sending requests.",
    )
    return parser.parse_args()


def load_urls_from_sitemap(sitemap_path: Path) -> list[str]:
    if not sitemap_path.exists():
        raise FileNotFoundError(f"Sitemap not found: {sitemap_path}")

    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    urls: list[str] = []

    for element in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = element.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc:
            urls.append(loc.strip())

    return urls


def filter_site_urls(urls: Iterable[str], site_root: str) -> list[str]:
    parsed_root = urlparse(site_root)
    root_netloc = parsed_root.netloc.lower()
    root_scheme = parsed_root.scheme.lower()

    filtered: list[str] = []
    for url in urls:
        parsed_url = urlparse(url)
        if parsed_url.scheme.lower() != root_scheme:
            continue
        if parsed_url.netloc.lower() != root_netloc:
            continue
        filtered.append(url)
    return filtered


def build_session(credentials_path: Path) -> AuthorizedSession:
    if not credentials_path.exists():
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=[INDEXING_SCOPE],
    )
    return AuthorizedSession(credentials)


def publish_url(session: AuthorizedSession, url: str, notification_type: str) -> dict:
    response = session.post(
        INDEXING_ENDPOINT,
        json={"url": url, "type": notification_type},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main() -> int:
    args = parse_args()

    urls = load_urls_from_sitemap(args.sitemap)
    urls = filter_site_urls(urls, args.site_root)

    if args.limit and args.limit > 0:
        urls = urls[: args.limit]

    if not urls:
        print("No matching URLs found.", file=sys.stderr)
        return 1

    print(f"Found {len(urls)} URL(s) for {args.site_root}")

    if args.dry_run:
        for url in urls:
            print(url)
        return 0

    session = build_session(args.credentials)

    success_count = 0
    for index, url in enumerate(urls, start=1):
        try:
            payload = publish_url(session, url, args.type)
        except Exception as exc:  # pragma: no cover - command-line diagnostics
            print(f"[{index}/{len(urls)}] ERROR {url}: {exc}", file=sys.stderr)
            continue

        success_count += 1
        print(f"[{index}/{len(urls)}] OK {url}")
        if payload:
            print(json.dumps(payload, ensure_ascii=False))

    print(f"Completed: {success_count}/{len(urls)} URLs sent successfully.")
    return 0 if success_count else 2


if __name__ == "__main__":
    raise SystemExit(main())