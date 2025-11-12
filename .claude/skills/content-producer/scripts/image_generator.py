#!/usr/bin/env python3
"""
Image generator for content-producer skill.
Creates master images and platform-specific renditions.
"""

import os
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
import textwrap


# Pillar color palette (fallback)
PILLAR_COLORS = {
    'safety_education': '#2563EB',      # Blue
    'token_community': '#7C3AED',       # Purple
    'advocacy_impact': '#DC2626',       # Red
    'product_tips': '#059669',          # Green
    'seasonal_trending': '#F59E0B',     # Amber
    'entertainment_humor': '#EC4899',   # Pink
}

DEFAULT_COLOR = '#6366F1'  # Indigo fallback


def get_pillar_color(pillar_id: str, config_path: str = None) -> str:
    """
    Get color for a pillar from config or fallback palette.
    """
    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
            pillars = config.get('pillars', [])
            for pillar in pillars:
                if pillar.get('id') == pillar_id:
                    return pillar.get('color', DEFAULT_COLOR)

    return PILLAR_COLORS.get(pillar_id, DEFAULT_COLOR)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient(draw: ImageDraw, width: int, height: int, base_color: str):
    """
    Create a subtle gradient background.
    """
    base_rgb = hex_to_rgb(base_color)

    # Create vertical gradient (lighter at top, darker at bottom)
    for y in range(height):
        # Calculate gradient factor (0.0 to 1.0)
        factor = y / height

        # Darken color as we go down
        r = int(base_rgb[0] * (1.0 - factor * 0.3))
        g = int(base_rgb[1] * (1.0 - factor * 0.3))
        b = int(base_rgb[2] * (1.0 - factor * 0.3))

        draw.line([(0, y), (width, y)], fill=(r, g, b))


def wrap_text(text: str, font: ImageFont, max_width: int) -> list[str]:
    """
    Wrap text to fit within max_width pixels.
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def create_master_image(
    core_message: str,
    pillar_id: str,
    output_path: Path,
    size: int = 2048,
    logo_path: str = None,
    config_path: str = None
) -> Path:
    """
    Create a master image (2048x2048 PNG).

    Args:
        core_message: Headline text to display
        pillar_id: Content pillar for color selection
        output_path: Where to save the image
        size: Image dimensions (square)
        logo_path: Optional path to logo image
        config_path: Optional path to pillars config

    Returns:
        Path to created image
    """
    # Create image
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)

    # Get pillar color
    pillar_color = get_pillar_color(pillar_id, config_path)

    # Draw gradient background
    create_gradient(draw, size, size, pillar_color)

    # Text settings
    safe_margin = int(size * 0.1)  # 10% margins
    text_box_width = size - (2 * safe_margin)

    # Try to load a nice font, fall back to default
    try:
        # Try common system fonts
        font_size = int(size * 0.08)  # 8% of image size
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        # Fallback to default
        font = ImageFont.load_default()

    # Wrap text
    lines = wrap_text(core_message, font, text_box_width - int(size * 0.05))

    # Calculate text height
    line_height = int(size * 0.1)
    total_text_height = len(lines) * line_height

    # Draw semi-transparent text box
    text_box_y = int((size - total_text_height) / 2)
    text_box_height = total_text_height + int(size * 0.1)

    # Draw text box background (semi-transparent white)
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        [safe_margin, text_box_y - int(size * 0.05),
         size - safe_margin, text_box_y + text_box_height],
        fill=(255, 255, 255, 230)
    )
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

    # Re-create draw object for text
    draw = ImageDraw.Draw(img)

    # Draw text lines (centered)
    y_offset = text_box_y
    for line in lines:
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (size - text_width) / 2
        draw.text((x, y_offset), line, fill='#1F2937', font=font)  # Dark gray text
        y_offset += line_height

    # Draw logo placeholder or actual logo
    logo_size = int(size * 0.12)
    logo_y = size - safe_margin - logo_size

    if logo_path and os.path.exists(logo_path):
        # Load and resize logo
        logo = Image.open(logo_path)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        # Center logo horizontally
        logo_x = (size - logo_size) // 2
        img.paste(logo, (logo_x, logo_y), logo if logo.mode == 'RGBA' else None)
    else:
        # Draw "LOGO" text placeholder
        try:
            logo_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(logo_size * 0.4))
        except:
            logo_font = ImageFont.load_default()

        bbox = logo_font.getbbox("LOGO")
        logo_text_width = bbox[2] - bbox[0]
        logo_x = (size - logo_text_width) // 2
        draw.text((logo_x, logo_y), "LOGO", fill='#FFFFFF', font=logo_font)

    # Save image
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')

    return output_path


def create_rendition(
    master_path: Path,
    output_path: Path,
    target_size: Tuple[int, int],
    focal_point: Tuple[float, float] = (0.5, 0.5)
) -> Path:
    """
    Create a platform-specific rendition from master image.

    Args:
        master_path: Path to master image
        output_path: Where to save rendition
        target_size: (width, height) for output
        focal_point: (x, y) focal point (0.0-1.0 each) for crop bias

    Returns:
        Path to created rendition
    """
    img = Image.open(master_path)
    original_width, original_height = img.size
    target_width, target_height = target_size

    # Calculate target aspect ratio
    target_aspect = target_width / target_height
    original_aspect = original_width / original_height

    if target_aspect > original_aspect:
        # Target is wider - crop height
        new_width = original_width
        new_height = int(original_width / target_aspect)
    else:
        # Target is taller - crop width
        new_height = original_height
        new_width = int(original_height * target_aspect)

    # Calculate crop box based on focal point
    focal_x = int(original_width * focal_point[0])
    focal_y = int(original_height * focal_point[1])

    # Center crop around focal point
    left = max(0, min(focal_x - new_width // 2, original_width - new_width))
    top = max(0, min(focal_y - new_height // 2, original_height - new_height))
    right = left + new_width
    bottom = top + new_height

    # Crop and resize
    img = img.crop((left, top, right, bottom))
    img = img.resize(target_size, Image.Resampling.LANCZOS)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')

    return output_path


def create_all_renditions(
    master_paths: list[Path],
    bundle_root: Path,
    focal_point: Tuple[float, float] = (0.5, 0.5)
) -> dict:
    """
    Create all platform renditions from master images.

    Returns:
        Dictionary mapping platform -> list of rendition paths
    """
    renditions = {
        'facebook': [],
        'instagram_portrait': [],
        'instagram_square': [],
        'reddit': []
    }

    for i, master_path in enumerate(master_paths, start=1):
        # Facebook: 1200x1200
        fb_path = bundle_root / 'images' / 'facebook' / f'image_{i}.png'
        create_rendition(master_path, fb_path, (1200, 1200), focal_point)
        renditions['facebook'].append(fb_path)

        # Instagram portrait: 1080x1350
        insta_portrait_path = bundle_root / 'images' / 'instagram' / f'portrait_{i}.png'
        create_rendition(master_path, insta_portrait_path, (1080, 1350), focal_point)
        renditions['instagram_portrait'].append(insta_portrait_path)

        # Instagram square: 1080x1080
        insta_square_path = bundle_root / 'images' / 'instagram' / f'square_{i}.png'
        create_rendition(master_path, insta_square_path, (1080, 1080), focal_point)
        renditions['instagram_square'].append(insta_square_path)

        # Reddit: 1200x1200
        reddit_path = bundle_root / 'images' / 'reddit' / f'image_{i}.png'
        create_rendition(master_path, reddit_path, (1200, 1200), focal_point)
        renditions['reddit'].append(reddit_path)

    return renditions
