"""The check's issues in the draft's own terms, and which of them may stay open
when the workflow is created (spec §4.3, §4.4).

Processes checks the converted config and names steps by node id; the model
fixes its draft by the draft's ids, so the issues are mapped back. A one-step
issue's message starts with the step's name, so the answer can quote it; an
issue of several steps or of the whole workflow keeps processes' message.
"""

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field

from assistant.workflows.draft import Converted, DatasetStep, Draft

#: Levels that stop a run (``goatlib.workflows.checks``).
BLOCKING_LEVELS = frozenset({"damaged", "error"})
#: The assistant's own code: a ``where`` field the step's layer does not have.
FILTER_FIELD_CODE = "filter_field_not_in_layer"
_LISTED_FIELDS = 30


class DraftIssue(BaseModel):
    code: str
    level: str
    #: The draft ids of the steps it concerns; empty for the whole workflow.
    steps: list[str] = Field(default_factory=list)
    #: A tool input or setting name, or a filter's field.
    field: str | None = None
    message: str


def _prefixed(message: str, label: str) -> str:
    return message if message.startswith(f"{label}:") else f"{label}: {message}"


def draft_issues(
    raw: Sequence[Mapping[str, Any]], converted: Converted
) -> list[DraftIssue]:
    """The check's issues (``Issue.to_dict()`` rows) with node ids mapped to
    draft ids; a one-step issue's message starts with that step's name."""
    found: list[DraftIssue] = []
    for row in raw:
        node_ids = [str(node) for node in row.get("node_ids") or []]
        steps = [
            converted.step_of[node] for node in node_ids if node in converted.step_of
        ]
        message = str(row.get("message") or row.get("code") or "")
        if len(steps) == 1:
            message = _prefixed(message, converted.labels[steps[0]])
        field = row.get("field")
        found.append(
            DraftIssue(
                code=str(row.get("code") or ""),
                level=str(row.get("level") or "error"),
                steps=steps,
                field=str(field) if field is not None else None,
                message=message,
            )
        )
    return found


def _field_list(fields: Sequence[str]) -> str:
    """The layer's fields for a message: at most ``_LISTED_FIELDS``, then the
    number of fields left out."""
    if not fields:
        return "The layer has no fields that can be filtered."
    listed = ", ".join(fields[:_LISTED_FIELDS])
    more = len(fields) - _LISTED_FIELDS
    suffix = f" (and {more} more)" if more > 0 else ""
    return f"Its fields: {listed}{suffix}."


def filter_field_issues(
    draft: Draft,
    fields: Mapping[str, Sequence[str] | None],
    labels: Mapping[str, str],
) -> list[DraftIssue]:
    """A ``where`` condition on a field the step's layer does not have.
    ``fields``: draft step id -> its layer's field names, None while they
    cannot be read (a catalog layer whose data is still being copied); such a
    step is not judged."""
    found: list[DraftIssue] = []
    for step in draft.steps:
        if not isinstance(step, DatasetStep) or step.filter is None:
            continue
        known = fields.get(step.id)
        if known is None:
            continue
        field_list = _field_list(known)
        for condition in step.filter.where:
            if condition.field in known:
                continue
            found.append(
                DraftIssue(
                    code=FILTER_FIELD_CODE,
                    level="error",
                    steps=[step.id],
                    field=condition.field,
                    message=(
                        f"{labels[step.id]}: the filter's field {condition.field!r} "
                        f"is not in the layer. {field_list}"
                    ),
                )
            )
    return found


def _named_in(issue: DraftIssue, settings: Mapping[str, frozenset[str]]) -> bool:
    return issue.field is not None and all(
        issue.field in settings.get(step, ()) for step in issue.steps
    )


def _stays_open(
    issue: DraftIssue,
    open_ids: frozenset[str],
    field_settings: Mapping[str, frozenset[str]],
    layer_settings: Mapping[str, frozenset[str]],
) -> bool:
    if issue.level != "error" or not issue.steps or not set(issue.steps) <= open_ids:
        return False
    # Reported on dataset steps only, and a dataset step is open only when
    # it is left open itself.
    if issue.code == "layer_not_chosen":
        return True
    if issue.code == "setting_invalid":
        # No field: a rejection of the step as a whole, whose cause the check
        # does not name; the layer still to be chosen may be it.
        return issue.field is None or _named_in(issue, layer_settings)
    return issue.code == "setting_required" and _named_in(issue, field_settings)


def split_issues(
    issues: Sequence[DraftIssue],
    open_ids: frozenset[str],
    *,
    field_settings: Mapping[str, frozenset[str]] = {},
    layer_settings: Mapping[str, frozenset[str]] = {},
) -> tuple[list[DraftIssue], list[DraftIssue]]:
    """``(blocking, open)``. Warnings are neither. An error stays open only
    when every step it names is an open step or reads from one
    (``draft.open_steps``) and the layer still to be chosen can cause it: no
    layer chosen; a required field setting reading that layer
    (``field_settings``: draft step id -> those settings); a setting the tool
    rejects when it reads that layer (``layer_settings``: draft step id ->
    the inputs fed from an open step and the settings reading them); and a
    rejection of the step as a whole (no field), whatever its cause, since
    the check does not name one. Everything else blocks: a damaged issue,
    an issue of the whole workflow, a rejected setting that reads no layer
    still to be chosen, and the other errors, such as a loop, an unknown
    input, a removed tool, a field missing from another input's layer or a
    filter on a chosen layer. ``field_not_in_layer`` is never open: processes
    judges a field setting only against a layer it can read."""
    blocking: list[DraftIssue] = []
    still_open: list[DraftIssue] = []
    for issue in issues:
        if issue.level not in BLOCKING_LEVELS:
            continue
        if _stays_open(issue, open_ids, field_settings, layer_settings):
            still_open.append(issue)
        else:
            blocking.append(issue)
    return blocking, still_open
