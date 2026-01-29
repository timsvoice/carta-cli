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
    prompt_for_plan: bool = False
    feature_path: str | None = None


@dataclass
class HomeResult:
    """Result from HomeScreen menu selection."""

    status: Literal["discovery", "plan", "quit"]


@dataclass
class PlanSelectResult:
    """Result from PlanSelectScreen after feature selection."""

    status: Literal["selected", "cancelled"]
    feature_path: str | None = None
    discovery_content: str | None = None


@dataclass
class PlanWizardResult:
    """Result from PlanWizardScreen after Q&A completion."""

    status: Literal["completed", "cancelled"]
    answers: list[dict] | None = None


@dataclass
class PlanDraftResult:
    """Result from PlanDraftScreen after plan display."""

    status: Literal["done", "restart"]
