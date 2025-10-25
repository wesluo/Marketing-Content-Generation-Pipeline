# Content Generation Pipeline for Zenlit

A systematic content idea generation pipeline that combines multiple data sources (Reddit stories, seasonal events, external feeds) with business pillars and platform specifications to create engaging social media content for safe driving token rewards platform.

## Overview

This pipeline transforms raw input data into platform-optimized content ideas through two main skills:

1. **idea-parser**: Extracts individual ideas from input files into structured JSON format
2. **content-generator**: Synthesizes parsed ideas with business pillars to create platform-specific content

## Project Structure

```
Content/
├── .claude/
│   └── skills/
│       ├── idea-parser/
│       │   └── skill.md              # Batch parsing skill
│       └── content-generator/
│           ├── skill.md              # Content synthesis skill
│           └── config/
│               ├── pillars.json      # 6 content pillars/themes
│               ├── platforms.json    # Platform specifications
│               └── segments.json     # Target audience segments
├── input/
│   ├── human_insights/
│   │   ├── Reddit Stories 100+ Content Ideas for Zenlit.md
│   │   └── parsed/
│   │       ├── idea_001.json
│   │       ├── idea_002.json
│   │       ├── ...
│   │       ├── idea_100.json
│   │       ├── .idea_001.used       # Usage tracking markers
│   │       └── .idea_002.used
│   ├── seasonal/
│   │   └── parsed/
│   └── external_feeds/
│       └── parsed/
├── output/
│   └── generated_ideas/
│       └── content_idea_YYYY-MM-DD_HHMM.json
├── pipeline.md                       # Conceptual framework & implementation status
└── README.md                         # This file
```

## Quick Start

### 1. Parse Input Ideas

Invoke the `idea-parser` skill to extract individual ideas from input files:

```bash
# In Claude Code, run:
/idea-parser
```

The skill will:
- Scan input files for numbered ideas
- Extract metadata (source, engagement, URLs)
- Create individual JSON files: `idea_001.json`, `idea_002.json`, etc.
- Store in category's `parsed/` directory

### 2. Generate Content

Invoke the `content-generator` skill to create content ideas:

```bash
# In Claude Code, run:
/content-generator

# Or be specific:
"Generate content idea from human-insights"
"Generate 5 content ideas"
"Generate from idea_042"
```

The skill will:
- Randomly select unused idea(s) from parsed pool
- Synthesize with business pillars and platform specs
- Generate generic + segment-specific variants
- Create platform adaptations (LinkedIn, TikTok, Twitter, etc.)
- Mark ideas as used with `.idea_NNN.used` markers
- Save output to `output/generated_ideas/`

## Features

### Batch Parsing
- Parses ALL ideas from input files in one run (not one-at-a-time)
- Supports Reddit-specific patterns: `**N. Title**` with metadata bullets
- Extracts engagement metrics, URLs, and source attribution
- Zero-padded numbering (001, 002) for proper sorting

### Intelligent Idea Selection
Four selection modes:

1. **Random (default)**: Picks random unused idea from pool
2. **Sequential**: Uses lowest numbered unused idea
3. **Specific**: Targets specific idea number
4. **Batch**: Generates from multiple ideas at once

### Usage Tracking
- Automatically marks used ideas with `.idea_NNN.used` files
- Prevents repetition across content calendar
- Tracks generation timestamp and output filename
- Enables analytics on idea performance

### Platform Optimization
Content adapted for each platform's requirements:

- **LinkedIn**: Professional, data-driven (100-300 chars)
- **TikTok**: Catchy, trend-aware (20-60 chars)
- **Twitter**: Timely, concise (100-280 chars)
- **Facebook**: Community-focused (40-80 chars)
- **Instagram**: Visual-first captions
- **Reddit**: Value-driven, non-promotional

### Segment Variants
- Generic version for broad audience
- Gig driver variant (~30% of ideas where relevant)
- Addresses specific pain points (gas costs, night safety, earnings)

## Configuration

### Content Pillars
Six core themes defined in `config/pillars.json`:

1. Safety Education & Best Practices
2. Token Rewards & Community
3. Advocacy & Impact
4. Product Tips & Features
5. Seasonal & Trending Events
6. Entertainment & Humor

### Target Segment
Primary segment: **Gig Economy Drivers** (Uber, Lyft, DoorDash, Instacart)

Pain points:
- High gas costs
- Vehicle wear and tear
- Safety during night deliveries
- Maximizing earnings per hour
- Insurance concerns

## Current Status

**Parsed Ideas**: 100 Reddit stories ready for content generation
**Used Ideas**: 2 (during testing)
**Available Ideas**: 98 unused ideas in pool
**Output Format**: Structured JSON with pillar alignment, variants, and platform adaptations

## Usage Tracking Analytics

Check usage status:

```bash
# Count total ideas
ls -1 input/human_insights/parsed/idea_*.json | wc -l

# Count used ideas
ls -1 input/human_insights/parsed/.idea_*.used | wc -l

# List unused ideas (Python)
python3 << 'EOF'
from pathlib import Path
parsed_dir = Path("input/human_insights/parsed")
ideas = set(f.stem for f in parsed_dir.glob("idea_*.json"))
used = set(f.stem[1:-5] for f in parsed_dir.glob(".idea_*.used"))
unused = ideas - used
print(f"Unused: {len(unused)}")
print(sorted(list(unused))[:10], "...")
EOF
```

## Output Format

Generated content ideas are saved as JSON:

```json
{
  "generated_date": "2025-10-24",
  "ideas": [
    {
      "id": "idea_001",
      "pillar": "safety_education",
      "source_idea": "idea_001",
      "source_href": "https://reddit.com/...",
      "base_idea": "Original story title",
      "variants": {
        "generic": "Content for general audience",
        "gig_driver": "Content optimized for gig drivers"
      },
      "platform_adaptations": {
        "linkedin": "Professional version",
        "tiktok": "Short catchy version",
        "twitter": "Timely tweet",
        "facebook": "Community post",
        "instagram": "Visual caption"
      },
      "hashtags": ["#SafeDriving", "#RoadSafety"],
      "score": 8.5,
      "score_rationale": "Highly timely, addresses pain point"
    }
  ]
}
```

## Next Steps

- [ ] Configure CRON job for daily automated generation
- [ ] Implement performance feedback loop
- [ ] Add analytics dashboard for idea usage patterns
- [ ] Expand input sources (seasonal calendar, external feeds)
- [ ] Track content performance to inform future selections

## Contributing

When adding new input sources:

1. Place raw files in appropriate category folder (`input/seasonal/`, `input/human_insights/`, `input/external_feeds/`)
2. Run `idea-parser` skill to extract individual ideas
3. Parser creates `parsed/` subdirectory with individual JSON files
4. Content generator automatically discovers new parsed ideas

## Skills Documentation

Detailed documentation for each skill:

- **idea-parser**: `.claude/skills/idea-parser/skill.md`
- **content-generator**: `.claude/skills/content-generator/skill.md`

## Pipeline Conceptual Framework

See `pipeline.md` for:
- System philosophy and design decisions
- Multi-trigger approach (scheduled, threshold, manual)
- CRON implementation details
- Quality control mechanisms
- Feedback and learning strategy
