#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Iterable


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
HUE_TARGETS = {
    "red": 28.0,
    "red-yellow": 45.0,
    "orange": 55.0,
    "yellow": 95.0,
    "green": 145.0,
    "mint": 165.0,
    "cyan": 205.0,
    "blue": 260.0,
    "purple": 305.0,
    "pink": 350.0,
    "红": 28.0,
    "橙": 55.0,
    "黄": 95.0,
    "绿": 145.0,
    "蓝": 260.0,
    "紫": 305.0,
    "粉": 350.0,
}
DIRECT_FAMILY_HINTS = {
    "red": "red-yellow",
    "orange": "red-yellow",
    "yellow": "red-yellow",
    "warm": "red-yellow",
    "红": "red-yellow",
    "红色": "red-yellow",
    "橙": "red-yellow",
    "黄色": "red-yellow",
    "暖": "red-yellow",
    "blue": "blue-purple",
    "purple": "blue-purple",
    "indigo": "blue-purple",
    "蓝": "blue-purple",
    "蓝色": "blue-purple",
    "紫": "blue-purple",
    "紫色": "blue-purple",
    "green": "green-yellow",
    "mint": "green-yellow",
    "fresh": "green-yellow",
    "绿": "green-yellow",
    "绿色": "green-yellow",
    "青": "green-yellow",
    "清爽": "green-yellow",
    "梦幻": "blue-purple",
    "科技": "blue-purple",
    "夜空": "blue-purple",
    "复古": "dark",
    "胶片": "dark",
    "暗调": "dark",
    "高级": "dark",
    "空气": "light",
    "空气感": "light",
    "护肤": "light",
}
PRESET_CUE_BOOSTS = {
    "梦幻": {
        "dream-haze": 24,
        "twilight-sky": 10,
        "stellar": 8,
    },
    "dreamy": {
        "dream-haze": 24,
        "twilight-sky": 10,
        "stellar": 8,
    },
    "清爽": {
        "mint-sugar": 18,
        "spring-days": 14,
        "lakeside-glow": 10,
        "tranquil-bay": 8,
    },
    "fresh": {
        "mint-sugar": 18,
        "spring-days": 14,
        "lakeside-glow": 10,
    },
    "红色": {
        "warm-glow": 16,
        "sunset-glow": 14,
        "dyed-horizon": 12,
        "peach-aura": 8,
    },
    "红色系": {
        "warm-glow": 18,
        "sunset-glow": 14,
        "dyed-horizon": 12,
        "peach-aura": 8,
    },
    "复古": {
        "phantom": 14,
        "fading-night": 12,
        "jungle": 10,
    },
}
CURVES = {
    "linear": ((0.0, 0.0), (1.0, 1.0)),
    "smooth": ((0.4, 0.0), (0.2, 1.0)),
    "ease-in": ((0.42, 0.0), (1.0, 1.0)),
    "ease-out": ((0.0, 0.0), (0.58, 1.0)),
    "ease-in-out": ((0.42, 0.0), (0.58, 1.0)),
    # "Top" assumes a CSS gradient such as "to top", where position 1 is the top.
    "top-empty": ((0.16, 0.82), (0.44, 1.0)),
    "top-active": ((0.56, 0.0), (1.0, 0.18)),
    "bottom-empty": ((0.56, 0.0), (0.84, 0.18)),
    "bottom-active": ((0.16, 0.82), (0.44, 1.0)),
}


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def normalize(text: str) -> str:
    lowered = text.lower().replace("_", " ").replace("-", " ")
    cleaned = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", " ", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()


