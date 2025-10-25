# Idea Generation Pipeline - Conceptual Framework

## Primary Use Case
Maintain a fresh, continuous pipeline of content ideas to support daily social media presence across multiple platforms, ensuring consistent brand visibility and engagement without content fatigue.

## The Core Challenge
Creating an agent that can intelligently combine heterogeneous data sources (seasonal patterns, human insights, external feeds) with stable business frameworks (pillars and platforms) to generate relevant content ideas on both scheduled and triggered basis.

## System Philosophy

**Think of this as a "Creative Intelligence Hub"** that:
- Acts like a skilled content strategist who reads the room
- Combines structured data with human intuition
- Responds to both routine needs and unexpected opportunities
- Learns from what works and what doesn't

## Data Source Strategy

### Seasonal/Calendar Sources
- Not just holidays, but business cycles, industry seasons, cultural moments
- Predictable patterns that can be planned months ahead
- Provides the "backbone" of evergreen content opportunities

### Human Input Sources
- The qualitative gold that algorithms miss
- Customer conversations, team observations, sales feedback
- Unstructured but rich in context and nuance
- Captures the "why" behind trends

### External Data Feeds
- The pulse of what's happening now
- News, social trends, competitor moves, industry shifts
- Provides urgency and relevance
- Helps identify gaps and opportunities

## The Adaptive Parsing Approach

Instead of forcing everything into one format, the system should:
- Respect the native "language" of each source
- Extract what's valuable from each without losing context
- Think like a translator, not a converter
- Preserve the unique insights each format provides

## Multi-Trigger Philosophy

**Why multiple triggers matter:**
- Scheduled runs provide consistency and planning capability
- Threshold events catch rising opportunities before they peak
- Manual requests serve urgent business needs
- Gap detection ensures continuous content flow
- External signals enable rapid response to market changes

Each trigger type serves a different business purpose - routine planning vs. opportunistic content vs. crisis response vs. strategic fills.

## Technical Implementation - Daily Trigger with CRON

### Decision: CRON for Scheduled Daily Runs

**Why CRON:**
- **Reliability**: Operating system-level scheduling that's been battle-tested for decades
- **Simplicity**: No external dependencies, frameworks, or services required
- **Universal**: Works across all Unix-like systems with identical behavior
- **Lightweight**: Minimal resource overhead compared to dedicated scheduling services
- **Visibility**: Easy to audit and monitor through system logs

### Daily Trigger Specification

**CRON Expression**: `0 6 * * *`
- Runs daily at 6:00 AM local server time
- Chosen for pre-business hours execution to have fresh content ready
- Allows time for review and refinement before publication

**Alternative Considered**:
- Cloud schedulers (Lambda, Cloud Functions): Overkill for simple daily runs
- Task queues (Celery, Airflow): Unnecessary complexity for single scheduled job
- Custom daemon: Reinventing the wheel with more failure points

### Implementation Details

**Script Execution**:
```
0 6 * * * /usr/bin/python3 /path/to/content_pipeline/daily_generator.py >> /var/log/content_pipeline/daily.log 2>&1
```

**Key Considerations**:
1. **Timezone Handling**: Server configured to business timezone, not UTC, for intuitive scheduling
2. **Overlap Prevention**: Script includes lock file mechanism to prevent concurrent runs
3. **Error Notification**: Pipe stderr to monitoring system for immediate alerts
4. **Execution Context**: Runs with dedicated service account with minimal necessary permissions

### Monitoring and Reliability

**Health Checks**:
- CRON execution logged to syslog for audit trail
- Application-level logging for debugging and performance tracking
- Daily success/failure metrics pushed to monitoring dashboard
- Email alerts on failure or no-run conditions

**Failure Recovery**:
- If daily run fails, manual trigger available through API
- Previous successful outputs cached for 7 days
- Graceful degradation: System can use yesterday's ideas if today's run fails

This CRON-based approach provides the right balance of simplicity and reliability for our daily content generation needs without introducing unnecessary architectural complexity.

## Synthesis Logic - The Creative Core

The agent should think like a content strategist:

1. **Context Gathering**: What's happening now? What's coming up? What are people talking about?

2. **Pattern Recognition**: Which themes appear across multiple sources? What combinations feel fresh?

3. **Pillar Alignment**: How does each potential idea serve the core business narratives?

4. **Platform Optimization**: What format would this idea take on each platform? Is it better suited for some than others?

5. **Timing Intelligence**: Is this idea urgent? Evergreen? Better saved for a specific moment?

## Quality Control Mechanisms

