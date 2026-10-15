"""All tools, in one fixed order (spec §7.3).

Sorted by wire name, so the tool list a provider sees is the same in every run
of a surface and prompt caching keeps working. New packs are added to
``ALL_TOOLS`` (spec §14: the registry takes extra packs).
"""

from typing import Any

from assistant.surfaces import Surface
from assistant.tools.catalog import CATALOG_TOOLS
from assistant.tools.core import CORE_TOOLS
from assistant.tools.project import PROJECT_TOOLS
from assistant.tools.runtime import ToolSpec

ALL_TOOLS: tuple[ToolSpec[Any, Any], ...] = tuple(
    sorted(
        (*CORE_TOOLS, *CATALOG_TOOLS, *PROJECT_TOOLS), key=lambda spec: spec.wire_name
    )
)
BY_WIRE_NAME: dict[str, ToolSpec[Any, Any]] = {
    spec.wire_name: spec for spec in ALL_TOOLS
}
MCP_TOOLS: tuple[ToolSpec[Any, Any], ...] = tuple(
    spec for spec in ALL_TOOLS if spec.mcp
)


def tools_for(surface: Surface) -> tuple[ToolSpec[Any, Any], ...]:
    return tuple(spec for spec in ALL_TOOLS if surface in spec.surfaces)
