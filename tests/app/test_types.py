"""Tests for carta.app.types module."""


from carta.app.types import (
    DraftResult,
    HomeResult,
    PlanSelectResult,
    PlanWizardResult,
    PlanDraftResult,
)


class TestHomeResult:
    """Tests for HomeResult dataclass."""

    def test_discovery_status(self):
        """HomeResult can be created with discovery status."""
        result = HomeResult(status="discovery")
        assert result.status == "discovery"

    def test_plan_status(self):
        """HomeResult can be created with plan status."""
        result = HomeResult(status="plan")
        assert result.status == "plan"

    def test_quit_status(self):
        """HomeResult can be created with quit status."""
        result = HomeResult(status="quit")
        assert result.status == "quit"


class TestPlanSelectResult:
    """Tests for PlanSelectResult dataclass."""

    def test_selected_status_with_path(self):
        """PlanSelectResult can be created with selected status and feature path."""
        result = PlanSelectResult(
            status="selected",
            feature_path="/path/to/feature",
            discovery_content="# Discovery\nContent here",
        )
        assert result.status == "selected"
        assert result.feature_path == "/path/to/feature"
        assert result.discovery_content == "# Discovery\nContent here"

    def test_cancelled_status(self):
        """PlanSelectResult can be created with cancelled status."""
        result = PlanSelectResult(status="cancelled")
        assert result.status == "cancelled"
        assert result.feature_path is None
        assert result.discovery_content is None

    def test_default_values(self):
        """PlanSelectResult has correct default values."""
        result = PlanSelectResult(status="selected")
        assert result.feature_path is None
        assert result.discovery_content is None


class TestPlanWizardResult:
    """Tests for PlanWizardResult dataclass."""

    def test_completed_status_with_answers(self):
        """PlanWizardResult can be created with completed status and answers."""
        answers = [{"topic": "Phasing", "question": "How to phase?", "answer": "Incrementally"}]
        result = PlanWizardResult(status="completed", answers=answers)
        assert result.status == "completed"
        assert result.answers == answers

    def test_cancelled_status(self):
        """PlanWizardResult can be created with cancelled status."""
        result = PlanWizardResult(status="cancelled")
        assert result.status == "cancelled"
        assert result.answers is None

    def test_default_answers(self):
        """PlanWizardResult has None as default answers."""
        result = PlanWizardResult(status="completed")
        assert result.answers is None


class TestPlanDraftResult:
    """Tests for PlanDraftResult dataclass."""

    def test_done_status(self):
        """PlanDraftResult can be created with done status."""
        result = PlanDraftResult(status="done")
        assert result.status == "done"

    def test_restart_status(self):
        """PlanDraftResult can be created with restart status."""
        result = PlanDraftResult(status="restart")
        assert result.status == "restart"


class TestDraftResult:
    """Tests for DraftResult dataclass with plan prompt fields."""

    def test_prompt_for_plan_default(self):
        """DraftResult has prompt_for_plan defaulting to False."""
        result = DraftResult(status="done")
        assert result.prompt_for_plan is False
        assert result.feature_path is None

    def test_prompt_for_plan_with_path(self):
        """DraftResult can include prompt_for_plan and feature_path."""
        result = DraftResult(
            status="done",
            prompt_for_plan=True,
            feature_path="/path/to/feature",
        )
        assert result.prompt_for_plan is True
        assert result.feature_path == "/path/to/feature"
