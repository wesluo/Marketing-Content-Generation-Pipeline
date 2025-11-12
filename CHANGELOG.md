# Changelog

All notable changes to the Content Generation Pipeline project will be documented in this file.

## [1.2.1] - 2025-11-11

### Added - CSV Content Parser

- **NEW: CSV Parsing Support**: Added `parse_csv_content.py` to idea-parser skill
  - Parses structured CSV files with pre-written content ideas
  - Supports columns: Pillar, Category, Content, Hashtags
  - Automatically extracts hashtags and formats as ready-to-use ideas
  - Integrates seamlessly with existing parsed idea workflow
- **New Input Source**: "ZENLIT SMM CONTENT PLAN.csv" with 67 pre-written content entries
  - Created ideas 101-167 from CSV content plan
  - Mix of seasonal, token stories, safety tips, and community content
  - Ready-made copy suitable for immediate use or LLM enhancement

### Content Generation Activity

- **12 Total Ideas Generated**: Active usage of content-generator skill
  - 8 from Reddit stories (human insights)
  - 4 from CSV content plan entries
- **8 Ideas Marked as Used**: idea_002, idea_014, idea_024, idea_054, idea_059, idea_068, idea_073, idea_102
  - Usage tracking system working correctly
  - Prevents duplicate content across calendar
- **Holiday Content Focus**: Generated Thanksgiving travel and winter driving content
  - Seasonal & trending pillar validation
  - Holiday traffic safety tips
  - Winter accident fairness advocacy

### Current State

- **167 Parsed Ideas Total**:
  - 100 Reddit stories (idea_001 to idea_100)
  - 67 CSV content plan entries (idea_101 to idea_167)
- **159 Unused Ideas Available**: Large pool ready for generation
- **Usage Rate**: ~5% of ideas converted to content (healthy reserve)

### Documentation Updates

- **README.md**: Updated current status, project structure, and parsed idea counts
- **CLAUDE.md**: Added CSV parser section, updated status and recent updates
- **CHANGELOG.md**: This entry documenting CSV integration and usage activity

## [1.2.0] - 2025-11-07

### Added - LLM-Based Visual Concept Extraction

- **MANDATORY LLM for Image Prompts**: content-producer now uses Claude LLM to extract unique visual concepts for each idea
  - Analyzes core_message, key_points, and title
  - Generates 3-5 specific, concrete visual concepts
  - Ensures each idea gets distinctive Midjourney prompts
  - NO FALLBACK MODE: Fails gracefully with clear error if LLM unavailable
- **New Script**: `call_claude_llm.sh` - Bash wrapper for Claude CLI integration in content-producer
- **Enhanced Prompt Quality**: Visual concepts are now content-specific instead of generic
  - Example: "dashcam on windshield" vs "professional driver in vehicle"
  - Dramatic improvement in AI image generation results

### Changed - content-generator Skill

- **Batch Mode Enhancement**: Now saves each idea as separate JSON file
  - Previous: One file with multiple ideas
  - Current: One idea = one file (`content_idea_YYYY-MM-DD_HHMM_idea_NNN.json`)
  - Easier to feed individual ideas to content-producer
  - Better tracking and organization
- **Improved JSON Parsing**: More robust handling of LLM responses
  - Better cleanup of markdown code blocks
  - Trailing comma removal
  - Enhanced error messages with temp file logging
- **Better Error Handling**: Clearer diagnostic messages when LLM synthesis fails

### Changed - content-producer Skill

- **Removed Keyword Fallback**: Visual concept extraction is now LLM-only
  - Ensures consistent high-quality prompts
  - No degraded generic prompts as fallback
  - Clear error messages if LLM unavailable
- **Enhanced Validation**: Minimum length checks on LLM responses
- **Improved Logging**: Shows extracted visual concepts in output

### Documentation Updates

- **README.md**:
  - Added content-producer workflow section
  - Documented LLM-based features prominently
  - Updated project structure with all 3 skills
  - Updated current status (167 ideas, 8 generated, 4 bundles)
  - Added AI image prompt generation feature section
- **CLAUDE.md**:
  - Updated architecture notes with no-fallback policy
  - Added content-producer scripts documentation
  - Updated recent updates section
  - Emphasized consistent LLM-first architecture
- **content-producer/SKILL.md**:
  - Added LLM extraction section with examples
  - Documented NO FALLBACK MODE policy
  - Added error handling section
  - Updated with before/after prompt examples
- **content-generator/SKILL.md**:
  - Updated batch mode behavior documentation

### Technical Improvements

- **Architecture Consistency**: Both skills now follow same LLM-mandatory pattern
  - content-generator: LLM synthesizes content (no fallback)
  - content-producer: LLM extracts visual concepts (no fallback)
  - Uniform error handling across both skills
