#!/bin/bash
# save.sh - Saves approved discovery and commits to discovery branch
# Usage: save.sh <user_requirement> <branch_name> <discover_file_path> [issue_number]

set -e

USER_REQUIREMENT="$1"
BRANCH_NAME="$2"
DISCOVER_FILE_PATH="$3"
ISSUE_NUMBER="${4:-}"

if [ -z "$USER_REQUIREMENT" ] || [ -z "$BRANCH_NAME" ] || [ -z "$DISCOVER_FILE_PATH" ]; then
  echo "Error: Missing required arguments"
  echo "Usage: save.sh <user_requirement> <branch_name> <discover_file_path> [issue_number]"
  exit 1
fi

# Verify initialization
if [ ! -d ".specimin/plans/" ]; then
  echo "Error: Discovery not initialized. Please run /init first."
  exit 1
fi

# Verify discovery file exists
if [ ! -f "$DISCOVER_FILE_PATH" ]; then
  echo "Error: Discovery file not found: $DISCOVER_FILE_PATH"
  exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run setup script
if [ -n "$ISSUE_NUMBER" ]; then
  SETUP_OUTPUT=$(bash "$SCRIPT_DIR/setup.sh" "$USER_REQUIREMENT" --json --no-commit --branch-name "$BRANCH_NAME" --issue-number "$ISSUE_NUMBER")
else
  SETUP_OUTPUT=$(bash "$SCRIPT_DIR/setup.sh" "$USER_REQUIREMENT" --json --no-commit --branch-name "$BRANCH_NAME")
fi

# Parse output
DISCOVER_DIR=$(echo "$SETUP_OUTPUT" | jq -r '.discover_dir')
BRANCH_NAME=$(echo "$SETUP_OUTPUT" | jq -r '.branch_name')

if [ -z "$DISCOVER_DIR" ] || [ "$DISCOVER_DIR" = "null" ]; then
  echo "Error: Failed to create discovery directory"
  exit 1
fi

# Copy discovery file to discovery directory
DISCOVER_DEST="$DISCOVER_DIR/discover.md"
cp "$DISCOVER_FILE_PATH" "$DISCOVER_DEST"

# Commit
git add "$DISCOVER_DEST"
git commit -m "Add specification: $USER_REQUIREMENT"

# Output success message with JSON
echo "{\"discover_dir\": \"$DISCOVER_DIR\", \"branch_name\": \"$BRANCH_NAME\", \"discover_path\": \"$DISCOVER_DEST\"}"
