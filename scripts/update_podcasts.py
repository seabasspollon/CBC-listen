#!/usr/bin/env python3
"""Fetch the newest playable CBC podcast episode from each official RSS feed."""
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

FEEDS = {
    "quirks": ("Quirks & Quarks", "https://www.cbc.ca/podcasting/includes/quirksaio.xml"),
    "whitecoat": ("White Coat, Black Art", "https://www.cbc.ca/podcasting/includes/whitecoat.xml"),
    "ideas": ("Ideas", "https://www.cbc.ca/podcasting/includes/ideas.xml"),
}

def local_name(tag):
    return tag.rsplit("}", 1)[-1].split(":")[-1].lower()

def child_text(node, wanted):
    for child in node.iter():
        if local_name(child.tag) == wanted:
            return (child.text or "").strip()
    return ""

def episode_date(item):
    value = child_text(item, "pubdate") or child_text(item, "published") or child_text(item, "date")
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = parsedate_to_datetime(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.min.replace(tzinfo=timezone.utc)

def extract_episode(item):
    candidates = []
    for node in item.iter():
        name = local_name(node.tag)
        if name == "enclosure":
            url = node.attrib.get("url") or node.attrib.get("href")
            mime = node.attrib.get("type", "")
            if url and (not mime or mime.startswith("audio/")):
                candidates.append(url)
        elif name == "content":
            url = node.attrib.get("url") or node.attrib.get("href")
            mime = node.attrib.get("type", "")
            if url and mime.startswith("audio/"):
                candidates.append(url)
        elif name == "link" and node.attrib.get("rel", "").lower() == "enclosure":
            url = node.attrib.get("href")
            mime = node.attrib.get("type", "")
            if url and (not mime or mime.startswith("audio/")):
                candidates.append(url)
    if not candidates:
        return None
    return {
        "title": child_text(item, "title") or "Latest episode",
        "audio_url": candidates[0],
        "published": child_text(item, "pubdate") or child_text(item, "published") or child_text(item, "date"),
        "duration": child_text(item, "duration"),
        "_date": episode_date(item),
    }

result = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "shows": {},
    "errors": {},
}
for key, (title, url) in FEEDS.items():
    request = urllib.request.Request(url, headers={"User-Agent": "CBC-Listen-Static-App/1.0 (RSS reader)"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            root = ET.fromstring(response.read())
        items = [node for node in root.iter() if local_name(node.tag) == "item"]
        episodes = [episode for item in items if (episode := extract_episode(item))]
        if not episodes:
            raise RuntimeError("Feed contained no playable audio enclosures")
        latest = max(episodes, key=lambda episode: episode["_date"])
        latest.pop("_date", None)
        result["shows"][key] = latest
        print(f"{title}: {latest['title']}")
    except Exception as exc:
        result["errors"][key] = str(exc)
        print(f"ERROR {title}: {exc}")

if not result["shows"]:
    raise SystemExit("No podcast feeds could be read; refusing to replace latest.json")

Path("latest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
