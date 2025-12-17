#!/bin/bash
# save-spec.sh - Saves approved specification and commits to feature branch
# Usage: save-spec.sh <user_requirement> <branch_name> <spec_file_path> [issue_number]

set -e

USER_REQUIREMENT="$1"
BRANCH_NAME="$2"
SPEC_FILE_PATH="$3"
ISSUE_NUMBER="${4:-}"

if [ -z "$USER_REQUIREMENT" ] || [ -z "$BRANCH_NAME" ] || [ -z "$SPEC_FILE_PATH" ]; then
  echo "Error: Missing required arguments"
  echo "Usage: save-spec.sh <user_requirement> <branch_name> <spec_file_path> [issue_number]"
  exit 1
fi

# Verify initialization
if [ ! -d ".specimen/plans/" ]; then
  echo "Error: specimen not initialized. Please run /init first."
  exit 1
fi

# Verify spec file exists
if [ ! -f "$SPEC_FILE_PATH" ]; then
  echo "Error: Spec file not found: $SPEC_FILE_PATH"
  exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run setup script
if [ -n "$ISSUE_NUMBER" ]; then
  SETUP_OUTPUT=$(bash "$SCRIPT_DIR/setup.feature.sh" "$USER_REQUIREMENT" --json --no-commit --branch-name "$BRANCH_NAME" --issue-number "$ISSUE_NUMBER")
else
  SETUP_OUTPUT=$(bash "$SCRIPT_DIR/setup.feature.sh" "$USER_REQUIREMENT" --json --no-commit --branch-name "$BRANCH_NAME")
fi

# Parse output
FEATURE_DIR=$(echo "$SETUP_OUTPUT" | jq -r '.feature_dir')
BRANCH_NAME=$(echo "$SETUP_OUTPUT" | jq -r '.branch_name')

if [ -z "$FEATURE_DIR" ] || [ "$FEATURE_DIR" = "null" ]; then
  echo "Error: Failed to create feature directory"
  exit 1
fi

# Copy spec file to feature directory
SPEC_DEST="$FEATURE_DIR/spec.md"
cp "$SPEC_FILE_PATH" "$SPEC_DEST"

# Commit
git add "$SPEC_DEST"
git commit -m "Add specification: $USER_REQUIREMENT"

# Output success message with JSON
echo "{\"feature_dir\": \"$FEATURE_DIR\", \"branch_name\": \"$BRANCH_NAME\", \"spec_path\": \"$SPEC_DEST\"}"
