# Content Generation Pipeline - Claude Code Implementation Notes

## Project Context

This is a content idea generation pipeline for Zenlit, a safe driving token rewards platform targeting gig economy drivers. The system transforms raw input data (Reddit stories, seasonal events, news feeds) into platform-optimized social media content ideas.

## Implementation Details

### Two-Skill Architecture

The pipeline uses two Claude Code skills that work together:

#### 1. idea-parser skill
**Location**: `.claude/skills/idea-parser/skill.md`

**Purpose**: Extract individual content ideas from raw input files

**Key Features**:
- **Batch parsing mode**: Parses ALL ideas in a file, not one-at-a-time (critical requirement)
- **Reddit-specific parsing**: Handles `**N. Title**` pattern with metadata bullets
- **Structured output**: Creates `idea_NNN.json` files with zero-padded numbers
- **Metadata extraction**: Captures source, engagement metrics, URLs, key points

**Important Pattern**:
```
**1. Story Title**
* **Source:** r/subreddit
* **Engagement:** X upvotes, Y comments
* **Appeal:** Key points
* **Content Angle:** Marketing angle
```

**Output Structure**:
```json
{
  "id": "idea_001",
  "source_file": "filename.md",
  "category": "human_insights",
  "title": "Story title",
  "raw_text": "Full text",
  "key_points": ["point1", "point2"],
  "href": "https://reddit.com/...",
  "metadata": {
    "engagement": "6,199 upvotes, 246 comments",
    "source_type": "reddit",
    "subreddit": "r/doordash"
  },
  "extracted_date": "2025-10-24"
}
```

#### 2. content-generator skill
**Location**: `.claude/skills/content-generator/skill.md`

**Purpose**: Synthesize parsed ideas with business pillars to create content

**Key Features**:
- **Idea Selection Strategy**: Four modes (random, sequential, specific, batch)
- **Usage Tracking**: MANDATORY `.idea_NNN.used` markers prevent repetition
- **LLM Synthesis**: Intelligent content generation, not string concatenation
- **Platform Adaptation**: Optimizes for LinkedIn, TikTok, Twitter, Facebook, Instagram, Reddit
- **Segment Variants**: Generic + gig driver-specific versions (~30% of ideas)

**Configuration Files** (in `.claude/skills/content-generator/config/`):
- `pillars.json`: 6 content pillars (safety_education, token_community, advocacy_impact, product_tips, seasonal_trending, entertainment_humor)
- `platforms.json`: Platform specs with character limits, tone, audience
- `segments.json`: Target segment (gig economy drivers) with pain points

### Critical Implementation Requirements

#### MUST: Batch Parsing
The idea-parser MUST parse ALL ideas in one run. Do NOT parse one idea and stop.

Pattern to match in Reddit file:
```regex
\*\*(\d+)\\\.\s+([^\*]+?)\*\*
```

#### MUST: Usage Tracking
The content-generator MUST create `.idea_NNN.used` marker files after generation.

Marker format:
```json
{
  "used_date": "2025-10-24",
  "used_timestamp": "2025-10-24T18:15:21.603861",
  "generated_file": "content_idea_2025-10-24_1815.json",
  "idea_id": "idea_001"
}
```

#### MUST: Filter Used Ideas
When selecting ideas, filter out those with `.idea_NNN.used` markers:

```python
unused_ideas = []
for idea_file in idea_files:
    idea_id = idea_file.stem  # e.g., "idea_001"
    marker = parsed_dir / f".{idea_id}.used"
    if not marker.exists():
        unused_ideas.append(idea_file)
```

#### MUST: Save JSON Output
Content generator MUST save output to `output/generated_ideas/content_idea_YYYY-MM-DD_HHMM.json`

### Directory Structure

```
Content/
├── .claude/skills/           # Claude Code skills
│   ├── idea-parser/
│   │   └── skill.md
│   └── content-generator/
│       ├── skill.md
│       └── config/           # Configuration files
├── input/                    # Raw input data (READ-ONLY)
│   ├── human_insights/
│   │   ├── *.md             # Raw files
│   │   └── parsed/          # Parsed JSON files
│   ├── seasonal/
│   └── external_feeds/
└── output/                   # Generated content
    └── generated_ideas/
```

### File Naming Conventions

**Parsed ideas**: `idea_001.json`, `idea_002.json`, ... `idea_100.json`
- Zero-padded for proper sorting
- Sequential numbering from source file

**Usage markers**: `.idea_001.used`, `.idea_002.used`
- Hidden files (starts with `.`)
- Same directory as parsed ideas
- JSON content with timestamp and reference

