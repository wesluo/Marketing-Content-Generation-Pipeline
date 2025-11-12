#!/usr/bin/env python3
"""
URL content extractor for content-producer skill.
Fetches and extracts valuable quotes/content from source URLs.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List


def fetch_url_content(url: str, idea_id: str = None) -> Optional[str]:
    """
    Load manually curated quotes by calling extract_url_quotes.py helper.

    Args:
        url: The URL (for reference)
        idea_id: Idea identifier to find quotes file

    Returns:
        Extracted quotes as JSON string, or None if not found
    """
    try:
        script_dir = Path(__file__).parent
        extract_script = script_dir / "extract_url_quotes.py"

        if not extract_script.exists():
            print(f"⚠️  URL extractor script not found at {extract_script}", file=sys.stderr)
            return None

        # Call the Python helper script with idea_id
        args = ["python3", str(extract_script), url]
        if idea_id:
            args.append(idea_id)

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"⚠️  Failed to load quotes: {result.stderr}", file=sys.stderr)
            return None

        output = result.stdout.strip()

        if not output or output == "" or output == "[]":
            # Print instructions from stderr if available
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return None

        return output

    except subprocess.TimeoutExpired:
        print(f"⚠️  Quote loading timed out", file=sys.stderr)
        return None
    except Exception as e:
        print(f"⚠️  Error loading quotes: {e}", file=sys.stderr)
        return None


def extract_golden_quotes(url: str, idea_id: str = None) -> List[Dict]:
    """
    Load manually curated golden quotes from file.

    Args:
        url: The source URL
        idea_id: Idea identifier to find quotes file

    Returns:
        List of quote dictionaries with text, source, and impact
    """
    content = fetch_url_content(url, idea_id)

    if not content:
        return []

    try:
        # Try to parse as JSON
        quotes = json.loads(content)

        # Validate structure
        if not isinstance(quotes, list):
            return []

        # Filter and validate each quote
        valid_quotes = []
        for quote in quotes:
            if isinstance(quote, dict) and 'text' in quote:
                valid_quotes.append({
                    'text': quote.get('text', ''),
                    'source': quote.get('source', 'unknown'),
                    'impact': quote.get('impact', '')
                })

        return valid_quotes

    except json.JSONDecodeError:
        # If not valid JSON, treat as plain text and extract manually
        print(f"⚠️  URL content not in expected JSON format", file=sys.stderr)
        return []


def enrich_copy_with_quotes(original_copy: str, quotes: List[Dict], max_quotes: int = 1) -> str:
    """
    Enrich copy with relevant quotes from the source.

    Args:
        original_copy: The original platform copy
        quotes: List of quote dictionaries
        max_quotes: Maximum number of quotes to add (default: 1)

    Returns:
        Enriched copy with quote(s) appended
    """
    if not quotes:
        return original_copy

    # Select top quotes (already sorted by impact during extraction)
    selected_quotes = quotes[:max_quotes]

    enriched = original_copy

    for quote in selected_quotes:
        quote_text = quote['text']
        # Format as a quoted addition
        enriched += f'\n\n"{quote_text}"'

    return enriched


def format_quotes_for_manifest(quotes: List[Dict]) -> Dict:
    """
    Format extracted quotes for inclusion in manifest.

    Args:
        quotes: List of quote dictionaries

    Returns:
        Formatted dictionary for manifest
    """
    return {
        'extracted': True,
        'count': len(quotes),
        'quotes': quotes
    }


if __name__ == '__main__':
    # CLI for testing
    import argparse

    parser = argparse.ArgumentParser(description='Extract golden quotes from a URL')
    parser.add_argument('url', help='URL to extract from')
    parser.add_argument('--output', help='Output JSON file (optional)')

    args = parser.parse_args()

    quotes = extract_golden_quotes(args.url)

    output = {
        'url': args.url,
        'quotes': quotes,
        'count': len(quotes)
    }

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Saved {len(quotes)} quotes to {args.output}")
    else:
        print(json.dumps(output, indent=2))
