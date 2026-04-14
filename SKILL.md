---
name: better-gradient
description: Design and suggest offline gradient presets from a bundled catalog, prioritizing hue-family matching before inventing new ramps and defaulting to OKLCH or OKLAB interpolation. Use when Codex needs to create or refine 渐变, gradient backgrounds, hero color ramps, brand color directions, CSS or SVG gradient code, or palette suggestions based on 色系, 氛围, 蓝紫, 青绿, 暖色, 撞色, 暗色, 浅色, or other modern color-family cues.
---

# Better Gradient

## Overview

Use the bundled offline preset pack to pick a close gradient before creating one from scratch.
Match by hue family first, then choose interpolation mode: default to `oklch` for short vivid ramps, and switch to `oklab` for multi-stop atmospheric gradients when a structured family preset is the best match.

## Default Rules

- Resolve the user's direction by color family or mood before editing individual stops.
- Prefer the named OKLAB families when the user clearly asks for a hue family such as warm sunset, blue-purple tech, green spring, contrast, dark, or light.
- Prefer the OKLCH pair presets when the user wants a cleaner two-stop ramp, neon pop, high chroma accents, or simple UI gradients.
- Keep the original stop positions unless the user explicitly asks to re-time the ramp.
- If the closest preset is not exact, tweak the nearest preset instead of inventing unrelated colors.
- Preserve the user's requested angle and output format. If they do not specify an angle, use `135deg`.

## Workflow

1. Resolve the direction.
Map the request to a family or mood using `references/family-guide.md`. Start with the explicit hue words if present. If the user only gives mood words like "科技感" or "空气感", use the guide's aliases.

2. Query the bundled catalog.
Run `python3 scripts/find_presets.py` from the skill directory to rank presets and emit CSS.

Common commands:

```bash
python3 scripts/find_presets.py --query "蓝紫 科技感 hero 背景" --limit 3
python3 scripts/find_presets.py --family green-yellow --mode oklab --limit 3
python3 scripts/find_presets.py --query "美妆 空气感 浅色" --mode oklch --format css
python3 scripts/find_presets.py --preset dream-haze --format css
```

3. Choose interpolation mode.
Use `oklch` for vivid, clean, two-stop, neon, or accent gradients.
Use `oklab` for multi-stop, cinematic, editorial, atmospheric, or family-driven gradients.
If the user asks for one mode explicitly, honor it.

4. Deliver the result.
Return the chosen preset name, why it matches the request, and the gradient code.
If browser compatibility matters, also add a fallback gradient without `in oklch` or `in oklab`.

## Output Rules

- Default CSS format for an OKLCH result:
  `background: linear-gradient(135deg in oklch, #66FFF5 0%, #FF1A75 100%);`
- Default CSS format for an OKLAB result:
  `background: linear-gradient(135deg in oklab, #EBD5EB 0%, #A1BEE8 47.1%, #807BCA 100%);`
- When the user wants SVG, translate the same stop list into `<linearGradient>` and preserve the stop percentages.
- When the user provides brand colors, bias toward the nearest family and only adjust the endpoints or one middle stop.
- When the user is vague, present two or three candidate directions from different families instead of pretending there is only one correct answer.

## Resources

- `scripts/find_presets.py`
Use this to rank presets by free-text query, family, or explicit preset id and to emit CSS or JSON.

- `references/family-guide.md`
Read this first when the request is about mood, style, or hue family rather than a known preset name.

- `references/preset-catalog.json`
This is the bundled offline preset catalog. Read it when you need the exact stop list or want to inspect the full preset inventory.
