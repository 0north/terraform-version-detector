from pathlib import Path

import pytest

from main import (
    check_version,
    find_required_version,
    find_terraform_version_file,
    parse_right_most,
)

TESTS_DIR = Path(__file__).parent


class TestParseRightMost:
    def test_two_part_version(self):
        assert parse_right_most("~> 1.2") == ">= 1.2.0, < 2.0.0"

    def test_three_part_version(self):
        assert parse_right_most("~> 1.2.3") == ">= 1.2.3, < 1.3.0"

    def test_rejects_non_right_most(self):
        with pytest.raises(ValueError, match="Not a right-most"):
            parse_right_most(">= 1.2.3")


class TestCheckVersion:
    @pytest.mark.parametrize(
        "spec, version, expected",
        [
            ("= 1.2.3", (1, 2, 3), True),
            ("= 1.2.3", (1, 2, 4), False),
            ("!= 1.2.3", (1, 2, 3), False),
            ("!= 1.2.3", (1, 2, 4), True),
            ("> 1.2.0", (1, 3, 0), True),
            ("> 1.2.0", (1, 2, 0), False),
            (">= 1.2.0", (1, 2, 0), True),
            ("< 1.3.0", (1, 2, 5), True),
            ("< 1.3.0", (1, 3, 0), False),
            ("<= 1.3.0", (1, 3, 0), True),
        ],
    )
    def test_single_constraint(self, spec, version, expected):
        assert check_version(spec, version) is expected

    def test_compound_constraint(self):
        assert check_version(">= 1.2.0, < 1.3.0", (1, 2, 5)) is True
        assert check_version(">= 1.2.0, < 1.3.0", (1, 3, 0)) is False

    def test_pessimistic_constraint(self):
        assert check_version("~> 1.10.0", (1, 10, 5)) is True
        assert check_version("~> 1.10.0", (1, 11, 0)) is False

    def test_two_part_version_spec(self):
        assert check_version(">= 1.2", (1, 2, 0)) is True
        assert check_version(">= 1.2", (1, 1, 9)) is False


class TestFindRequiredVersion:
    def test_finds_version_in_tf_files(self):
        result = find_required_version(TESTS_DIR / "app1")
        assert result is not None
        assert ">= 1.11" in result

    def test_finds_pessimistic_constraint(self):
        result = find_required_version(TESTS_DIR / "app2")
        assert result == "~> 1.10.0"

    def test_returns_none_when_no_version(self, tmp_path):
        (tmp_path / "main.tf").write_text("terraform {}\n")
        assert find_required_version(tmp_path) is None

    def test_returns_none_for_empty_directory(self, tmp_path):
        assert find_required_version(tmp_path) is None


class TestFindTerraformVersionFile:
    def test_finds_version_file(self):
        result = find_terraform_version_file(TESTS_DIR / "app3")
        assert result == "1.10.5"

    def test_strips_v_prefix(self, tmp_path):
        (tmp_path / ".terraform-version").write_text("v1.9.0\n")
        assert find_terraform_version_file(tmp_path) == "1.9.0"

    def test_returns_none_when_missing(self, tmp_path):
        assert find_terraform_version_file(tmp_path) is None

    def test_returns_none_when_empty(self, tmp_path):
        (tmp_path / ".terraform-version").write_text("")
        assert find_terraform_version_file(tmp_path) is None
