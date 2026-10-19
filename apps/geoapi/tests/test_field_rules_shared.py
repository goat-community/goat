"""geoapi keeps using the field-config rules goatlib now owns."""

from geoapi.services import computed_columns
from goatlib.utils import field_rules


def test_geoapi_reexports_same_objects() -> None:
    for name in (
        "column_defaults",
        "allowed_value_columns",
        "check_allowed_values",
        "parse_computed_columns",
        "select_recompute_specs",
    ):
        assert getattr(computed_columns, name) is getattr(field_rules, name)


def test_layer_lock_key_shared_with_goatlib() -> None:
    from geoapi.services.layer_write_lock import LOCK_NAMESPACE, _lock_key
    from goatlib.utils.layer_lock import LAYER_LOCK_NAMESPACE, layer_lock_key

    assert _lock_key is layer_lock_key
    assert LOCK_NAMESPACE == LAYER_LOCK_NAMESPACE
