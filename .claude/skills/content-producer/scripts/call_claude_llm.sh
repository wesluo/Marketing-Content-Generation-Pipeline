#!/bin/bash
#
# LLM Call Wrapper for Content Producer
#
# This script accepts a structured JSON prompt via stdin and pipes it to
# Claude CLI for LLM-based processing. It returns the LLM response.
#
# Usage: echo "$json_prompt" | bash call_claude_llm.sh
#

set -euo pipefail

# Read the full JSON input from stdin
INPUT=$(cat)

# Extract the prompt text from the JSON input
# The input should have a "prompt" field containing the request
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
RESPONSE=$(cat "$TEMP_PROMPT" | claude --print 2>/dev/null || echo "ERROR")

# Clean up temp file
rm -f "$TEMP_PROMPT"

# Check if Claude call succeeded
if [ "$RESPONSE" = "ERROR" ]; then
    echo '{"error": "Claude CLI call failed"}' >&2
    exit 1
fi

# Output the response
echo "$RESPONSE"
