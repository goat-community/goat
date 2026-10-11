"""Workflow variables resolve by name; label and description are display-only.

The editor lets an author give a variable a ``label`` (what users see
instead of ``max_abstand_gruppierung``) and a ``description`` (help text).
Both travel with the variable to the runner, which must accept them, keep
them, and never let them change what a ``{{@name}}`` reference resolves to.
"""

from typing import Any

import pytest
from goatlib.tools.workflow_runner import (
    WorkflowRunnerParams,
    build_tool_inputs,
    variable_map,
)

pytestmark = pytest.mark.unit

LABELLED: dict[str, Any] = {
    "id": "var-1",
    "name": "max_abstand_gruppierung",
    "label": "Maximaler Abstand",
    "description": "Größter Abstand zwischen zwei Punkten einer Gruppe, in Metern.",
    "type": "number",
    "defaultValue": 250,
    "order": 0,
}
LEGACY: dict[str, Any] = {
    "id": "var-2",
    "name": "suffix",
    "type": "string",
    "defaultValue": "_neu",
    "order": 1,
}


def _params(variables: list[dict[str, Any]]) -> WorkflowRunnerParams:
    return WorkflowRunnerParams(
        user_id="00000000-0000-0000-0000-000000000001",
        project_id="00000000-0000-0000-0000-000000000002",
        workflow_id="00000000-0000-0000-0000-000000000003",
        folder_id="00000000-0000-0000-0000-000000000004",
        nodes=[],
        edges=[],
        variables=variables,
    )


def _tool(config: dict[str, Any]) -> dict[str, Any]:
    # No processId: schema coercion is not what is under test.
    return {"id": "tool-1", "type": "tool", "data": {"type": "tool", "config": config}}


def test_the_runner_accepts_and_keeps_label_and_description() -> None:
    params = _params([LABELLED, LEGACY])
    assert params.variables == [LABELLED, LEGACY]
    assert params.model_dump()["variables"][0]["label"] == "Maximaler Abstand"


def test_the_variable_map_is_keyed_by_name_and_ignores_display_fields() -> None:
    assert variable_map([LABELLED, LEGACY]) == {
        "max_abstand_gruppierung": 250,
        "suffix": "_neu",
    }


def test_the_variable_map_skips_nameless_entries() -> None:
    assert variable_map([{"label": "Nur ein Label", "defaultValue": 1}]) == {}
    assert variable_map([]) == {}


def test_a_reference_resolves_by_name_whatever_the_label() -> None:
    inputs = build_tool_inputs(
        _tool(
            {
                "distance": "{{@max_abstand_gruppierung}}",
                "name": "Gruppen{{@suffix}}",
            }
        ),
        edges=[],
        all_nodes=[],
        results={},
        params=_params([LABELLED, LEGACY]),
    )
    assert inputs["distance"] == 250
    assert inputs["name"] == "Gruppen_neu"


def test_labelled_and_unlabelled_variables_resolve_alike() -> None:
    without_label = {
        k: v for k, v in LABELLED.items() if k not in ("label", "description")
    }
    config = {"distance": "{{@max_abstand_gruppierung}}"}
    labelled = build_tool_inputs(_tool(config), [], [], {}, _params([LABELLED]))
    legacy = build_tool_inputs(_tool(config), [], [], {}, _params([without_label]))
    assert labelled["distance"] == legacy["distance"] == 250


def test_a_label_is_not_a_name_a_reference_can_use() -> None:
    labelled = {**LABELLED, "label": "abstand"}
    with pytest.raises(ValueError, match="Unknown workflow variable: abstand"):
        build_tool_inputs(
            _tool({"distance": "{{@abstand}}"}), [], [], {}, _params([labelled])
        )
