---
name: content-generator
description: This skill generates content ideas for social media marketing by synthesizing multiple data sources (seasonal events, human insights, external feeds) with business pillars and target segments. This skill should be used when user ask to generate idea or content, generating daily content ideas, preparing content calendars, or creating platform-specific content strategies for a safe driving token rewards platform.
---

# Content Generator

## Overview

This skill enables intelligent content idea generation for social media platforms by combining heterogeneous data sources with established business pillars, platform specifications, and target segment preferences to create both generic and segment-optimized content ideas.

## Workflow Decision Tree

To generate content ideas, follow this decision flow:

1. **Check configurations exist**
   - Verify `pillars.json`, `platforms.json`, and `segments.json` are present
   - Read and parse all configuration files

2. **Gather input sources**
   - Check `input/` folder for available data sources
   - Process seasonal, human insights, and external feeds

3. **Synthesize ideas**
   - Generate 10-15 base ideas combining inputs with pillars
   - Create segment variants for ~30% of ideas where relevant

4. **Format output**
   - Structure ideas with pillar alignment
   - Include platform-specific adaptations
   - Add both generic and segment-optimized versions

5. **CRITICAL: Save output to JSON file**
   - ALWAYS create a JSON file in `output/generated_ideas/` directory
   - Use naming format: `content_idea_YYYY-MM-DD_HHMM.json` or `content_idea_YYYY-MM-DD_descriptive-name.json`
   - For multiple generations per day, use timestamps or descriptive names to avoid conflicts
   - Include all generated ideas in structured JSON format
   - Never skip this step - JSON output is mandatory for workflow integration

## Configuration Files

### Required Configurations

Configuration files are stored in the skill's `config/` directory:

- **config/pillars.json** - Defines 6 content pillars (themes) for all content
- **config/platforms.json** - Specifications for each social media platform
- **config/segments.json** - Target segment definition (currently: gig economy drivers)

To read configurations:
```python
import json
from pathlib import Path

# Config files are in the skill's config directory
config_path = Path(__file__).parent.parent / 'config'

# Load pillars
with open(config_path / 'pillars.json', 'r') as f:
    pillars = json.load(f)

# Load platforms
with open(config_path / 'platforms.json', 'r') as f:
    platforms = json.load(f)

# Load segments
with open(config_path / 'segments.json', 'r') as f:
    segments = json.load(f)
```

## Input Processing

### CRITICAL: Input Folder Protection Policy

⚠️ **This skill NEVER modifies the input folder without explicit human approval**

- The skill operates in READ-ONLY mode for all input sources
- Never creates, edits, or deletes files in the input folder automatically
- If no input files exist, the skill will exit gracefully with a message
- In rare cases, the skill may suggest new input ideas but requires explicit human approval before creating any files

### Data Source Location

Content ideas come from two sources:

1. **Parsed idea files** (preferred):
   - `input/seasonal/parsed/` - Individual idea JSON files
   - `input/human_insights/parsed/` - Individual idea JSON files
   - `input/external_feeds/parsed/` - Individual idea JSON files

2. **Unparsed source files** (requires parsing first):
   - `input/seasonal/` - Raw calendar events, holidays, seasonal trends
   - `input/human_insights/` - Raw team observations, customer feedback, Reddit stories
   - `input/external_feeds/` - Raw news, trending topics, industry updates

### Processing Workflow

1. **Check for parsed ideas first**
   - Look in each category's `parsed/` subdirectory for JSON files
   - These are ready for immediate synthesis

2. **Handle unparsed files**
   - Check for files in category directories (excluding `parsed/` folders)
   - Check for `.filename.processed` markers
   - If unparsed files exist without markers:
     - Invoke the **idea-parser** skill to extract individual ideas
     - Parser will create JSON files in the category's `parsed/` folder
     - Create `.filename.processed` marker to avoid re-parsing

3. **Read parsed ideas for synthesis**
   - Load individual idea JSON files
   - Each contains: title, raw_text, key_points, href, metadata

### Idea Selection Strategy

**CRITICAL: This section is mandatory when multiple parsed ideas are available.**

When multiple parsed ideas exist in a category's `parsed/` directory:

1. **List all available parsed ideas**
   - Scan the category's `parsed/` directory (e.g., `input/human_insights/parsed/`)
   - Identify all `idea_NNN.json` files
   - Check for corresponding `.idea_NNN.used` marker files

