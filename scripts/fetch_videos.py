#!/usr/bin/env python3
"""
Fetches the latest videos from a YouTube channel RSS feed
and updates the video section in markdown/index.md.
"""

import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import sys

CHANNEL_ID = "UCafepdaI30MCpNn_jSK_NiQ"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
INDEX_MD = "markdown/index.md"
MAX_VIDEOS = 3
MAX_SCAN_ENTRIES = 20

NS = {
    "atom":  "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "yt":    "http://www.youtube.com/xml/schemas/2015",
}


def fetch_rss(url: str) -> ET.Element:
    with urllib.request.urlopen(url, timeout=15) as resp:
        return ET.fromstring(resp.read())


def is_livestream(video_id: str) -> bool:
    """True if the watch page marks this video as live content.

    The RSS feed does not say whether an entry is a livestream, so each
    video's watch page is probed and ``videoDetails.isLiveContent`` is
    read. Tries the lightweight mobile page first, falling back to the
    desktop page. Returns False if the probe fails, so a transient error
    never hides a regular video.
    """
    if not video_id:
        return False

    urls = [
        f"https://m.youtube.com/watch?v={video_id}",
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            m = re.search(r'"isLiveContent":(true|false)', html)
            if m:
                return m.group(1) == "true"
        except Exception:
            continue
    return False


def first_paragraph(text: str) -> str:
    """Return the first meaningful paragraph, skipping ==== separators."""
    if not text:
        return ""
    for para in text.strip().split("\n\n"):
        para = para.strip()
        # skip separator lines and lines that are just dashes or equals
        if para and not all(c in "=- \n" for c in para):
            return para
    return ""


def format_date(iso: str) -> str:
    """2025-07-10T14:00:00+00:00  →  July 10, 2025"""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%B %-d, %Y")
    except Exception:
        return iso[:10]


def video_id_from_url(url: str) -> str:
    """https://www.youtube.com/watch?v=XXXX → XXXX"""
    m = re.search(r"v=([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else ""


def parse_videos(root: ET.Element) -> list[dict]:
    videos = []
    for entry in root.findall("atom:entry", NS)[:MAX_SCAN_ENTRIES]:
        title   = entry.findtext("atom:title", "", NS)
        link_el = entry.find("atom:link", NS)
        url     = link_el.get("href", "") if link_el is not None else ""
        pub     = entry.findtext("atom:published", "", NS)

        desc_el = entry.find("media:group/media:description", NS)
        desc    = desc_el.text if desc_el is not None else ""

        videos.append({
            "title":   title,
            "url":     url,
            "date":    format_date(pub),
            "desc":    first_paragraph(desc or ""),
            "videoid": video_id_from_url(url),
        })
    return videos


def render_videos(videos: list[dict]) -> str:
    parts = []
    for v in videos:
        embed = ""
        if v["videoid"]:
            embed = (
                f'<iframe class="video-embed" '
                f'src="https://www.youtube.com/embed/{v["videoid"]}?rel=0" '
                f'title="{v["title"]}" '
                f'allow="accelerometer; autoplay; clipboard-write; '
                f'encrypted-media; gyroscope; picture-in-picture" '
                f'allowfullscreen loading="lazy"></iframe>\n'
                f'<p class="video-link"><a href="{v["url"]}">▶ Watch on YouTube</a></p>'
            )

        desc_html = ""
        if v["desc"]:
            desc_html = f'<p class="video-description">{v["desc"]}</p>'

        parts.append(
            f'<div class="video-entry">\n'
            f'<h3><a href="{v["url"]}">{v["title"]}</a></h3>\n'
            f'<p class="video-date">{v["date"]}</p>\n'
            f'{embed}\n'
            f'{desc_html}\n'
            f'</div>'
        )
    return "\n\n".join(parts)


def update_index(md_path: str, videos_html: str) -> bool:
    with open(md_path, "r") as f:
        content = f.read()

    new_block = (
        "<!-- VIDEOS_START -->\n"
        + videos_html
        + "\n<!-- VIDEOS_END -->"
    )

    updated = re.sub(
        r"<!-- VIDEOS_START -->.*?<!-- VIDEOS_END -->",
        new_block,
        content,
        flags=re.DOTALL,
    )

    if updated == content:
        print("No changes to video content.")
        return False

    with open(md_path, "w") as f:
        f.write(updated)
    print(f"Updated {md_path} with {len(videos)} video(s).")
    return True


if __name__ == "__main__":
    print(f"Fetching RSS: {RSS_URL}")
    try:
        root = fetch_rss(RSS_URL)
    except Exception as e:
        print(f"Error fetching RSS: {e}", file=sys.stderr)
        sys.exit(1)

    videos = parse_videos(root)
    if not videos:
        print("No videos found in feed.", file=sys.stderr)
        sys.exit(1)

    # Skip livestreams and Shorts; keep the newest MAX_VIDEOS regular uploads.
    regular = []
    for v in videos:
        if is_livestream(v["videoid"]):
            print(f"Skipping livestream: {v['title'][:60]}")
            continue
        if "/shorts/" in v["url"]:
            print(f"Skipping short: {v['title'][:60]}")
            continue
        regular.append(v)
        if len(regular) == MAX_VIDEOS:
            break
    videos = regular
    if not videos:
        print("No non-livestream videos found in feed.", file=sys.stderr)
        sys.exit(1)

    videos_html = render_videos(videos)
    changed = update_index(INDEX_MD, videos_html)
    sys.exit(0 if changed else 0)
