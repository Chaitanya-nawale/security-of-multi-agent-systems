"""Deterministic unit tests for dynamic tool prompt configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.utils.tool_config import (
    configure_tools,
    get_available_profiles,
    load_tool_config,
)
from src.utils.tools import WorkerTools


@pytest.fixture
def fixture_config_path(tmp_path: Path) -> Path:
    """Provide an isolated, hermetic YAML config for testing."""
    test_yaml = """
test_override:
  send_email:
    description: "HERMETIC_TEST_OVERRIDE_DESCRIPTION"
  read_document:
    description: "HERMETIC_READ_DESCRIPTION"

test_append:
  send_email:
    append: "HERMETIC_APPENDED_INSTRUCTION"
"""
    cfg_file = tmp_path / "fixture_tool_prompts.yaml"
    cfg_file.write_text(test_yaml, encoding="utf-8")
    return cfg_file


def test_get_available_profiles_hermetic(fixture_config_path: Path) -> None:
    """Verify available profiles are correctly discovered from YAML."""
    profiles = get_available_profiles(config_path=fixture_config_path)
    assert "test_override" in profiles
    assert "test_append" in profiles


def test_load_tool_config_hermetic(fixture_config_path: Path) -> None:
    """Verify tool configuration dictionary is parsed properly."""
    cfg = load_tool_config("test_override", config_path=fixture_config_path)
    assert "send_email" in cfg
    assert cfg["send_email"]["description"] == "HERMETIC_TEST_OVERRIDE_DESCRIPTION"


def test_configure_tools_override_hermetic(fixture_config_path: Path) -> None:
    """Verify configure_tools replaces tool description in override mode."""
    original_tools = WorkerTools.get_tools()
    configured = configure_tools(
        original_tools,
        profile="test_override",
        config_path=fixture_config_path,
    )

    email_tool = next(t for t in configured if t.name == "send_email")
    assert email_tool.description == "HERMETIC_TEST_OVERRIDE_DESCRIPTION"


def test_configure_tools_append_hermetic(fixture_config_path: Path) -> None:
    """Verify configure_tools appends instructions to existing description."""
    original_tools = WorkerTools.get_tools()
    orig_email_desc = next(t for t in original_tools if t.name == "send_email").description

    configured = configure_tools(
        original_tools,
        profile="test_append",
        config_path=fixture_config_path,
    )

    email_tool = next(t for t in configured if t.name == "send_email")
    assert "HERMETIC_APPENDED_INSTRUCTION" in email_tool.description
    assert orig_email_desc in email_tool.description


def test_configure_tools_unknown_profile(fixture_config_path: Path) -> None:
    """Verify configure_tools safely falls back to original tools when profile is missing."""
    original_tools = WorkerTools.get_tools()
    orig_desc = next(t for t in original_tools if t.name == "send_email").description

    configured = configure_tools(
        original_tools,
        profile="non_existent_profile_xyz",
        config_path=fixture_config_path,
    )
    email_tool = next(t for t in configured if t.name == "send_email")
    assert email_tool.description == orig_desc


def test_configure_tools_missing_file(tmp_path: Path) -> None:
    """Verify graceful fallback when YAML file does not exist."""
    missing_file = tmp_path / "does_not_exist.yaml"
    original_tools = WorkerTools.get_tools()
    configured = configure_tools(
        original_tools,
        profile="baseline",
        config_path=missing_file,
    )
    assert len(configured) == len(original_tools)


def test_default_config_file_syntax() -> None:
    """Smoke test ensuring default config/tool_prompts.yaml parses without syntax errors if present."""
    profiles = get_available_profiles()
    # If the default file exists, it should return a list of profile names without crashing
    assert isinstance(profiles, list)
