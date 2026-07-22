#!/usr/bin/env python3
"""Build a deterministic JSON index from docs/wiki/*.md."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "docs" / "wiki"
OUTPUT = ROOT / "data" / "wiki-index.json"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def extract_title(path: Path, content: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", content, re.MULTILINE)
    return match.group(1).strip() if match else path.stem


def extract_headings(content: str) -> list[dict[str, object]]:
    return [
        {"level": len(match.group(1)), "text": match.group(2).strip()}
        for match in HEADING_RE.finditer(content)
    ]


def extract_links(content: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for match in WIKI_LINK_RE.finditer(content):
        if match.group(2) is None:
            target = match.group(1).strip()
            label = target
        else:
            label = match.group(1).strip()
            target = match.group(2).strip()
        links.append({"target": target, "label": label})
    return links


def main() -> None:
    paths = sorted(WIKI_DIR.glob("*.md"), key=lambda p: p.name.casefold())
    raw_pages: list[dict[str, object]] = []

    for path in paths:
        content = path.read_text(encoding="utf-8")
        title = extract_title(path, content)
        raw_pages.append(
            {
                "title": title,
                "path": path.relative_to(ROOT).as_posix(),
                "content": content,
                "contentHash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "headings": extract_headings(content),
                "links": extract_links(content),
            }
        )

    existing_titles = {str(page["title"]) for page in raw_pages}
    pages: list[dict[str, object]] = []
    backlinks: dict[str, list[str]] = {title: [] for title in existing_titles}

    for page in raw_pages:
        source_title = str(page["title"])
        links = page["links"]
        assert isinstance(links, list)
        missing = sorted(
            {
                str(link["target"])
                for link in links
                if isinstance(link, dict) and str(link["target"]) not in existing_titles
            },
            key=str.casefold,
        )
        for link in links:
            if not isinstance(link, dict):
                continue
            target = str(link["target"])
            if target in backlinks:
                backlinks[target].append(source_title)

        pages.append({**page, "missingLinks": missing})

    pages.sort(key=lambda page: str(page["title"]).casefold())
    normalized_backlinks = {
        title: sorted(set(sources), key=str.casefold)
        for title, sources in sorted(backlinks.items(), key=lambda item: item[0].casefold())
        if sources
    }

    index = {
        "schemaVersion": 1,
        "source": "docs/wiki/*.md",
        "pageCount": len(pages),
        "pages": pages,
        "backlinks": normalized_backlinks,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(index, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
