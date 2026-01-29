"""Filename validation and sanitization utilities for Carta feature directories."""

import re
from pathlib import Path


def validate_draft_filename(raw: str) -> tuple[str, bool]:
    """Validate and normalize a draft filename.

    Expected format: 2-4 words in kebab-case (e.g., "user-session-persistence").

    Args:
        raw: The raw filename string from the LLM response.

    Returns:
        A tuple of (normalized_name, is_valid) where is_valid indicates
        whether the original input matched the expected format.
    """
    name = raw.strip().lower()

    # Valid kebab-case: 2-4 lowercase words separated by hyphens
    pattern = r"^[a-z]+(-[a-z]+){1,3}$"

    if re.match(pattern, name):
        return name, True

    # Invalid format - sanitize it
    sanitized = sanitize_to_kebab_case(raw)
    return sanitized, False


def sanitize_to_kebab_case(raw: str) -> str:
    """Convert an arbitrary string to valid kebab-case.

    Args:
        raw: Any string to convert.

    Returns:
        A kebab-case string with at most 3 words.
        Returns "untitled-feature" if input is empty or produces no valid words.
    """
    # Replace non-alphanumeric characters with spaces
    cleaned = re.sub(r"[^a-zA-Z0-9\s-]", " ", raw)

    # Split into words and lowercase
    words = cleaned.lower().split()

    # Filter out empty strings and take first 3 words
    words = [w for w in words if w][:3]

    if not words:
        return "untitled-feature"

    return "-".join(words)


def get_next_sequence_number(carta_dir: Path) -> int:
    """Find the next available sequence number for a feature directory.

    Scans the .carta directory for existing NNN-* directories and returns
    the next number in sequence.

    Args:
        carta_dir: Path to the .carta directory.

    Returns:
        The next sequence number (1 if no existing directories).
    """
    if not carta_dir.exists():
        return 1

    # Pattern to match directories starting with 3-digit number
    sequence_pattern = re.compile(r"^(\d{3})-")

    max_number = 0
    for item in carta_dir.iterdir():
        if item.is_dir():
            match = sequence_pattern.match(item.name)
            if match:
                number = int(match.group(1))
                max_number = max(max_number, number)

    return max_number + 1


def format_feature_dirname(sequence: int, name: str) -> str:
    """Format a feature directory name with sequence prefix.

    Args:
        sequence: The sequence number (1-999).
        name: The kebab-case feature name.

    Returns:
        Formatted directory name (e.g., "001-user-auth").
    """
    return f"{sequence:03d}-{name}"


def list_feature_directories(carta_dir: Path) -> list[Path]:
    """List all feature directories in the .carta directory.

    Returns directories that have a discovery.md file, sorted by sequence number.

    Args:
        carta_dir: Path to the .carta directory.

    Returns:
        List of Path objects for feature directories with discovery.md files.
    """
    if not carta_dir.exists():
        return []

    # Pattern to match directories starting with 3-digit number
    sequence_pattern = re.compile(r"^(\d{3})-")

    features = []
    for item in carta_dir.iterdir():
        if item.is_dir():
            match = sequence_pattern.match(item.name)
            if match and (item / "discovery.md").exists():
                features.append(item)

    # Sort by sequence number
    features.sort(key=lambda p: p.name)
    return features


def plan_exists(feature_dir: Path) -> bool:
    """Check if a non-empty plan.md exists in the feature directory.

    Args:
        feature_dir: Path to the feature directory.

    Returns:
        True if plan.md exists and is non-empty.
    """
    plan_path = feature_dir / "plan.md"
    if not plan_path.exists():
        return False
    return plan_path.stat().st_size > 0
