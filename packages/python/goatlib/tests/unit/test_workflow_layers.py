"""The layers a workflow names, and a workflow without some of them."""

import pytest
from goatlib.utils.workflow_layers import drop_layer_refs, workflow_layer_refs

pytestmark = pytest.mark.unit

A = "9a99003e-1111-4222-8333-444455556666"
B = "5a84bfa1-1111-4222-8333-444455556666"
C = "b59800b0-1111-4222-8333-444455556666"
BUNDLE = "0f3ac6d0-b178-4f09-a3c9-fd529d7389df"

CONFIG = {
    "nodes": [
        {
            "id": "a",
            "data": {
                "type": "dataset",
                "label": "Schools",
                "layerId": A,
                "projectLayerId": 7,
            },
        },
        {
            "id": "sql",
            "data": {
                "type": "tool",
                "processId": "custom_sql",
                "config": {
                    "input_layer_2_id": B,
                    "additional_layers": [{"alias": "extra", "layer_id": C}],
                    "pt_network_bundle_id": BUNDLE,
                    "sql_query": f"SELECT '{A}' AS not_a_reference",
                },
            },
        },
        {"id": "note", "data": {"type": "textAnnotation", "text": A}},
    ]
}


def test_dataset_nodes_and_layer_shaped_tool_settings_are_found() -> None:
    # Not the bundle, not an id inside SQL text or a note.
    assert workflow_layer_refs(CONFIG) == {A, B, C}


def test_dropped_layers_leave_empty_nodes_and_inputs() -> None:
    cleaned = drop_layer_refs(CONFIG, {A, C})
    dataset = cleaned["nodes"][0]["data"]
    assert "layerId" not in dataset and "projectLayerId" not in dataset
    assert dataset["label"] == "Schools"
    tool = cleaned["nodes"][1]["data"]["config"]
    assert tool["input_layer_2_id"] == B
    assert tool["additional_layers"] == [{"alias": "extra", "layer_id": None}]
    assert tool["pt_network_bundle_id"] == BUNDLE
    # The original is untouched.
    assert CONFIG["nodes"][0]["data"]["layerId"] == A
