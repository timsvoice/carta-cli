"""
Minimal codebase cache for LLM context.
Strips function/method bodies while preserving signatures, docstrings, and structure.
Also includes text files (markdown, yaml, json, toml) for additional context.
"""

import ast
import os
from pathlib import Path

# Python files get stripped, these are copied as-is
TEXT_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".toml"}


class BodyStripper(ast.NodeTransformer):
    """Remove function/method bodies, keeping only signatures and docstrings."""

    def _strip_body(self, node):
        """Replace body with docstring + ellipsis, remove decorators."""
        new_body = []

        # Keep docstring if present
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            new_body.append(node.body[0])

        # Add ellipsis as placeholder
        new_body.append(ast.Expr(value=ast.Constant(value=...)))
        node.body = new_body

        # Strip decorators (implementation detail)
        node.decorator_list = []
        return node

    def visit_FunctionDef(self, node):
        self.generic_visit(node)  # Process nested classes/functions first
        return self._strip_body(node)

    def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)
        return self._strip_body(node)


def strip_python_file(file_path: Path) -> str | None:
    """Parse a Python file and return stripped source."""
    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return None

    stripped = BodyStripper().visit(tree)
    ast.fix_missing_locations(stripped)
    return ast.unparse(stripped)


def read_text_file(file_path: Path) -> str | None:
    """Read a text file, returning None if it can't be read."""
    try:
        return file_path.read_text()
    except (UnicodeDecodeError, OSError):
        return None


def build_cache(source_dir: Path | None = None, cache_dir: Path | None = None) -> dict[str, str]:
    """Build cache of Python files (stripped) and text files (as-is)."""
    source_path = (source_dir or Path.cwd()).resolve()
    cache_path = (cache_dir or Path.cwd() / ".cache").resolve()
    exclude_dirs = {"__pycache__", ".git", ".venv", "venv", ".cache", "node_modules", ".carta"}

    cached = {}
    for root, dirs, files in os.walk(source_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.endswith(".egg-info")]

        for file in files:
            file_path = Path(root) / file
            suffix = file_path.suffix.lower()

            # Process Python files (strip bodies)
            if suffix == ".py":
                content = strip_python_file(file_path)
            # Copy text files as-is
            elif suffix in TEXT_EXTENSIONS:
                content = read_text_file(file_path)
            else:
                continue

            if content:
                rel_path = str(file_path.relative_to(source_path))
                cached[rel_path] = content

                out_path = cache_path / rel_path
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(content)

    return cached