**Generated content**: `content_idea_2025-10-24_1815.json`
- Date-based naming
- Optional timestamp or descriptive suffix to avoid conflicts
- Stored in `output/generated_ideas/`

### Input Folder Protection Policy

⚠️ **CRITICAL**: The skills NEVER modify the input folder without explicit human approval.

- Skills operate in READ-ONLY mode for all input sources
- Never create, edit, or delete files in `input/` automatically
- Only exception: Creating `parsed/` subdirectories and files
- Usage markers (`.idea_NNN.used`) are created in `parsed/` directory

### Testing Approach

When testing implementations:

1. **Parse a sample**: Test with first 10 ideas to verify pattern matching
2. **Check output**: Verify JSON structure matches specification
3. **Test selection**: Ensure random selection picks different ideas
4. **Verify markers**: Confirm `.idea_NNN.used` files are created
5. **Test filtering**: Ensure used ideas are excluded from selection
6. **Clean up**: Remove interim test scripts (keep only idea outputs)

### Common Pitfalls

❌ **Don't**: Parse one idea and stop
✅ **Do**: Parse ALL numbered ideas in the file

❌ **Don't**: Use string concatenation for content synthesis
✅ **Do**: Use LLM-style intelligent synthesis with context

❌ **Don't**: Forget to create usage markers
✅ **Do**: ALWAYS create `.idea_NNN.used` after generation

❌ **Don't**: Reuse the same idea repeatedly
✅ **Do**: Filter out used ideas during selection

❌ **Don't**: Modify input folder without permission
✅ **Do**: Only write to `parsed/` and `output/` directories

### Performance Notes

- **100 ideas parsed**: ~30 seconds on standard hardware
- **Content generation**: ~5-10 seconds per idea (with LLM synthesis)
- **File I/O**: Minimal - JSON files are small (<5KB each)
- **Memory**: Low - processes one idea at a time

### Current State (as of 2025-10-24)

**Completed**:
- ✅ Batch parsing capability in idea-parser skill
- ✅ Reddit-specific parsing patterns documented
- ✅ 100 Reddit stories parsed to individual JSON files
- ✅ Idea selection strategy in content-generator skill
- ✅ Usage tracking system with `.idea_NNN.used` markers
- ✅ Four selection modes (random, sequential, specific, batch)
- ✅ Tested and validated with real data

**Status**:
- 100 parsed ideas in `input/human_insights/parsed/`
- 2 ideas marked as used during testing
- 98 unused ideas available for content generation

**Not Yet Implemented**:
- CRON job for daily automated generation
- Performance feedback loop
- Analytics dashboard
- Additional input sources (seasonal, external feeds)

### Future Enhancements

1. **CRON Automation**: Daily content generation at 6:00 AM
2. **Feedback Loop**: Track which ideas generate best-performing content
3. **Analytics Dashboard**: Visualize idea usage and content performance
4. **Multi-Source**: Add seasonal calendar and external feeds
5. **Learning System**: Adjust pillar selection based on historical performance

### Troubleshooting

**No unused ideas found**:
- Check: Do `.idea_*.used` files exist for all ideas?
- Solution: Delete usage markers to reset, or add new input ideas

**Parsing found 0 ideas**:
- Check: Regex pattern matches the file format
- Common issue: Escaped backslash in markdown (`\\.` vs `.`)
- Solution: Test regex on sample text first

**Content generation reuses same idea**:
- Check: Is `.idea_NNN.used` marker being created?
- Check: Is selection code filtering based on markers?
- Solution: Verify marker creation and filtering logic

**Output file not found**:
- Check: Does `output/generated_ideas/` directory exist?
- Solution: Create directory with `mkdir -p output/generated_ideas`

### Maintenance

**Weekly**:
- Check usage marker count vs. available ideas
- Review generated content quality
- Monitor for duplicate content

**Monthly**:
- Add new input sources (Reddit stories, seasonal events)
- Review pillar alignment of generated content
- Analyze which ideas performed best

**Quarterly**:
- Refresh configuration files (pillars, platforms, segments)
- Review and update skill documentation
- Optimize selection algorithms based on performance data

## Key Learnings

1. **Batch processing is essential**: Parsing one-at-a-time defeats the purpose
2. **Usage tracking prevents fatigue**: Mandatory markers ensure content variety
3. **Configuration files enable flexibility**: Easy to update without changing code
4. **LLM synthesis > templates**: Intelligent synthesis produces better content than string concatenation
5. **Skills are reusable**: Same skills work across different content categories

## Related Documentation

- `README.md`: User-facing project documentation
- `pipeline.md`: Conceptual framework and design decisions
- `.claude/skills/idea-parser/skill.md`: Parser skill documentation
- `.claude/skills/content-generator/skill.md`: Generator skill documentation