2. **Selection modes** (choose based on user request):

   - **Random (default)**: Pick a random unused idea from available pool
     - Filter out ideas with `.idea_NNN.used` markers
     - Randomly select from remaining unused ideas
     - Use when user says: "generate idea from human-insights" or "generate content idea"

   - **Sequential**: Use lowest numbered unused idea
     - Find the first `idea_NNN.json` without a `.idea_NNN.used` marker
     - Use when user says: "generate next idea" or "use next unused idea"

   - **Specific**: Accept parameter to use a particular idea
     - Use when user says: "use idea #25" or "generate from idea_042"
     - Load the specified `idea_NNN.json` file directly

   - **Batch**: Generate from multiple ideas
     - Select N random unused ideas
     - Use when user says: "generate 5 ideas" or "create batch of 10 content ideas"
     - Ensure each selected idea is different

3. **Mark ideas as used (MANDATORY)**:
   - **This step is REQUIRED** after every content generation to prevent repetition
   - After successfully generating content from an idea, create a marker file
   - Marker file naming: `.idea_NNN.used` (e.g., `.idea_001.used`, `.idea_042.used`)
   - Marker file location: Same directory as the idea JSON file (e.g., `input/human_insights/parsed/.idea_001.used`)
   - Marker file content: JSON with timestamp and generation info:
     ```json
     {
       "used_date": "2025-10-24",
       "generated_file": "content_idea_2025-10-24_1430.json",
       "idea_id": "idea_001"
     }
     ```
   - **Never skip this step** - it prevents accidentally reusing the same ideas

4. **Default behavior**:
   - If user says "generate idea from human-insights" → randomly select ONE unused idea
   - If user says "generate 5 ideas" → randomly select 5 different unused ideas
   - If user says "generate from idea_042" → use that specific idea (even if already used)
   - If all ideas are used → notify user and ask whether to:
     - Reset usage markers (delete all `.idea_NNN.used` files)
     - Generate from used ideas anyway
     - Add new input ideas first

5. **Usage tracking benefits**:
   - Prevents repetitive content generation
   - Ensures variety across content calendar
   - Allows tracking which ideas have been converted to content
   - Enables usage analytics (e.g., "Which ideas generated best content?")

### Example Selection Workflow

**Scenario 1: Random selection (default)**
```python
import os
import json
import random
from pathlib import Path

parsed_dir = Path("input/human_insights/parsed")
idea_files = list(parsed_dir.glob("idea_*.json"))

# Filter out used ideas
unused_ideas = []
for idea_file in idea_files:
    idea_num = idea_file.stem  # e.g., "idea_001"
    marker = parsed_dir / f".{idea_num}.used"
    if not marker.exists():
        unused_ideas.append(idea_file)

# Select random unused idea
if unused_ideas:
    selected = random.choice(unused_ideas)
    print(f"Selected: {selected.name}")
else:
    print("All ideas have been used!")
```

**Scenario 2: Mark idea as used**
```python
from datetime import date
import json
from pathlib import Path

def mark_idea_used(idea_id, generated_file, parsed_dir):
    """Create usage marker file"""
    marker_path = parsed_dir / f".{idea_id}.used"
    marker_data = {
        "used_date": str(date.today()),
        "generated_file": generated_file,
        "idea_id": idea_id
    }
    with open(marker_path, 'w') as f:
        json.dump(marker_data, f, indent=2)
    print(f"Marked {idea_id} as used")

# After generating content from idea_001
mark_idea_used("idea_001", "content_idea_2025-10-24_1430.json",
               Path("input/human_insights/parsed"))
```

## Content Synthesis Using LLM

### LLM-Based Synthesis Process

Instead of robotic string concatenation, use intelligent LLM synthesis:

1. **Read parsed idea** from JSON file
2. **Load configurations** (pillars, platforms, segments)
3. **Invoke LLM synthesis** with structured prompt
4. **Generate intelligent variations** based on context and meaning

### LLM Synthesis Prompt Template

```
Given this parsed content idea:
[Insert JSON content of parsed idea]

Available content pillars:
[Insert pillars from config/pillars.json]

Platform requirements:
[Insert relevant platforms from config/platforms.json with character limits]

Target segment information:
[Insert segment data from config/segments.json]

Please synthesize this into a content idea by:

1. **Select the most appropriate pillar** based on the idea's theme and message
2. **Create a core message** that connects the idea to our safe driving token platform
3. **Generate variations**:
   - Generic version: Suitable for all audiences
   - Gig driver version (if relevant): Specifically addressing gig economy drivers' pain points
4. **Adapt for platforms**:
   - LinkedIn (100-300 chars): Professional, data-driven
   - Instagram: Visual-focused caption
   - TikTok (20-60 chars): Catchy, trend-aware
   - Twitter (100-280 chars): Timely, concise
   - Facebook (40-80 chars): Community-focused
5. **Score the idea** (1-10) based on:
   - Relevance to our mission
   - Timeliness
   - Engagement potential
   - Actionability

Output as structured JSON.
```

### Example LLM Synthesis

