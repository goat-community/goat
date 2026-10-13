"""A workflow variable's optional label and description survive every copy.

The editor stores variables in the workflow's JSONB config next to nodes and
edges. Core does not validate a variable's shape, so a ``label`` (what users
see instead of the technical ``name``) and a ``description`` (help text) must
come back exactly as saved: on read, after an update, through a duplicate,
and through a workflow or project template's save and use. Variables saved
before those fields existed must come back without them.
"""

import copy
from typing import Any, Awaitable, Callable
from uuid import UUID

import pytest
from core.core.config import settings
from core.db.models.folder import Folder
from core.db.models.user import User
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.test_template_api import (
    _create_project,
    _create_workflow,
    _dataset_workflow_config,
)

API = settings.API_V2_STR

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
VARIABLES = [LABELLED, LEGACY]


def _plain_config() -> dict[str, Any]:
    """A workflow with no dataset node, so a template of it asks for nothing."""
    return {
        "nodes": [
            {
                "id": "note-1",
                "type": "textAnnotation",
                "position": {"x": 0, "y": 0},
                "data": {"text": "Uses {{@max_abstand_gruppierung}}"},
            }
        ],
        "edges": [],
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "variables": copy.deepcopy(VARIABLES),
    }


def _assert_variables(variables: list[dict[str, Any]]) -> None:
    assert variables == VARIABLES
    assert "label" not in variables[1]
    assert "description" not in variables[1]


async def _read_workflow(
    client: AsyncClient, project_id: str, workflow_id: str
) -> dict[str, Any]:
    r = await client.get(f"{API}/project/{project_id}/workflow/{workflow_id}")
    assert r.status_code == 200, r.text
    return r.json()


@pytest.mark.asyncio
async def test_save_load_update_and_duplicate_keep_label_and_description(
    client: AsyncClient,
    fixture_get_home_folder: dict[str, object],
) -> None:
    home = str(fixture_get_home_folder["id"])
    project_id = await _create_project(client, home)
    workflow_id = await _create_workflow(client, project_id, _plain_config())

    _assert_variables(
        (await _read_workflow(client, project_id, workflow_id))["config"]["variables"]
    )

    listed = await client.get(f"{API}/project/{project_id}/workflow")
    assert listed.status_code == 200, listed.text
    _assert_variables(listed.json()[0]["config"]["variables"])

    # An edit of the label and description is stored as sent; the variable
    # without either keeps its old shape.
    edited = _plain_config()
    edited["variables"][0] = {
        **LABELLED,
        "label": "Abstand (m)",
        "description": "Neuer Hilfetext.",
    }
    r = await client.put(
        f"{API}/project/{project_id}/workflow/{workflow_id}",
        json={"config": edited},
    )
    assert r.status_code == 200, r.text
    stored = (await _read_workflow(client, project_id, workflow_id))["config"][
        "variables"
    ]
    assert stored[0]["label"] == "Abstand (m)"
    assert stored[0]["description"] == "Neuer Hilfetext."
    assert stored[1] == LEGACY

    # Back to the original variables; a duplicate copies them as they are.
    r = await client.put(
        f"{API}/project/{project_id}/workflow/{workflow_id}",
        json={"config": _plain_config()},
    )
    assert r.status_code == 200, r.text

    dup = await client.post(
        f"{API}/project/{project_id}/workflow/{workflow_id}/duplicate"
    )
    assert dup.status_code == 201, dup.text
    _assert_variables(dup.json()["config"]["variables"])


@pytest.mark.asyncio
async def test_a_workflow_template_keeps_label_and_description_through_save_and_use(
    client: AsyncClient,
    db_session: AsyncSession,
    fixture_create_user: UUID,
    fixture_get_home_folder: dict[str, object],
    make_layer: Callable[..., Awaitable[Any]],
) -> None:
    home = str(fixture_get_home_folder["id"])
    owner = await db_session.get(User, fixture_create_user)
    assert owner is not None
    home_folder = await db_session.get(Folder, UUID(home))
    assert home_folder is not None
    layer = await make_layer(owner, home_folder)
    await db_session.commit()

    config = _dataset_workflow_config(layer.id)
    config["variables"] = copy.deepcopy(VARIABLES)
    source_project_id = await _create_project(client, home, name="source")
    workflow_id = await _create_workflow(client, source_project_id, config)

    create_resp = await client.post(
        f"{API}/template",
        json={
            "name": "Labelled variables",
            "folder_id": home,
            "source": {
                "kind": "workflow",
                "project_id": source_project_id,
                "workflow_id": workflow_id,
            },
            "inputs": [
                {
                    "key": "node:dataset-1",
                    "label": "Input Layer",
                    "mode": "ship",
                    "layer_id": str(layer.id),
                    "layer_type": "feature",
                    "geometry_type": "polygon",
                }
            ],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    tid = create_resp.json()["id"]

    # The frozen config the template stores.
    read = await client.get(f"{API}/template/{tid}", params={"include_config": True})
    assert read.status_code == 200, read.text
    _assert_variables(read.json()["config"]["variables"])

    # Used into another project, the new workflow carries them unchanged.
    target_project_id = await _create_project(client, home, name="target")
    use_resp = await client.post(
        f"{API}/template/{tid}/use", json={"project_id": target_project_id}
    )
    assert use_resp.status_code == 200, use_resp.text
    body = use_resp.json()
    assert body["unresolved_inputs"] == []
    used = await _read_workflow(client, target_project_id, body["workflow_id"])
    _assert_variables(used["config"]["variables"])


@pytest.mark.asyncio
async def test_a_project_template_keeps_label_and_description_through_save_and_use(
    client: AsyncClient,
    fixture_get_home_folder: dict[str, object],
) -> None:
    home = str(fixture_get_home_folder["id"])
    source_project_id = await _create_project(client, home, name="project-src")
    await _create_workflow(client, source_project_id, _plain_config())

    create_resp = await client.post(
        f"{API}/template",
        json={
            "name": "Project with labelled variables",
            "folder_id": home,
            "source": {"kind": "project", "project_id": source_project_id},
            "inputs": [],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    tid = create_resp.json()["id"]

    use_resp = await client.post(
        f"{API}/template/{tid}/use",
        json={"target_folder_id": home, "name": "Copy with variables"},
    )
    assert use_resp.status_code == 200, use_resp.text
    new_project_id = use_resp.json()["project_id"]

    listed = await client.get(f"{API}/project/{new_project_id}/workflow")
    assert listed.status_code == 200, listed.text
    workflows = listed.json()
    assert len(workflows) == 1
    _assert_variables(workflows[0]["config"]["variables"])
