---
name: content-producer
description: Transform content-generator output (one idea) into platform-ready social media assets with optimized copy and AI image prompts for all major social platforms (Facebook, Instagram, Reddit, LinkedIn, Twitter/X, TikTok). This skill should be used when converting generated content ideas into final deliverable bundles ready for posting or review, including per-platform copy adaptation, Midjourney-optimized AI prompts, and packaging with manifests and validation reports.
---

# Content Producer

## Overview

Transform a single content-generator output into complete, platform-ready social media bundles. The skill takes one generated idea and produces:

- **Platform-optimized copy** (Facebook, Instagram, Reddit, LinkedIn, Twitter/X, TikTok) with proper length constraints and CTA insertion
- **AI image prompts** (Midjourney-optimized, pillar-aware with 1 core + N variations)
- **Structured bundle** with manifest, validation report, and optional zip archive

Designed for the Zenlit content pipeline, creating production-ready assets from content-generator JSON files. Image prompts are ready to feed into Midjourney, DALL-E, Stable Diffusion, or similar AI image generation tools.

## When to Use This Skill

Invoke this skill when:

1. **Converting ideas to assets**: User has a content-generator output file and needs platform-ready deliverables
2. **Batch production**: Producing assets for multiple ideas sequentially or as part of automated pipeline
3. **Testing content flow**: Validating that generated ideas can be successfully converted to final assets
4. **Quality review**: Creating bundles for content review before posting

Example user requests:
- "Take this content idea and produce the final assets for Facebook and Instagram"
- "Create a complete bundle from content_idea_2025-10-28_1836.json"
- "Generate the AI prompts and copy for all platforms from this idea"
- "Produce assets for Reddit only from this generated content"

## Core Workflow

### Step 1: Invoke the produce CLI

The primary interface is the `produce.py` script located in `scripts/`. Execute with required parameters:

```bash
python3 scripts/produce.py \
  --input <path/to/content_idea.json> \
  --outdir output/bundles \
  --platforms facebook,instagram,reddit,linkedin,twitter,tiktok \
  --images 2 \
  --cta "[CTA_PLACEHOLDER]"
```

**Required parameters:**
- `--input`: Path to content-generator JSON file

**Optional parameters:**
- `--outdir`: Output directory (default: `output/bundles`)
- `--platforms`: Comma-separated platform list (options: facebook, instagram, reddit, linkedin, twitter, tiktok; default: `facebook,instagram,reddit`)
- `--images`: Number of prompt variations to generate (default: `2`)
- `--cta`: CTA placeholder text (default: `[CTA_PLACEHOLDER]`)
- `--no-zip`: Skip creating zip archive
- `--no-prompts`: Skip AI prompt generation, copy only
- `--extract-quotes`: Load golden quotes from manual quote files

### Step 2: Understand the Input Contract

The input JSON must contain `ideas[0]` with:

**Required fields:**
- `id`: Unique idea identifier
- `pillar`: Content pillar ID (maps to visual theme and prompt styling)
- `core_message`: Core message used for AI prompt generation
- `variants.generic`: Fallback copy text

**Preferred fields (fallback to generic if missing):**
- `platform_adaptations.facebook`: Facebook-optimized copy
- `platform_adaptations.instagram`: Instagram-optimized copy
- `platform_adaptations.reddit`: Reddit-optimized copy
- `platform_adaptations.linkedin`: LinkedIn-optimized copy
- `platform_adaptations.twitter`: Twitter/X-optimized copy
- `platform_adaptations.tiktok`: TikTok-optimized copy

**Optional fields:**
- `source_idea.href`: Enables CTA placeholder insertion
- `source_idea.key_points[]`: Enhances AI prompt generation with additional context
- `pillar_rationale`: Context for pillar selection
- `score`, `score_rationale`: Quality metrics

### Step 3: Verify Output Structure

After execution, the bundle directory contains:

```
output/bundles/<idea_id>_<timestamp>/
├── manifest.json              # Structured metadata and paths
├── report.txt                 # Human-readable validation report
├── copy/
│   ├── facebook.txt
│   ├── instagram.txt
│   ├── reddit_title.txt
│   ├── reddit_body.txt
│   ├── linkedin.txt
│   ├── twitter.txt
│   └── tiktok.txt
└── images/
    └── prompts/
        ├── core_prompt.json      # Core prompt with metadata
        ├── core_prompt.txt       # Core prompt (copy-paste ready)
        ├── variation_1.txt       # First variation
        └── variation_2.txt       # Second variation
```

