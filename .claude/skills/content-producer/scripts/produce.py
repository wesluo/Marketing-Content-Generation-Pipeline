#!/usr/bin/env python3
"""
Main CLI for content-producer skill.

Transforms content-generator output into platform-ready assets.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import zipfile

# Import local modules
from copy_processor import (
    process_facebook_copy,
    process_instagram_copy,
    process_reddit_copy,
    process_linkedin_copy,
    process_twitter_copy,
    process_tiktok_copy,
    generate_alt_text,
    normalize_text
)
from prompt_generator import PromptGenerator
from url_extractor import extract_golden_quotes


class ContentProducer:
    """Main content producer class."""

    def __init__(self, args):
        self.args = args
        self.warnings = []
        self.trims = 0
        self.fallbacks = 0
        self.prompt_count = 0
        self.golden_quotes = []
        self.prompt_generator = PromptGenerator()

    def load_idea(self, input_path: Path) -> dict:
        """Load and validate the first idea from input JSON."""
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            sys.exit(3)

        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input file: {e}")
            sys.exit(3)

        # Get first idea
        ideas = data.get('ideas', [])
        if not ideas:
            print("Error: No ideas found in input file")
            sys.exit(3)

        idea = ideas[0]

        # Validate required fields
        required = ['id', 'pillar', 'core_message', 'variants']
        for field in required:
            if field not in idea:
                print(f"Error: Missing required field '{field}' in idea")
                sys.exit(3)

        if 'generic' not in idea.get('variants', {}):
            print("Error: Missing 'variants.generic' in idea")
            sys.exit(3)

        return idea

    def get_platform_copy(self, idea: dict, platform: str) -> str:
        """
        Get platform-specific copy, falling back to generic variant.
        """
        adaptations = idea.get('platform_adaptations', {})

        if platform in adaptations:
            return adaptations[platform]
        else:
            self.fallbacks += 1
            self.warnings.append(f"No {platform} adaptation; using generic variant")
            return idea['variants']['generic']

    def create_bundle_dir(self, idea_id: str) -> Path:
        """Create bundle directory with timestamp."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        bundle_name = f"{idea_id}_{timestamp}"
        bundle_root = Path(self.args.outdir) / bundle_name
        bundle_root.mkdir(parents=True, exist_ok=True)
        return bundle_root

    def generate_copy_files(self, idea: dict, bundle_root: Path) -> dict:
        """
        Generate all copy files for requested platforms.

        Returns:
            Dictionary with copy paths per platform
        """
        copy_dir = bundle_root / 'copy'
        copy_dir.mkdir(exist_ok=True)

        platforms = self.args.platforms.split(',')
        copy_paths = {}
        source_href = idea.get('source_idea', {}).get('href')

        for platform in platforms:
            platform = platform.strip()

            if platform == 'facebook':
                copy_text = self.get_platform_copy(idea, 'facebook')
                processed, trimmed = process_facebook_copy(
                    copy_text,
                    cta=self.args.cta,
                    source_href=source_href
                )
                if trimmed:
                    self.trims += 1
                    self.warnings.append(f"Facebook copy trimmed to fit limits")

                fb_path = copy_dir / 'facebook.txt'
                fb_path.write_text(processed, encoding='utf-8')
                copy_paths['facebook'] = str(fb_path.relative_to(bundle_root))

            elif platform == 'instagram':
                copy_text = self.get_platform_copy(idea, 'instagram')
                processed, trimmed = process_instagram_copy(
                    copy_text,
                    cta=self.args.cta,
                    source_href=source_href
                )
                if trimmed:
                    self.trims += 1
                    self.warnings.append(f"Instagram copy trimmed to fit limits")

                ig_path = copy_dir / 'instagram.txt'
                ig_path.write_text(processed, encoding='utf-8')
                copy_paths['instagram'] = str(ig_path.relative_to(bundle_root))

            elif platform == 'reddit':
                copy_text = self.get_platform_copy(idea, 'reddit')
                title, body, trimmed = process_reddit_copy(copy_text)

                if trimmed:
                    self.trims += 1
                    self.warnings.append(f"Reddit copy trimmed to fit limits")

                title_path = copy_dir / 'reddit_title.txt'
                body_path = copy_dir / 'reddit_body.txt'
                title_path.write_text(title, encoding='utf-8')
                body_path.write_text(body, encoding='utf-8')

                copy_paths['reddit'] = {
                    'title': str(title_path.relative_to(bundle_root)),
                    'body': str(body_path.relative_to(bundle_root))
                }

            elif platform == 'linkedin':
                copy_text = self.get_platform_copy(idea, 'linkedin')
                processed, trimmed = process_linkedin_copy(
                    copy_text,
                    cta=self.args.cta,
                    source_href=source_href
                )
                if trimmed:
                    self.trims += 1
                    self.warnings.append(f"LinkedIn copy trimmed to fit limits")

                linkedin_path = copy_dir / 'linkedin.txt'
                linkedin_path.write_text(processed, encoding='utf-8')
                copy_paths['linkedin'] = str(linkedin_path.relative_to(bundle_root))

            elif platform == 'twitter':
                copy_text = self.get_platform_copy(idea, 'twitter')
                processed, trimmed = process_twitter_copy(
                    copy_text,
                    cta=self.args.cta,
                    source_href=source_href
                )
                if trimmed:
                    self.trims += 1
                    self.warnings.append(f"Twitter copy trimmed to fit limits")

                twitter_path = copy_dir / 'twitter.txt'
                twitter_path.write_text(processed, encoding='utf-8')
                copy_paths['twitter'] = str(twitter_path.relative_to(bundle_root))

            elif platform == 'tiktok':
                copy_text = self.get_platform_copy(idea, 'tiktok')
                processed, trimmed = process_tiktok_copy(
                    copy_text,
                    cta=self.args.cta,
                    source_href=source_href
                )
                if trimmed:
                    self.trims += 1
                    self.warnings.append(f"TikTok copy trimmed to fit limits")

                tiktok_path = copy_dir / 'tiktok.txt'
                tiktok_path.write_text(processed, encoding='utf-8')
                copy_paths['tiktok'] = str(tiktok_path.relative_to(bundle_root))

        return copy_paths

    def generate_prompts(self, idea: dict, bundle_root: Path) -> dict:
        """
        Generate AI image prompts instead of actual images.

        Returns:
            Dictionary with prompt file paths
        """
        if self.args.no_prompts:
            return {}

        prompts_dir = bundle_root / 'images' / 'prompts'
        prompts_dir.mkdir(parents=True, exist_ok=True)

        # Determine number of variations (images - 1 for core + variations model)
        num_variations = self.args.images if self.args.images > 1 else 2

        # Generate prompts (1 core + N variations)
        core_prompt, variations = self.prompt_generator.generate_prompts(
            idea=idea,
            num_variations=num_variations,
            aspect_ratio="1:1",
            version="6.1"
        )

        # Save prompts
        saved_files = self.prompt_generator.save_prompts(
            output_dir=prompts_dir,
            core_prompt=core_prompt,
            variations=variations,
            idea_id=idea['id']
        )

        self.prompt_count = 1 + len(variations)  # core + variations

        return saved_files


    def create_manifest(self, idea: dict, bundle_root: Path, copy_paths: dict,
                       prompt_files: dict) -> Path:
        """Create manifest.json file."""
        manifest = {
            'idea_id': idea['id'],
            'source_file': str(self.args.input),
            'pillar_id': idea['pillar'],
            'generated_timestamp': datetime.now().isoformat(),
            'cta_placeholder': self.args.cta if idea.get('source_idea', {}).get('href') else None,
            'platforms': {},
            'image_prompts': prompt_files,
            'golden_quotes': {
                'extracted': len(self.golden_quotes) > 0,
                'count': len(self.golden_quotes),
                'quotes': self.golden_quotes,
                'source_url': idea.get('source_idea', {}).get('href')
            } if self.golden_quotes else None,
            'validations': {
                'warnings': self.warnings,
                'counts': {
                    'trims': self.trims,
                    'fallbacks': self.fallbacks,
                    'prompts': self.prompt_count,
                    'quotes': len(self.golden_quotes)
                }
            }
        }

        # Build platform sections (copy only, no images)
        platforms = self.args.platforms.split(',')

        for platform in platforms:
            platform = platform.strip()

            if platform == 'facebook':
                manifest['platforms']['facebook'] = {
                    'copy_path': copy_paths.get('facebook')
                }

            elif platform == 'instagram':
                manifest['platforms']['instagram'] = {
                    'copy_path': copy_paths.get('instagram')
                }

            elif platform == 'reddit':
                manifest['platforms']['reddit'] = {
                    'title_path': copy_paths.get('reddit', {}).get('title'),
                    'body_path': copy_paths.get('reddit', {}).get('body')
                }

            elif platform == 'linkedin':
                manifest['platforms']['linkedin'] = {
                    'copy_path': copy_paths.get('linkedin')
                }

            elif platform == 'twitter':
                manifest['platforms']['twitter'] = {
                    'copy_path': copy_paths.get('twitter')
                }

            elif platform == 'tiktok':
                manifest['platforms']['tiktok'] = {
                    'copy_path': copy_paths.get('tiktok')
                }

        manifest_path = bundle_root / 'manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        return manifest_path

    def extract_url_quotes(self, idea: dict) -> None:
        """
        Load manually curated golden quotes from file if available.
        Stores quotes in self.golden_quotes for use in copy enrichment.
        """
        if not self.args.extract_quotes:
            return

        source_href = idea.get('source_idea', {}).get('href')
        idea_id = idea.get('id')

        if not source_href:
            return

        print(f"🔍 Loading quotes for: {idea_id} ({source_href})")

        try:
            quotes = extract_golden_quotes(source_href, idea_id)

            if quotes:
                self.golden_quotes = quotes
                print(f"✓ Loaded {len(quotes)} golden quote(s)")
            else:
                print(f"ℹ️  No quotes file found (create input/url_quotes/{idea_id}.json to add quotes)")

        except Exception as e:
            print(f"⚠️  Quote loading failed: {e}")
            self.warnings.append(f"Quote loading failed: {str(e)}")

    def create_report(self, idea: dict, bundle_root: Path) -> Path:
        """Create report.txt file."""
        report_lines = [
            "Content Production Report",
            "=" * 50,
            f"Idea ID: {idea['id']}",
            f"Pillar: {idea['pillar']}",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "Summary:",
            f"  - Trims: {self.trims}",
            f"  - Fallbacks: {self.fallbacks}",
            f"  - AI Prompts: {self.prompt_count}",
            f"  - Golden Quotes: {len(self.golden_quotes)}",
            "",
        ]

        if self.golden_quotes:
            report_lines.append("Extracted Quotes:")
            for i, quote in enumerate(self.golden_quotes, 1):
                report_lines.append(f"  {i}. \"{quote['text']}\" ({quote['source']})")
            report_lines.append("")

        if self.warnings:
            report_lines.append("Warnings:")
            for warning in self.warnings:
                report_lines.append(f"  - {warning}")
            report_lines.append("")

        report_lines.append("Output validated successfully.")

        report_path = bundle_root / 'report.txt'
        report_path.write_text('\n'.join(report_lines), encoding='utf-8')

        return report_path

    def create_zip(self, bundle_root: Path) -> Optional[Path]:
        """Create zip archive of bundle."""
        if self.args.no_zip:
            return None

        zip_path = bundle_root.parent / f"{bundle_root.name}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in bundle_root.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(bundle_root.parent)
                    zipf.write(file_path, arcname)

        return zip_path

    def run(self) -> int:
        """Main execution flow."""
        print(f"🚀 Content Producer")
        print(f"   Input: {self.args.input}")
        print(f"   Platforms: {self.args.platforms}")
        print()

        # Load idea
        idea = self.load_idea(Path(self.args.input))
        print(f"✓ Loaded idea: {idea['id']}")

        # Extract golden quotes from URL if enabled
        self.extract_url_quotes(idea)

        # Create bundle directory
        bundle_root = self.create_bundle_dir(idea['id'])
        print(f"✓ Bundle directory: {bundle_root}")

        # Generate copy
        copy_paths = self.generate_copy_files(idea, bundle_root)
        print(f"✓ Generated copy files")

        # Generate prompts
        prompt_files = self.generate_prompts(idea, bundle_root)
        if not self.args.no_prompts:
            print(f"✓ Generated {self.prompt_count} AI image prompts (Midjourney-ready)")
        else:
            print(f"✓ Skipped prompt generation (--no-prompts)")

        # Create manifest
        manifest_path = self.create_manifest(idea, bundle_root, copy_paths, prompt_files)
        print(f"✓ Created manifest: {manifest_path.name}")

        # Create report
        report_path = self.create_report(idea, bundle_root)
        print(f"✓ Created report: {report_path.name}")

        # Create zip
        zip_path = self.create_zip(bundle_root)
        if zip_path:
            print(f"✓ Created archive: {zip_path.name}")

        print()
        print(f"✅ Bundle created: {bundle_root}")

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warning(s) - see report.txt")
            return 2

        return 0


