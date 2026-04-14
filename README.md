# gradient-presets

A publishable Codex skill repo for choosing gradient presets by color family, with `oklch` and `oklab` as the default interpolation modes.

This repository is structured as a single-skill repo, so `SKILL.md` lives at the repository root and can be installed directly with the Skills CLI.

## Install

After you push this folder to GitHub, install it with:

```bash
npx skills add BIAsia/gradient-presets -g -y
```

You can also install from the GitHub URL directly:

```bash
npx skills add https://github.com/BIAsia/gradient-presets -g -y
```

After installing, restart Codex so the new skill is picked up immediately.

## What This Skill Does

- Picks gradients by hue family first, instead of inventing colors from scratch every time
- Defaults to `oklch` for vivid short ramps and simple UI gradients
- Falls back to `oklab` for multi-stop atmospheric backgrounds and structured family presets
- Ships with a fully bundled offline preset pack, so the skill works without network access after install
- Does not depend on any external repo, API, or runtime download once installed

## Included Files

- `SKILL.md`: the skill instructions Codex reads
- `agents/openai.yaml`: UI metadata for skill lists and chips
- `references/family-guide.md`: quick mapping from mood and color language to families
- `references/preset-catalog.json`: bundled offline preset catalog
- `scripts/find_presets.py`: local preset search and CSS output helper

## Example Usage

After installing, ask Codex things like:

- `用 $gradient-presets 给我一个蓝紫科技感的 hero 背景`
- `用 $gradient-presets 推荐 3 个护肤空气感的浅色渐变`
- `Use $gradient-presets to find an oklch gradient for a bold poster CTA`

You can also run the helper script directly inside the repo:

```bash
python3 scripts/find_presets.py --query "蓝紫 科技感 hero 背景" --limit 3
python3 scripts/find_presets.py --query "护肤 空气感 浅色" --mode oklch --format css --limit 3
```

## Local Validation

```bash
python3 scripts/find_presets.py --query "蓝紫 科技感 hero 背景" --limit 3
python3 scripts/find_presets.py --query "护肤 空气感 浅色" --mode oklch --format css --limit 3
npx skills add . --list
```

## Publish To GitHub

```bash
git init -b main
git add .
git commit -m "Add gradient-presets skill"
git remote add origin https://github.com/BIAsia/gradient-presets.git
git push -u origin main
```
