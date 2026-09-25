#!/usr/bin/env python3
"""Pull the latest videos from the YouTube channel feed into README.md.

Run it after uploading a new video, then commit and push:
    python3 scripts/update_videos.py
"""

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = "UCEu34nU4gy867u8Cy7obc6w"
MAX_VIDEOS = 6
PER_ROW = 3
README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- BEGIN YOUTUBE-CARDS -->", "<!-- END YOUTUBE-CARDS -->"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def latest_videos():
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
    with urllib.request.urlopen(url, timeout=15) as res:
        feed = ET.fromstring(res.read())
    for entry in feed.findall("a:entry", NS)[:MAX_VIDEOS]:
        yield entry.find("yt:videoId", NS).text, entry.find("a:title", NS).text


def card(video_id, title):
    title = html.escape(title)
    return (
        f'<td align="center" width="33%">'
        f'<a href="https://www.youtube.com/watch?v={video_id}">'
        f'<img src="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" width="250" alt="{title}" /></a>'
        f"<br><sub>{title}</sub></td>"
    )


def main():
    cards = [card(*v) for v in latest_videos()]
    rows = [cards[i : i + PER_ROW] for i in range(0, len(cards), PER_ROW)]
    table = "<table>\n" + "\n".join(f"<tr>{''.join(r)}</tr>" for r in rows) + "\n</table>"

    readme = README.read_text()
    pattern = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)
    if not pattern.search(readme):
        raise SystemExit(f"markers not found in {README}")
    README.write_text(pattern.sub(lambda _: f"{START}\n{table}\n{END}", readme))
    print(f"updated README with {len(cards)} videos")


if __name__ == "__main__":
    main()
