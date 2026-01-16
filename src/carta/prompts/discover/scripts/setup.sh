#!/usr/bin/env bash
set -euo pipefail

# Script: setup.sh
# Description: Create discovery branch and planning directory
# Usage: ./setup.sh "discovery description" [--json] [--no-commit] [--branch-name "custom-name"] [--issue-number "123"]

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_error() { echo -e "${RED}ERROR: $1${NC}" >&2; }
print_success() { echo -e "${GREEN}SUCCESS: $1${NC}"; }
print_info() { echo -e "${YELLOW}INFO: $1${NC}"; }

get_next_branch_number() {
    # Get all branches matching the pattern and extract the highest number
    local max_num=$(git branch -a | \
        grep -oE '[0-9]{3}-' | \
        grep -oE '[0-9]{3}' | \
        sort -n | \
        tail -1)

    if [[ -z "$max_num" ]]; then
        echo "001"
    else
        printf "%03d" $((10#$max_num + 1))
    fi
}

generate_branch_name() {
    local description="$1"

    # Extract first two words and clean them
    local two_words=$(echo "$description" | \
        tr '[:upper:]' '[:lower:]' | \
        sed 's/[^a-z0-9 -]//g' | \
        tr -s ' ' | \
        awk '{print $1"-"$2}' | \
        sed 's/^-//;s/-$//')

    # Get next branch number
    local branch_num=$(get_next_branch_number)

    echo "${branch_num}-${two_words}"
}

check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not a git repository"
        exit 1
    fi
}

check_working_tree() {
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        print_error "Uncommitted changes exist. Commit or stash first."
        exit 1
    fi
}

check_branch_exists() {
    local branch_name="$1"
    if git rev-parse --verify "$branch_name" > /dev/null 2>&1; then
        print_error "Branch '$branch_name' already exists"
        exit 1
    fi
}

main() {
    local discover_description="${1:-}"
    local json_output=false
    local no_commit=false
    local custom_branch_name=""
    local issue_number=""

    # Parse flags
    local i=2
    while [[ $i -le $# ]]; do
        case "${!i}" in
            --json) json_output=true ;;
            --no-commit) no_commit=true ;;
            --branch-name)
                ((i++))
                custom_branch_name="${!i}"
                ;;
            --issue-number)
                ((i++))
                issue_number="${!i}"
                ;;
        esac
        ((i++))
    done

    if [[ -z "$discover_description" ]]; then
        print_error "Discovery description required"
        echo "Usage: $0 \"discovery description\" [--json] [--no-commit] [--branch-name \"custom-name\"] [--issue-number \"123\"]"
        exit 1
    fi

    check_git_repo
    check_working_tree

    local branch_name
    local branch_num

    # Determine branch number
    if [[ -n "$issue_number" ]]; then
        # Use issue number (padded to 3 digits)
        branch_num=$(printf "%03d" "$issue_number")
    else
        # Auto-increment (backward compatible)
        branch_num=$(get_next_branch_number)
    fi

    if [[ -n "$custom_branch_name" ]]; then
        # Use custom branch name with branch number
        branch_name="${branch_num}-${custom_branch_name}"
    else
        # Generate from description (backward compatible)
        # Extract first two words and clean them
        local two_words=$(echo "$discover_description" | \
            tr '[:upper:]' '[:lower:]' | \
            sed 's/[^a-z0-9 -]//g' | \
            tr -s ' ' | \
            awk '{print $1"-"$2}' | \
            sed 's/^-//;s/-$//')
        branch_name="${branch_num}-${two_words}"
    fi

    check_branch_exists "$branch_name"

    local discover_dir=".specimin/plans/${branch_name}"

    # Create directory
    mkdir -p "$discover_dir"

    # Create and checkout branch
    git checkout -b "$branch_name" --quiet

    if [[ "$no_commit" == false ]]; then
        # Commit empty directory structure (backward compatible behavior)
        touch "$discover_dir/.gitkeep"
        git add "$discover_dir"
        git commit -m "Initialize discovery: $discover_description" --quiet
    fi

    if [[ "$json_output" == true ]]; then
        cat << EOF
{
  "branch_name": "$branch_name",
  "discover_dir": "$discover_dir",
  "absolute_path": "$(pwd)/$discover_dir",
  "status": "success"
}
EOF
    else
        print_success "Discovery setup complete!"
        echo ""
        echo "Branch: $branch_name"
        echo "Directory: $discover_dir"
        if [[ "$no_commit" == false ]]; then
            echo ""
            echo "Next: Use discover template to create $discover_dir/discover.md"
        fi
    fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
