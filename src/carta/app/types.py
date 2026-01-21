"""Result types for screen communication."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class FeatureResult:
    """Result from FeatureScreen after gather agent completes."""

    status: Literal["success", "error"]
    feature_description: str = ""
    questions: list[dict] | None = None
    error: str | None = None


@dataclass
class WizardResult:
    """Result from WizardScreen after Q&A completion."""

    status: Literal["completed", "cancelled"]
    answers: list[dict] | None = None


@dataclass
class DraftResult:
    """Result from DraftScreen after draft display."""

    status: Literal["done", "restart"]
