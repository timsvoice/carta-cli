#!/bin/bash
# save-plan.sh - Saves approved implementation plan and commits to feature branch
# Usage: save-plan.sh <branch_name> <plan_file_path>

set -e

BRANCH_NAME="$1"
PLAN_FILE_PATH="$2"

if [ -z "$BRANCH_NAME" ] || [ -z "$PLAN_FILE_PATH" ]; then
  echo "Error: Missing required arguments"
  echo "Usage: save-plan.sh <branch_name> <plan_file_path>"
  exit 1
fi

# Verify initialization
FEATURE_DIR=".specimen/plans/$BRANCH_NAME"
if [ ! -d "$FEATURE_DIR" ]; then
  echo "Error: Feature directory not found: $FEATURE_DIR"
  echo "Have you run /spec yet for this branch?"
  exit 1
fi

# Verify plan file exists
if [ ! -f "$PLAN_FILE_PATH" ]; then
  echo "Error: Plan file not found: $PLAN_FILE_PATH"
  exit 1
fi

# Verify spec exists (plan requires spec)
SPEC_PATH="$FEATURE_DIR/spec.md"
if [ ! -f "$SPEC_PATH" ]; then
  echo "Error: Specification not found: $SPEC_PATH"
  echo "You must create a spec before generating a plan."
  exit 1
fi

# Copy plan file to feature directory
PLAN_DEST="$FEATURE_DIR/plan.md"
cp "$PLAN_FILE_PATH" "$PLAN_DEST"

# Commit
git add "$PLAN_DEST"
git commit -m "Add implementation plan for branch: $BRANCH_NAME"

# Output success message with JSON
echo "{\"feature_dir\": \"$FEATURE_DIR\", \"branch_name\": \"$BRANCH_NAME\", \"plan_path\": \"$PLAN_DEST\"}"
