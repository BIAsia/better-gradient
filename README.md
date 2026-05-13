# better-gradient

A publishable, offline gradient skill for Codex, Claude Code, Cursor, Gemini CLI, and other agentic coding tools that use the shared Skills CLI workflow.

This repository contains two pieces:

- the skill itself at the repo root
- a standalone marketing/docs site in `site/`

## Install

After you push this folder to GitHub, install it with:

```bash
npx skills add BIAsia/better-gradient -g -y
```

You can also install from the GitHub URL directly:

```bash
npx skills add https://github.com/BIAsia/better-gradient -g -y
```

After installing, restart Codex so the new skill is picked up immediately.

## Works With

- Codex CLI
- Claude Code
- Cursor
- Gemini CLI
- OpenCode
- Kiro
- VS Code Copilot
- Antigravity
- other tools supported by `npx skills add`

## What This Skill Does

- Picks gradients by hue family first, instead of inventing colors from scratch every time
- Defaults to `oklch` for vivid short ramps and simple UI gradients
- Falls back to `oklab` for multi-stop atmospheric backgrounds and structured family presets
- Turns OKLCH interpolation into segmented hex stops for production compatibility
- Warps gradients with curve presets such as `top-empty` and `top-active`
- Makes existing gradients more vivid by increasing OKLCH chroma
- Shifts a gradient toward a supplied color, image average color, or hue direction while preserving relative color movement
- Exports CSS, SwiftUI, Android Compose, and Figma Plugin API snippets
- Ships with a fully bundled offline preset pack, so the skill works without network access after install
- Does not depend on any external repo, API, or runtime download once installed

## Site

- Live site: `https://better-gradient-red.vercel.app`
- Marketing/docs site source: `site/`
- Intended deployment target: Vercel
- Local preview: `cd site && python3 -m http.server 8123`

## Included Files

- `SKILL.md`: the skill instructions Codex reads
- `agents/openai.yaml`: UI metadata for skill lists and chips
- `references/family-guide.md`: quick mapping from mood and color language to families
- `references/preset-catalog.json`: bundled offline preset catalog
- `scripts/find_presets.py`: local preset search and CSS output helper
- `scripts/gradient_tool.py`: search, transform, segment, recolor, warp, and export helper

## Example Usage

After installing, ask Codex things like:

- `用 $better-gradient 给我一个蓝紫科技感的 hero 背景`
- `用 $better-gradient 推荐 3 个护肤空气感的浅色渐变`
- `Use $better-gradient to find an oklch gradient for a bold poster CTA`

You can also run the helper script directly inside the repo:

```bash
python3 scripts/find_presets.py --query "蓝紫 科技感 hero 背景" --limit 3
python3 scripts/find_presets.py --query "护肤 空气感 浅色" --mode oklch --format css --limit 3
python3 scripts/gradient_tool.py transform --query "红色系 渐变 文字" --scope text --oklch-segments
python3 scripts/gradient_tool.py transform --preset dream-haze --curve top-empty --samples 14
python3 scripts/gradient_tool.py transform --preset dream-haze --shift-color "#3B82F6" --format figma
```

## Local Validation

```bash
python3 scripts/find_presets.py --query "蓝紫 科技感 hero 背景" --limit 3
python3 scripts/find_presets.py --query "护肤 空气感 浅色" --mode oklch --format css --limit 3
python3 scripts/gradient_tool.py transform --query "梦幻感 背景" --oklch-segments --samples 12
npx skills add . --list
```

## Publish To GitHub

```bash
git init -b main
git add .
git commit -m "Add better-gradient skill"
git remote add origin https://github.com/BIAsia/better-gradient.git
git push -u origin main
```