### Deduplication isn't just about avoiding repeats:
- Recognize when ideas are variations of the same theme
- Identify when to refresh vs. create new
- Understand content fatigue patterns

### Scoring should consider:
- Alignment with business goals
- Resource requirements vs. potential impact
- Historical performance of similar ideas
- Current content inventory and gaps

## Feedback and Learning

The system needs memory and pattern recognition:
- Which idea types perform well on which platforms?
- What combinations of sources produce the best ideas?
- When do certain triggers lead to successful content?
- How do different pillars resonate at different times?

## Output Philosophy

Rather than one-size-fits-all output:
- Content calendars for planners
- Quick briefs for creators
- Detailed specs for production teams
- Priority lists for decision makers

Each stakeholder should receive ideas in the format that helps them act.

## Critical Success Factors

1. **Balance automation with human judgment** - The agent suggests, humans decide
2. **Maintain idea freshness** - Avoid formulaic combinations
3. **Respect platform nuances** - LinkedIn isn't Twitter, blog isn't YouTube
4. **Time sensitivity awareness** - Know when timing matters vs. when quality matters more
5. **Resource reality** - Great ideas that can't be executed aren't helpful

## Evolution Path

Start simple and grow:
- Begin with a few reliable sources and basic synthesis
- Add complexity as patterns become clear
- Introduce learning after establishing baselines
- Expand triggers based on actual needs, not theoretical possibilities

## Key Questions to Consider

- How do you weight different sources when they conflict?
- What's the right balance between reactive and proactive idea generation?
- How do you preserve serendipity in an automated system?
- When should the system admit it doesn't have good ideas vs. forcing output?
- How do you measure success beyond just quantity of ideas?

## Configuration Files

All configuration files are stored within the content-generator skill for self-contained operation:

### Content Pillars
Content pillars are defined in `.claude/skills/content-generator/config/pillars.json` which provides a structured, machine-readable format for the core content themes. The agent references this file to ensure all generated ideas align with established content pillars.

### Platform Specifications
Platform configurations are defined in `.claude/skills/content-generator/config/platforms.json` which provides comprehensive specifications for each social media platform including audience demographics, content formats, posting schedules, and engagement strategies. The agent uses this to tailor content ideas for optimal platform performance.

### Market Segments
Market segment targeting is defined in `.claude/skills/content-generator/config/segments.json` which identifies the primary audience segment for optimization. The agent generates generic ideas suitable for all audiences, and when relevant (~30% of the time), also creates a variant specifically optimized for the target segment. This ensures broad appeal while addressing specific segment needs.

## Implementation Status

### ✅ Completed

#### Idea Parsing System
- **Batch parsing capability**: The `idea-parser` skill now parses ALL ideas from input files in a single run
- **Reddit integration**: Successfully parsed 100+ Reddit stories into individual JSON files
- **File structure**: Each parsed idea stored as `idea_NNN.json` with metadata, engagement metrics, and source URLs
- **Location**: `input/human_insights/parsed/` directory contains all parsed ideas

#### Content Generation System
- **Random selection**: Content generator randomly selects unused ideas from the parsed pool
- **Sequential mode**: Support for using lowest numbered unused idea
- **Specific targeting**: Ability to generate from a specific idea by number
- **Batch generation**: Can generate multiple content ideas in one run

#### Usage Tracking System
- **Automatic marking**: Each used idea is marked with a `.idea_NNN.used` file
- **Prevention of repetition**: System filters out used ideas during selection
- **Metadata tracking**: Usage markers include timestamp, generated file reference, and idea ID
- **Analytics support**: Usage tracking enables future analysis of which ideas generate best content

#### Skills Configuration
- **idea-parser skill**: Located at `.claude/skills/idea-parser/skill.md`
  - Batch parsing mode for processing all ideas at once
  - Reddit-specific parsing patterns documented
  - Automatic JSON file generation with structured metadata

- **content-generator skill**: Located at `.claude/skills/content-generator/skill.md`
  - Idea Selection Strategy section added
  - Four selection modes implemented (random, sequential, specific, batch)
  - Mandatory usage tracking documented
  - Example code provided for implementation

### Current State

**Parsed Ideas**: 100 Reddit stories parsed and ready for content generation
**Usage Tracking**: 2 ideas marked as used during testing
**Available Ideas**: 98 unused ideas remaining in pool
**Output Format**: JSON files in `output/generated_ideas/` with structured content

### Next Steps

- Configure CRON job for daily automated content generation
- Implement feedback collection mechanism based on generated content performance
- Add analytics dashboard to track idea usage patterns and content success
- Expand input sources beyond Reddit (seasonal calendar, external feeds)
- Implement content performance tracking to inform future idea selection