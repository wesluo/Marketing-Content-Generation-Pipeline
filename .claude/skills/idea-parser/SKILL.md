---
name: idea-parser
description: This skill extracts individual content ideas from any text file (Reddit posts, articles, reports, etc.) and stores them as separate JSON files with metadata and source references. This skill should be used when you have input files containing multiple ideas that need to be parsed into discrete, reusable units for content generation.
---

# Idea Parser

## Overview

This skill intelligently extracts individual content ideas from text files of any format and stores them as separate JSON files, preserving source references and metadata for traceability.

## When to Use This Skill

Use this skill when:
- Processing input files with multiple content ideas (like the Reddit stories document)
- Preparing raw input for the content synthesis pipeline
- Need to extract discrete ideas from articles, reports, or any text source
- Want to preserve source attribution and references

## Parsing Process

### 1. Analyze Document Structure

First, identify the structure of the input document:
- **Numbered lists**: Look for patterns like "1.", "2.", etc.
- **Markdown headers**: Sections marked with #, ##, ###
- **Paragraphs**: Natural paragraph breaks
- **Bullet points**: Lists with -, *, or •
- **Custom delimiters**: Any consistent pattern separating ideas

### 2. Batch Parsing Mode (Default)

**CRITICAL: Always parse ALL ideas in a file, not just one.**

When encountering a file with multiple numbered ideas (like the Reddit stories file):

1. **Scan entire file** to identify ALL numbered entries matching the pattern `**N. Title**` or `**N\. Title**`
2. **Extract each story** with its associated metadata (Source, Engagement, Appeal, Content Angle)
3. **Create individual JSON files** for each idea: `idea_001.json`, `idea_002.json`, ... `idea_NNN.json`
4. **Parse ALL ideas in one run** - do not stop after the first one
5. **Report total count** of ideas parsed at completion

#### Reddit File Parsing Pattern

For the Reddit stories file specifically:
- **Title pattern**: `**[number]\. [Title]**` or `**[number]. [Title]**`
- **Metadata extraction**:
  - Source: Look for `* **Source:** r/subreddit`
  - Engagement: Look for `* **Engagement:** X upvotes, Y comments`
  - URL: Extract from markdown link `[text](url)` in Engagement line
  - Appeal: Look for `* **Appeal:** ...`
  - Content Angle: Look for `* **Content Angle:** ...`
- **Stop conditions**: Next numbered entry or end of file
- **Section headers**: Skip markdown headers (##) - these are category markers, not ideas
- **ID numbering**: Use zero-padded numbers (001, 002, etc.) for proper sorting

### 3. Extract Individual Ideas

For each identified section/idea:
- Extract the main text content
- Identify any URLs or references (href links)
- Capture metadata (engagement metrics, dates, author info if available)
- Note key themes or topics mentioned

### 4. Parse URLs and References

Look for and preserve:
- Direct URLs: `https://www.reddit.com/r/...`
- Markdown links: `[text](url)`
- Reference indicators: "Source:", "Via:", "From:"
- Citation patterns

### 5. Generate Output Structure

Create a JSON file for each parsed idea with this structure:

```json
{
  "id": "idea_[number]",
  "source_file": "[original filename]",
  "category": "[seasonal|human_insights|external_feeds]",
  "title": "[extracted title or first line summary]",
  "raw_text": "[full text of this idea]",
  "key_points": ["point1", "point2", "point3"],
  "href": "[source URL if found]",
  "metadata": {
    "engagement": "[likes/upvotes/comments if available]",
    "source_type": "[reddit|article|report|etc]",
    "author": "[if available]",
    "date": "[if available]"
  },
  "extracted_date": "[current date]"
}
```

## File Organization

Store parsed ideas in a `parsed` subdirectory within each category:
```
input/
├── seasonal/
│   └── parsed/
│       └── idea_XXX.json
├── human_insights/
│   └── parsed/
│       └── idea_XXX.json
└── external_feeds/
    └── parsed/
        └── idea_XXX.json
```

Mark processed files with a hidden file marker (e.g., `.filename.processed`) to avoid re-parsing.

## Examples

### Example 1: Parsing Reddit Stories

Input text:
```
**1. DoorDash Driver Crashed While Delivering - Car Upside Down, Still Delivered Food**
* **Source:** r/doordash
* **Engagement:** 6,199 upvotes, 246 comments[reddit](https://www.reddit.com/r/doordash/comments/1g7s8ta/)
* **Appeal:** Shows extreme dedication vs safety
```

Output (idea_001.json):
```json
{
  "id": "idea_001",
  "source_file": "Reddit Stories 100+ Content Ideas for Zenlit.md",
  "category": "human_insights",
  "title": "DoorDash Driver Crashed While Delivering",
  "raw_text": "DoorDash Driver Crashed While Delivering - Car Upside Down, Still Delivered Food",
  "key_points": ["extreme dedication", "safety dilemma", "viral story"],
  "href": "https://www.reddit.com/r/doordash/comments/1g7s8ta/",
  "metadata": {
    "engagement": "6,199 upvotes, 246 comments",
    "source_type": "reddit",
    "subreddit": "r/doordash"
  },
  "extracted_date": "2025-10-24"
}
```

### Example 2: Parsing News Article

Input text:
```
Gas prices have risen 15% this month due to supply chain issues.
Experts predict continued increases through winter.
[Continue reading at Reuters](https://reuters.com/article/123)
```

Output (idea_002.json):
```json
{
  "id": "idea_002",
  "source_file": "news_updates.txt",
  "category": "external_feeds",
  "title": "Gas prices risen 15% this month",
  "raw_text": "Gas prices have risen 15% this month due to supply chain issues...",
  "key_points": ["15% increase", "supply chain", "winter predictions"],
  "href": "https://reuters.com/article/123",
  "metadata": {
    "source_type": "news",
    "publisher": "Reuters"
  },
  "extracted_date": "2025-10-24"
}
```

## Important Notes

- **Preserve ALL source URLs** for attribution
- **Don't modify** the original input files
- **Create unique IDs** for each parsed idea
- **Handle various formats** gracefully
- **Extract as much metadata** as available
- **Group by category** based on source folder