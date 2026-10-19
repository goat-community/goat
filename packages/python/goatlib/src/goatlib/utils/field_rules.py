"""Rules a layer's ``field_config`` sets for writes to its rows.

Computed columns, locked columns, defaults and allowed values: pure functions
over the ``field_config`` JSONB, shared by geoapi's feature writes and by
goatlib tools that write rows (the workflow's "Append to dataset" node).
"""

from typing import Any

from goatlib.computed_columns import COMPUTED_KIND_REGISTRY


class ComputedColumnSpec:
    """A computed column on a layer: name + dependency-set + compute SQL."""

    __slots__ = ("name", "depends_on", "compute_sql")

    def __init__(
        self,
        name: str,
        depends_on: tuple[str, ...],
        compute_sql: str,
    ) -> None:
        self.name = name
        self.depends_on = depends_on
        self.compute_sql = compute_sql


# Sentinel dependency meaning "recompute on any change to the row".
DEPENDS_ON_ANY = "*"


def parse_computed_columns(
    field_config: dict[str, Any] | None,
    geom_column: str = "geometry",
) -> list[ComputedColumnSpec]:
    """Convert a layer's `field_config` JSONB into a list of specs."""
    specs: list[ComputedColumnSpec] = []
    for name, entry in (field_config or {}).items():
        if not entry.get("is_computed"):
            continue
        kind_name = entry.get("kind")
        if kind_name == "formula":
            # Formula columns carry their own expression. The expression was
            # validated (function whitelist, column existence, no subqueries)
            # when it was stored; parenthesize so it splices safely into a
            # SET clause.
            formula_sql = entry.get("formula")
            if not formula_sql:
                continue
            specs.append(
                ComputedColumnSpec(
                    name=name,
                    depends_on=tuple(entry.get("depends_on") or (DEPENDS_ON_ANY,)),
                    compute_sql=f"({formula_sql})",
                )
            )
            continue
        kind = COMPUTED_KIND_REGISTRY.get(kind_name) if kind_name else None
        if kind is None:
            # Unknown kind (e.g. JSONB written by a newer release).
            # Skip — we can't safely generate SQL for it.
            continue
        specs.append(
            ComputedColumnSpec(
                name=name,
                depends_on=tuple(entry.get("depends_on", kind.depends_on)),
                compute_sql=kind.compute_sql(geom_column),
            )
        )
    return specs


def locked_column_names(field_config: dict[str, Any] | None) -> set[str]:
    """Columns whose owner maintains them, so no write may set them.

    Separate from a computed column, which this service also excludes from
    writes but can regenerate from its own formula. A locked column's value
    comes from somewhere the layer cannot express — a street network's edge
    endpoints are resolved against its nodes layer by the bundle editor — so
    there is nothing to recompute here, only something to refuse to overwrite.
    """
    return {
        name
        for name, entry in (field_config or {}).items()
        if isinstance(entry, dict) and entry.get("is_locked")
    }


def allowed_value_columns(
    field_config: dict[str, Any] | None,
) -> dict[str, list[Any]]:
    """Columns constrained to a vocabulary -> the values a write may set.

    Only columns that actually enforce one: an entry with ``allow_other`` true
    still carries its list, because an editor should offer it as suggestions,
    but a write is not refused for going outside it.
    """
    constrained: dict[str, list[Any]] = {}
    for name, entry in (field_config or {}).items():
        if not isinstance(entry, dict) or entry.get("allow_other"):
            continue
        values = entry.get("allowed_values")
        if isinstance(values, list) and values:
            constrained[name] = values
    return constrained


def column_defaults(field_config: dict[str, Any] | None) -> dict[str, Any]:
    """Columns that supply a value when a new feature leaves them blank."""
    return {
        name: entry["default_value"]
        for name, entry in (field_config or {}).items()
        if isinstance(entry, dict) and entry.get("default_value") is not None
    }


def apply_defaults(
    field_config: dict[str, Any] | None,
    properties: dict[str, Any],
    blank_is_absent: bool = False,
) -> dict[str, Any]:
    """Fill in what a feature did not state. Returns a new dict.

    Creation only, for the per-feature paths. An update that omits a column
    means "leave it alone", so applying defaults there would silently reset
    columns the caller never mentioned.

    ``blank_is_absent`` is the second rule, for a write that replaces a row
    whole: a null or an empty string then means the column was left blank
    rather than deliberately cleared, so it takes the default too. The bundle
    editor writes that way — it sends the whole edge back on every save, and an
    edge with no class is not a routable street. Without the flag an explicit
    null stays null, because clearing a column is a choice and a default that
    overrode it could not be cleared at all.

    This is the only thing that applies a default. A column created with one
    also carries a DuckDB ``DEFAULT``, which would cover an INSERT that omitted
    it, but every write goes through here and names the column explicitly — so
    the ``field_config`` entry is the default of record and the DDL default is
    never consulted.
    """
    return fill_defaults(
        column_defaults(field_config), properties, blank_is_absent=blank_is_absent
    )


def fill_defaults(
    defaults: dict[str, Any],
    properties: dict[str, Any],
    blank_is_absent: bool = False,
) -> dict[str, Any]:
    """``apply_defaults`` against an already-derived default map.

    Separate so a bulk write derives the map once for the whole request rather
    than once per feature.
    """
    filled = dict(properties)
    for name, value in defaults.items():
        if name not in filled or (blank_is_absent and filled[name] in (None, "")):
            filled[name] = value
    return filled


def validate_allowed_values(
    field_config: dict[str, Any] | None, properties: dict[str, Any]
) -> None:
    """Refuse a write that sets a constrained column to something else.

    Refused rather than dropped, which is how a computed or locked column is
    handled: those the caller was never invited to set, so ignoring the value is
    right. Here the caller *is* invited to set it and got it wrong, and silently
    keeping the old value would look like a successful edit.

    A null clears the column, which is not a vocabulary violation — a column
    with no value is a different thing from one holding a value nobody allows.
    """
    check_allowed_values(allowed_value_columns(field_config), properties)


def check_allowed_values(
    constrained: dict[str, list[Any]], properties: dict[str, Any]
) -> None:
    """``validate_allowed_values`` against an already-derived vocabulary map.

    Separate for the same reason as ``fill_defaults``: a bulk write derives the
    map once rather than once per feature.
    """
    for name, value in properties.items():
        if value is None or name not in constrained:
            continue
        if value not in constrained[name]:
            allowed = ", ".join(str(v) for v in constrained[name])
            raise ValueError(
                f"'{value}' is not an accepted value for '{name}'. "
                f"Accepted: {allowed}."
            )


def select_recompute_specs(
    specs: list[ComputedColumnSpec],
    changed_source_cols: set[str],
) -> list[ComputedColumnSpec]:
    """Return the subset whose dependencies overlap the changed cols."""
    if not changed_source_cols:
        return []
    return [
        s
        for s in specs
        if DEPENDS_ON_ANY in s.depends_on
        or changed_source_cols.intersection(s.depends_on)
    ]
