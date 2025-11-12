# content-producer — Skill Specification

## Purpose
- Transform a single content-generator output (one idea) into platform-ready assets: per-platform copy, AI image prompts (Midjourney-optimized), and a zipped bundle, organized for easy deployment.

## Scope
- Platforms: Facebook, Instagram, Reddit, LinkedIn, Twitter/X, TikTok (all 6 major social platforms)
- Inputs: one content-generator JSON file (e.g., `content_idea_2025-10-28_1836.json`)
- Outputs: bundle folder per idea with per-platform subfolders, manifest, report, and zip
- Optional: Manual quote loading from `input/url_quotes/<idea_id>.json` files (when `--extract-quotes` flag enabled)
- Constraints: local-only; no network access; use placeholder brand assets and CTA

## CLI
- Command:
  - `produce --input <path/to/content_idea.json> --outdir output/bundles --platforms facebook,instagram,reddit,linkedin,twitter,tiktok --images 2 --cta "[CTA_PLACEHOLDER]" [--no-zip] [--no-prompts] [--extract-quotes]`
- Parameters:
  - `--input`: Path to content-generator JSON file (required)
  - `--outdir`: Output directory (default: `output/bundles`)
  - `--platforms`: Comma-separated platform list (default: `facebook,instagram,reddit`)
  - `--images`: Number of prompt variations (default: 2)
  - `--cta`: CTA placeholder text (default: `[CTA_PLACEHOLDER]`)
  - `--no-zip`: Skip creating zip archive
  - `--no-prompts`: Skip AI prompt generation, copy only
  - `--extract-quotes`: Load golden quotes from manual quote files (input/url_quotes/<idea_id>.json)
- Behavior:
  - Loads first idea from the JSON (`ideas[0]`).
  - Optionally loads golden quotes from `input/url_quotes/<idea_id>.json` if `--extract-quotes` enabled.
  - Generates AI image prompts (1 core + N variations) with pillar-aware styling.
  - Writes platform-optimized copy files for all requested platforms.
  - Builds `manifest.json` (including golden_quotes section if loaded), `report.txt`, and optional zip.
- Exit codes:
  - 0: success
  - 2: success with warnings (e.g., trims/fallbacks)
  - 3: missing/invalid input

## Input Contract
- JSON structure (first idea at `ideas[0]`):
  - Must: `id`, `pillar`, `core_message`, `variants.generic`.
  - Prefer: `platform_adaptations.facebook`, `.instagram`, `.reddit` (fallback to `variants.generic` if missing).
  - Optional: `source_idea.href` (enables CTA placeholder), `source_idea.key_points[]`, `pillar_rationale`, `score`, `score_rationale`.

## Output Layout
- Bundle root: `output/bundles/<idea_id>_<YYYYMMDD_HHMMSS>/`
- Files and folders:
  - `manifest.json` (includes `image_prompts` section)
  - `report.txt`
  - `copy/facebook.txt`
  - `copy/instagram.txt`
  - `copy/reddit_title.txt`, `copy/reddit_body.txt`
  - `images/prompts/core_prompt.json` (metadata + prompt)
  - `images/prompts/core_prompt.txt` (copy-paste ready)
  - `images/prompts/variation_1.txt`, `variation_2.txt`, ... (variations based on `--images N`)
  - Zip: `<bundle_root>.zip` (unless `--no-zip`)

## Copy Rules
- Source selection:
  - Use `platform_adaptations.<platform>` if present; else `variants.generic`.
  - Normalize UTF‑8; remove control characters; trim excessive whitespace.
- CTA placeholder:
  - If `source_idea.href` exists, append a space + CTA string from `--cta` to Facebook and Instagram copy.
  - Store CTA placeholder in `manifest.json` for later replacement.
- Reddit specifics:
  - `reddit_title.txt`: first sentence or first 120 chars; no hashtags/CTA; hard cap 140 chars.
  - `reddit_body.txt`: full adaptation or generic; no CTA; up to 10,000 chars.
- Length guardrails (defaults if not available in `config/platforms.json`):
  - Facebook: target 40–80 chars; soft trim at 120 with ellipsis; hard cap 500.
  - Instagram: target 125–150 visible; soft trim at 300 with ellipsis; hard cap 2200.
  - Reddit title: hard cap 140; body cap 10,000.
- Record any trims/fallbacks in `report.txt` and `manifest.validations`.

## AI Prompt Generation
- Prompt count:
  - Configurable via `--images N` (default: 2).
  - Generates 1 core prompt + N variations.
- Pillar-aware styling:
  - Reads visual guidelines from `config/pillar_styles.json`.
  - Each pillar defines: visual_theme, color_palette, mood, style_references, composition_hints, midjourney_base.
  - Applies pillar-specific styling to prompts (e.g., advocacy_impact → documentary photography, red/orange tones).
- Prompt structure:
  - Visual concepts: extracted from `core_message` and `key_points[]`.
  - Pillar style base: pulled from pillar configuration.
  - Quality modifiers: "high quality, professional photography".
  - Midjourney parameters: `--ar 1:1 --v 6.1`.