Optional: `<idea_id>_<timestamp>.zip` in parent directory (unless `--no-zip` used)

**AI Prompt Files:**
- `core_prompt.json`: Structured format with metadata (pillar, style, parameters)
- `core_prompt.txt`: Plain text format ready for Midjourney, DALL-E, etc.
- `variation_N.txt`: Alternative compositions/styles based on core prompt

## Copy Processing Details

### Platform Constraints

**Facebook:**
- Target: 40-80 chars
- Soft trim: 120 chars (ellipsis added)
- Hard cap: 500 chars
- CTA: Appended if `source_idea.href` exists

**Instagram:**
- Target: 125-150 visible chars
- Soft trim: 300 chars (ellipsis added)
- Hard cap: 2200 chars
- CTA: Appended if `source_idea.href` exists

**Reddit:**
- Title: First sentence or 120 chars; hard cap 140 chars; no hashtags/CTA
- Body: Full adaptation; hard cap 10,000 chars; no CTA

**LinkedIn:**
- Target: 100-300 chars
- Soft trim: 400 chars (ellipsis added)
- Hard cap: 3000 chars
- CTA: Appended if `source_idea.href` exists

**Twitter/X:**
- Target: 100-280 chars
- Soft trim: 280 chars (strict Twitter limit)
- Hard cap: 280 chars
- CTA: Appended if `source_idea.href` exists

**TikTok:**
- Target: 20-60 chars (very short, punchy captions)
- Soft trim: 100 chars (ellipsis added)
- Hard cap: 150 chars
- CTA: Appended if `source_idea.href` exists (though rare for TikTok)

### Text Normalization

All copy undergoes:
1. UTF-8 normalization (NFKC)
2. Control character removal (except newlines/tabs)
3. Whitespace normalization (multiple spaces → single, trim lines)
4. Trim/cap enforcement per platform

### Fallback Behavior

If `platform_adaptations.<platform>` is missing, the script:
1. Falls back to `variants.generic`
2. Records warning in `manifest.json` validations
3. Increments fallback counter in report

## AI Prompt Generation Details

### LLM-Based Visual Concept Extraction

**MANDATORY**: The content-producer skill uses Claude LLM to generate unique, content-specific visual concepts for each idea. This ensures consistent high-quality prompts that accurately represent the content.

**⚠️ NO FALLBACK MODE**: If LLM extraction fails, the entire prompt generation will fail with a clear error message. This is intentional to maintain quality standards.

**How it works:**
1. The skill analyzes the idea's `core_message`, `key_points`, and `title`
2. Calls Claude LLM to extract 3-5 specific, concrete visual concepts unique to this idea
3. Validates LLM response (minimum 10 characters, proper format)
4. Combines LLM-generated concepts with pillar-specific styling for final prompt
5. **If LLM fails**: Raises RuntimeError with diagnostic information

**Benefits:**
- ✅ Each idea gets unique, content-aware visual concepts
- ✅ No more generic "professional driver in vehicle" for all safety ideas
- ✅ Specific objects and scenes (e.g., "dashcam on windshield" vs "passenger ejection moment")
- ✅ Consistent quality - no degraded fallback mode
- ✅ Better AI image generation results with more distinctive prompts

**Example outputs:**

*Idea about dashcams:*
```
dashcam mounted on windshield, driver reviewing footage on phone screen,
accident documentation moment, professional infographic style,
clean modern design, blue color scheme, high contrast, editorial photography...
```

*Idea about passenger safety:*
```
rideshare driver gesturing passenger to exit vehicle, tense safety boundary moment,
driver prioritizing personal safety, professional infographic style,
clean modern design, blue color scheme, high contrast, editorial photography...
```

### Pillar-Aware Styling

Prompts combine LLM-extracted visual concepts with pillar-specific style guidelines from `config/pillar_styles.json`:

