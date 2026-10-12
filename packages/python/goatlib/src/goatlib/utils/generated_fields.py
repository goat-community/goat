"""Generated field kinds: columns whose value GOAT assigns, never the user.

Two kinds today, sharing one path through every writer:

- ``serial`` — a running number (BIGINT) that is never handed out twice. The
  next value is ``max(high_water, max(existing), start - 1) + 1``: an empty
  layer starts at ``start``, a gap left by a delete stays a gap, and the
  high-water mark — the highest number ever handed out, kept in core's
  ``layer_serial_counter`` table — keeps the number of a deleted feature from
  coming back, even when it was the highest. A copy of a layer has no counter
  of its own yet and continues from the highest number it holds. The
  computation is only safe while one writer at a time assigns numbers for a
  layer: geoapi holds a per-layer Postgres advisory lock around every create
  into a layer with a serial column, reads the mark and advances it in that
  same transaction (``geoapi.services.layer_write_lock``), on top of the
  per-process lock its DuckLake write manager already takes.
- ``uuid`` — a random identifier (UUID v4, stored as text). Unique without any
  coordination, so it needs no lock. v4 rather than v7: Python 3.11 has no v7,
  and a v7 id would publish when each feature was created to everyone who can
  read the layer.

A column's settings live flat in its ``field_config`` entry, next to ``kind``,
the way a formula's ``formula`` and ``output_kind`` do::

    {"kind": "serial", "start": 1, ...}
    {"kind": "uuid", ...}

Later variants are meant to be further settings on the same entry, so they need
no migration — none of them is implemented yet:

- ``format`` for serial, e.g. ``"V-{0000}"``: a rendering of the stored
  integer (prefix, zero padding). The column stays BIGINT and keeps counting;
  only what editors and exports show changes.
- ``reset`` for serial, e.g. ``"yearly"``: numbering restarts per period. Needs
  a reference date per row (a creation timestamp the layer does not have yet),
  and uniqueness then holds per (period, number) rather than per number.
- ``version`` for uuid, e.g. ``7``: time-ordered ids where that is wanted.
"""

import uuid
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any, Self

#: The kinds whose values GOAT generates.
GENERATED_KINDS: frozenset[str] = frozenset({"serial", "uuid"})

#: DuckDB storage type per generated kind.
GENERATED_STORAGE_TYPES: dict[str, str] = {"serial": "BIGINT", "uuid": "VARCHAR"}

#: Where a serial column starts counting when its entry names no ``start``.
DEFAULT_SERIAL_START = 1

#: The largest number a browser can hold exactly (2**53 - 1). A serial column
#: is BIGINT, but every value goes through JSON to the web app, where a larger
#: one would silently round to a neighbour — a duplicate on screen.
MAX_SERIAL_VALUE = 9_007_199_254_740_991


def is_generated_kind(kind: str | None) -> bool:
    """Whether GOAT assigns this kind's values."""
    return kind in GENERATED_KINDS


def validate_serial_start(start: Any) -> int:
    """The start of a serial column as an int, or a ValueError saying why not."""
    if start is None:
        return DEFAULT_SERIAL_START
    if isinstance(start, bool) or not isinstance(start, (int, float, str)):
        raise ValueError("The start of a serial number must be a whole number.")
    try:
        number = float(start)
    except ValueError:
        raise ValueError(
            "The start of a serial number must be a whole number."
        ) from None
    if not number.is_integer():
        raise ValueError("The start of a serial number must be a whole number.")
    value = int(number)
    if value < 0 or value > MAX_SERIAL_VALUE:
        raise ValueError(
            f"The start of a serial number must be between 0 and {MAX_SERIAL_VALUE}."
        )
    return value


def generated_entry_settings(kind: str, start: Any = None) -> dict[str, Any]:
    """The settings a generated column's ``field_config`` entry carries.

    Merged into the entry next to ``kind`` by both writers of an entry (geoapi's
    add-column endpoint and the layer-create tool), so a column means the same
    thing however it was made.
    """
    if kind == "serial":
        return {"start": validate_serial_start(start)}
    if kind == "uuid":
        if start is not None:
            raise ValueError("A UUID field has no start value.")
        return {}
    raise ValueError(f"'{kind}' is not a generated field kind.")


@dataclass(frozen=True)
class GeneratedField:
    """One generated column of a layer."""

    name: str
    kind: str
    start: int = DEFAULT_SERIAL_START

    def backfill_sql(self: Self, table: str, high_water: int | None = None) -> str:
        """Fill this column on every row that has no value yet.

        Rows are numbered in ``rowid`` order — the order features were created
        in, and what their public feature id is derived from — continuing after
        the highest number already present or ever handed out (``high_water``).
        On a column just added that is every row, starting at ``start``.
        """
        column = f'"{self.name}"'
        if self.kind == "uuid":
            return (
                f"UPDATE {table} SET {column} = gen_random_uuid()::VARCHAR "
                f"WHERE {column} IS NULL"
            )
        floor = self.start - 1
        if high_water is not None:
            floor = max(floor, int(high_water))
        base = (
            f"(SELECT greatest(coalesce(max({column}), {floor}), {floor}) FROM {table})"
        )
        return (
            f"UPDATE {table} SET {column} = numbered.value "
            f"FROM (SELECT rowid AS rid, {base} + row_number() OVER (ORDER BY rowid) "
            f"AS value FROM {table} WHERE {column} IS NULL) AS numbered "
            f"WHERE {table}.rowid = numbered.rid"
        )