- Variations:
  - Core: Base prompt with standard quality modifiers.
  - Variation 1: Cinematic composition, shallow depth of field, editorial quality.
  - Variation 2: Dramatic lighting, golden hour, atmospheric mood.
  - Variation 3+: Wide angle, environmental context, dynamic perspective (if N ≥ 3).
- Output formats:
  - JSON (`core_prompt.json`): Includes metadata (pillar, style theme, parameters) for future automation.
  - Plain text (`.txt` files): Ready to copy-paste into Midjourney, DALL-E, Stable Diffusion, etc.

## Validation
- Copy:
  - Enforce platform caps; apply soft trims; warn on fallbacks to generic.
  - Normalize punctuation/whitespace.
- Prompts:
  - Confirm core prompt and all variations exist.
  - Verify JSON structure includes required metadata.
- Outputs:
  - Ensure manifest references valid paths.
  - Count warnings; set exit code 2 if any.
- Reporting:
  - `report.txt` lists trims, fallbacks, prompt count, and warnings count.

## Manifest Schema (outline)
```json
{
  "idea_id": "string",
  "source_file": "string",
  "pillar_id": "string",
  "generated_timestamp": "ISO-8601 string",
  "cta_placeholder": "string or null",
  "platforms": {
    "facebook": {
      "copy_path": "string"
    },
    "instagram": {
      "copy_path": "string"
    },
    "reddit": {
      "title_path": "string",
      "body_path": "string"
    }
  },
  "image_prompts": {
    "core_json": "string (path to core_prompt.json)",
    "core_txt": "string (path to core_prompt.txt)",
    "variation_1": "string (path to variation_1.txt)",
    "variation_2": "string (path to variation_2.txt)"
  },
  "validations": {
    "warnings": ["string"],
    "counts": { "trims": 0, "fallbacks": 0, "prompts": 0 }
  }
}
```

## Configuration and Assets
- Platform constraints:
  - If present, read from `config/platforms.json`; otherwise use defaults above.
- Pillar visual styles:
  - **Required**: Read from `config/pillar_styles.json` for AI prompt generation.
  - Each pillar defines: visual_theme, color_palette, mood, style_references, composition_hints, midjourney_base.
  - Fallback to hardcoded defaults if config missing.
- Assets:
  - No assets required for current MVP (AI prompts only).
  - Reserved for future image generation automation.

## Non-Goals (MVP)
- No ingestion of new ideas.
- No actual image generation (prompts only; automation hook stubbed for future).
- No auto-posting (provide an `autopost_hook()` stub only).
- No database; filesystem outputs only.

## Implementation Notes
- Language: Python 3.
- Libraries: Standard library only (no Pillow required for prompt generation).
- Determinism: timestamp in bundle name; deterministic layout from inputs.
- Performance: target < 10 seconds per idea (typical: 3-5 seconds).
- Logging: concise stdout; full details in `report.txt`.
- Future: Structured JSON format enables automation hooks for image generation.

## Acceptance Criteria
- Running the CLI on a valid content-generator JSON produces:
  - Bundle folder with per-platform copy files.
  - AI image prompts (1 core + N variations) with pillar-aware styling.
  - Prompts in both JSON (with metadata) and plain text formats.
  - Copy within caps or trimmed with notes.
  - Valid `manifest.json` with `image_prompts` section and `report.txt`.
  - Zip archive unless `--no-zip` passed.
  - Prompts ready to copy-paste into Midjourney, DALL-E, or similar AI tools.

## Example Invocation
- `produce --input content_idea_2025-10-28_1836.json --outdir output/bundles --platforms facebook,instagram,reddit --images 2 --cta "[CTA_PLACEHOLDER]"`

## Example AI Prompt Output

For an advocacy_impact idea about fair pay and driver safety:

**Core prompt:**
```
professional driver in vehicle, safety-focused scene, diverse community of drivers,
economic fairness concept, modern mobile app interface, documentary photography style,
powerful emotional impact, red and orange color grading, dramatic lighting,
photojournalistic, high quality, professional photography, --ar 1:1, --v 6.1
```

**Variation 1:** (Cinematic approach)
```
professional driver in vehicle, safety-focused scene, diverse community of drivers,
economic fairness concept, modern mobile app interface, documentary photography style,
powerful emotional impact, red and orange color grading, dramatic lighting,
photojournalistic, cinematic composition, shallow depth of field, editorial quality, --ar 1:1, --v 6.1
```

**Variation 2:** (Atmospheric approach)
```
professional driver in vehicle, safety-focused scene, diverse community of drivers,
economic fairness concept, modern mobile app interface, documentary photography style,
powerful emotional impact, red and orange color grading, dramatic lighting,
photojournalistic, dramatic lighting, golden hour, atmospheric mood, --ar 1:1, --v 6.1
```

## Future Enhancements
- **Automated image generation**: Hook to pipe prompts directly to Midjourney CLI, DALL-E API, or Stable Diffusion.
- **Integration points already in place**:
  - `manifest.json` includes `image_prompts` paths
  - `core_prompt.json` includes metadata (pillar, aspect ratio, parameters)
  - Modular architecture allows drop-in automation without breaking existing workflow