- **safety_education**: Professional, clean, data-driven | Blue tones, infographic style
- **token_community**: Vibrant, community-focused | Purple/warm tones, authentic candid style
- **advocacy_impact**: Bold, emotional, impactful | Red/orange tones, documentary/photojournalistic
- **product_tips**: Practical, UI-focused | Green/tech colors, modern app interface style
- **seasonal_trending**: Dynamic, trend-aligned | Seasonal palettes, trending social aesthetics
- **entertainment_humor**: Playful, meme-friendly | Bright varied colors, pop culture references

### Prompt Structure

Generated prompts use Midjourney-optimized syntax:

1. **Visual concepts**: Extracted from `core_message` and `key_points[]`
2. **Pillar style base**: Pulled from pillar configuration (e.g., "documentary photography style")
3. **Quality modifiers**: "high quality, professional photography"
4. **Parameters**: `--ar 1:1 --v 6.1` (aspect ratio and Midjourney version)

**Example prompt:**
```
professional driver in vehicle, safety-focused scene, diverse community of drivers,
documentary photography style, powerful emotional impact, red and orange color grading,
dramatic lighting, photojournalistic, high quality, professional photography, --ar 1:1, --v 6.1
```

### Variations

The `--images N` parameter controls variation count (default: 2):
- **Core prompt**: Base prompt with standard quality modifiers
- **Variation 1**: Cinematic composition, shallow depth of field, editorial quality
- **Variation 2**: Dramatic lighting, golden hour, atmospheric mood
- **Variation 3+**: Wide angle, environmental context, dynamic perspective (if N ≥ 3)

### Output Formats

Prompts are saved in dual formats:
- **JSON** (`core_prompt.json`): Includes metadata (pillar, style theme, parameters) for automation hooks
- **Plain text** (`.txt` files): Ready to copy-paste into AI tools

### Error Handling

**LLM Extraction Failures**: If Claude CLI is unavailable or returns invalid responses, prompt generation will fail with a clear error:

```
❌ FATAL: LLM visual concept extraction failed and no fallback is available.
   Ensure Claude CLI is installed and accessible.
   Test with: echo 'hello' | claude --print
```

**Common causes**:
- Claude CLI not installed or not in PATH
- Network issues preventing Claude access
- Timeout (>30 seconds for LLM call)
- Invalid/malformed LLM response

**Resolution**:
1. Verify Claude CLI: `claude --version`
2. Test Claude access: `echo 'test' | claude --print`
3. Check internet connectivity
4. Retry the production command

**Note**: No degraded fallback mode exists - this ensures all prompts maintain consistent quality.

### Future: Automated Image Generation

**Currently**: Prompts are generated as text files for manual use in Midjourney, DALL-E, etc.

**Planned**: Automation hook to pipe prompts directly to AI image generation APIs (e.g., `cat core_prompt.txt | midjourney-cli`). The structured JSON format already includes metadata needed for future automation.

## URL Quote Extraction (Manual Curation)

### Overview

When `--extract-quotes` flag is enabled and the idea contains a `source_idea.href` URL, the skill loads manually curated "golden quotes" from a file. These quotes enrich the content bundle with authentic, impactful statements from the original source.

### How It Works

1. **Manual Curation**: You visit the source URL and extract 3-5 impactful quotes
2. **File Creation**: Create a JSON file at `input/url_quotes/<idea_id>.json` with your quotes
3. **Automatic Loading**: When producing the bundle, the skill reads this file
4. **Storage**: Quotes are included in manifest.json and report.txt for reference

### Quote Structure

Each extracted quote includes:
- `text`: The actual quote text
- `source`: Where it came from ("main post", "comment", "article", etc.)
- `impact`: Why this quote is valuable for content creation

### Usage

```bash
python3 scripts/produce.py \
  --input content_idea.json \
  --extract-quotes
```

### Manifest Output

When quotes are extracted, the manifest includes:

```json
{
  "golden_quotes": {
    "extracted": true,
    "count": 3,
    "source_url": "https://example.com/article",
    "quotes": [
      {
        "text": "No excuse is worth it for safety",
        "source": "comment",
        "impact": "Powerful statement about safety priorities"
      }
    ]
  }
}
```

### Quote File Format

Create `input/url_quotes/<idea_id>.json`:

