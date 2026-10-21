"""The text of a failed workflow step, as people see it.

A Windmill job that raised stores `{"error": {"name", "message", "stack",
...}}` as its result. The workflow runner lists each failed step with this
reduction of its error, and processes applies the same one to a failed
child job while the run goes on, so a step's error reads the same during
and after a run: the message (the name when there is none), never the stack
or the extra details, cut to a length a step badge and the issue list can
show, without credentials. Standard library only, like the rest of
`goatlib.workflows`.
"""

import re

from goatlib.utils.credentials import redact_credentials

MAX_MESSAGE_LENGTH = 500

# Windmill names who cancelled a job ("cancelled by <username>"); the name
# is not shown.
_CANCELLED_BY = re.compile(r"cancelled by \S+")


def error_message(error: object) -> str:
    """A step error's message: a Windmill error's `message` (its `name` when
    the message is empty), an exception's text (its type when the text is
    empty), or the text of anything else."""
    if isinstance(error, dict):
        text = str(error.get("message") or error.get("name") or "")
    elif isinstance(error, BaseException):
        text = str(error) or type(error).__name__
    elif error is None:
        text = ""
    else:
        text = str(error)
    text = _CANCELLED_BY.sub("cancelled", text).strip() or "Unknown error"
    text = redact_credentials(text)
    if len(text) > MAX_MESSAGE_LENGTH:
        text = text[: MAX_MESSAGE_LENGTH - 1] + "…"
    return text


def step_errors(errors: object) -> dict[str, str]:
    """Each failed step's message, keyed by step id, from a run result's
    `errors` list.

    An entry is `{"node_id", "message"}`; an entry holding the raw error
    instead (`{"node_id", "error"}`) is reduced the same way. Entries
    without a step id are left out; the first entry of a step wins.
    """
    found: dict[str, str] = {}
    if not isinstance(errors, list):
        return found
    for entry in errors:
        if not isinstance(entry, dict) or not entry.get("node_id"):
            continue
        raw = entry["message"] if "message" in entry else entry.get("error")
        found.setdefault(str(entry["node_id"]), error_message(raw))
    return found
