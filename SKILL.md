---
name: better-gradient
description: Select, transform, recolor, segment, and export gradients from a wrap-gradient-derived OKLCH/OKLAB catalog. Use for semantic gradient requests such as 红色系渐变, 梦幻感渐变, 清爽渐变, 复古渐变, text/background gradient CSS, OKLCH segmentation, chroma/vividness changes, curve warping, image or brand-color matching, hue shifts, and iOS/Android/Figma export.
---

# Better Gradient

Use this skill to choose and transform gradients from the bundled wrap-gradient catalog. Prefer catalog matches before inventing new ramps. Use OKLCH for vivid, simple, UI-facing ramps; use OKLAB for multi-stop, atmospheric, family-driven backgrounds.

## Fast Workflow

1. Resolve the user's intent.
   - Hue/family first: red, blue, green, warm, cool, dark, light.
   - Mood second: 梦幻 -> blue-purple or light; 清爽 -> green-yellow or calm cool; 复古 -> warm, dark, muted; 红色系 -> red-yellow.
   - Scope: 文字/text/headline -> text CSS; 背景/hero/page -> background CSS; 描边/border -> border CSS.

2. Search presets before editing.

```bash
python3 scripts/gradient_tool.py find --query "梦幻感 背景" --limit 3
python3 scripts/gradient_tool.py find --query "红色系 文字" --mode oklch --limit 3
python3 scripts/gradient_tool.py find --family green-yellow --limit 3
```

3. Transform only what the user asks to change.

```bash
# Use OKLCH interpolation but emit plain segmented CSS for compatibility.
python3 scripts/gradient_tool.py transform --preset dream-haze --oklch-segments --samples 12

# Apply to text automatically.
python3 scripts/gradient_tool.py transform --query "红色系 渐变 文字" --scope text --oklch-segments

# Make the top quieter / more empty.
python3 scripts/gradient_tool.py transform --preset dream-haze --curve top-empty --samples 14

# Make the top change more.
python3 scripts/gradient_tool.py transform --preset dream-haze --curve top-active --samples 14

# Make an existing CSS/RGB gradient more vivid in OKLCH.
python3 scripts/gradient_tool.py transform --gradient "linear-gradient(90deg, rgb(230,120,90), #7755DD)" --vivid --samples 12

# Shift the whole ramp toward a brand color using the midpoint as reference.
python3 scripts/gradient_tool.py transform --preset dream-haze --shift-color "#3B82F6" --samples 12

# Shift the whole ramp hue toward blue/green/red, preserving relative hue relationships.
python3 scripts/gradient_tool.py transform --preset sunset-glow --shift-hue blue --samples 12

# Export to platforms.
python3 scripts/gradient_tool.py transform --preset dream-haze --format ios
python3 scripts/gradient_tool.py transform --preset dream-haze --format android
python3 scripts/gradient_tool.py transform --preset dream-haze --format figma
python3 scripts/gradient_tool.py transform --preset dream-haze --format all
```

4. Return the chosen preset, the transformation, and final code. If the output uses OKLCH/OKLAB in CSS, include a plain fallback or segmented hex version unless the user explicitly wants only modern CSS.

## Semantic Defaults

- 红色系 / 暖色 / 夕阳 / 复古暖调: start with `red-yellow`.
- 梦幻 / 科技 / 蓝紫 / 夜空: start with `blue-purple`.
- 清爽 / 自然 / 春日 / 薄荷: start with `green-yellow`.
- 复古 / 高级 / 胶片 / 暗调: start with `dark` or a muted `red-yellow` preset.
- 空气感 / 护肤 / 柔和: start with `light`.
- 撞色 / 活力 / 高饱和: start with `contrast` or OKLCH pair presets.

Read `references/family-guide.md` when the user's wording is mood-heavy or ambiguous.

## Curve Rules

Use curve changes to redistribute where the gradient changes, not to recolor it.

- "顶部更空", "上面留白", "顶部更安静": use `--curve top-empty`.
- "上面变化更大", "顶部更丰富": use `--curve top-active`.
- "底部更空": use `--curve bottom-empty`.
- "更自然/柔和": use `--curve smooth`.
- For exact control use `--custom-curve x1,y1,x2,y2`.

The script samples the warped curve into hex stops, so the result is portable to CSS, iOS, Android, and Figma.

## OKLCH Compatibility Rules

When the user says "用 OKLCH 做这个渐变", "OKLCH 版本", or the target platform may not support CSS Color 4, use `--oklch-segments`. This computes the interpolation in OKLCH but emits regular hex stops. Default to 12 samples; raise to 16-20 for large hero backgrounds or visible banding.

When the user says "更鲜艳", "更亮眼", "更高饱和", use `--vivid`. It converts stops to OKLCH, increases chroma, clips back to sRGB, and emits segmented stops. Do not increase chroma equally in RGB.

## Color Shift Rules

When the user provides a color or image and asks a gradient to become that color direction:

- Default reference point is the gradient midpoint (`--reference 0.5`).
- Compute the OKLCH delta from the midpoint color to the target color.
- Apply that delta to every stop, preserving the original gradient's internal contrast and relative hue motion.
- If the user says "更蓝/更绿/更红", use hue-only shifting with `--shift-hue blue|green|red` instead of applying one flat hue to all stops.
- For images, use `--shift-image path/to/image`; this requires Pillow. If Pillow is unavailable, ask for a main hex color or install Pillow.

## Export Rules

- CSS background: default `--format css --scope background`.
- CSS text: `--scope text`.
- iOS: `--format ios` emits SwiftUI `LinearGradient` stops.
- Android: `--format android` emits Kotlin Compose `Brush.linearGradient` with arbitrary stops.
- Figma: `--format figma` emits a Figma Plugin API snippet that applies a linear gradient to selected nodes.
- All platforms: `--format all`.

## Resources

- `scripts/gradient_tool.py`: primary tool for search, transform, curve warping, OKLCH segmentation, vividness, color/image shifting, and export.
- `scripts/find_presets.py`: legacy preset search helper.
- `references/family-guide.md`: semantic family mapping.
- `references/preset-catalog.json`: exact preset inventory derived from wrap-gradient.
