"""The layers a workflow names, and a workflow without some of them.

A workflow names layers in its dataset nodes (`layerId`) and in its tools'
settings, under keys shaped like layer references (`input_layer_id`,
`layer_ids`, an SQL node's extra inputs' `layer_id`). Exporting a project
needs that set, to decide what the archive may carry.
"""

import copy
import re
from typing import Any

# Keys of a tool's config that name a layer: the shapes the processes access
# check treats as layer references.
_LAYER_KEY = re.compile(r"^(?:\w+_)?layer(?:_\d+)?_id$|^(?:\w+_)?layer_ids$|^layerId$")
_UUID = re.compile(r"^[0-9a-f]{8}-?(?:[0-9a-f]{4}-?){3}[0-9a-f]{12}$", re.IGNORECASE)


def _layer_values(value: Any) -> list[str]:
    values = value if isinstance(value, list) else [value]
    return [v for v in values if isinstance(v, str) and _UUID.fullmatch(v)]


def _tool_layer_refs(node: Any) -> set[str]:
    """Layer ids under layer-shaped keys, at any depth of a tool's config."""
    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str) and _LAYER_KEY.match(key):
                found.update(_layer_values(value))
            found |= _tool_layer_refs(value)
    elif isinstance(node, list):
        for item in node:
            found |= _tool_layer_refs(item)
    return found


def workflow_layer_refs(config: dict[str, Any] | None) -> set[str]:
    """Every layer a workflow names: its dataset nodes' and its tools'."""
    found: set[str] = set()
    for node in (config or {}).get("nodes") or []:
        data = node.get("data") if isinstance(node, dict) else None
        if not isinstance(data, dict):
            continue
        if data.get("type") == "dataset":
            found.update(_layer_values(data.get("layerId")))
        elif data.get("type") == "tool":
            found |= _tool_layer_refs(data.get("config"))
    return found


def _drop_tool_layer_refs(node: Any, drop: set[str]) -> Any:
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str) and _LAYER_KEY.match(key):
                if isinstance(value, list):
                    node[key] = [v for v in value if v not in drop]
                elif value in drop:
                    node[key] = None
            else:
                _drop_tool_layer_refs(value, drop)
    elif isinstance(node, list):
        for item in node:
            _drop_tool_layer_refs(item, drop)
    return node


def drop_layer_refs(config: dict[str, Any], drop: set[str]) -> dict[str, Any]:
    """The config without the given layers: a dataset node naming one loses
    its dataset (keeping its label, so it shows what it held) and asks for
    another; a tool input naming one is emptied."""
    cleaned = copy.deepcopy(config)
    for node in cleaned.get("nodes") or []:
        data = node.get("data") if isinstance(node, dict) else None
        if not isinstance(data, dict):
            continue
        if data.get("type") == "dataset" and data.get("layerId") in drop:
            data.pop("layerId", None)
            data.pop("projectLayerId", None)
        elif data.get("type") == "tool":
            _drop_tool_layer_refs(data.get("config"), drop)
    return cleaned
