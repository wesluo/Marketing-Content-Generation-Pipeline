#!/usr/bin/env python3
"""
Content Idea Generator for Safe Driving Token Platform
Generates social media content ideas by synthesizing multiple data sources
with business pillars, platform specs, and target segments.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ContentGenerator:
    def __init__(self, base_path: Path = None, config_path: Path = None):
        """Initialize the content generator with configuration files."""
        if config_path is None:
            # Config files are in ../config/ relative to this script
            config_path = Path(__file__).resolve().parent.parent / 'config'

        if base_path is None:
            # For input/output, go up to Content directory
            base_path = Path(__file__).resolve().parent.parent.parent.parent.parent

        self.base_path = base_path
        self.config_path = config_path
        self.pillars = self._load_config('pillars.json')
        self.platforms = self._load_config('platforms.json')
        self.segments = self._load_config('segments.json')
        self.input_dir = base_path / 'input'

    def _load_config(self, filename: str) -> Dict:
        """Load a JSON configuration file from the config directory."""
        file_path = self.config_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Required configuration file not found: {filename} in {self.config_path}")

        with open(file_path, 'r') as f:
            return json.load(f)

    def gather_input_sources(self) -> Dict[str, List[str]]:
        """Gather all input sources from the input directory."""
        sources = {
            'seasonal': [],
            'human_insights': [],
            'external_feeds': []
        }

        if not self.input_dir.exists():
            print(f"Warning: Input directory not found at {self.input_dir}")
            return sources

        for category in sources.keys():
            category_path = self.input_dir / category
            if category_path.exists():
                for file in category_path.iterdir():
                    if file.is_file():
                        try:
                            with open(file, 'r') as f:
                                content = f.read().strip()
                                if content:
                                    sources[category].append(content)
                        except Exception as e:
                            print(f"Error reading {file}: {e}")

        return sources

    def synthesize_idea(self, input_text: str, pillar: Dict, source_type: str) -> Dict:
        """Synthesize a single content idea from input and pillar."""
        pillar_id = pillar['id']
        pillar_name = pillar['name']

        # Base idea combining input with pillar theme
        base_idea = f"{input_text} - {pillar_name}"

        # Determine if this idea should have a segment variant (30% chance)
        include_segment = random.random() < 0.3

        # Create variants
        variants = {
            'generic': self._create_generic_version(input_text, pillar)
        }

        if include_segment:
            variants['gig_driver'] = self._create_segment_version(
                input_text, pillar, self.segments['primary_segment']
            )

        # Create platform adaptations
        platform_adaptations = {}
        for platform in self.platforms['platforms'][:3]:  # Top 3 platforms for example
            platform_id = platform['id']
            platform_adaptations[platform_id] = self._adapt_for_platform(
                variants['generic'], platform
            )

        # Generate relevant hashtags
        hashtags = self._generate_hashtags(pillar, source_type)

        return {
            'pillar': pillar_id,
            'source_type': source_type,
            'base_idea': base_idea,
            'variants': variants,
            'platform_adaptations': platform_adaptations,
            'hashtags': hashtags
        }

    def _create_generic_version(self, input_text: str, pillar: Dict) -> str:
        """Create a generic version of the content idea - more concise."""
        # Keep messages under 100 chars for maximum platform compatibility
        short_input = input_text[:40] if len(input_text) > 40 else input_text
        templates = [
            f"{short_input} - earn tokens!",
            f"Tip: {short_input}",
            f"{short_input} 🚗",
            f"Safety alert: {short_input}"
        ]
        return random.choice(templates)

    def _create_segment_version(self, input_text: str, pillar: Dict, segment: Dict) -> str:
        """Create a segment-specific version for gig drivers - concise."""
        # Keep messages concise for platform limits
        short_input = input_text[:35] if len(input_text) > 35 else input_text
        templates = [
            f"Drivers: {short_input} = $$ saved",
            f"Gig tip: {short_input}",
            f"Rideshare: {short_input} = more tokens",
            f"Night shift? {short_input}"
        ]
        return random.choice(templates)

    def _adapt_for_platform(self, content: str, platform: Dict) -> str:
        """Adapt content for a specific platform with new concise character limits."""
        platform_id = platform['id']

        # Extract first key point for ultra-short platforms
        short_content = content.split('.')[0] if '.' in content else content

        # Platform-specific adaptations with new character limits
        adaptations = {
            'linkedin': short_content[:250] if len(short_content) > 250 else short_content,  # 100-300 chars
            'instagram': f"📸 {content}",  # Visual focus, caption secondary
            'tiktok': short_content[:50],  # 20-60 char captions
            'twitter': short_content[:200],  # 100-280 chars
            'facebook': short_content[:60],  # 40-80 chars
            'reddit': f"PSA: {content}"  # No strict limit, discussion focused
        }

        return adaptations.get(platform_id, content)

    def _generate_hashtags(self, pillar: Dict, source_type: str) -> List[str]:
        """Generate relevant hashtags for the content."""
        base_hashtags = ['#SafeDriving', '#TokenRewards', '#DriveToEarn']

        pillar_hashtags = {
            'safety_education': ['#DrivingSafety', '#SafetyFirst'],
            'token_community': ['#CommunityRewards', '#TokenEconomy'],
            'advocacy_impact': ['#RoadSafety', '#MakeADifference'],
            'product_tips': ['#AppTips', '#MaximizeRewards'],
            'seasonal_trending': ['#Trending', '#Seasonal'],
            'entertainment_humor': ['#DrivingHumor', '#FunFact']
        }

        hashtags = base_hashtags.copy()
        if pillar['id'] in pillar_hashtags:
            hashtags.extend(pillar_hashtags[pillar['id']])

        return hashtags[:5]  # Limit to 5 hashtags

    def generate_ideas(self, count: int = 10) -> Dict:
        """Generate multiple content ideas from existing input files only."""
        sources = self.gather_input_sources()
        ideas = []
        idea_counter = 1

        # If no input sources, exit gracefully
        if not any(sources.values()):
            print("❌ No input files found in the input/ directory.")
            print("Please add content to:")
            print("  - input/seasonal/")
            print("  - input/human_insights/")
            print("  - input/external_feeds/")
            return {
                'generated_date': datetime.now().strftime('%Y-%m-%d'),
                'total_ideas': 0,
                'ideas': [],
                'error': 'No input files found'
            }

        # Generate ideas from available sources
        for source_type, inputs in sources.items():
            if not inputs:
                continue

            for input_text in inputs[:count//3]:  # Distribute across source types
                # Select a random pillar
                pillar = random.choice(self.pillars['pillars'])

                idea = self.synthesize_idea(input_text, pillar, source_type)
                idea['id'] = f"idea_{idea_counter:03d}"
                ideas.append(idea)
                idea_counter += 1

                if len(ideas) >= count:
                    break

            if len(ideas) >= count:
                break

        return {
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'total_ideas': len(ideas),
            'ideas': ideas
        }

    def save_output(self, ideas: Dict, output_file: str = 'content_ideas.json'):
        """Save generated ideas to a JSON file."""
        # Only save if there are ideas to save
        if ideas.get('total_ideas', 0) > 0:
            output_path = self.base_path / output_file
            with open(output_path, 'w') as f:
                json.dump(ideas, f, indent=2)
            print(f"✅ Generated {ideas['total_ideas']} content ideas")
            print(f"📝 Saved to: {output_path}")
        else:
            print("⚠️ No ideas generated - output file not created")


def main():
    """Main execution function."""
    try:
        generator = ContentGenerator()
        ideas = generator.generate_ideas(count=10)
        generator.save_output(ideas)

        # Only print summary if ideas were generated
        if ideas.get('total_ideas', 0) > 0:
            # Print summary
            print("\n📊 Summary:")
            print(f"- Total ideas: {ideas['total_ideas']}")

            # Count ideas by pillar
            pillar_counts = {}
            for idea in ideas['ideas']:
                pillar = idea['pillar']
                pillar_counts[pillar] = pillar_counts.get(pillar, 0) + 1

            print("\n🎯 Ideas by Pillar:")
            for pillar, count in pillar_counts.items():
                print(f"  - {pillar}: {count}")

            # Count segment variants
            segment_variants = sum(1 for idea in ideas['ideas']
                                  if 'gig_driver' in idea.get('variants', {}))
            print(f"\n🚗 Gig driver variants: {segment_variants}/{ideas['total_ideas']}")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure pillars.json, platforms.json, and segments.json exist in the parent directory")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()