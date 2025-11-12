# URL Quotes Directory

This directory contains manually curated quotes extracted from source URLs for content enrichment.

## Purpose

When the content-producer skill's `--extract-quotes` flag is enabled, it looks for quote files here to enrich the generated content bundles with authentic, impactful statements from original sources.

## File Format

Each file should be named `<idea_id>.json` (e.g., `idea_037.json`) and contain:

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

## Quote Structure

Each quote object should include:
- `text`: The actual quote text (verbatim from source)
- `source`: Where it came from ("main post", "comment", "article", etc.)
- `impact`: Brief explanation of why this quote is valuable for content creation

## Workflow

1. Content-generator creates an idea with `source_idea.href` field
2. Note the `idea_id` (e.g., "idea_037")
3. Visit the source URL
4. Read through and identify 3-5 golden quotes
5. Create `<idea_id>.json` in this directory
6. Run content-producer with `--extract-quotes` flag
7. Quotes will be included in the bundle manifest and report

## Example

For `idea_037` about the Toronto Uber crash:

**File**: `idea_037.json`

```json
{
  "url": "https://www.reddit.com/r/toronto/comments/8816dw/uber_driver_charged_in_fatal_gardiner_crash/",
  "quotes": [
    {
      "text": "No excuse is worth it for safety",
      "source": "comment",
      "impact": "Powerful statement about safety priorities"
    },
    {
      "text": "Uber Driver Charged in Fatal Gardiner Crash",
      "source": "main post title",
      "impact": "Clear headline establishes severity"
    }
  ]
}
```

## Benefits

- **Quality Control**: Manual selection ensures only impactful quotes
- **Works Everywhere**: No API or site blocking issues (Reddit, news sites, etc.)
- **Context Awareness**: Human judgment ensures quotes fit brand voice
- **Reliable**: No dependency on WebFetch or external services
