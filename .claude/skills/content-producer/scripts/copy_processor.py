#!/usr/bin/env python3
"""
Copy processor for content-producer skill.
Handles text normalization, length validation, and CTA insertion.
"""

import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, Optional


# Cache for platform constraints
_PLATFORM_CONSTRAINTS_CACHE: Optional[Dict] = None


def _validate_platform_config(config: dict) -> list[str]:
    """
    Validate platform config structure.

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(config, dict):
        errors.append("Config must be a dictionary")
        return errors

    if "platforms" not in config:
        errors.append("Missing required 'platforms' key")
        return errors

    if not isinstance(config["platforms"], list):
        errors.append("'platforms' must be a list")
        return errors

    for i, platform in enumerate(config["platforms"]):
        if not isinstance(platform, dict):
            errors.append(f"Platform {i} must be a dictionary")
            continue

        if "id" not in platform:
            errors.append(f"Platform {i} missing 'id' field")

        if "characteristics" not in platform:
            errors.append(f"Platform {i} ({platform.get('id', 'unknown')}) missing 'characteristics' field")

    return errors


def _load_platform_constraints() -> Dict:
    """
    Load platform constraints from config/platforms.json.
    Falls back to hardcoded defaults if config not found.
    """
    global _PLATFORM_CONSTRAINTS_CACHE

    if _PLATFORM_CONSTRAINTS_CACHE is not None:
        return _PLATFORM_CONSTRAINTS_CACHE

    # Try to load from config
    config_path = Path(__file__).parent.parent / "config" / "platforms.json"

    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                platforms_data = json.load(f)

            # Validate config structure
            validation_errors = _validate_platform_config(platforms_data)
            if validation_errors:
                print(f"⚠️  Platform config validation errors: {', '.join(validation_errors)}")
                print(f"⚠️  Falling back to hardcoded defaults")
            else:
                # Config is valid, extract constraints
                constraints = {}
                for platform in platforms_data.get("platforms", []):
                    platform_id = platform["id"]
                    optimal = platform.get("characteristics", {}).get("optimal_length", {})
                    constraints[platform_id] = optimal
                _PLATFORM_CONSTRAINTS_CACHE = constraints
                return constraints
        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON in platforms.json: {e}")
            print(f"⚠️  Falling back to hardcoded defaults")
        except Exception as e:
            print(f"⚠️  Error loading platform config: {e}")
            print(f"⚠️  Falling back to hardcoded defaults")

    # Fallback to hardcoded defaults
    _PLATFORM_CONSTRAINTS_CACHE = {
        "facebook": {"text": "40-80 characters"},
        "instagram": {"caption": "125-150 characters visible"},
        "reddit": {"title": "Clear and descriptive"},
    }
    return _PLATFORM_CONSTRAINTS_CACHE


def _parse_char_range(text: str) -> tuple[int, int]:
    """Parse character range like '40-80 characters' to (40, 80)."""
    import re
    match = re.search(r'(\d+)-(\d+)', text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


def normalize_text(text: str) -> str:
    """
    Normalize UTF-8 text: remove control characters, normalize whitespace.
    """
    if not text:
        return ""

    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)

    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t')

    # Normalize whitespace: multiple spaces to single, trim lines
    lines = [' '.join(line.split()) for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)

    return text.strip()


def extract_reddit_title(text: str, max_chars: int = 140) -> str:
    """
    Extract Reddit title from text: first sentence or first 120 chars.
    Remove hashtags and CTAs. Hard cap at max_chars.
    """
    text = normalize_text(text)

    # Remove hashtags
    text = re.sub(r'#\w+', '', text)

    # Remove common CTA patterns
    cta_patterns = [
        r'\[CTA_PLACEHOLDER\]',
        r'Learn more:.*',
        r'Click here.*',
        r'Visit.*http\S+',
        r'Check out.*',
    ]
    for pattern in cta_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    text = normalize_text(text)  # Re-normalize after removals

    # Extract first sentence
    sentences = re.split(r'[.!?]+', text)
    if sentences:
        title = sentences[0].strip()
    else:
        title = text[:120]

    # Hard cap
    if len(title) > max_chars:
        title = title[:max_chars-3] + '...'

    return title


def trim_copy(text: str, target_min: int, target_max: int,
              soft_cap: int, hard_cap: int) -> tuple[str, bool]:
    """
    Trim copy to platform limits.

    Returns:
        (trimmed_text, was_trimmed)
    """
    text = normalize_text(text)
    was_trimmed = False

    # Within target range - no action needed
    if target_min <= len(text) <= target_max:
        return text, False

    # Exceeds soft cap - trim with ellipsis
    if len(text) > soft_cap:
        text = text[:soft_cap-3] + '...'
        was_trimmed = True

    # Hard cap enforcement
    if len(text) > hard_cap:
        text = text[:hard_cap]
        was_trimmed = True

    return text, was_trimmed


def process_facebook_copy(text: str, cta: str = None, source_href: str = None) -> tuple[str, bool]:
    """
    Process Facebook copy: normalize, add CTA if applicable, trim.

    Platform constraints (from config or defaults):
    - Target: 40-80 chars
    - Soft trim: 120 chars with ellipsis
    - Hard cap: 500 chars

    Returns:
        (processed_text, was_trimmed)
    """
    text = normalize_text(text)

    # Add CTA if source link exists
    if source_href and cta:
        text = f"{text} {cta}"

    # Load constraints from config
    constraints = _load_platform_constraints()
    fb_config = constraints.get("facebook", {})

    # Parse target range from config (e.g., "40-80 characters")
    target_text = fb_config.get("text", "40-80 characters")
    target_min, target_max = _parse_char_range(target_text)

    # Use defaults if parsing failed
    if target_min == 0:
        target_min, target_max = 40, 80

    # Hardcoded soft/hard caps (not in config)
    return trim_copy(text, target_min=target_min, target_max=target_max, soft_cap=120, hard_cap=500)


def process_instagram_copy(text: str, cta: str = None, source_href: str = None) -> tuple[str, bool]:
    """
    Process Instagram copy: normalize, add CTA if applicable, trim.

    Platform constraints (from config or defaults):
    - Target: 125-150 visible chars
    - Soft trim: 300 chars with ellipsis
    - Hard cap: 2200 chars

    Returns:
        (processed_text, was_trimmed)
    """
    text = normalize_text(text)

    # Add CTA if source link exists
    if source_href and cta:
        text = f"{text} {cta}"

    # Load constraints from config
    constraints = _load_platform_constraints()
    ig_config = constraints.get("instagram", {})

    # Parse target range from config (e.g., "125-150 characters visible")
    caption_text = ig_config.get("caption", "125-150 characters visible")
    target_min, target_max = _parse_char_range(caption_text)

    # Use defaults if parsing failed
    if target_min == 0:
        target_min, target_max = 125, 150

    # Hardcoded soft/hard caps (not in config)
    return trim_copy(text, target_min=target_min, target_max=target_max, soft_cap=300, hard_cap=2200)


def process_reddit_copy(text: str) -> tuple[str, str, bool]:
    """
    Process Reddit copy: extract title and body, no CTA.

    Platform constraints:
    - Title: hard cap 140 chars
    - Body: hard cap 10,000 chars

    Returns:
        (title, body, was_trimmed)
    """
    text = normalize_text(text)
    was_trimmed = False

    # Extract title
    title = extract_reddit_title(text, max_chars=140)

    # Body is the full text, capped
    body = text
    if len(body) > 10000:
        body = body[:10000]
        was_trimmed = True

    return title, body, was_trimmed


def process_linkedin_copy(text: str, cta: str = None, source_href: str = None) -> tuple[str, bool]:
    """
    Process LinkedIn copy: normalize, add CTA if applicable, trim.

    Platform constraints (from config or defaults):
    - Target: 100-300 chars
    - Soft trim: 400 chars with ellipsis
    - Hard cap: 3000 chars

    Returns:
        (processed_text, was_trimmed)
    """
    text = normalize_text(text)

    # Add CTA if source link exists
    if source_href and cta:
        text = f"{text} {cta}"

    # Load constraints from config
    constraints = _load_platform_constraints()
    linkedin_config = constraints.get("linkedin", {})

    # Parse target range from config (e.g., "100-300 characters")
    target_text = linkedin_config.get("text", "100-300 characters")
    target_min, target_max = _parse_char_range(target_text)

    # Use defaults if parsing failed
    if target_min == 0:
        target_min, target_max = 100, 300

    # Hardcoded soft/hard caps (not in config)
    return trim_copy(text, target_min=target_min, target_max=target_max, soft_cap=400, hard_cap=3000)


def process_twitter_copy(text: str, cta: str = None, source_href: str = None) -> tuple[str, bool]:
    """
    Process Twitter/X copy: normalize, add CTA if applicable, trim.

    Platform constraints (from config or defaults):
    - Target: 100-280 chars
    - Soft trim: 280 chars (hard limit for Twitter)
    - Hard cap: 280 chars

    Returns:
        (processed_text, was_trimmed)
    """
    text = normalize_text(text)

    # Add CTA if source link exists
    if source_href and cta:
        text = f"{text} {cta}"

    # Load constraints from config
    constraints = _load_platform_constraints()
    twitter_config = constraints.get("twitter", {})

    # Parse target range from config (e.g., "100-280 characters")
    target_text = twitter_config.get("text", "100-280 characters")
    target_min, target_max = _parse_char_range(target_text)

    # Use defaults if parsing failed
    if target_min == 0:
        target_min, target_max = 100, 280

    # Twitter has a strict 280 char limit
    return trim_copy(text, target_min=target_min, target_max=target_max, soft_cap=280, hard_cap=280)


def process_tiktok_copy(text: str, cta: str = None, source_href: str = None) -> tuple[str, bool]:
    """
    Process TikTok copy: normalize, add CTA if applicable, trim.

    Platform constraints (from config or defaults):
    - Target: 20-60 chars (very short, punchy captions)
    - Soft trim: 100 chars with ellipsis
    - Hard cap: 150 chars

    Returns:
        (processed_text, was_trimmed)
    """
    text = normalize_text(text)

    # Add CTA if source link exists (though rare for TikTok)
    if source_href and cta:
        text = f"{text} {cta}"

    # Load constraints from config
    constraints = _load_platform_constraints()
    tiktok_config = constraints.get("tiktok", {})

    # Parse target range from config (e.g., "20-60 characters")
    target_text = tiktok_config.get("text", "20-60 characters")
    target_min, target_max = _parse_char_range(target_text)

    # Use defaults if parsing failed
    if target_min == 0:
        target_min, target_max = 20, 60

    # TikTok captions are very short
    return trim_copy(text, target_min=target_min, target_max=target_max, soft_cap=100, hard_cap=150)


def generate_alt_text(core_message: str, pillar: str, key_points: list = None) -> str:
    """
    Generate alt text for an image.

    Target: 120-250 chars describing background, overlay text, visual emphasis.
    Avoid marketing language.

    NOTE: This function is currently unused but reserved for future automated image
    generation from AI prompts. When image automation is implemented, this will generate
    accessibility alt text for the generated images.
    """
    # Start with core message
    alt_parts = []

    # Add pillar context if available
    if pillar:
        pillar_context = pillar.replace('_', ' ').title()
        alt_parts.append(f"Image related to {pillar_context}")

    # Add core message
    if core_message:
        alt_parts.append(f"featuring text: \"{core_message}\"")

    # Add key points if available (limit to first 2)
    if key_points:
        points = key_points[:2]
        if points:
            alt_parts.append(f"Highlights: {', '.join(points)}")

    alt_text = '. '.join(alt_parts) + '.'

    # Ensure within 120-250 chars
    if len(alt_text) < 120:
        alt_text += " Visual design emphasizes the message with clear typography and brand colors."

    if len(alt_text) > 250:
        alt_text = alt_text[:247] + '...'

    return alt_text