- **Code Cleanup**: Removed ~50 lines of keyword fallback code from prompt_generator.py
- **Quality Assurance**: Validation ensures all prompts meet minimum quality standards

### Migration Notes

**Upgrading from 1.1.0 to 1.2.0**:

1. **Claude CLI Required**: Both content-generator and content-producer now require Claude CLI
   - Test: `claude --version`
   - Install if missing: Follow Claude Code documentation
2. **No Behavioral Changes**: Existing workflows work the same
3. **Quality Improvement**: Image prompts are now consistently unique and content-specific
4. **Error Handling**: If LLM fails, you'll see clear error messages instead of silent degradation

## [1.1.0] - 2025-10-29

### Added - content-producer Skill
- **All 6 Social Platforms Support**: LinkedIn, Twitter/X, and TikTok added to existing Facebook, Instagram, Reddit
- **Manual Quote Extraction**: New feature to enrich content with golden quotes from source URLs
  - Quotes stored in `input/url_quotes/<idea_id>.json` files
  - Manual curation workflow for quality control
  - Quotes included in manifest.json and report.txt
- **Platform-Specific Character Limits**:
  - LinkedIn: 100-300 chars (target), 400 soft cap, 3000 hard cap
  - Twitter/X: 100-280 chars (strict 280 limit)
  - TikTok: 20-60 chars (target), 100 soft cap, 150 hard cap
- **New Scripts**:
  - `url_extractor.py`: Quote file loading logic
  - `extract_url_quotes.py`: Helper script for manual quote files
- **New Directory**: `input/url_quotes/` for manual quote files with README

### Changed - content-producer Skill
- **Removed WebFetch Dependency**: Replaced automated extraction with manual curation workflow
- **Updated CLI**: `--extract-quotes` now loads from files instead of fetching URLs
- **Improved User Feedback**: Better messages when quote files missing
- **Documentation**: Complete rewrite of quote extraction documentation

### Removed - content-producer Skill
- **fetch_url_content.sh**: Obsolete WebFetch wrapper script
- **WebFetch Integration**: All Claude Code WebFetch references and dependencies

### Documentation Updates
- **SKILL.md**: Updated with manual quote workflow, all 6 platforms, removed WebFetch
- **CLAUDE.md**: Updated URL extraction section, current state, removed WebFetch references
- **producer_spec.md**: Updated scope, CLI parameters, removed network access requirements
- **README Created**: Added `input/url_quotes/README.md` with complete workflow documentation

## [1.0.0] - 2025-10-28

### Added - Initial Release
- **idea-parser Skill**: Extract individual ideas from raw input files (Reddit, etc.)
- **content-generator Skill**: Synthesize ideas with business pillars using LLM
- **content-producer Skill**: Transform ideas into platform-ready assets (Facebook, Instagram, Reddit only)
- **Configuration System**: Platform specs, pillar styles, segment definitions
- **Usage Tracking**: `.idea_NNN.used` markers prevent repetition
- **AI Image Prompts**: Midjourney-optimized prompt generation
- **Structured Bundles**: Manifest, validation report, zip archive

### Features
- Batch parsing of 100 Reddit stories
- Four idea selection modes (random, sequential, specific, batch)
- LLM-based content synthesis
- Platform-specific copy optimization
- Pillar-aware visual styling for AI prompts

## Future Roadmap

### Planned Enhancements
- **CRON Automation**: Daily content generation at 6:00 AM
- **Feedback Loop**: Track which ideas generate best-performing content
- **Analytics Dashboard**: Visualize idea usage and content performance
- **Multi-Source**: Add seasonal calendar and external feeds
- **Learning System**: Adjust pillar selection based on historical performance
- **Quote Integration**: Auto-inject loaded quotes into platform copy
- **Image Generation**: Pipe AI prompts to Midjourney/DALL-E APIs for automated image creation

### Technical Debt
- Config file sync mechanism between content-generator and content-producer
- Hardcoded soft/hard caps in copy_processor.py (should read from config)

## Migration Notes

### Upgrading from 1.0.0 to 1.1.0

1. **Quote Extraction Users**:
   - Create `input/url_quotes/` directory
   - Manually curate quotes from source URLs
   - Save as `<idea_id>.json` files
   - Run producer with `--extract-quotes` flag

2. **Platform Support**:
   - Can now specify `--platforms facebook,instagram,reddit,linkedin,twitter,tiktok`
   - Default remains `facebook,instagram,reddit` for backward compatibility

3. **No Breaking Changes**:
   - Existing workflows continue to work
   - Quote extraction is optional feature
   - All previous CLI parameters remain unchanged
