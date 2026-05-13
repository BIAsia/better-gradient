# Gradient Family Guide

## Fast Rules

- Match hue family first, then pick the closest preset.
- Default to `oklch` for vivid two-stop ramps and clean UI work.
- Default to `oklab` for multi-stop, atmospheric, or family-driven backgrounds from `g.json`.
- If the user clearly names a family, prefer the `g.json` family presets before the generic OKLCH pair presets.

## OKLAB Families From `g.json`

| Family | Common cues | Use for | Representative presets |
| --- | --- | --- | --- |
| `red-yellow` | 红色系, 暖色, 夕阳, 朝霞, 桃色, coral, sunrise, sunset | Warm hero backgrounds, editorial covers, beauty, festival, energetic landing pages | `Sunset Glow 夕霞`, `Warm Glow 晨曦`, `Peach Aura 桃霓` |
| `blue-purple` | 蓝色系, 紫色系, 蓝紫, 科技, 夜空, 梦幻, cosmic, tech, twilight | Tech sites, AI products, nightlife, cosmic scenes, dreamy posters | `Dream Haze 梦霭`, `Twilight Sky 夜阑`, `Stellar 星幕` |
| `green-yellow` | 绿色系, 青绿, 春日, 薄荷, 湖水, 自然, fresh, spring | Wellness, sustainability, nature products, travel, fresh consumer UI | `Mint Sugar 薄荷糖`, `Lakeside Glow 湖光`, `Spring Days 春日` |
| `contrast` | 撞色, 高对比, 活力, 时尚, vivid, fashion | Bold marketing, youth brands, posters, music, sporty motion graphics | `Floral 花漾`, `Waltz 华尔兹`, `Amber Mist 雾色暖阳` |
| `dark` | 暗色, 电影感, 高级, 厚重, moody, luxury | Premium brands, cinematic UI, dark hero sections, nightlife campaigns | `Phantom 魅影`, `Fading Night 渐明`, `Jungle 丛林` |
| `light` | 浅色, 空气感, 护肤, 粉彩, airy, soft, skincare | Beauty, lifestyle, wellness, onboarding screens, soft editorial cards | `Soft Bubble 泡沫`, `Peach 水蜜桃`, `Sun Flower 向阳` |

## OKLCH Pair Presets

These are best when you want something punchy, short, or simplified.

| Tag direction | Use for | Good starting presets |
| --- | --- | --- |
| Neon warm | Loud posters, pop buttons, accent backgrounds | `Lime Pink Burst`, `Mint Apricot Pop` |
| Neon cool | Cyber, club, electric UI accents | `Cyan Magenta Flash`, `Mint Magenta Surge` |
| Complementary contrast | High-energy editorial gradients | `Blue Orange Spark`, `Violet Lime Voltage` |
| Soft pastel | Beauty, airy, light lifestyle work | `Peach Sky Soft`, `Peach Lilac Mist`, `Pistachio Orchid Drift` |
| Calm cool | Premium cool-tone gradients without heavy darkness | `Lilac Teal Bridge`, `Violet Mint Fizz` |
| Quiet premium | Muted, premium, restrained transitions | `Sage Indigo Dusk` |

## Practical Mapping

- "蓝紫科技感" -> start with `blue-purple`, then check `Dream Haze 梦霭`, `Twilight Sky 夜阑`, or `Cyan Magenta Flash`.
- "青绿自然感" -> start with `green-yellow`, then check `Mint Sugar 薄荷糖`, `Spring Days 春日`, or `Lilac Teal Bridge` if it needs more cool calm.
- "暖色落日" -> start with `red-yellow`, then check `Sunset Glow 夕霞`, `Warm Glow 晨曦`, or `Peach Sky Soft` if the result should be lighter.
- "高饱和撞色" -> start with `contrast` or the OKLCH complementary pairs.
- "高级暗色" -> start with `dark`; only use OKLCH if the user explicitly wants a simpler two-stop version.
- "护肤空气感" -> start with `light`, then try `Peach 水蜜桃` or `Peach Lilac Mist`.

## Where To Look Next

- Read `preset-catalog.json` for exact stop positions and colors.
- Run `python3 scripts/find_presets.py --query "<user request>" --limit 3` for a ranked shortlist.