def main():
    parser = argparse.ArgumentParser(
        description='Transform content-generator output into platform-ready assets'
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Path to content-generator JSON file'
    )

    parser.add_argument(
        '--outdir',
        default='output/bundles',
        help='Output directory for bundles (default: output/bundles)'
    )

    parser.add_argument(
        '--platforms',
        default='facebook,instagram,reddit',
        help='Comma-separated list of platforms (options: facebook,instagram,reddit,linkedin,twitter,tiktok; default: facebook,instagram,reddit)'
    )

    parser.add_argument(
        '--images',
        type=int,
        default=2,
        help='Number of prompt variations (produces 1 core + N variations, default: 2)'
    )

    parser.add_argument(
        '--cta',
        default='[CTA_PLACEHOLDER]',
        help='CTA placeholder text (default: [CTA_PLACEHOLDER])'
    )

    parser.add_argument(
        '--no-zip',
        action='store_true',
        help='Skip creating zip archive'
    )

    parser.add_argument(
        '--no-prompts',
        action='store_true',
        help='Skip AI prompt generation (copy only)'
    )

    parser.add_argument(
        '--extract-quotes',
        action='store_true',
        help='Load golden quotes from manual quote files (input/url_quotes/<idea_id>.json)'
    )

    args = parser.parse_args()

    producer = ContentProducer(args)
    exit_code = producer.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
