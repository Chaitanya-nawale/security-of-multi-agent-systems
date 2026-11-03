"""Dynamic tool prompt configuration loader.

Reads tool prompt profiles from YAML and applies them to BaseTool instances
without requiring any code modifications when new profiles are defined.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from langchain_core.tools import BaseTool, StructuredTool

from src.utils.logger import get_logger

logger = get_logger("mas.utils.tool_config")

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "tool_prompts.yaml"


def _read_yaml(config_path: Path) -> dict[str, Any]:
    """Safely read and parse a YAML mapping file."""
    if not config_path.is_file():
        return {}
    try:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception as exc:
        logger.error("Error reading YAML config '%s': %s", config_path, exc)
        return {}


def get_available_profiles(config_path: Path = DEFAULT_CONFIG_PATH) -> list[str]:
    """Retrieve all available profile names defined in the tool prompts YAML."""
    return list(_read_yaml(config_path).keys())


def load_tool_config(
    profile: str = "baseline",
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Any]:
    """Load tool prompt overrides for a given profile."""
    data = _read_yaml(config_path)
    if not data:
        return {}

    if profile not in data:
        logger.warning(
            "Profile '%s' not found in '%s'. Available profiles: %s. Using default tools.",
            profile,
            config_path,
            list(data.keys()),
        )
        return {}

    profile_data = data[profile]
    return profile_data if isinstance(profile_data, dict) else {}


def configure_tool(tool: BaseTool, tool_cfg: dict[str, Any]) -> BaseTool:
    """Return a clone of the tool with updated description from config."""
    new_desc = tool.description

    if "description" in tool_cfg and tool_cfg["description"]:
        new_desc = str(tool_cfg["description"]).strip()
    elif "append" in tool_cfg and tool_cfg["append"]:
        new_desc = f"{new_desc}\n\n{str(tool_cfg['append']).strip()}"
    else:
        return tool

    func = getattr(tool, "func", None) or tool._run
    coroutine = getattr(tool, "coroutine", None) or getattr(tool, "_arun", None)

    return StructuredTool.from_function(
        func=func,
        coroutine=coroutine,
        name=tool.name,
        description=new_desc,
        args_schema=tool.args_schema,
    )


def configure_tools(
    tools: list[BaseTool],
    profile: str = "baseline",
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> list[BaseTool]:
    """Apply prompt overrides from a YAML profile to a list of BaseTools."""
    profile_cfg = load_tool_config(profile=profile, config_path=config_path)
    if not profile_cfg:
        return list(tools)

    configured: list[BaseTool] = []
    for tool in tools:
        if tool.name in profile_cfg and isinstance(profile_cfg[tool.name], dict):
            updated_tool = configure_tool(tool, profile_cfg[tool.name])
            logger.info("Configured prompt for tool '%s' under profile '%s'.", tool.name, profile)
            configured.append(updated_tool)
        else:
            configured.append(tool)

    return configured


__all__ = [
    "configure_tool",
    "configure_tools",
    "get_available_profiles",
    "load_tool_config",
]