def generated_fields(field_config: dict[str, Any] | None) -> list[GeneratedField]:
    """The layer's generated columns, read from its ``field_config``.

    An entry with a malformed ``start`` falls back to the default rather than
    failing every write to the layer: the start was validated when the column
    was created, so a bad one can only come from a hand-edited blob.
    """
    fields: list[GeneratedField] = []
    for name, entry in (field_config or {}).items():
        if not isinstance(entry, dict) or not is_generated_kind(entry.get("kind")):
            continue
        start = DEFAULT_SERIAL_START
        if entry["kind"] == "serial":
            try:
                start = validate_serial_start(entry.get("start"))
            except ValueError:
                start = DEFAULT_SERIAL_START
        fields.append(GeneratedField(name=name, kind=entry["kind"], start=start))
    return fields


def needs_write_lock(fields: list[GeneratedField]) -> bool:
    """Whether assigning these columns' values needs the layer's write lock.

    Only a serial number depends on what other writers do; a UUID is unique on
    its own.
    """
    return any(f.kind == "serial" for f in fields)


def _same_value(kind: str, stored: Any, sent: Any) -> bool:
    """Whether a value a client sent back is the one already stored.

    Loose about representation only: a serial arrives from JSON as 7, 7.0 or
    "7", and all of those are the stored 7.
    """
    if stored is None or sent is None:
        return stored is None and sent is None
    if kind == "serial":
        try:
            return float(sent) == float(stored)
        except (TypeError, ValueError):
            return False
    return str(sent).lower() == str(stored).lower()


def refuse_generated_changes(
    fields: list[GeneratedField],
    current: dict[str, Any],
    properties: dict[str, Any],
) -> None:
    """Refuse an update that would change a generated value.

    A client that round-trips a whole feature sends the stored value back
    unchanged, which is fine and simply not written. Anything else — another
    number, a blank — is refused with a message that says why, rather than
    dropped, because silently keeping the old value would look like a
    successful edit.
    """
    for field in fields:
        if field.name not in properties or field.name not in current:
            continue
        if not _same_value(field.kind, current[field.name], properties[field.name]):
            raise ValueError(
                f"'{field.name}' is assigned automatically and cannot be changed."
            )


@dataclass
class SerialCounters:
    """A layer's serial high-water marks, in and out of one write.

    ``high_water`` is what the counter table held when the write took the
    layer's lock; ``assigned`` is the highest number the write handed out (or
    found in the table) per column, which the lock's owner stores back before
    releasing it. A column with no mark — a copy, a layer from before the
    table existed — simply has no entry and falls back to the table's own
    maximum.
    """

    high_water: dict[str, int] = dataclass_field(default_factory=dict)
    assigned: dict[str, int] = dataclass_field(default_factory=dict)

    def record(self: Self, name: str, value: int) -> None:
        """Note a number as handed out; the mark only ever moves up."""
        if value > self.assigned.get(name, value - 1):
            self.assigned[name] = value


class GeneratedValues:
    """Hands out the values of a layer's generated columns, one row at a time.

    Built inside the write — after the layer's write lock is held, on the
    connection that then inserts — so the serial numbers it starts from are the
    ones actually in the table. In a DuckDB transaction it sees the
    transaction's own earlier inserts, which is what lets one batch hand out
    consecutive numbers.

    It also fills in any row that is still missing a value first. A column is
    added and backfilled before its ``field_config`` entry exists, so a feature
    created in between, or by a writer that does not know about generated
    columns, would otherwise keep a blank for good; repairing it here, under the
    same lock, keeps every row numbered.
    """

    def __init__(
        self: Self,
        con: Any,
        table: str,
        fields: list[GeneratedField],
        counters: SerialCounters | None = None,
    ) -> None:
        self._fields = fields
        self._next: dict[str, int] = {}
        self._counters = counters if counters is not None else SerialCounters()
        if not fields:
            return
        marks = self._counters.high_water
        missing_sql = ", ".join(
            f'count(*) FILTER (WHERE "{f.name}" IS NULL)' for f in fields
        )
        row = con.execute(f"SELECT {missing_sql} FROM {table}").fetchone() or ()
        for gen, missing in zip(fields, row):
            if missing:
                con.execute(gen.backfill_sql(table, marks.get(gen.name)))
        serials = [f for f in fields if f.kind == "serial"]
        if serials:
            max_sql = ", ".join(f'max("{f.name}")' for f in serials)
            maxima = con.execute(f"SELECT {max_sql} FROM {table}").fetchone() or ()
            for gen, highest in zip(serials, maxima):
                last = max(
                    gen.start - 1,
                    int(highest) if highest is not None else gen.start - 1,
                    int(marks.get(gen.name, gen.start - 1)),
                )
                self._next[gen.name] = last + 1
                if highest is not None:
                    # What the table already holds — a repaired blank, or a
                    # copy's own numbers — is part of the mark from now on.
                    self._counters.record(gen.name, int(highest))

    @property
    def names(self: Self) -> set[str]:
        """The columns this hands out values for."""
        return {f.name for f in self._fields}

    def next_row(self: Self) -> dict[str, Any]:
        """The generated values of the next row to be inserted."""
        values: dict[str, Any] = {}
        for field in self._fields:
            if field.kind == "serial":
                value = self._next[field.name]
                if value > MAX_SERIAL_VALUE:
                    raise ValueError(f"'{field.name}' has run out of serial numbers.")
                values[field.name] = value
                self._next[field.name] = value + 1
                self._counters.record(field.name, value)
            else:
                values[field.name] = str(uuid.uuid4())
        return values
