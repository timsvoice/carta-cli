"""Tests for carta.utils.filename module."""


from carta.utils.filename import (
    validate_draft_filename,
    get_next_sequence_number,
    format_feature_dirname,
    list_feature_directories,
    plan_exists,
)


class TestListFeatureDirectories:
    """Tests for list_feature_directories function."""

    def test_empty_directory(self, tmp_path):
        """Returns empty list when .carta directory is empty."""
        carta_dir = tmp_path / ".carta"
        carta_dir.mkdir()

        result = list_feature_directories(carta_dir)
        assert result == []

    def test_nonexistent_directory(self, tmp_path):
        """Returns empty list when .carta directory doesn't exist."""
        carta_dir = tmp_path / ".carta"

        result = list_feature_directories(carta_dir)
        assert result == []

    def test_finds_features_with_discovery(self, tmp_path):
        """Finds feature directories that have discovery.md files."""
        carta_dir = tmp_path / ".carta"
        carta_dir.mkdir()

        # Create feature with discovery.md
        feature1 = carta_dir / "001-feature-one"
        feature1.mkdir()
        (feature1 / "discovery.md").write_text("# Discovery")

        # Create feature without discovery.md
        feature2 = carta_dir / "002-feature-two"
        feature2.mkdir()

        result = list_feature_directories(carta_dir)
        assert len(result) == 1
        assert result[0].name == "001-feature-one"

    def test_sorts_by_sequence_number(self, tmp_path):
        """Features are sorted by sequence number."""
        carta_dir = tmp_path / ".carta"
        carta_dir.mkdir()

        # Create features out of order
        for num in [3, 1, 2]:
            feature = carta_dir / f"00{num}-feature-{num}"
            feature.mkdir()
            (feature / "discovery.md").write_text("# Discovery")

        result = list_feature_directories(carta_dir)
        assert len(result) == 3
        assert result[0].name == "001-feature-1"
        assert result[1].name == "002-feature-2"
        assert result[2].name == "003-feature-3"

    def test_ignores_non_matching_directories(self, tmp_path):
        """Ignores directories that don't match NNN- pattern."""
        carta_dir = tmp_path / ".carta"
        carta_dir.mkdir()

        # Create valid feature
        feature1 = carta_dir / "001-valid-feature"
        feature1.mkdir()
        (feature1 / "discovery.md").write_text("# Discovery")

        # Create invalid directories
        invalid1 = carta_dir / "not-a-feature"
        invalid1.mkdir()
        (invalid1 / "discovery.md").write_text("# Discovery")

        invalid2 = carta_dir / "1-short-prefix"
        invalid2.mkdir()
        (invalid2 / "discovery.md").write_text("# Discovery")

        result = list_feature_directories(carta_dir)
        assert len(result) == 1
        assert result[0].name == "001-valid-feature"


class TestPlanExists:
    """Tests for plan_exists function."""

    def test_returns_false_when_no_plan(self, tmp_path):
        """Returns False when plan.md doesn't exist."""
        feature_dir = tmp_path / "001-feature"
        feature_dir.mkdir()

        result = plan_exists(feature_dir)
        assert result is False

    def test_returns_false_when_plan_empty(self, tmp_path):
        """Returns False when plan.md exists but is empty."""
        feature_dir = tmp_path / "001-feature"
        feature_dir.mkdir()
        (feature_dir / "plan.md").touch()

        result = plan_exists(feature_dir)
        assert result is False

    def test_returns_true_when_plan_has_content(self, tmp_path):
        """Returns True when plan.md exists and has content."""
        feature_dir = tmp_path / "001-feature"
        feature_dir.mkdir()
        (feature_dir / "plan.md").write_text("# Implementation Plan")

        result = plan_exists(feature_dir)
        assert result is True


class TestValidateDraftFilename:
    """Tests for validate_draft_filename function."""

    def test_valid_two_word_name(self):
        """Accepts valid two-word kebab-case name."""
        name, is_valid = validate_draft_filename("user-auth")
        assert name == "user-auth"
        assert is_valid is True

    def test_valid_three_word_name(self):
        """Accepts valid three-word kebab-case name."""
        name, is_valid = validate_draft_filename("user-session-persistence")
        assert name == "user-session-persistence"
        assert is_valid is True

    def test_normalizes_uppercase(self):
        """Normalizes uppercase to lowercase."""
        name, is_valid = validate_draft_filename("User-Auth")
        assert name == "user-auth"
        assert is_valid is True

    def test_sanitizes_invalid_format(self):
        """Sanitizes invalid format to kebab-case."""
        name, is_valid = validate_draft_filename("User Auth Feature!")
        assert name == "user-auth-feature"
        assert is_valid is False


class TestGetNextSequenceNumber:
    """Tests for get_next_sequence_number function."""

    def test_returns_1_for_empty_directory(self, tmp_path):
        """Returns 1 when .carta directory is empty."""
        carta_dir = tmp_path / ".carta"
        carta_dir.mkdir()

        result = get_next_sequence_number(carta_dir)
        assert result == 1

    def test_returns_1_for_nonexistent_directory(self, tmp_path):
        """Returns 1 when .carta directory doesn't exist."""
        carta_dir = tmp_path / ".carta"

        result = get_next_sequence_number(carta_dir)
        assert result == 1

    def test_returns_next_number(self, tmp_path):
        """Returns next number after existing features."""
        carta_dir = tmp_path / ".carta"
        carta_dir.mkdir()

        (carta_dir / "001-feature").mkdir()
        (carta_dir / "002-feature").mkdir()

        result = get_next_sequence_number(carta_dir)
        assert result == 3


class TestFormatFeatureDirname:
    """Tests for format_feature_dirname function."""

    def test_formats_with_padding(self):
        """Formats sequence number with zero padding."""
        result = format_feature_dirname(1, "user-auth")
        assert result == "001-user-auth"

    def test_formats_larger_numbers(self):
        """Formats larger sequence numbers correctly."""
        result = format_feature_dirname(42, "feature-name")
        assert result == "042-feature-name"