```json
{
  "url": "https://www.reddit.com/r/toronto/comments/...",
  "quotes": [
    {
      "text": "No excuse is worth it for safety",
      "source": "comment",
      "impact": "Powerful statement about safety priorities"
    },
    {
      "text": "I am the driver of the BMW that hit from behind",
      "source": "comment",
      "impact": "First-person witness perspective adds authenticity"
    }
  ]
}
```

### Benefits of Manual Curation

- **Quality Control**: You select only the most impactful quotes
- **Context Awareness**: You understand nuance and choose appropriate content
- **No API Limitations**: Works with any site (Reddit, news sites, etc.)
- **Reliability**: No dependency on automated extraction or API access

### Workflow

1. Content-generator creates idea with `source_idea.href`
2. Visit the URL and read the content
3. Identify 3-5 golden quotes that add value
4. Create `input/url_quotes/<idea_id>.json` with structured quotes
5. Run producer with `--extract-quotes` flag
6. Quotes appear in manifest and report for use in final content

## Validation and Exit Codes

### Exit Codes

- **0**: Success (no warnings)
- **2**: Success with warnings (trims, fallbacks, or minor issues)
- **3**: Failure (missing/invalid input, missing required fields)

### Validation Checks

1. **Input validation**: Required fields present, valid JSON structure
2. **Copy validation**: Platform caps enforced, trims recorded
3. **Prompt validation**: Prompt files created, metadata complete
4. **Manifest validation**: Paths reference actual files

All warnings and counts stored in `manifest.json` under `validations` key.

## Configuration and Assets

### Platform Config

Platform constraints are read from `config/platforms.json` within the skill directory. The config defines optimal text lengths for each platform (Facebook, Instagram, Reddit, etc.). If the config file is not found, the system falls back to hardcoded defaults:

- **Facebook**: 40-80 characters (target)
- **Instagram**: 125-150 characters (visible caption)
- **Reddit**: Title extracted from first sentence

Soft and hard caps are currently hardcoded in `copy_processor.py` but use target ranges from config when available.

### Pillar Style Config

Pillar visual guidelines are read from `config/pillar_styles.json` within the skill directory. Each pillar defines:
- `visual_theme`: Overall aesthetic (e.g., "Bold, emotional, impactful")
- `color_palette`: Dominant colors and tone
- `mood`: Emotional qualities
- `style_references`: Photography/design styles
- `composition_hints`: Layout and framing guidance
- `midjourney_base`: Base prompt template for Midjourney

If config missing, falls back to default hardcoded styles.

## Usage Examples

### Basic Usage

```bash
python3 scripts/produce.py \
  --input output/generated_ideas/content_idea_2025-10-28_1836.json
```

Produces bundle with default platforms (Facebook, Instagram, Reddit), 2 prompt variations, default CTA.

### All Platforms

```bash
python3 scripts/produce.py \
  --input content_idea_XYZ.json \
  --platforms facebook,instagram,reddit,linkedin,twitter,tiktok
```

Produces assets for all six supported platforms.

### Selective Platforms

```bash
python3 scripts/produce.py \
  --input content_idea_ABC.json \
  --platforms linkedin,twitter
```

Produces assets for LinkedIn and Twitter only.

### Copy-Only Mode

```bash
python3 scripts/produce.py \
  --input content_idea_DEF.json \
  --no-prompts
```

Generates copy files only, skips AI prompt generation (useful for text-only review).

### More Prompt Variations

```bash
python3 scripts/produce.py \
  --input content_idea_GHI.json \
  --images 4
```

Generates 4 prompt variations (more creative options for image generation).

### Fast Batch Production

```bash
python3 scripts/produce.py \
  --input content_idea_JKL.json \
  --images 2 \
  --no-zip
```

Generates 2 prompt variations, skips zip creation (faster for batch workflows).

### With URL Quote Extraction

```bash
python3 scripts/produce.py \
  --input content_idea_MNO.json \
  --extract-quotes \
  --platforms facebook,instagram,reddit,linkedin,twitter,tiktok
```

Extracts golden quotes from the source URL (if available) and produces assets for all platforms. The quotes will be included in the manifest and report for reference.

## Troubleshooting

### "No ideas found in input file"
**Cause**: Input JSON missing `ideas` array or empty.
**Fix**: Verify input file structure matches content-generator output format.

