#!/bin/bash
#
# LLM Synthesis Wrapper for Content Generator
#
# This script accepts a structured JSON prompt via stdin and pipes it to
# Claude CLI for true LLM-based content synthesis. It returns JSON output
# containing the synthesized content idea.
#
# Usage: echo "$json_prompt" | bash synthesize_with_llm.sh
#

set -euo pipefail

# Read the full JSON input from stdin
INPUT=$(cat)

# Extract the prompt text from the JSON input
# The input should have a "prompt" field containing the synthesis request
PROMPT=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('prompt', ''))")

if [ -z "$PROMPT" ]; then
    echo '{"error": "No prompt provided in input JSON"}' >&2
    exit 1
fi

# Create a temporary file for the prompt to ensure proper handling of multiline content
TEMP_PROMPT=$(mktemp)
echo "$PROMPT" > "$TEMP_PROMPT"

# Call Claude CLI with the prompt
# Use --print for non-interactive mode
# Request JSON output format
RESPONSE=$(cat "$TEMP_PROMPT" | claude --print 2>/dev/null || echo "ERROR")

# Clean up temp file
rm -f "$TEMP_PROMPT"

# Check if Claude call succeeded
if [ "$RESPONSE" = "ERROR" ]; then
    echo '{"error": "Claude CLI call failed"}' >&2
    exit 1
fi

# Output the response
# Note: Claude's response might need to be wrapped in JSON structure
# For now, we'll return it as-is and let Python handle parsing
echo "$RESPONSE"