def tokenize(text: str) -> list[str]:
    return [token for token in normalize(text).split(" ") if token]


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def expand_hex(value: str) -> str:
    value = value.strip()
    if not value.startswith("#"):
        value = "#" + value
    raw = value[1:]
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) == 4:
        raw = "".join(ch * 2 for ch in raw[:3])
    if len(raw) >= 6:
        raw = raw[:6]
    if not re.fullmatch(r"[0-9a-fA-F]{6}", raw):
        raise ValueError(f"Invalid hex color: {value}")
    return "#" + raw.upper()


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    raw = expand_hex(hex_color)[1:]
    return (
        int(raw[0:2], 16) / 255.0,
        int(raw[2:4], 16) / 255.0,
        int(raw[4:6], 16) / 255.0,
    )


def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#%02X%02X%02X" % (
        round(clamp(r) * 255),
        round(clamp(g) * 255),
        round(clamp(b) * 255),
    )


def srgb_transfer(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def srgb_transfer_inv(v: float) -> float:
    return 12.92 * v if v <= 0.0031308 else 1.055 * (max(v, 0.0) ** (1.0 / 2.4)) - 0.055


def rgb_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    lr = srgb_transfer(r)
    lg = srgb_transfer(g)
    lb = srgb_transfer(b)
    l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
    m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
    s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb
    l_ = math.copysign(abs(l) ** (1.0 / 3.0), l)
    m_ = math.copysign(abs(m) ** (1.0 / 3.0), m)
    s_ = math.copysign(abs(s) ** (1.0 / 3.0), s)
    return (
        0.2104542553 * l_ + 0.793617785 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.428592205 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.808675766 * s_,
    )


def oklab_to_rgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.291485548 * b
    l = l_ * l_ * l_
    m = m_ * m_ * m_
    s = s_ * s_ * s_
    return (
        srgb_transfer_inv(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
        srgb_transfer_inv(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
        srgb_transfer_inv(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
    )


def oklab_to_oklch(L: float, a: float, b: float) -> tuple[float, float, float]:
    C = math.sqrt(a * a + b * b)
    h = math.degrees(math.atan2(b, a))
    if h < 0:
        h += 360.0
    return L, C, h


def oklch_to_oklab(L: float, C: float, h: float) -> tuple[float, float, float]:
    h_rad = math.radians(h)
    return L, C * math.cos(h_rad), C * math.sin(h_rad)


def hex_to_oklch(hex_color: str) -> tuple[float, float, float]:
    return oklab_to_oklch(*rgb_to_oklab(*hex_to_rgb(hex_color)))


def oklch_to_hex(L: float, C: float, h: float) -> str:
    r, g, b = oklab_to_rgb(*oklch_to_oklab(clamp(L), max(0.0, C), h % 360.0))
    return rgb_to_hex(r, g, b)


def in_srgb(rgb: tuple[float, float, float]) -> bool:
    return all(-0.00001 <= channel <= 1.00001 for channel in rgb)


def clip_oklch_to_hex(L: float, C: float, h: float) -> str:
    L = clamp(L)
    C = max(0.0, C)
    h = h % 360.0
    rgb = oklab_to_rgb(*oklch_to_oklab(L, C, h))
    if in_srgb(rgb):
        return rgb_to_hex(*rgb)
    low = 0.0
    high = C
    for _ in range(24):
        mid = (low + high) / 2.0
        rgb = oklab_to_rgb(*oklch_to_oklab(L, mid, h))
        if in_srgb(rgb):
            low = mid
        else:
            high = mid
    return oklch_to_hex(L, low, h)


def shortest_hue_delta(start: float, end: float) -> float:
    delta = (end - start + 540.0) % 360.0 - 180.0
    return delta


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def interpolate_rgb(color_a: str, color_b: str, t: float) -> str:
    a = hex_to_rgb(color_a)
    b = hex_to_rgb(color_b)
    return rgb_to_hex(*(lerp(a[i], b[i], t) for i in range(3)))


def interpolate_oklab(color_a: str, color_b: str, t: float) -> str:
    a = rgb_to_oklab(*hex_to_rgb(color_a))
    b = rgb_to_oklab(*hex_to_rgb(color_b))
    return rgb_to_hex(*oklab_to_rgb(*(lerp(a[i], b[i], t) for i in range(3))))


def interpolate_oklch(color_a: str, color_b: str, t: float) -> str:
    L1, C1, h1 = hex_to_oklch(color_a)
    L2, C2, h2 = hex_to_oklch(color_b)
    if C1 < 0.0001:
        h1 = h2
    if C2 < 0.0001:
        h2 = h1
    return clip_oklch_to_hex(
        lerp(L1, L2, t),
        lerp(C1, C2, t),
        h1 + shortest_hue_delta(h1, h2) * t,
    )


def interpolate_color(color_a: str, color_b: str, t: float, mode: str) -> str:
    if mode == "oklch":
        return interpolate_oklch(color_a, color_b, t)
    if mode == "oklab":
        return interpolate_oklab(color_a, color_b, t)
    return interpolate_rgb(color_a, color_b, t)


def format_percent(position: float) -> str:
    value = round(position * 100, 2)
    if float(value).is_integer():
        return f"{int(value)}%"
    return f"{value:.2f}".rstrip("0").rstrip(".") + "%"


def sorted_stops(stops: Iterable[dict]) -> list[dict]:
    return sorted(
        [{"color": expand_hex(stop["color"]), "position": clamp(float(stop["position"]))} for stop in stops],
        key=lambda item: item["position"],
    )


def rgba_to_hex(value: str) -> str:
    numbers = [float(part.strip().rstrip("%")) for part in re.split(r"\s*,\s*", value[value.find("(") + 1 : value.rfind(")")])[:3]]
    if len(numbers) < 3:
        raise ValueError(f"Invalid rgb color: {value}")
    if any(number > 1.0 for number in numbers):
        numbers = [number / 255.0 for number in numbers]
    return rgb_to_hex(numbers[0], numbers[1], numbers[2])


def parse_stops(text: str) -> list[dict]:
    token_re = re.compile(r"(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))\s*([0-9.]+%?)?", re.I)
    matches = list(token_re.finditer(text))
    if len(matches) < 2:
        raise ValueError("Expected at least two color stops in CSS, rgb(), or hex-list form.")
    raw_stops = []
    for index, match in enumerate(matches):
        color = match.group(1)
        if color.lower().startswith("rgb"):
            color = rgba_to_hex(color)
        else:
            color = expand_hex(color)
        raw_pos = match.group(2)
        if raw_pos:
            position = float(raw_pos.rstrip("%")) / (100.0 if raw_pos.endswith("%") else 1.0)
        else:
            position = index / max(1, len(matches) - 1)
        raw_stops.append({"color": color, "position": clamp(position)})
    return sorted_stops(raw_stops)


def color_at(stops: list[dict], position: float, mode: str) -> str:
    stops = sorted_stops(stops)
    position = clamp(position)
    if position <= stops[0]["position"]:
        return stops[0]["color"]
    if position >= stops[-1]["position"]:
        return stops[-1]["color"]
    for left, right in zip(stops, stops[1:]):
        if left["position"] <= position <= right["position"]:
            span = right["position"] - left["position"]
            local = 0.0 if span == 0 else (position - left["position"]) / span
            return interpolate_color(left["color"], right["color"], local, mode)
    return stops[-1]["color"]


def sample_curve_x(t: float, p1x: float, p2x: float) -> float:
    return 3 * (1 - t) ** 2 * t * p1x + 3 * (1 - t) * t**2 * p2x + t**3


def sample_curve_y(t: float, p1y: float, p2y: float) -> float:
    return 3 * (1 - t) ** 2 * t * p1y + 3 * (1 - t) * t**2 * p2y + t**3


def sample_curve_derivative_x(t: float, p1x: float, p2x: float) -> float:
    return 3 * (1 - t) ** 2 * p1x + 6 * (1 - t) * t * (p2x - p1x) + 3 * t**2 * (1 - p2x)


def sample_curve_derivative_y(t: float, p1y: float, p2y: float) -> float:
    return 3 * (1 - t) ** 2 * p1y + 6 * (1 - t) * t * (p2y - p1y) + 3 * t**2 * (1 - p2y)


def solve_cubic_bezier(x: float, p1: tuple[float, float], p2: tuple[float, float]) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    t = x
    for _ in range(8):
        x_est = sample_curve_x(t, p1[0], p2[0])
        if abs(x_est - x) < 1e-6:
            return sample_curve_y(t, p1[1], p2[1])
        dx = sample_curve_derivative_x(t, p1[0], p2[0])
        if abs(dx) < 1e-6:
            break
        t -= (x_est - x) / dx
    low = 0.0
    high = 1.0
    t = x
    for _ in range(24):
        t = (low + high) / 2.0
        x_est = sample_curve_x(t, p1[0], p2[0])
        if abs(x_est - x) < 1e-6:
            break
        if x_est > x:
            high = t
        else:
            low = t
    return sample_curve_y(t, p1[1], p2[1])


def curve_derivative_magnitude(x: float, p1: tuple[float, float], p2: tuple[float, float]) -> float:
    if x <= 0 or x >= 1:
        return 1.0
    t = x
    for _ in range(8):
        x_est = sample_curve_x(t, p1[0], p2[0])
        if abs(x_est - x) < 1e-6:
            break
        dx = sample_curve_derivative_x(t, p1[0], p2[0])
        if abs(dx) < 1e-6:
            break
        t -= (x_est - x) / dx
    dx = sample_curve_derivative_x(t, p1[0], p2[0])
    dy = sample_curve_derivative_y(t, p1[1], p2[1])
    return math.sqrt(dx * dx + dy * dy)


def adaptive_positions(count: int, p1: tuple[float, float], p2: tuple[float, float]) -> list[float]:
    count = max(2, count)
    uniform = 100
    magnitudes = [curve_derivative_magnitude(i / uniform, p1, p2) for i in range(uniform + 1)]
    total = sum(magnitudes)
    target = total / count
    positions = [0.0]
    acc = 0.0
    for index in range(uniform):
        acc += magnitudes[index]
        while acc >= target and len(positions) < count:
            start = index / uniform
            end = (index + 1) / uniform
            ratio = 1 - ((acc - target) / max(magnitudes[index], 1e-9))
            positions.append(clamp(start + ratio * (end - start)))
            acc -= target
    if positions[-1] != 1.0:
        positions.append(1.0)
    return positions[: count - 1] + [1.0] if len(positions) > count else positions


def parse_curve(name: str, custom: str | None) -> tuple[tuple[float, float], tuple[float, float]]:
    if custom:
        values = [float(part.strip()) for part in custom.split(",")]
        if len(values) != 4:
            raise ValueError("--custom-curve expects x1,y1,x2,y2")
        return (clamp(values[0]), clamp(values[1])), (clamp(values[2]), clamp(values[3]))
    if name not in CURVES:
        raise ValueError(f"Unknown curve '{name}'. Use one of: {', '.join(sorted(CURVES))}")
    return CURVES[name]


def warp_stops(stops: list[dict], mode: str, curve: str, samples: int, custom_curve: str | None = None) -> list[dict]:
    p1, p2 = parse_curve(curve, custom_curve)
    result = []
    for x in adaptive_positions(samples, p1, p2):
        y = solve_cubic_bezier(x, p1, p2)
        result.append({"color": color_at(stops, y, mode), "position": x})
    return sorted_stops(result)


def increase_chroma(stops: list[dict], factor: float, delta: float) -> list[dict]:
    result = []
    for stop in sorted_stops(stops):
        L, C, h = hex_to_oklch(stop["color"])
        result.append(
            {
                "position": stop["position"],
                "color": clip_oklch_to_hex(L, C * factor + delta, h),
            }
        )
    return result


def average_image_color(path: str) -> str:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Image target requires Pillow. Install with: python3 -m pip install --user pillow") from exc
    with Image.open(path) as image:
        image = image.convert("RGB").resize((1, 1))
        r, g, b = image.getpixel((0, 0))
    return rgb_to_hex(r / 255.0, g / 255.0, b / 255.0)


def shift_stops(stops: list[dict], target_color: str | None, target_hue: str | None, reference: float, mode: str) -> list[dict]:
    mid = color_at(stops, reference, mode)
    mid_L, mid_C, mid_h = hex_to_oklch(mid)
    if target_hue:
        if normalize(target_hue) not in HUE_TARGETS:
            raise ValueError(f"Unknown target hue '{target_hue}'. Use red, green, blue, purple, or a target color.")
        target_L, target_C, target_h = mid_L, mid_C, HUE_TARGETS[normalize(target_hue)]
    elif target_color:
        target_L, target_C, target_h = hex_to_oklch(target_color)
    else:
        return stops
    dL = target_L - mid_L if target_color else 0.0
    dC = target_C - mid_C if target_color else 0.0
    dh = shortest_hue_delta(mid_h, target_h)
    shifted = []
    for stop in sorted_stops(stops):
        L, C, h = hex_to_oklch(stop["color"])
        shifted.append(
            {
                "position": stop["position"],
                "color": clip_oklch_to_hex(L + dL, C + dC, h + dh),
            }
        )
    return shifted


def gradient_css(stops: list[dict], direction: str, include_space: str | None = None, property_name: str = "background") -> str:
    space = f" in {include_space}" if include_space else ""
    stop_text = ", ".join(f"{stop['color']} {format_percent(stop['position'])}" for stop in sorted_stops(stops))
    return f"{property_name}: linear-gradient({direction}{space}, {stop_text});"


def scope_css(stops: list[dict], direction: str, scope: str, include_space: str | None = None) -> str:
    base = gradient_css(stops, direction, include_space)
    if scope == "text":
        return "\n".join(
            [
                base,
                "-webkit-background-clip: text;",
                "background-clip: text;",
                "color: transparent;",
                "-webkit-text-fill-color: transparent;",
            ]
        )
    if scope == "border":
        gradient = gradient_css(stops, direction, include_space).removeprefix("background: ")
        return "\n".join(
            [
                f"background: linear-gradient(Canvas, Canvas) padding-box, {gradient.removesuffix(';')} border-box;",
                "border: 1px solid transparent;",
            ]
        )
    return base


def hex_to_figma_rgb(hex_color: str) -> tuple[float, float, float]:
    return hex_to_rgb(hex_color)


def export_ios(stops: list[dict]) -> str:
    lines = [
        "import SwiftUI",
        "",
        "let gradient = LinearGradient(",
        "    gradient: Gradient(stops: [",
    ]
    for stop in sorted_stops(stops):
        r, g, b = hex_to_rgb(stop["color"])
        lines.append(
            f"        .init(color: Color(red: {r:.4f}, green: {g:.4f}, blue: {b:.4f}), location: {stop['position']:.4f}),"
        )
    lines.extend(["    ]),", "    startPoint: .topLeading,", "    endPoint: .bottomTrailing", ")"])
    return "\n".join(lines)


def export_android(stops: list[dict]) -> str:
    lines = ["val gradientBrush = Brush.linearGradient(", "    colorStops = arrayOf("]
    for stop in sorted_stops(stops):
        lines.append(f"        {stop['position']:.4f}f to Color(0xFF{expand_hex(stop['color'])[1:]}),")
    lines.extend(["    )", ")"])
    return "\n".join(lines)


def export_figma(stops: list[dict]) -> str:
    lines = [
        "const gradient = {",
        "  type: 'GRADIENT_LINEAR',",
        "  gradientTransform: [[1, 0, 0], [0, 1, 0]],",
        "  gradientStops: [",
    ]
    for stop in sorted_stops(stops):
        r, g, b = hex_to_figma_rgb(stop["color"])
        lines.append(
            f"    {{ position: {stop['position']:.4f}, color: {{ r: {r:.4f}, g: {g:.4f}, b: {b:.4f}, a: 1 }} }},"
        )
    lines.extend(
        [
            "  ]",
            "};",
            "",
            "for (const node of figma.currentPage.selection) {",
            "  if ('fills' in node) node.fills = [gradient];",
            "}",
        ]
    )
    return "\n".join(lines)


def export_payload(stops: list[dict], fmt: str, direction: str, scope: str, mode_hint: str | None = None) -> str:
    if fmt == "json":
        return json.dumps({"stops": sorted_stops(stops)}, ensure_ascii=False, indent=2)
    if fmt == "ios":
        return export_ios(stops)
    if fmt == "android":
        return export_android(stops)
    if fmt == "figma":
        return export_figma(stops)
    if fmt == "all":
        return "\n\n".join(
            [
                "/* CSS */\n" + scope_css(stops, direction, scope, None),
                "/* iOS SwiftUI */\n" + export_ios(stops),
                "/* Android Compose */\n" + export_android(stops),
                "/* Figma Plugin API */\n" + export_figma(stops),
            ]
        )
    return scope_css(stops, direction, scope, mode_hint)


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
        for cue, family_id in DIRECT_FAMILY_HINTS.items():
            if normalize(cue) in normalized_source:
                return family_id
        for term, family_id in family_index.items():
            if term and term in normalized_source:
                return family_id
    return None


def infer_mode_order(query: str, requested_mode: str, matched_family: str | None) -> list[str]:
    if requested_mode in {"oklch", "oklab", "rgb"}:
        return [requested_mode] + [mode for mode in ["oklch", "oklab", "rgb"] if mode != requested_mode]
    normalized_query = normalize(query)
    if "oklch" in normalized_query:
        return ["oklch", "oklab", "rgb"]
    if "oklab" in normalized_query:
        return ["oklab", "oklch", "rgb"]
    oklab_score = 2 if matched_family else 0
    oklch_score = 3
    for hint in OKLAB_HINTS:
        if normalize(hint) in normalized_query:
            oklab_score += 2
    for hint in OKLCH_HINTS:
        if normalize(hint) in normalized_query:
            oklch_score += 2
    return ["oklab", "oklch", "rgb"] if oklab_score > oklch_score else ["oklch", "oklab", "rgb"]


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


def score_preset(preset: dict, query_tokens: list[str], matched_family: str | None, mode_order: list[str]) -> int:
    score = 0
    haystack = preset_search_text(preset)
    normalized_query = normalize(" ".join(query_tokens))
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
    for cue, boosts in PRESET_CUE_BOOSTS.items():
        if normalize(cue) in normalized_query:
            for preset_fragment, boost in boosts.items():
                if normalize(preset_fragment) in haystack:
                    score += boost
    return score


def find_presets(query: str, family: str, preset_filter: str, mode: str, limit: int) -> dict:
    catalog = load_catalog()
    matched_family = resolve_family(family, query, build_family_index(catalog))
    mode_order = infer_mode_order(query, mode, matched_family)
    needle = normalize(preset_filter)
    candidates = [
        preset
        for preset in catalog["presets"]
        if (not needle or needle in preset_search_text(preset)) and (mode == "auto" or preset["mode"] == mode)
    ]
    ranked = sorted(
        candidates,
        key=lambda preset: (score_preset(preset, tokenize(query), matched_family, mode_order), len(preset["stops"]), preset["name"]),
        reverse=True,
    )[: max(1, limit)]
    return {"mode_order": mode_order, "matched_family": matched_family, "results": ranked}


def source_stops(args: argparse.Namespace) -> tuple[list[dict], str]:
    if args.gradient:
        return parse_stops(args.gradient), args.mode if args.mode != "auto" else "oklch"
    payload = find_presets(args.query, args.family, args.preset, args.mode, 1)
    if not payload["results"]:
        raise ValueError("No preset matched the request.")
    preset = payload["results"][0]
    mode = args.mode if args.mode != "auto" else preset["mode"]
    return sorted_stops(preset["stops"]), mode


def command_find(args: argparse.Namespace) -> int:
    payload = find_presets(args.query, args.family, args.preset, args.mode, args.limit)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    for index, preset in enumerate(payload["results"], start=1):
        print(f"{index}. {preset['name']}")
        print(f"   id: {preset['id']}")
        print(f"   mode: {preset['mode']}")
        print(f"   family: {preset.get('family_id', 'n/a')}")
        print(f"   summary: {preset.get('summary', '')}")
        print(f"   css: {gradient_css(preset['stops'], args.direction, preset['mode'])}")
        print(f"   fallback: {gradient_css(preset['stops'], args.direction)}")
        print()
    return 0


def command_transform(args: argparse.Namespace) -> int:
    stops, source_mode = source_stops(args)
    mode = "oklch" if args.oklch_segments else source_mode
    if args.shift_image:
        args.shift_color = average_image_color(args.shift_image)
    if args.shift_color or args.shift_hue:
        stops = shift_stops(stops, expand_hex(args.shift_color) if args.shift_color else None, args.shift_hue, args.reference, mode)
    if args.vivid:
        stops = increase_chroma(stops, args.chroma_factor, args.chroma_delta)
    should_segment = args.oklch_segments or args.vivid or args.shift_color or args.shift_hue or args.shift_image or args.curve != "linear" or args.custom_curve
    if should_segment:
        stops = warp_stops(stops, "oklch" if args.oklch_segments or args.vivid or args.shift_color or args.shift_hue else mode, args.curve, args.samples, args.custom_curve)
    mode_hint = "oklch" if args.format == "css" and args.keep_color_space_hint else None
    print(export_payload(stops, args.format, args.direction, args.scope, mode_hint))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Select, warp, recolor, segment, and export wrap-gradient presets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    find = subparsers.add_parser("find", help="Rank presets by semantic query, family, and mode.")
    find.add_argument("--query", default="")
    find.add_argument("--family", default="")
    find.add_argument("--preset", default="")
    find.add_argument("--mode", choices=["auto", "oklch", "oklab", "rgb"], default="auto")
    find.add_argument("--direction", default="135deg")
    find.add_argument("--limit", type=int, default=3)
    find.add_argument("--format", choices=["text", "json"], default="text")
    find.set_defaults(func=command_find)

    transform = subparsers.add_parser("transform", help="Transform a preset or supplied gradient.")
    transform.add_argument("--query", default="")
    transform.add_argument("--family", default="")
    transform.add_argument("--preset", default="")
    transform.add_argument("--gradient", default="", help="CSS gradient, hex list, or rgb() list.")
    transform.add_argument("--mode", choices=["auto", "oklch", "oklab", "rgb"], default="auto")
    transform.add_argument("--direction", default="135deg")
    transform.add_argument("--scope", choices=["background", "text", "border"], default="background")
    transform.add_argument("--format", choices=["css", "json", "ios", "android", "figma", "all"], default="css")
    transform.add_argument("--samples", type=int, default=12)
    transform.add_argument("--curve", choices=sorted(CURVES.keys()), default="linear")
    transform.add_argument("--custom-curve", default="", help="x1,y1,x2,y2 cubic-bezier control points.")
    transform.add_argument("--oklch-segments", action="store_true")
    transform.add_argument("--vivid", action="store_true")
    transform.add_argument("--chroma-factor", type=float, default=1.18)
    transform.add_argument("--chroma-delta", type=float, default=0.015)
    transform.add_argument("--shift-color", default="")
    transform.add_argument("--shift-image", default="")
    transform.add_argument("--shift-hue", default="")
    transform.add_argument("--reference", type=float, default=0.5)
    transform.add_argument("--keep-color-space-hint", action="store_true")
    transform.set_defaults(func=command_transform)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
