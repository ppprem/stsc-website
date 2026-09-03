from __future__ import annotations

from seo_report_runtime import main

if __name__ == "__main__":
    raise SystemExit(main())

def status_label(row: InspectionRow) -> str:
    if row.signal_a or row.signal_b:
        return "Signal aktiv"
    if row.blocked:
        return "Blockiert"
    if row.live_in_serps:
        return "Live in SERPs"
    return "Unklar"


def status_class(row: InspectionRow) -> str:
    if row.signal_a or row.signal_b:
        return "signal"
    if row.blocked:
        return "blocked"
    if row.live_in_serps:
        return "live"
    return "neutral"


def render_html_report(rows: list[InspectionRow], site_root: str, generated_at: datetime, title: str) -> str:
    total_count = len(rows)
    blocked_count = sum(1 for row in rows if row.blocked)
    live_count = sum(1 for row in rows if row.live_in_serps)
    signal_count = sum(1 for row in rows if row.signal_a or row.signal_b)

    table_rows = []
    for row in rows:
        signal_text = ", ".join(filter(None, ["Signal A" if row.signal_a else "", "Signal B" if row.signal_b else ""])) or "-"
        notes_text = "<br>".join(escape(note) for note in row.notes) if row.notes else "-"
        crawl_text = format_timestamp(row.last_crawl_time) if row.last_crawl_time else "nie"
        status = status_label(row)
        badge_class = status_class(row)
        table_rows.append(
            f"""
            <tr class="{badge_class}">
                <td><a href="{escape(row.target.url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(row.target.url)}</a></td>
                <td>{escape(row.target.source)}</td>
                <td>{escape(format_timestamp(row.target.last_seo_update))}</td>
                <td>{escape(crawl_text)}</td>
                <td>{escape(row.verdict or '-')}</td>
                <td>{escape(row.coverage_state or '-')}</td>
                <td><span class="status-badge {badge_class}">{escape(status)}</span></td>
                <td>{escape(signal_text)}</td>
                <td class="note-text">{notes_text}</td>
            </tr>
            """.strip()
        )

    generated_text = escape(format_timestamp(generated_at))
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>
  :root {{
    --bg: #f4efe7;
    --surface: #ffffff;
    --ink: #162015;
    --muted: #5c655f;
    --accent: #f8951b;
    --accent-dark: #ab4201;
    --success: #e9f8ed;
    --warning: #fff4df;
    --danger: #fdecec;
    --border: #e6ded1;
    --shadow: 0 16px 40px rgba(22, 32, 21, 0.08);
  }}
  body {{ font-family: system-ui, sans-serif; margin: 0; background: radial-gradient(circle at top left, #fff8ef 0%, var(--bg) 55%, #efe7db 100%); color: var(--ink); }}
  header {{ background: linear-gradient(135deg, var(--accent-dark), var(--accent)); color: white; padding: 28px 28px 32px; box-shadow: var(--shadow); }}
  header h1 {{ margin: 0 0 8px; font-size: clamp(2rem, 4vw, 3.4rem); line-height: 1.05; }}
  header > div {{ margin-top: 6px; opacity: 0.95; }}
  main {{ padding: 24px 28px 40px; max-width: 1440px; margin: 0 auto; }}
  .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 16px; margin: -22px 0 24px; }}
  .card {{ background: var(--surface); border-radius: 16px; padding: 16px 18px; box-shadow: var(--shadow); border: 1px solid rgba(255,255,255,0.75); }}
  .card strong {{ display: block; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 8px; }}
  .card span {{ font-size: 1.9rem; font-weight: 800; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }}
  .pill {{ border-radius: 999px; padding: 8px 14px; font-size: 0.9rem; background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.22); }}
  .toolbar {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin: 8px 0 18px; color: var(--muted); }}
  .toolbar .chip {{ background: rgba(22, 32, 21, 0.06); padding: 8px 12px; border-radius: 999px; }}
  table {{ width: 100%; border-collapse: separate; border-spacing: 0; background: var(--surface); box-shadow: var(--shadow); border-radius: 18px; overflow: hidden; border: 1px solid var(--border); }}
  th, td {{ padding: 12px 10px; border-bottom: 1px solid #e8e2d8; vertical-align: top; text-align: left; }}
  th {{ background: #162015; color: white; position: sticky; top: 0; z-index: 1; font-size: 0.82rem; letter-spacing: 0.04em; text-transform: uppercase; }}
  tbody tr:nth-child(even) {{ background: rgba(22, 32, 21, 0.02); }}
  tr.blocked {{ background: var(--danger); }}
  tr.live {{ background: var(--success); }}
  tr.signal {{ background: var(--warning); }}
  tr.neutral {{ background: #fbfaf7; }}
  tr:hover {{ filter: brightness(0.985); }}
  td:first-child a {{ font-weight: 700; color: #0c4a6e; word-break: break-word; }}
  td:nth-child(7) {{ font-weight: 700; white-space: nowrap; }}
  .status-badge {{ display: inline-block; padding: 6px 10px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; }}
  .status-badge.blocked {{ background: #f9cfcf; color: #7a1717; }}
  .status-badge.live {{ background: #cdeed4; color: #16512a; }}
  .status-badge.signal {{ background: #ffe6af; color: #805400; }}
  .status-badge.neutral {{ background: #e6e2d8; color: #424242; }}
  .note-text {{ color: var(--muted); font-size: 0.92rem; line-height: 1.45; }}
  .scroll {{ overflow-x: auto; }}
  .section-title {{ margin: 24px 0 12px; font-size: 1.1rem; }}
</style>
</head>
<body>
<header>
  <h1>{escape(title)}</h1>
  <div>Site root: {escape(site_root)}</div>
  <div>Generated at: {generated_text}</div>
  <div class="legend">
    <span class="pill">Blockiert</span>
    <span class="pill">Live in SERPs</span>
    <span class="pill">Signal aktiv</span>
  </div>
</header>
<main>
  <div class="meta">
    <div class="card"><strong>Seiten</strong><span>{total_count}</span></div>
    <div class="card"><strong>Blockiert</strong><span>{blocked_count}</span></div>
    <div class="card"><strong>Live in SERPs</strong><span>{live_count}</span></div>
    <div class="card"><strong>Signale aktiv</strong><span>{signal_count}</span></div>
  </div>
  <div class="toolbar">
    <span class="chip">Grün = Google ist aktuell</span>
    <span class="chip">Gelb = Signal A/B wurde gesetzt</span>
    <span class="chip">Rot = aktuell blockiert oder nicht sauber crawlt</span>
  </div>
  <div class="scroll">
    <table>
      <thead>
        <tr>
          <th>URL</th>
          <th>Quelle</th>
          <th>last_seo_update</th>
          <th>lastCrawlTime</th>
          <th>verdict</th>
          <th>coverageState</th>
          <th>Status</th>
          <th>Signale</th>
          <th>Notizen</th>
        </tr>
      </thead>
      <tbody>
        {''.join(table_rows)}
      </tbody>
    </table>
  </div>
</main>
</body>
</html>
"""


def build_history_index(history: list[dict], history_dir: Path, latest_report_name: str) -> str:
    entries = []
    for item in history:
        report_name = str(item.get("report_name", latest_report_name))
        generated_at = escape(str(item.get("generated_at", "")))
        counts = item.get("counts", {})
        entries.append(
            f"""
            <tr>
              <td><a href="{escape(report_name, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(report_name)}</a></td>
              <td>{generated_at}</td>
              <td>{escape(str(counts.get('total', 0)))}</td>
              <td>{escape(str(counts.get('blocked', 0)))}</td>
              <td>{escape(str(counts.get('live', 0)))}</td>
              <td>{escape(str(counts.get('signals', 0)))}</td>
            </tr>
            """.strip()
        )

    if not entries:
        entries_html = "<tr><td colspan='6'>Noch kein Verlauf vorhanden.</td></tr>"
    else:
        entries_html = "\n".join(entries)

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SEO Report Verlauf</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 0; background: #f4efe7; color: #162015; }}
  header {{ background: linear-gradient(135deg, #ab4201, #f8951b); color: white; padding: 28px; }}
  main {{ padding: 24px 28px 40px; max-width: 1200px; margin: 0 auto; }}
  table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 12px 30px rgba(22,32,21,0.08); border-radius: 16px; overflow: hidden; }}
  th, td {{ padding: 12px 10px; border-bottom: 1px solid #e8e2d8; text-align: left; }}
  th {{ background: #162015; color: white; text-transform: uppercase; font-size: 0.82rem; letter-spacing: 0.04em; }}
  a {{ color: #0c4a6e; }}
  .note {{ margin: 16px 0 20px; color: #5c655f; }}
</style>
</head>
<body>
<header>
  <h1>SEO Report Verlauf</h1>
  <div>Letzter Lauf und archivierte Berichte in einem Überblick.</div>
</header>
<main>
  <div class="note">Aktueller Bericht: <a href="{escape(latest_report_name, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(latest_report_name)}</a></div>
  <table>
    <thead>
      <tr>
        <th>Report</th>
        <th>Generiert</th>
        <th>Seiten</th>
        <th>Blockiert</th>
        <th>Live in SERPs</th>
        <th>Signale</th>
      </tr>
    </thead>
    <tbody>
      {entries_html}
    </tbody>
  </table>
</main>
</body>
</html>
"""


def write_report_outputs(rows: list[InspectionRow], report_path: Path, site_root: str) -> tuple[Path, Path]:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0)
    report_title = "SEO Diagnose Report"
    report_html = render_html_report(rows, site_root, generated_at, report_title)
    report_path.write_text(report_html, encoding="utf-8")

    history_dir = report_path.parent / "seo_report_history"
    history_dir.mkdir(parents=True, exist_ok=True)

    archive_name = f"seo_report_{generated_at.strftime('%Y%m%d_%H%M%S')}.html"
    archive_path = history_dir / archive_name
    archive_path.write_text(report_html, encoding="utf-8")

    history_path = history_dir / "history.json"
    history: list[dict] = []
    if history_path.exists():
        try:
            loaded_history = json.loads(history_path.read_text(encoding="utf-8"))
            if isinstance(loaded_history, list):
                history = [item for item in loaded_history if isinstance(item, dict)]
        except json.JSONDecodeError:
            history = []

    summary = {
        "generated_at": format_timestamp(generated_at),
        "report_name": archive_name,
        "counts": {
            "total": len(rows),
            "blocked": sum(1 for row in rows if row.blocked),
            "live": sum(1 for row in rows if row.live_in_serps),
            "signals": sum(1 for row in rows if row.signal_a or row.signal_b),
        },
    }
    history.insert(0, summary)
    history = history[:20]
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

    index_html = build_history_index(history, history_dir, archive_name)
    index_path = history_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")

    return archive_path, index_path


def open_report(report_path: Path) -> None:
    try:
        webbrowser.open(report_path.resolve().as_uri())
    except Exception:
        pass


def load_posts_mapping(posts_path: Path, site_root: str) -> dict[str, datetime]:
    if not posts_path.exists():
        return {}

    data = json.loads(posts_path.read_text(encoding="utf-8"))
    mapping: dict[str, datetime] = {}
    for post in data.get("posts", []):
        relative_url = str(post.get("url", "")).strip()
        if not relative_url:
            continue

        update = parse_timestamp(str(post.get("date", "")).strip())
        if update is None:
            continue

        mapping[absolute_url(site_root, relative_url)] = update

    return mapping


def load_sitemap_urls(sitemap_path: Path) -> list[str]:
    if not sitemap_path.exists():
        raise FileNotFoundError(f"Sitemap not found: {sitemap_path}")

    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    urls: list[str] = []

    for element in root.findall(f"{{{SITEMAP_NAMESPACE}}}url"):
        loc = element.findtext(f"{{{SITEMAP_NAMESPACE}}}loc")
        if loc:
            urls.append(loc.strip())

    return urls


def build_seo_targets(sitemap_path: Path, posts_path: Path, site_root: str) -> list[SeoTarget]:
    posts_mapping = load_posts_mapping(posts_path, site_root)
    targets: list[SeoTarget] = []

    for url in load_sitemap_urls(sitemap_path):
        local_path = local_path_from_url(url, site_root)
        seo_update = posts_mapping.get(url)

        if seo_update is None and local_path is not None and local_path.exists():
            seo_update = datetime.fromtimestamp(local_path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0)

        if seo_update is None:
            continue

        source = "posts.json" if url in posts_mapping else "file-mtime"
        targets.append(
            SeoTarget(
                url=url,
                last_seo_update=seo_update,
                source=source,
                local_path=local_path,
            )
        )

    return targets


def refresh_seo_database(db_path: Path, sitemap_path: Path, posts_path: Path, site_root: str) -> list[SeoTarget]:
    targets = build_seo_targets(sitemap_path, posts_path, site_root)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS seo_targets (
                url TEXT PRIMARY KEY,
                last_seo_update TEXT NOT NULL,
                source TEXT NOT NULL,
                local_path TEXT
            )
            """
        )
        connection.execute("DELETE FROM seo_targets")
        connection.executemany(
            "INSERT OR REPLACE INTO seo_targets (url, last_seo_update, source, local_path) VALUES (?, ?, ?, ?)",
            [
                (
                    target.url,
                    format_timestamp(target.last_seo_update),
                    target.source,
                    str(target.local_path) if target.local_path is not None else None,
                )
                for target in targets
            ],
        )
        connection.commit()

    return targets


def load_targets_from_database(db_path: Path) -> list[SeoTarget]:
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT url, last_seo_update, source, local_path FROM seo_targets ORDER BY last_seo_update DESC, url ASC"
        ).fetchall()

    targets: list[SeoTarget] = []
    for url, last_seo_update, source, local_path in rows:
        targets.append(
            SeoTarget(
                url=url,
                last_seo_update=parse_timestamp(last_seo_update) or datetime.now(timezone.utc),
                source=source,
                local_path=Path(local_path) if local_path else None,
            )
        )

    return targets


def inspect_url(service, property_url: str, target: SeoTarget, language_code: str) -> tuple[dict, datetime | None, str | None, str | None]:
    request_body = {
        "inspectionUrl": target.url,
        "siteUrl": property_url,
        "languageCode": language_code,
    }

    response = service.urlInspection().index().inspect(body=request_body).execute()
    result = response.get("inspectionResult", {})
    index_status = result.get("indexStatusResult", {})
    last_crawl = parse_timestamp(index_status.get("lastCrawlTime"))
    return response, last_crawl, index_status.get("verdict"), index_status.get("coverageState")


def is_blocked(verdict: str | None, coverage_state: str | None, response: dict) -> bool:
    combined = f"{verdict or ''} {coverage_state or ''} {response!r}".lower()
    blocked_markers = ("blocked", "noindex", "robots", "excluded", "crawl anomaly", "fail")
    return any(marker in combined for marker in blocked_markers)


def update_sitemap_lastmods(sitemap_path: Path, urls: Iterable[str], new_timestamp: datetime, dry_run: bool) -> list[str]:
    target_urls = {url for url in urls}
    if not target_urls:
        return []

    updated_urls: list[str] = []
    if dry_run:
        return list(target_urls)

    ET.register_namespace("", SITEMAP_NAMESPACE)
    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    for url_node in root.findall(f"{{{SITEMAP_NAMESPACE}}}url"):
        loc = url_node.findtext(f"{{{SITEMAP_NAMESPACE}}}loc")
        if not loc or loc.strip() not in target_urls:
            continue

        lastmod = url_node.find(f"{{{SITEMAP_NAMESPACE}}}lastmod")
        if lastmod is None:
            lastmod = ET.SubElement(url_node, f"{{{SITEMAP_NAMESPACE}}}lastmod")
        lastmod.text = format_timestamp(new_timestamp)
        updated_urls.append(loc.strip())

    indent = getattr(ET, "indent", None)
    if callable(indent):
        indent(tree, space="  ")

    tree.write(sitemap_path, encoding="utf-8", xml_declaration=True)
    return updated_urls


def render_priority_block(urls: Iterable[str]) -> str:
    normalized_urls = list(dict.fromkeys(urls))
    if not normalized_urls:
        items = "      <li>Aktuell keine Priority-Crawl-URLs aktiv.</li>"
    else:
        rendered_items = []
        for url in normalized_urls:
            parsed = urlparse(url)
            path = parsed.path or "/"
            normalized_path = unquote(path.lstrip("/"))
            href = "/" if path == "/" else quote(normalized_path)
            label = "Startseite" if path == "/" else normalized_path
            rendered_items.append(f'      <li><a href="{escape(href, quote=True)}">{escape(label)}</a></li>')
        items = "\n".join(rendered_items)

    return (
        f"{PRIORITY_MARKER_START}\n"
        f"    <ul class=\"priority-crawl-list\">\n"
        f"{items}\n"
        f"    </ul>\n"
        f"{PRIORITY_MARKER_END}"
    )


def update_homepage_priority_block(homepage_path: Path, urls: Iterable[str], dry_run: bool) -> bool:
    if dry_run:
        return True

    content = homepage_path.read_text(encoding="utf-8")
    replacement = render_priority_block(urls)
    pattern = re.compile(
        rf"{re.escape(PRIORITY_MARKER_START)}.*?{re.escape(PRIORITY_MARKER_END)}",
        re.DOTALL,
    )

    if not pattern.search(content):
        raise ValueError(f"Priority crawl marker block not found in {homepage_path}")

    updated_content = pattern.sub(replacement, content)
    if updated_content != content:
        homepage_path.write_text(updated_content, encoding="utf-8")

    return True


def determine_actions(
    blocked: bool,
    seo_update: datetime,
    last_crawl: datetime | None,
) -> tuple[bool, bool, list[str]]:
    stale = last_crawl is None or last_crawl < seo_update
    live = last_crawl is not None and last_crawl >= seo_update and not blocked
    notes: list[str] = []

    if stale:
        notes.append("Google-Crawl älter als last_seo_update")
    elif live:
        notes.append("SEO-Update bereits live in Google")

    if blocked:
        notes.append("aktuell blockiert")

    return stale, live, notes


def print_summary(rows: list[InspectionRow]) -> None:
    blocked_rows = [row for row in rows if row.blocked]
    live_rows = [row for row in rows if row.live_in_serps]
    active_rows = [row for row in rows if row.signal_a or row.signal_b]

    print("\n=== DIAGNOSE-ÜBERSICHT ===")
    print(f"Aktuell blockiert: {len(blocked_rows)}")
    print(f"SEO-Update live in den SERPs: {len(live_rows)}")
    print(f"Alternative Signale aktiv: {len(active_rows)}")

    if blocked_rows:
        print("\nBlockierte Seiten:")
        for row in blocked_rows:
            print(f"- {row.target.url} | {row.coverage_state or 'kein coverageState'}")

    if live_rows:
        print("\nLive in den SERPs:")
        for row in live_rows:
            crawl = format_timestamp(row.last_crawl_time) if row.last_crawl_time else "kein lastCrawlTime"
            print(f"- {row.target.url} | Crawl: {crawl}")

    if active_rows:
        print("\nAktive alternative Signale:")
        for row in active_rows:
            signals = []
            if row.signal_a:
                signals.append("Signal A")
            if row.signal_b:
                signals.append("Signal B")
            print(f"- {row.target.url} | {', '.join(signals)}")


def status_label(row: InspectionRow) -> str:
    if row.signal_a or row.signal_b:
        return "Signal aktiv"
    if row.blocked:
        return "Blockiert"
    if row.live_in_serps:
        return "Live in SERPs"
    return "Unklar"


def build_html_report(rows: list[InspectionRow], report_path: Path, site_root: str) -> None:
    generated_at = format_timestamp(datetime.now(timezone.utc).replace(microsecond=0))
    total_count = len(rows)
    blocked_count = sum(1 for row in rows if row.blocked)
    live_count = sum(1 for row in rows if row.live_in_serps)
    signal_count = sum(1 for row in rows if row.signal_a or row.signal_b)

    def tone_class(row: InspectionRow) -> str:
        if row.signal_a or row.signal_b:
            return "signal"
        if row.blocked:
            return "blocked"
        if row.live_in_serps:
            return "live"
        return "neutral"

        table_rows = []
        for row in rows:
            signal_text = ", ".join(filter(None, ["Signal A" if row.signal_a else "", "Signal B" if row.signal_b else ""])) or "-"
            notes_text = "<br>".join(escape(note) for note in row.notes) if row.notes else "-"
            crawl_text = format_timestamp(row.last_crawl_time) if row.last_crawl_time else "nie"
            status = status_label(row)
            table_rows.append(
                f"""
            <tr class=\"{tone_class(row)}\">
                    <td><a href=\"{escape(row.target.url, quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{escape(row.target.url)}</a></td>
                    <td>{escape(row.target.source)}</td>
                    <td>{escape(format_timestamp(row.target.last_seo_update))}</td>
                    <td>{escape(crawl_text)}</td>
                    <td>{escape(row.verdict or '-')}</td>
                    <td>{escape(row.coverage_state or '-')}</td>
                    <td><span class=\"status-badge {escape(tone_class(row))}\">{escape(status)}</span></td>
                    <td>{escape(signal_text)}</td>
                    <td class=\"note-text\">{notes_text}</td>
                </tr>
                """.strip()
            )

        report_html = f"""<!DOCTYPE html>
<html lang=\"de\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>STSC SEO Report</title>
<style>
    :root {{
        --bg: #f4efe7;
        --surface: #ffffff;
        --ink: #162015;
        --muted: #5c655f;
        --accent: #f8951b;
        --accent-dark: #ab4201;
        --success: #e9f8ed;
        --warning: #fff4df;
        --danger: #fdecec;
        --border: #e6ded1;
        --shadow: 0 16px 40px rgba(22, 32, 21, 0.08);
    }}
    body {{ font-family: system-ui, sans-serif; margin: 0; background: radial-gradient(circle at top left, #fff8ef 0%, var(--bg) 55%, #efe7db 100%); color: var(--ink); }}
    header {{ background: linear-gradient(135deg, var(--accent-dark), var(--accent)); color: white; padding: 28px 28px 32px; box-shadow: var(--shadow); }}
    header h1 {{ margin: 0 0 8px; font-size: clamp(2rem, 4vw, 3.4rem); line-height: 1.05; }}
    header > div {{ margin-top: 6px; opacity: 0.95; }}
    main {{ padding: 24px 28px 40px; max-width: 1440px; margin: 0 auto; }}
    .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 16px; margin: -22px 0 24px; }}
    .card {{ background: var(--surface); border-radius: 16px; padding: 16px 18px; box-shadow: var(--shadow); border: 1px solid rgba(255,255,255,0.75); }}
    .card strong {{ display: block; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 8px; }}
    .card span {{ font-size: 1.9rem; font-weight: 800; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }}
    .pill {{ border-radius: 999px; padding: 8px 14px; font-size: 0.9rem; background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.22); }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin: 8px 0 18px; color: var(--muted); }}
    .toolbar .chip {{ background: rgba(22, 32, 21, 0.06); padding: 8px 12px; border-radius: 999px; }}
    table {{ width: 100%; border-collapse: separate; border-spacing: 0; background: var(--surface); box-shadow: var(--shadow); border-radius: 18px; overflow: hidden; border: 1px solid var(--border); }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid #e8e2d8; vertical-align: top; text-align: left; }}
    th {{ background: #162015; color: white; position: sticky; top: 0; z-index: 1; font-size: 0.82rem; letter-spacing: 0.04em; text-transform: uppercase; }}
    tbody tr:nth-child(even) {{ background: rgba(22, 32, 21, 0.02); }}
    tr.blocked {{ background: var(--danger); }}
    tr.live {{ background: var(--success); }}
    tr.signal {{ background: var(--warning); }}
    tr.neutral {{ background: #fbfaf7; }}
    tr:hover {{ filter: brightness(0.985); }}
    td:first-child a {{ font-weight: 700; color: #0c4a6e; word-break: break-word; }}
    td:nth-child(7) {{ font-weight: 700; white-space: nowrap; }}
    .status-badge {{ display: inline-block; padding: 6px 10px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; }}
    .status-badge.blocked {{ background: #f9cfcf; color: #7a1717; }}
    .status-badge.live {{ background: #cdeed4; color: #16512a; }}
    .status-badge.signal {{ background: #ffe6af; color: #805400; }}
    .status-badge.neutral {{ background: #e6e2d8; color: #424242; }}
    .note-text {{ color: var(--muted); font-size: 0.92rem; line-height: 1.45; }}
    .scroll {{ overflow-x: auto; }}
    .section-title {{ margin: 24px 0 12px; font-size: 1.1rem; }}
</style>
</head>
<body>
<header>
    <h1>SEO Diagnose Report</h1>
    <div>Site root: {escape(site_root)}</div>
    <div>Generated at: {escape(generated_at)}</div>
    <div class=\"legend\">
        <span class=\"pill\">Blockiert</span>
        <span class=\"pill\">Live in SERPs</span>
        <span class=\"pill\">Signal aktiv</span>
    </div>
</header>
<main>
    <div class=\"meta\">
        <div class=\"card\"><strong>Seiten</strong><span>{total_count}</span></div>
        <div class=\"card\"><strong>Blockiert</strong><span>{blocked_count}</span></div>
        <div class=\"card\"><strong>Live in SERPs</strong><span>{live_count}</span></div>
        <div class=\"card\"><strong>Signale aktiv</strong><span>{signal_count}</span></div>
    </div>
    <div class=\"toolbar\">
        <span class=\"chip\">Grün = Google ist aktuell</span>
        <span class=\"chip\">Gelb = Signal A/B wurde gesetzt</span>
        <span class=\"chip\">Rot = aktuell blockiert oder nicht sauber crawlt</span>
    </div>
    <div class=\"scroll\">
        <table>
            <thead>
                <tr>
                    <th>URL</th>
                    <th>Quelle</th>
                    <th>last_seo_update</th>
                    <th>lastCrawlTime</th>
                    <th>verdict</th>
                    <th>coverageState</th>
                    <th>Status</th>
                    <th>Signale</th>
                    <th>Notizen</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </div>
</main>
</body>
</html>
"""

    report_path.write_text(report_html, encoding="utf-8")


def open_report(report_path: Path) -> None:
    try:
        webbrowser.open(report_path.resolve().as_uri())
    except Exception:
        pass


def main() -> int:
    args = parse_args()

    service = load_service(args.credentials)
    refresh_seo_database(args.db_path, args.sitemap, args.posts, args.site_root)
    targets = load_targets_from_database(args.db_path)

    if not targets:
        print("No SEO targets found.", file=sys.stderr)
        return 1

    print(f"Found {len(targets)} SEO target(s) for {args.site_root}")

    rows: list[InspectionRow] = []
    stale_urls: list[str] = []

    for index, target in enumerate(targets, start=1):
        try:
            response, last_crawl, verdict, coverage_state = inspect_url(
                service,
                args.property_url,
                target,
                args.language_code,
            )
        except Exception as exc:  # pragma: no cover - command-line diagnostics
            print(f"[{index}/{len(targets)}] ERROR {target.url}: {exc}", file=sys.stderr)
            rows.append(
                InspectionRow(
                    target=target,
                    verdict=None,
                    coverage_state=None,
                    last_crawl_time=None,
                    blocked=True,
                    live_in_serps=False,
                    signal_a=False,
                    signal_b=False,
                    notes=[f"Inspection failed: {exc}"],
                )
            )
            continue

        blocked = is_blocked(verdict, coverage_state, response)
        stale, live, notes = determine_actions(blocked, target.last_seo_update, last_crawl)

        signal_a = False
        signal_b = False
        if stale:
            stale_urls.append(target.url)
            signal_a = True
            signal_b = True

        row = InspectionRow(
            target=target,
            verdict=verdict,
            coverage_state=coverage_state,
            last_crawl_time=last_crawl,
            blocked=blocked,
            live_in_serps=live,
            signal_a=signal_a,
            signal_b=signal_b,
            notes=notes,
        )
        rows.append(row)

        crawl_text = format_timestamp(last_crawl) if last_crawl else "never"
        print(
            f"[{index}/{len(targets)}] {target.url} | verdict={verdict or 'n/a'} | coverage={coverage_state or 'n/a'} | crawl={crawl_text}"
        )

    if stale_urls:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        sitemap_updates = update_sitemap_lastmods(args.sitemap, stale_urls, now, args.dry_run)
        update_homepage_priority_block(
            args.homepage,
            stale_urls[: args.priority_limit] if args.priority_limit > 0 else stale_urls,
            args.dry_run,
        )

        if args.dry_run:
            print(f"\nDry-run: would refresh sitemap lastmod for {len(sitemap_updates)} URL(s).")
            print(f"Dry-run: would update homepage priority list with {len(stale_urls)} URL(s).")
        else:
            print(f"\nUpdated sitemap lastmod for {len(sitemap_updates)} URL(s).")
            print(f"Updated homepage priority list with {len(stale_urls)} URL(s).")
    else:
        update_homepage_priority_block(args.homepage, [], args.dry_run)
        print("\nNo stale URLs detected. No alternate signals were activated.")

    archive_path, history_index_path = write_report_outputs(rows, args.report, args.site_root)
    if not args.dry_run:
        open_report(history_index_path)
    print(f"\nHTML report written to: {args.report}")
    print(f"Report archive written to: {archive_path}")
    print(f"History index written to: {history_index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())