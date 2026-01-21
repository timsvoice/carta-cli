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
