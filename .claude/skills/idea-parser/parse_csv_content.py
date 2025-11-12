#!/usr/bin/env python3
"""
Parse ZENLIT SMM CONTENT PLAN.csv into individual idea JSON files.
Creates idea_101.json, idea_102.json, etc. (continuing from existing idea_100.json)
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def parse_csv_to_ideas(csv_path, output_dir, start_id=101):
    """Parse CSV file with Category and Copy columns into individual idea JSON files."""

    csv_path = Path(csv_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ideas_created = []
    idea_num = start_id

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            category = row.get('Category', '').strip()
            copy = row.get('Copy', '').strip()

            # Skip empty rows
            if not category and not copy:
                continue
            if not copy:  # Skip rows with only category
                continue

            # Map CSV categories to content pillars
            pillar_mapping = {
                'Events & Holidays': 'seasonal_trending',
                'World News': 'seasonal_trending',
                'News': 'seasonal_trending',
                'AZ related news': 'seasonal_trending',
                'Zenlit News': 'product_tips',
                'Education': 'safety_education',
                'Token Stories': 'token_community',
                'Safety & Analytics': 'safety_education',
                'Interactive': 'entertainment_humor',
                'Friday night travel tips': 'safety_education'
            }

            # Extract hashtags and URLs from copy
            hashtags = []
            urls = []
            clean_copy = copy

            # Simple hashtag extraction
            import re
            hashtag_pattern = r'#\w+'
            hashtags = re.findall(hashtag_pattern, copy)

            # Extract key points from the copy (first sentence or main message)
            sentences = copy.split('.')
            key_points = [s.strip() for s in sentences[:2] if s.strip()]

            # Create title from first sentence or first 50 chars
            title = sentences[0][:80] if sentences else copy[:80]
            if len(title) == 80 and len(copy) > 80:
                title += "..."

            # Build idea JSON structure
            idea = {
                "id": f"idea_{idea_num:03d}",
                "source_file": csv_path.name,
                "category": "human_insights",
                "pillar_hint": pillar_mapping.get(category, "safety_education"),
                "csv_category": category,
                "title": title,
                "raw_text": copy,
                "key_points": key_points if key_points else [copy[:100]],
                "href": None,  # No URLs in this dataset
                "hashtags": hashtags,
                "metadata": {
                    "source_type": "csv_content_plan",
                    "category": category,
                    "format": "ready_copy"  # This is pre-written copy, not a story
                },
                "extracted_date": datetime.now().strftime("%Y-%m-%d")
            }

            # Write JSON file
            output_file = output_dir / f"idea_{idea_num:03d}.json"
            with open(output_file, 'w', encoding='utf-8') as out_f:
                json.dump(idea, out_f, indent=2, ensure_ascii=False)

            ideas_created.append(idea['id'])
            idea_num += 1

    return ideas_created


if __name__ == "__main__":
    csv_file = Path("input/human_insights/ZENLIT SMM CONTENT PLAN.csv")
    output_directory = Path("input/human_insights/parsed")

    # Check what's the highest existing idea number
    existing_ideas = list(output_directory.glob("idea_*.json"))
    if existing_ideas:
        max_num = max(int(f.stem.split('_')[1]) for f in existing_ideas)
        start_id = max_num + 1
    else:
        start_id = 1

    print(f"Starting from idea_{start_id:03d}")

    ideas = parse_csv_to_ideas(csv_file, output_directory, start_id=start_id)

    print(f"\n✓ Parsed {len(ideas)} ideas from CSV")
    print(f"✓ Created files: {ideas[0]} through {ideas[-1]}")
    print(f"✓ Output directory: {output_directory}")
    print(f"\nTotal ideas now available: {len(list(output_directory.glob('idea_*.json')))}")
