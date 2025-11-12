#!/usr/bin/env python3
"""
Image Prompt Generator for Content Producer

Generates Midjourney-optimized image prompts based on content ideas,
pillar themes, and platform requirements. Outputs prompts in both
structured JSON and plain text formats for manual or automated use.

Uses LLM-based visual concept extraction for unique, content-specific prompts.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class PromptGenerator:
    """Generate AI image prompts from content ideas with pillar-aware styling."""

    def __init__(self, config_path: Path = None):
        """
        Initialize prompt generator with pillar style configuration.

        Args:
            config_path: Path to pillar_styles.json (defaults to skill config dir)

        Note:
            LLM-based visual concept extraction is MANDATORY for quality consistency.
            No fallback mode exists - failures will raise exceptions.
        """
        if config_path is None:
            # Default to local content-producer config directory
            config_path = Path(__file__).parent.parent / "config" / "pillar_styles.json"

        self.pillar_styles = self._load_pillar_styles(config_path)
        self.script_dir = Path(__file__).resolve().parent

    def _validate_pillar_styles_config(self, config: dict) -> list[str]:
        """
        Validate pillar styles config structure.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not isinstance(config, dict):
            errors.append("Config must be a dictionary")
            return errors

        # Expected pillars
        expected_pillars = [
            "safety_education",
            "token_community",
            "advocacy_impact",
            "product_tips",
            "seasonal_trending",
            "entertainment_humor"
        ]

        for pillar in expected_pillars:
            if pillar not in config:
                errors.append(f"Missing pillar configuration: {pillar}")
            elif not isinstance(config[pillar], dict):
                errors.append(f"Pillar {pillar} must be a dictionary")
            elif "midjourney_base" not in config[pillar]:
                errors.append(f"Pillar {pillar} missing 'midjourney_base' field")

        return errors

    def _load_pillar_styles(self, config_path: Path) -> Dict:
        """Load pillar visual style guidelines from JSON config."""
        if not config_path.exists():
            print(f"⚠️  Pillar styles config not found at {config_path}, using defaults")
            return self._get_default_styles()

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Validate config structure
            validation_errors = self._validate_pillar_styles_config(config)
            if validation_errors:
                print(f"⚠️  Pillar styles config validation errors:")
                for error in validation_errors:
                    print(f"     - {error}")
                print(f"⚠️  Falling back to defaults")
                return self._get_default_styles()

            return config

        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON in pillar_styles.json: {e}")
            print(f"⚠️  Falling back to defaults")
            return self._get_default_styles()
        except Exception as e:
            print(f"⚠️  Error loading pillar styles config: {e}")
            print(f"⚠️  Falling back to defaults")
            return self._get_default_styles()

    def _get_default_styles(self) -> Dict:
        """Fallback pillar styles if config file missing."""
        return {
            "safety_education": {
                "midjourney_base": "professional infographic style, clean modern design, blue color scheme"
            },
            "token_community": {
                "midjourney_base": "vibrant community photography, diverse group, warm purple tones"
            },
            "advocacy_impact": {
                "midjourney_base": "documentary photography style, powerful emotional impact, red color grading"
            },
            "product_tips": {
                "midjourney_base": "modern app interface design, clean UI, green accent colors"
            },
            "seasonal_trending": {
                "midjourney_base": "trending social media aesthetic, seasonal theme, contemporary style"
            },
            "entertainment_humor": {
                "midjourney_base": "humorous social media content, bright playful colors, meme-friendly"
            }
        }

    def generate_prompts(
        self,
        idea: Dict,
        num_variations: int = 2,
        aspect_ratio: str = "1:1",
        version: str = "6.1"
    ) -> Tuple[Dict, List[str]]:
        """
        Generate core prompt + variations for an idea.

        Args:
            idea: Content idea dict with pillar, core_message, etc.
            num_variations: Number of variations to generate (default 2)
            aspect_ratio: Midjourney aspect ratio (default "1:1" for square)
            version: Midjourney version (default "6.1")

        Returns:
            Tuple of (core_prompt_dict, variation_texts_list)
        """
        pillar = idea.get("pillar", "safety_education")
        core_message = idea.get("core_message", "")
        key_points = idea.get("source_idea", {}).get("key_points", [])
        title = idea.get("source_idea", {}).get("title", "")

        # Get pillar style guidelines
        pillar_style = self.pillar_styles.get(pillar, self.pillar_styles["safety_education"])
        base_style = pillar_style.get("midjourney_base", "modern professional photography")

        # Build core prompt
        core_prompt_text = self._build_core_prompt(
            core_message=core_message,
            key_points=key_points,
            base_style=base_style,
            aspect_ratio=aspect_ratio,
            version=version,
            title=title
        )

        # Build core prompt metadata
        core_prompt = {
            "prompt": core_prompt_text,
            "pillar": pillar,
            "pillar_style": pillar_style.get("visual_theme", ""),
            "aspect_ratio": aspect_ratio,
            "version": version,
            "parameters": {
                "ar": aspect_ratio,
                "v": version
            }
        }

        # Generate variations
        variations = self._generate_variations(
            core_prompt_text=core_prompt_text,
            base_style=base_style,
            num_variations=num_variations,
            aspect_ratio=aspect_ratio,
            version=version
        )

        return core_prompt, variations

    def _build_core_prompt(
        self,
        core_message: str,
        key_points: List[str],
        base_style: str,
        aspect_ratio: str,
        version: str,
        title: str = ""
    ) -> str:
        """Build the core Midjourney prompt."""
        # Extract key visual concepts from core message and key points
        visual_concepts = self._extract_visual_concepts(core_message, key_points, title)

        # Construct prompt with Midjourney syntax
        prompt_parts = [
            visual_concepts,
            base_style,
            "high contrast, editorial photography",
            "high quality, professional photography",
            f"--ar {aspect_ratio}",
            f"--v {version}"
        ]

        return ", ".join(prompt_parts)

    def _call_claude_llm(self, prompt: str) -> Optional[str]:
        """Call Claude CLI to extract visual concepts using LLM."""
        try:
            # Prepare input JSON for bash wrapper
            input_data = {'prompt': prompt}
            input_json = json.dumps(input_data)

            # Call the bash wrapper script
            wrapper_script = self.script_dir / 'call_claude_llm.sh'
            result = subprocess.run(
                ['bash', str(wrapper_script)],
                input=input_json,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"  ⚠️ Claude CLI error: {result.stderr}")
                return None

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            print("  ⚠️ Claude CLI call timed out after 30 seconds")
            return None
        except Exception as e:
            print(f"  ⚠️ Error calling Claude CLI: {e}")
            return None

    def _extract_visual_concepts_with_llm(
        self,
        core_message: str,
        key_points: List[str],
        title: str = ""
    ) -> str:
        """
        Extract visual concepts using LLM for content-specific, unique prompts.

        MANDATORY LLM extraction - NO FALLBACK. Raises exception on failure.

        Args:
            core_message: Core message from the idea
            key_points: Key points from the idea
            title: Optional title for additional context

        Returns:
            Comma-separated visual concepts

        Raises:
            RuntimeError: If LLM call fails or returns invalid response
        """
        # Build LLM prompt for visual concept extraction
        llm_prompt = f"""Analyze this content idea and extract 3-5 specific, concrete visual concepts for a Midjourney image prompt.

Core Message: {core_message}
Key Points: {', '.join(key_points)}
{f'Title: {title}' if title else ''}

Focus on:
- Specific objects unique to this idea (e.g., "dashcam on windshield", "passenger gesturing angrily")
- Concrete scenes (e.g., "accident documentation moment", "tense conversation in vehicle interior")
- Visual elements that make THIS idea distinctive (avoid generic terms like "driver" or "safety")

Guidelines:
- Each concept should be 2-5 words
- Be specific and visual, not abstract
- Focus on what would appear in the actual image
- Avoid duplicate or overlapping concepts

Return ONLY a comma-separated list of 3-5 visual concepts, nothing else.

Example good output: "dashcam mounted on windshield, driver reviewing footage on phone screen, accident scene in rearview mirror"

Your visual concepts:"""

        print("  🎨 Calling Claude LLM for visual concept extraction...")
        llm_response = self._call_claude_llm(llm_prompt)

        if not llm_response:
            raise RuntimeError(
                "❌ FATAL: LLM visual concept extraction failed and no fallback is available.\n"
                "   Ensure Claude CLI is installed and accessible.\n"
                "   Test with: echo 'hello' | claude --print"
            )

        # Clean the response - remove any markdown, quotes, or extra text
        cleaned = llm_response.strip()

        # Remove markdown code blocks if present
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            cleaned = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned

        # Remove quotes if wrapped
        cleaned = cleaned.strip('"\'')

        # Take only the first line if multi-line response
        cleaned = cleaned.split('\n')[0].strip()

        # Validate that we got something useful
        if not cleaned or len(cleaned) < 10:
            raise RuntimeError(
                f"❌ FATAL: LLM returned invalid visual concepts.\n"
                f"   Response was too short or empty: '{cleaned}'\n"
                f"   Full LLM response: {llm_response[:200]}"
            )

        print(f"  ✅ LLM extracted concepts: {cleaned[:80]}...")
        return cleaned

    def _extract_visual_concepts(self, core_message: str, key_points: List[str], title: str = "") -> str:
        """
        Extract visual concepts from text content using MANDATORY LLM extraction.

        NO FALLBACK MODE - ensures consistent high-quality prompts.

        Args:
            core_message: Core message from the idea
            key_points: Key points from the idea
            title: Optional title for additional context

        Returns:
            Comma-separated visual concepts from LLM

        Raises:
            RuntimeError: If LLM extraction fails
        """
        # MANDATORY LLM extraction - no fallback
        return self._extract_visual_concepts_with_llm(core_message, key_points, title)

    def _generate_variations(
        self,
        core_prompt_text: str,
        base_style: str,
        num_variations: int,
        aspect_ratio: str,
        version: str
    ) -> List[str]:
        """Generate variations of the core prompt."""
        variations = []

        # Variation 1: Alternative composition
        var1 = core_prompt_text.replace("high quality, professional photography",
                                        "cinematic composition, shallow depth of field, editorial quality")
        variations.append(var1)

        # Variation 2: Alternative lighting/mood
        if num_variations >= 2:
            var2 = core_prompt_text.replace("high quality, professional photography",
                                           "dramatic lighting, golden hour, atmospheric mood")
            variations.append(var2)

        # Variation 3: Alternative perspective (if requested)
        if num_variations >= 3:
            var3 = core_prompt_text.replace("high quality, professional photography",
                                           "wide angle shot, environmental context, dynamic perspective")
            variations.append(var3)

        return variations[:num_variations]

    def save_prompts(
        self,
        output_dir: Path,
        core_prompt: Dict,
        variations: List[str],
        idea_id: str
    ) -> Dict[str, str]:
        """
        Save prompts in both JSON and text formats.

        Args:
            output_dir: Directory to save prompts (e.g., bundle/images/prompts/)
            core_prompt: Core prompt dictionary with metadata
            variations: List of variation prompt texts
            idea_id: Idea identifier for filename

        Returns:
            Dict mapping format type to file path
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        # Save core prompt JSON (with metadata)
        core_json_path = output_dir / "core_prompt.json"
        with open(core_json_path, 'w', encoding='utf-8') as f:
            json.dump(core_prompt, f, indent=2, ensure_ascii=False)
        saved_files["core_json"] = str(core_json_path)

        # Save core prompt text (for easy copy-paste)
        core_txt_path = output_dir / "core_prompt.txt"
        with open(core_txt_path, 'w', encoding='utf-8') as f:
            f.write(core_prompt["prompt"])
        saved_files["core_txt"] = str(core_txt_path)

        # Save variations as separate text files
        for i, variation in enumerate(variations, start=1):
            var_path = output_dir / f"variation_{i}.txt"
            with open(var_path, 'w', encoding='utf-8') as f:
                f.write(variation)
            saved_files[f"variation_{i}"] = str(var_path)

        return saved_files


def main():
    """CLI entry point for testing prompt generation."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 prompt_generator.py <idea_json_path>")
        sys.exit(1)

    idea_path = Path(sys.argv[1])

    if not idea_path.exists():
        print(f"Error: Idea file not found: {idea_path}")
        sys.exit(1)

    # Load idea
    with open(idea_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "ideas" not in data or len(data["ideas"]) == 0:
        print("Error: No ideas found in input file")
        sys.exit(1)

    idea = data["ideas"][0]

    # Generate prompts
    generator = PromptGenerator()
    core_prompt, variations = generator.generate_prompts(idea, num_variations=2)

    # Print results
    print("=" * 60)
    print("CORE PROMPT")
    print("=" * 60)
    print(f"Pillar: {core_prompt['pillar']}")
    print(f"Style: {core_prompt['pillar_style']}")
    print()
    print(core_prompt['prompt'])
    print()

    print("=" * 60)
    print("VARIATIONS")
    print("=" * 60)
    for i, var in enumerate(variations, start=1):
        print(f"\nVariation {i}:")
        print(var)

    # Save to temp directory for testing
    temp_dir = Path("/tmp/prompt_test")
    saved = generator.save_prompts(temp_dir, core_prompt, variations, idea["id"])

    print()
    print("=" * 60)
    print(f"Saved {len(saved)} files to {temp_dir}")
    for key, path in saved.items():
        print(f"  {key}: {path}")


if __name__ == "__main__":
    main()
