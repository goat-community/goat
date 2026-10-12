"""``layer_create_filtered`` ("Save as new layer") carries the source layer's
field_config over to the copy.

The copy is the same kind of layer: without its entries a serial column would
come out as a plain number column users have to type into, and a vocabulary or
a computed formula would stop applying. The rows themselves are copied by the
export; this covers only the metadata step.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from goatlib.tools.base import BaseToolRunner
from goatlib.tools.layer_create_filtered import (
    LayerCreateFilteredParams,
    LayerCreateFilteredToolRunner,
)

SOURCE_CONFIG = {
    "vorhaben_id": {"kind": "serial", "start": 1},
    "uid": {"kind": "uuid"},
    "status": {"kind": "string", "allowed_values": ["neu", "alt"]},
}


def _params(**extra):
    return LayerCreateFilteredParams(
        user_id="00000000-0000-0000-0000-000000000001",
        source_layer_id="11111111-1111-1111-1111-111111111111",
        cql_filter={"op": "=", "args": [{"property": "status"}, "neu"]},
        **extra,
    )


def _runner(source):
    runner = LayerCreateFilteredToolRunner()
    db = MagicMock()
    db.get_layer_info = AsyncMock(return_value=source)
    db.set_layer_field_config = AsyncMock()
    db.copy_layer_serial_counters = AsyncMock()

    async def init():
        runner.db_service = db

    runner._init_db_service = init
    runner._close_db_service = AsyncMock()
    return runner, db


def test_the_copy_gets_the_source_field_config():
    runner, db = _runner({"field_config": SOURCE_CONFIG})
    with patch.object(BaseToolRunner, "run", return_value={"layer_id": "new-layer"}):
        result = runner.run(_params())

    assert result == {"layer_id": "new-layer"}
    db.get_layer_info.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")
    db.set_layer_field_config.assert_awaited_once_with("new-layer", SOURCE_CONFIG)
    # The serial marks go along, so the copy never reuses a deleted number.
    db.copy_layer_serial_counters.assert_awaited_once_with(
        "11111111-1111-1111-1111-111111111111", "new-layer"
    )


def test_a_copy_without_a_serial_column_copies_no_marks():
    runner, db = _runner({"field_config": {"status": {"kind": "string"}}})
    with patch.object(BaseToolRunner, "run", return_value={"layer_id": "new-layer"}):
        runner.run(_params())
    db.copy_layer_serial_counters.assert_not_awaited()


def test_a_source_without_field_config_writes_nothing():
    runner, db = _runner({"field_config": {}})
    with patch.object(BaseToolRunner, "run", return_value={"layer_id": "new-layer"}):
        runner.run(_params())
    db.set_layer_field_config.assert_not_awaited()


def test_temp_mode_writes_nothing():
    runner, db = _runner({"field_config": SOURCE_CONFIG})
    with patch.object(BaseToolRunner, "run", return_value={"layer_id": "tmp"}):
        runner.run(_params(temp_mode=True, workflow_id="w", node_id="n"))
    db.get_layer_info.assert_not_awaited()


def test_a_failure_is_logged_not_raised():
    """The copy and its rows are real by now; the metadata can be redone."""
    runner, db = _runner({"field_config": SOURCE_CONFIG})
    db.set_layer_field_config.side_effect = RuntimeError("db gone")
    with patch.object(BaseToolRunner, "run", return_value={"layer_id": "new-layer"}):
        assert runner.run(_params()) == {"layer_id": "new-layer"}
