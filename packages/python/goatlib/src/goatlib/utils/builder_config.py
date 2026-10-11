"""Layer references in a project's ``builder_config`` (dashboard widgets).

Widgets point at project entries (``layer_project`` link ids) in two shapes:
a ``layer_project_id`` field, and a few lists of link ids named in
``LAYER_PROJECT_ID_LISTS``. A project copy or import gives every entry a new
id, so these are rewritten; nothing else is. Every other number in the config
(shadow, opacity, font sizes, axis ticks) stays as it is, even when it equals
an old link id.

The dashboard's interaction rules (``interactions``) name their sources by a
``sourceId`` whose meaning depends on the rule: an entry for a visibility sync,
a layer group for a tab switch (``remap_interactions``).
"""

from typing import Any

# Lists of link ids in widget options (apps/web/lib/validations/widget.ts).
LAYER_PROJECT_ID_LISTS = frozenset(
    {
        "downloadable_layers",
        "excluded_layers",
        "legend_hidden_layers",
        "legend_simple_layers",
    }
)


def _new_id(value: Any, lp_id_map: dict[int, int]) -> Any:
    if isinstance(value, int) and not isinstance(value, bool):
        return lp_id_map.get(value, value)
    return value


def remap_layer_project_ids(node: Any, lp_id_map: dict[int, int]) -> Any:
    """Return ``node`` with its link-id references mapped through ``lp_id_map``.

    Walks the tree once, so an id is mapped at most once: an old id that
    equals another entry's new id is not rewritten twice. Ids with no mapping
    are kept.
    """
    if isinstance(node, dict):
        out: dict[str, Any] = {}
        for key, value in node.items():
            if key == "layer_project_id":
                out[key] = _new_id(value, lp_id_map)
            elif key in LAYER_PROJECT_ID_LISTS and isinstance(value, list):
                out[key] = [_new_id(item, lp_id_map) for item in value]
            else:
                out[key] = remap_layer_project_ids(value, lp_id_map)
        return out
    if isinstance(node, list):
        return [remap_layer_project_ids(item, lp_id_map) for item in node]
    return node


# Interaction rules (apps/web/lib/validations/interaction.ts) and what their
# `sourceId`s name: the entries of a visibility sync, or the layer groups
# (`layer_project_group` ids) whose activation switches a tab.
_INTERACTION_SOURCE = {"visibility_changed": "link", "group_activated": "group"}


def remap_interactions(
    config: Any, lp_id_map: dict[int, int], group_id_map: dict[int, int]
) -> Any:
    """Return ``config`` with the ``sourceId``s of its ``interactions`` rules
    mapped through the link map or the group map, by rule type.

    ``trigger.sourceId`` and ``mapping[].sourceId`` are both rewritten. A rule
    of another type, and an id with no mapping, are kept as they are.
    """
    if not isinstance(config, dict) or not isinstance(config.get("interactions"), list):
        return config
    rules = []
    for rule in config["interactions"]:
        trigger = rule.get("trigger") if isinstance(rule, dict) else None
        kind = (
            _INTERACTION_SOURCE.get(trigger.get("type"))
            if isinstance(trigger, dict)
            else None
        )
        if kind is None:
            rules.append(rule)
            continue
        id_map = lp_id_map if kind == "link" else group_id_map
        new_rule = {**rule}
        if "sourceId" in trigger:
            new_rule["trigger"] = {
                **trigger,
                "sourceId": _new_id(trigger["sourceId"], id_map),
            }
        if isinstance(rule.get("mapping"), list):
            new_rule["mapping"] = [
                {**m, "sourceId": _new_id(m.get("sourceId"), id_map)}
                if isinstance(m, dict) and "sourceId" in m
                else m
                for m in rule["mapping"]
            ]
        rules.append(new_rule)
    return {**config, "interactions": rules}
