#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CATALOG_PATH = Path(__file__).resolve().parents[1] / "references" / "preset-catalog.json"
OKLAB_HINTS = {
    "background",
    "hero",
    "editorial",
    "atmospheric",
    "cinematic",
    "mesh",
    "moody",
    "luxury",
    "multi",
    "multi-stop",
    "背景",
    "电影感",
    "氛围",
    "层次",
    "高级",
    "暗色",
    "多段",
    "多色",
}
OKLCH_HINTS = {
    "accent",
    "badge",
    "button",
    "clean",
    "neon",
    "pop",
    "simple",
    "two-stop",
    "vivid",
    "ui",
    "按钮",
    "高饱和",
    "霓虹",
    "双色",
    "简洁",
    "明亮",
}
FAMILY_TAG_HINTS = {
    "red-yellow": {"warm", "pop", "playful", "beauty"},
    "blue-purple": {"cool", "cyber", "calm", "editorial"},
    "green-yellow": {"fresh", "calm", "playful", "soft-pop"},
    "contrast": {"contrast", "neon", "bold", "pop"},
    "dark": {"dark", "premium", "quiet", "editorial"},
    "light": {"light", "pastel", "soft", "beauty", "fresh"},
}


def normalize(text: str) -> str:
    lowered = text.lower().replace("_", " ").replace("-", " ")
    cleaned = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", " ", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()


def tokenize(text: str) -> list[str]:
    normalized = normalize(text)
    return [token for token in normalized.split(" ") if token]


def format_percent(position: float) -> str:
    value = round(position * 100, 1)
    if value.is_integer():
        return f"{int(value)}%"
    return f"{value:.1f}%"


def gradient_css(preset: dict, direction: str, include_space: bool = True) -> str:
    stops = ", ".join(
        f"{stop['color']} {format_percent(stop['position'])}"
        for stop in sorted(preset["stops"], key=lambda item: item["position"])
    )
    if include_space:
        return f"background: linear-gradient({direction} in {preset['mode']}, {stops});"
    return f"background: linear-gradient({direction}, {stops});"


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def build_family_index(catalog: dict) -> dict[str, str]:
    index: dict[str, str] = {}
    for family in catalog["families"]:
        terms = {family["id"], family["label"], family["cn_label"], family["source_name"]}
        terms.update(family.get("aliases", []))
        for term in terms:
            normalized = normalize(str(term))
            if normalized:
                index[normalized] = family["id"]
    return index


def resolve_family(explicit_family: str, query: str, family_index: dict[str, str]) -> str | None:
    for source in [explicit_family, query]:
        normalized_source = normalize(source)
        if not normalized_source:
            continue
        for term, family_id in family_index.items():
            if term and term in normalized_source:
                return family_id
    return None


def infer_mode_order(query: str, requested_mode: str, matched_family: str | None) -> list[str]:
    if requested_mode in {"oklch", "oklab"}:
        return [requested_mode, "oklab" if requested_mode == "oklch" else "oklch"]

    normalized_query = normalize(query)
    if "oklch" in normalized_query:
        return ["oklch", "oklab"]
    if "oklab" in normalized_query:
        return ["oklab", "oklch"]

    oklab_score = 2 if matched_family else 0
    oklch_score = 3

    for hint in OKLAB_HINTS:
        if normalize(hint) in normalized_query:
            oklab_score += 2
    for hint in OKLCH_HINTS:
        if normalize(hint) in normalized_query:
            oklch_score += 2

    if oklab_score > oklch_score:
        return ["oklab", "oklch"]
    return ["oklch", "oklab"]


def preset_search_text(preset: dict) -> str:
    parts = [
        preset["id"],
        preset["name"],
        preset.get("family_id", ""),
        preset.get("family_label", ""),
        preset.get("summary", ""),
        " ".join(preset.get("aliases", [])),
        " ".join(preset.get("tags", [])),
    ]
    return normalize(" ".join(parts))


def preset_matches_filter(preset: dict, preset_filter: str) -> bool:
    if not preset_filter:
        return True
    needle = normalize(preset_filter)
    haystack = preset_search_text(preset)
    return needle in haystack


def score_preset(
    preset: dict,
    query_tokens: list[str],
    matched_family: str | None,
    mode_order: list[str],
) -> int:
    score = 0
    haystack = preset_search_text(preset)

    for index, mode in enumerate(mode_order):
        if preset["mode"] == mode:
            score += 16 - index * 6

    if matched_family:
        if preset.get("family_id") == matched_family:
            score += 40
        elif preset["mode"] == "oklch":
            score += 4
            for tag in preset.get("tags", []):
                if tag in FAMILY_TAG_HINTS.get(matched_family, set()):
                    score += 4

    for token in query_tokens:
        if token and token in haystack:
            score += 6 if token in normalize(preset["name"]) else 3

    if not query_tokens and preset["mode"] == mode_order[0]:
        score += 2

    return score


def render_text(results: list[dict], matched_family: str | None, mode_order: list[str], direction: str) -> str:
    lines = [
        f"mode_order: {' -> '.join(mode_order)}",
        f"matched_family: {matched_family or 'none'}",
        "",
    ]
    for index, preset in enumerate(results, start=1):
        lines.extend(
            [
                f"{index}. {preset['name']}",
                f"   id: {preset['id']}",
                f"   mode: {preset['mode']}",
                f"   family: {preset.get('family_id', 'n/a')}",
                f"   summary: {preset.get('summary', '')}",
                f"   css: {gradient_css(preset, direction, include_space=True)}",
                f"   fallback: {gradient_css(preset, direction, include_space=False)}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def render_css(results: list[dict], direction: str) -> str:
    chunks = []
    for preset in results:
        chunks.append(f"/* {preset['name']} [{preset['id']}] */")
        chunks.append(gradient_css(preset, direction, include_space=True))
        chunks.append(gradient_css(preset, direction, include_space=False))
        chunks.append("")
    return "\n".join(chunks).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rank wrap-gradient-derived presets by query, family, and interpolation mode."
    )
    parser.add_argument("--query", default="", help="Free-text request such as '蓝紫 科技感 hero 背景'")
    parser.add_argument("--family", default="", help="Optional family override such as red-yellow or blue-purple")
    parser.add_argument("--preset", default="", help="Optional preset id or name filter")
    parser.add_argument("--mode", choices=["auto", "oklch", "oklab"], default="auto")
    parser.add_argument("--format", choices=["text", "css", "json"], default="text")
    parser.add_argument("--direction", default="135deg", help="Gradient direction for generated CSS")
    parser.add_argument("--limit", type=int, default=3, help="Number of results to return")
    args = parser.parse_args()

    catalog = load_catalog()
    family_index = build_family_index(catalog)
    matched_family = resolve_family(args.family, args.query, family_index)
    mode_order = infer_mode_order(args.query, args.mode, matched_family)
    query_tokens = tokenize(args.query)

    candidates = [
        preset
        for preset in catalog["presets"]
        if preset_matches_filter(preset, args.preset)
        and (args.mode == "auto" or preset["mode"] == args.mode)
    ]

    ranked = sorted(
        candidates,
        key=lambda preset: (
            score_preset(preset, query_tokens, matched_family, mode_order),
            -len(preset["stops"]),
            preset["name"],
        ),
        reverse=True,
    )[: max(1, args.limit)]

    if args.format == "json":
        payload = {
            "mode_order": mode_order,
            "matched_family": matched_family,
            "results": ranked,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.format == "css":
        print(render_css(ranked, args.direction))
        return 0

    print(render_text(ranked, matched_family, mode_order, args.direction))
    return 0


if __name__ == "__main__":
    sys.exit(main())