### "Missing required field 'X' in idea"
**Cause**: Idea missing `id`, `pillar`, `core_message`, or `variants.generic`.
**Fix**: Ensure input was generated by content-generator with all required fields.

### Prompts seem generic or off-theme
**Cause**: Pillar style config missing or visual keyword extraction not matching content.
**Fix**: Ensure `pillar_styles.json` exists with comprehensive style guidelines. Review `prompt_generator.py` keyword extraction logic.

### Excessive warnings about fallbacks
**Cause**: Input ideas lack platform-specific adaptations.
**Fix**: Expected behavior if using generic variants. To reduce warnings, ensure content-generator produces platform adaptations.

### Midjourney parameters not working
**Cause**: Midjourney version or parameter syntax changed.
**Fix**: Update `--v` version number and parameter format in `prompt_generator.py` to match current Midjourney specs.

## Advanced: Integration Hooks

### Image Generation Automation Hook (Future)

**Status**: Prompts currently generated as text files for manual use.

**Planned**: Automated image generation from prompts using AI APIs. Implementation approach:

```python
def generate_images_from_prompts(bundle_root: Path, manifest: dict) -> dict:
    """
    Generate images from AI prompts using Midjourney/DALL-E/Stable Diffusion API.

    Args:
        bundle_root: Path to bundle directory
        manifest: Loaded manifest.json with image_prompts paths

    Returns:
        Dictionary mapping prompt files to generated image paths
    """
    # Read core_prompt.txt and variations
    # Call AI image generation API (e.g., Midjourney CLI, OpenAI DALL-E 3)
    # Save generated images to bundle/images/generated/
    # Update manifest with image paths
    pass
```

**Integration points**:
- `manifest.json` already includes `image_prompts` paths
- `core_prompt.json` includes metadata (pillar, aspect ratio, parameters)
- CLI wrapper: `cat core_prompt.txt | midjourney-cli --output bundle/images/generated/`

### Autopost Hook (Future)

For future integration with posting automation, implement `autopost_hook()` in a separate module:

```python
def autopost_hook(bundle_root: Path, manifest: dict) -> bool:
    """
    Post content to platforms using bundle manifest.

    Args:
        bundle_root: Path to bundle directory
        manifest: Loaded manifest.json dict

    Returns:
        True if posting succeeded, False otherwise
    """
    # Implementation: read copy/images, call platform APIs
    pass
```

Call after bundle creation in `produce.py` if `--autopost` flag added.

### Batch Processing

For multiple ideas, use shell loop:

```bash
for idea_file in output/generated_ideas/*.json; do
  python3 scripts/produce.py --input "$idea_file" --no-zip
done
```

Or create wrapper script reading from directory.

## Performance Notes

- **Target**: < 10 seconds per idea (typical: 3-5 seconds)
- **AI prompt generation**: ~1-2 seconds for core + variations
- **Copy processing**: < 1 second
- **Zip creation**: ~1-2 seconds depending on bundle size

Significantly faster than previous image generation approach (~30 seconds → ~5 seconds per idea).

Use `--no-zip` for batch workflows to save ~1-2 seconds per bundle.

## Resources

This skill includes three types of bundled resources:

### scripts/

Executable Python modules for content production:

- **`produce.py`**: Main CLI entry point; orchestrates workflow, validates inputs/outputs
- **`copy_processor.py`**: Text normalization, platform-specific trimming, CTA insertion
- **`prompt_generator.py`**: AI image prompt generation with pillar-aware styling and Midjourney optimization

Execute `produce.py` directly. The other modules are imported as libraries.

### config/

Required configuration files within the skill:

- **`pillar_styles.json`**: Pillar visual guidelines for AI prompt generation
- **`platforms.json`**: Platform-specific constraints (character limits, optimal lengths, etc.)

### references/

*(Empty for this skill - no reference documentation needed)*

### assets/

*(Not currently used - reserved for future image generation automation)*

---

**Note on MVP Scope**: This skill focuses on content production only. It does NOT:
- Ingest or select ideas (handled by content-generator skill)
- Generate actual images (produces AI prompts for manual/future automated generation)
- Post to platforms (autopost hook stubbed for future)
- Store data in databases (filesystem outputs only)