**Input parsed idea:**
```json
{
  "title": "Gas prices risen 15% this month",
  "raw_text": "Gas prices have risen 15% due to supply chain issues...",
  "key_points": ["15% increase", "supply chain", "affecting gig workers"],
  "href": "https://reuters.com/article/123"
}
```

**LLM Output:**
```json
{
  "pillar": "token_community",
  "pillar_rationale": "Directly addresses economic pain point where tokens provide relief",
  "core_message": "Rising gas costs make safe driving rewards more valuable than ever",
  "variants": {
    "generic": "Gas up 15%? Your safe driving tokens are worth more than ever. Start earning!",
    "gig_driver": "15% gas hike hitting hard? Safe drivers earning $200+ monthly in tokens. Join now!"
  },
  "platform_adaptations": {
    "linkedin": "New data: Safe driving tokens offset 15% gas price surge. Learn how companies are helping drivers.",
    "tiktok": "Gas prices 📈 Tokens 💰 Do the math",
    "twitter": "Gas +15% 😱 But safe drivers earning $200/mo in tokens 🎉 Which side are you on?",
    "facebook": "Gas prices up? We've got you covered! 💪",
    "instagram": "Swipe to see how drivers beat the 15% gas hike → [visual story format]"
  },
  "score": 8.5,
  "score_rationale": "Highly timely, addresses real pain point, clear value proposition"
}
```

## Output Format

### CRITICAL: JSON File Output is Mandatory

**ALWAYS save generated content ideas to a JSON file.** This is a required step, not optional.

**Output location:** `output/generated_ideas/content_idea_YYYY-MM-DD_HHMM.json`

**Naming conventions:**
- For single generation: `content_idea_YYYY-MM-DD.json`
- For multiple generations same day: `content_idea_YYYY-MM-DD_HHMM.json` (with timestamp)
- For descriptive naming: `content_idea_YYYY-MM-DD_gas-prices.json` (with topic/theme)
- Choose the format that best prevents filename conflicts

**Process:**
1. Create the `output/generated_ideas/` directory if it doesn't exist
2. Generate the content ideas using LLM synthesis
3. Check if a file with the same name already exists
4. If exists, append timestamp or descriptive suffix to filename
5. Save to JSON file and verify creation was successful

### Standard Output Structure

Generate content ideas in this JSON format:

```json
{
  "generated_date": "2024-01-15",
  "ideas": [
    {
      "id": "idea_001",
      "pillar": "safety_education",
      "source_type": "seasonal",
      "base_idea": "Winter tire safety check reminder",
      "variants": {
        "generic": "Time for your winter tire check! Proper tread depth = safer winter driving",
        "gig_driver": "Quick tire check between deliveries: Good tread = $50/month saved on gas + safer night deliveries"
      },
      "platform_adaptations": {
        "linkedin": "Data-driven approach to winter tire safety...",
        "tiktok": "30-second tire check hack that could save your life...",
        "instagram": "Swipe for our 5-point winter tire safety checklist..."
      },
      "hashtags": ["#WinterDriving", "#SafetyFirst", "#TireSafety"]
    }
  ]
}
```

### Platform-Specific Considerations

When adapting ideas for platforms (with updated optimal lengths from platforms.json):

- **LinkedIn**: Professional tone, data/statistics (100-300 chars text, 30 sec videos)
- **Instagram**: Visual-first, community stories, lifestyle angle
- **TikTok**: Trending sounds, quick tips (20-60 char captions, 15-30 sec videos)
- **Twitter/X**: Timely, news tie-ins (100-280 chars text, 30 sec videos max)
- **Facebook**: Community groups, local relevance (40-80 chars text, 30-60 sec videos)
- **Reddit**: Value-first, non-promotional, discussion starters

Note: These concise character limits require punchy, impactful messaging that gets to the point quickly.

## Final Step: Verify JSON Output

After generating content ideas, ALWAYS:

1. Confirm the JSON file was created in `output/generated_ideas/`
2. Verify the file contains all generated ideas in proper JSON format
3. Report the output file path to the user

Example confirmation messages:
```
Content ideas generated successfully!
Output saved to: output/generated_ideas/content_idea_2025-10-24_1430.json
Total ideas generated: 3
```

```
Content ideas generated successfully!
Output saved to: output/generated_ideas/content_idea_2025-10-24_gas-prices.json
Total ideas generated: 1
```

## Resources

### config/

Contains all configuration files:
- `pillars.json` - Content themes/pillars definition
- `platforms.json` - Social media platform specifications
- `segments.json` - Target audience segment configuration

### scripts/

The `generate_ideas.py` script automates the entire content generation workflow, from reading configurations to producing formatted output.

### input/ (in main Content directory)

The input folder structure where all data sources are stored:
- `input/seasonal/` - Holiday calendars, seasonal events
- `input/human_insights/` - Team observations, customer feedback
- `input/external_feeds/` - News feeds, trending topics