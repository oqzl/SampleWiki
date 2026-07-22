#!/usr/bin/env python3
"""Move flat Wiki pages into ontology folders and generate a hierarchical sidebar."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "docs" / "wiki"

SPECIAL = {"Home.md", "_Sidebar.md", "_Footer.md", "_Header.md"}

CATEGORY_LABELS = {
    "meta": "運用・索引",
    "concepts": "概念",
    "software/wiki": "ソフトウェア / Wiki",
    "software/ios": "ソフトウェア / iOS",
    "software/platforms": "ソフトウェア / プラットフォーム",
    "games/board-game-mechanics": "ゲーム / ボードゲームのメカニクス",
    "games/board-game-design": "ゲーム / ボードゲーム設計",
    "games/digital": "ゲーム / デジタルゲーム",
    "music/theory": "音楽 / 理論",
    "music/instruments": "音楽 / 楽器",
    "food-and-drink": "食・飲料",
    "hardware-and-devices": "ハードウェア・デバイス",
    "people-and-personal": "人物・個人",
    "culture-and-history": "文化・歴史",
    "science-and-health": "科学・健康",
    "projects": "プロジェクト",
    "misc": "その他",
}


def classify(name: str) -> str:
    stem = Path(name).stem

    exact: dict[str, str] = {
        "運用ルール": "meta",
        "Markdown": "software/wiki",
        "バックリンク": "software/wiki",
        "ページ間リンク": "software/wiki",
        "WikiベースSNS": "software/wiki",
        "ローグライクWiki": "software/wiki",
        "ChatGPT連携": "software/wiki",
        "GitHub Actions": "software/platforms",
        "App Store審査": "software/ios",
        "iOSアプリ制作": "software/ios",
        "実験的UI": "software/ios",
        "カメラと画像処理": "software/ios",
        "楽譜ビューアー": "software/ios",
        "ボードゲームのメカニクス": "games/board-game-mechanics",
        "フレーバーとメカニクス": "games/board-game-mechanics",
        "協力型ゲーム": "games/board-game-mechanics",
        "変則的な勝利条件": "games/board-game-mechanics",
        "ボードゲーム制作": "games/board-game-design",
        "ローグライクSNS": "games/digital",
        "ループ系": "concepts",
        "タイムライン": "concepts",
        "音価": "music/theory",
        "和声の重心": "music/theory",
        "マンドローネ": "music/instruments",
        "低音楽器": "music/instruments",
        "ビール": "food-and-drink",
        "ビールの泡": "food-and-drink",
        "ホップ": "food-and-drink",
        "チャーハン": "food-and-drink",
        "ウコン": "science-and-health",
        "酒豪伝説プレミアム": "food-and-drink",
        "センサー": "hardware-and-devices",
        "石川の趣味": "people-and-personal",
        "偏愛マップ-2016": "people-and-personal",
        "最近の偏愛マップ": "people-and-personal",
        "アドベントカレンダー": "culture-and-history",
    }
    if stem in exact:
        return exact[stem]

    rules = [
        (r"ボードゲーム|勝利条件|メカニクス|ドラフト|ワーカー|デッキ|セットコレクション", "games/board-game-mechanics"),
        (r"ゲーム|ローグライク|Roblox|ROBLOX", "games/digital"),
        (r"Wiki|Markdown|リンク|索引", "software/wiki"),
        (r"iOS|App Store|UI|カメラ|画像|Swift|Xcode", "software/ios"),
        (r"GitHub|Actions|API|SNS", "software/platforms"),
        (r"音|和声|楽譜|作曲", "music/theory"),
        (r"楽器|マンドロ", "music/instruments"),
        (r"ビール|酒|食|ラーメン|チャーハン|ホップ", "food-and-drink"),
        (r"センサー|デバイス|カメラ|メガネ", "hardware-and-devices"),
        (r"健康|医療|ウコン|内臓", "science-and-health"),
        (r"偏愛|石川|人物", "people-and-personal"),
        (r"歴史|文化|アドベント", "culture-and-history"),
        (r"設計|方式|問題|現象|モデル|仮説|原則|パターン|系$", "concepts"),
    ]
    for pattern, category in rules:
        if re.search(pattern, stem, re.IGNORECASE):
            return category
    return "misc"


def title_of(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else path.stem


def move_flat_pages() -> None:
    for path in sorted(WIKI.glob("*.md")):
        if path.name in SPECIAL:
            continue
        category = classify(path.name)
        destination = WIKI / category / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise SystemExit(f"Destination already exists: {destination}")
        shutil.move(path, destination)


def generate_sidebar() -> None:
    grouped: dict[str, list[Path]] = {}
    for path in sorted(WIKI.rglob("*.md")):
        if path.name in SPECIAL or path.name.startswith("_"):
            continue
        category = path.parent.relative_to(WIKI).as_posix()
        grouped.setdefault(category, []).append(path)

    lines = ["# ページ分類", "", "- [[Home]]", ""]
    for category in sorted(grouped, key=lambda c: (c == "misc", CATEGORY_LABELS.get(c, c))):
        label = CATEGORY_LABELS.get(category, category)
        lines.append(f"## {label}")
        lines.append("")
        for path in sorted(grouped[category], key=lambda p: title_of(p).casefold()):
            title = title_of(path)
            lines.append(f"- [[{title}]]")
        lines.append("")

    (WIKI / "_Sidebar.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    move_flat_pages()
    generate_sidebar()


if __name__ == "__main__":
    main()
