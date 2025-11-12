#!/usr/bin/env python3
"""
URL Quote Extractor - Helper script for content-producer skill

MANUAL QUOTE EXTRACTION APPROACH:
Since WebFetch doesn't work for many sites (Reddit, etc.), this script uses a workaround:

1. Looks for a pre-created quotes file: `input/url_quotes/<idea_id>.json`
2. If found, loads and returns those quotes
3. If not found, returns empty array with instructions for manual extraction

WORKFLOW:
- User visits the source URL manually
- User creates `input/url_quotes/<idea_id>.json` with extracted quotes
- Producer reads quotes from this file when generating bundle

This allows manual curation of golden quotes while maintaining automation for the rest.
"""

import sys
import json
from pathlib import Path


def load_manual_quotes(url: str, idea_id: str = None) -> list:
    """
    Load manually curated quotes from JSON file.

    Args:
        url: Source URL (used for reference only)
        idea_id: Idea identifier to find corresponding quotes file

    Returns:
        List of quote dictionaries or empty list if not found
    """
    # Determine quotes directory
    quotes_dir = Path("input/url_quotes")

    if not quotes_dir.exists():
        return []

    # Try to find quotes file
    # Format: idea_NNN.json or url_hash.json
    if idea_id:
        quote_file = quotes_dir / f"{idea_id}.json"
        if quote_file.exists():
            try:
                with open(quote_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('quotes', [])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to parse {quote_file}: {e}", file=sys.stderr)
                return []

    return []


def main():
    if len(sys.argv) < 2:
        print("Error: URL parameter required", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    idea_id = sys.argv[2] if len(sys.argv) > 2 else None

    # Try to load manual quotes
    quotes = load_manual_quotes(url, idea_id)

    if quotes:
        print(json.dumps(quotes, indent=2))
    else:
        # No quotes found - output instructions
        print(f"# No quotes file found for {idea_id or 'URL'}", file=sys.stderr)
        print(f"# To add quotes manually:", file=sys.stderr)
        print(f"# 1. Visit: {url}", file=sys.stderr)
        print(f"# 2. Extract 3-5 impactful quotes", file=sys.stderr)
        if idea_id:
            print(f"# 3. Create: input/url_quotes/{idea_id}.json", file=sys.stderr)
            print(f"# Format:", file=sys.stderr)
            print(f'#   {{"url": "{url}", "quotes": [{{"text": "...", "source": "...", "impact": "..."}}]}}', file=sys.stderr)

        # Return empty array
        print("[]")


if __name__ == "__main__":
    main()
