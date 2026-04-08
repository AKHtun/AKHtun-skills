# DISPLAY.json Specification

**Spec Version:** 0.1.0

## Overview

`DISPLAY.json` is a presentation metadata file for agent skills. It lives alongside `SKILL.md` in a skill's root directory and describes how the skill should appear in a UI — icon, cover image, tags, and integration badges.

To see examples of how `DISPLAY.json` data gets used to present skills, see https://www.zo.computer/skills (with both [image](https://www.zo.computer/skills/minecraft-server) and [video](https://www.zo.computer/skills/manim-composer) examples)

`DISPLAY.json` is strictly a **display layer**. It does not duplicate or override anything in `SKILL.md`, which remains the source of truth for a skill's identity and behavior.

| File | Purpose |
| --- | --- |
| `SKILL.md` | Identity + behavior — what the skill is, what it does, how to run it |
| `DISPLAY.json` | Presentation — how to render the skill in a UI |

## Schema

```jsonc
{
  "specVersion": "0.1.0",
  "icon": "globe",
  "image": "assets/cover.png",
  "video": "assets/demo.mp4",
  "tags": ["social", "automation"],
  "integrations": ["x", "linkedin"]
}
```

All fields are optional. A skill with no `DISPLAY.json` or an empty `{}` still works — it just gets default rendering.

## Fields

### `specVersion`

- **Type:** `string`
- **Format:** [Semantic Versioning 2.0.0](https://semver.org/)
- **Description:** The version of this spec the file conforms to.

```json
"specVersion": "0.1.0"
```

### `icon`

- **Type:** `string`
- **Description:** Icon name for the skill in compact views (lists, cards). Use a [Lucide](https://lucide.dev/icons) icon name or a logo name from [Iconify](https://icon-sets.iconify.design/). Plain lowercase name — no prefixes, no file extensions.

```json
"icon": "globe"
```

```json
"icon": "x"
```

### `image`

- **Type:** `string`
- **Description:** Cover image for the skill card. Relative path within the skill folder or an absolute URL.
- **Allowed formats:** PNG, JPEG, WebP.
- **Recommended:** 16:9 aspect ratio, minimum 800×450.

```json
"image": "assets/cover.png"
```

```json
"image": "https://example.com/skills/my-skill/cover.jpg"
```

### `video`

- **Type:** `string`
- **Description:** Short demo or preview video. Relative path or absolute URL. When both `video` and `image` are present, `image` serves as the poster frame / fallback.
- **Allowed formats:** MP4, WebM.
- **Recommended:** 16:9 aspect ratio, 5–15 seconds.

```json
"video": "assets/demo.mp4"
```

### `tags`

- **Type:** `string[]`
- **Description:** Freeform tags for filtering and search. Lowercase, short, descriptive.

```json
"tags": ["social", "automation", "posting"]
```

### `integrations`

- **Type:** `string[]`
- **Description:** External services this skill interacts with. Used to show service badges alongside the skill. Plain lowercase slugs using the service's common name.

```json
"integrations": ["x", "linkedin", "gmail"]
```

## File placement

```
my-skill/
├── SKILL.md          # Identity + behavior
├── DISPLAY.json      # Presentation metadata (this spec)
├── assets/
│   ├── cover.png     # Referenced by "image"
│   └── demo.mp4      # Referenced by "video"
├── scripts/
│   └── run.py
└── references/
    └── api-notes.md
```

## Example

A minimal `DISPLAY.json`:

```json
{
  "icon": "send",
  "tags": ["social"]
}
```

A fuller example:

```json
{
  "specVersion": "0.1.0",
  "icon": "globe",
  "image": "assets/cover.png",
  "video": "assets/demo.mp4",
  "tags": ["social", "automation", "posting"],
  "integrations": ["x", "linkedin"]
}
```
