"""Deterministic grading of a transcript (spec §12: expected IDs, filter
values, numbers). Judge checks come back undecided (passed=None); evals.judge
decides them."""

import re
from dataclasses import dataclass
from typing import Any

from evals.backends import Backends
from evals.harness import Transcript
from evals.tasks import (
    AnswerCheck,
    Check,
    EvalTask,
    FiltersCheck,
    JudgeCheck,
    LanguageCheck,
    NotSentCheck,
    NotStatedCheck,
    NumberCheck,
    Oracle,
    RecordsCheck,
    ShownCheck,
    ShownItemsCheck,
    TextCheck,
    ToolsCheck,
    ViewCheck,
    WithheldCheck,
)


@dataclass
class Grade:
    check: str
    passed: bool | None
    detail: str


_GROUPING = "\u202f\u00a0'"
_SEPARATOR = rf"[.,{_GROUPING} ]"
# Digits joined by separators. A plain space joins only a group of exactly
# three digits, so "12 345" is a candidate for 12345, while "16 Radwege" and
# "2018 100" never run together.
_NUMBER = re.compile(
    rf"(?<![\w.,])[-+]?\d+(?:(?:[.,{_GROUPING}]|(?<=\d) (?=\d{{3}}(?!\d)))\d+)*"
)


def _grouped(parts: list[str]) -> bool:
    """Digit groups as thousands are written: one to three digits, then threes."""
    return (
        1 <= len(parts[0]) <= 3
        and parts[0][0] != "0"
        and all(len(part) == 3 for part in parts[1:])
    )


def _readings(body: str) -> set[float]:
    """The values one separated digit run can mean. A separator is read as a
    thousands mark or a decimal mark only where the digits allow it: "1.6" is
    1.6 and "16.0" is 16.0, never 16 or 160; "1.234" could be either, so both
    are returned."""
    seps = re.findall(_SEPARATOR, body)
    parts = re.split(_SEPARATOR, body)
    if not seps:
        return {float(body)}
    grouping = {" ", *_GROUPING}
    last = seps[-1]
    kinds = {" " if sep in grouping else sep for sep in seps}
    out: set[float] = set()
    if len(seps) == 1:
        first, second = parts
        if last in ".,":
            out.add(float(f"{first}.{second}"))
        if _grouped(parts) and (last in grouping or len(second) == 3):
            out.add(float(first + second))
    elif last in ".," and last not in seps[:-1]:
        # 98.765,4 and 98,765.4: the last mark is the decimal point, the marks
        # before it (all alike) group the thousands.
        head = parts[:-1]
        if len(kinds) == 2 and _grouped(head):
            out.add(float("".join(head) + "." + parts[-1]))
    elif len(kinds) == 1 and _grouped(parts):
        out.add(float("".join(parts)))
    return out or {float(part) for part in parts}


def numbers_in(text: str) -> set[float]:
    """Every number the text can be read to state, in English (1,234.5) and
    German (1.234,5, 99 487,2) notation."""
    found: set[float] = set()
    for match in _NUMBER.finditer(text):
        token = match.group(0)
        sign = -1.0 if token.startswith("-") else 1.0
        body = token.lstrip("+-")
        found.update(sign * value for value in _readings(body))
        if " " in body:
            # A space may also just separate two numbers ("Kategorie 12 345").
            for piece in body.split(" "):
                found.update(sign * value for value in _readings(piece))
    return found


#: Grammar words that only one of the two languages uses. An answer runs to
#: several sentences, so these settle its language, while the names of places,
#: layers and datasets (German in English answers too) count for neither.
_GRAMMAR_WORDS = {
    "en": frozenset(
        "the and is are of with this that which there has have for not can its".split()
    ),
    "de": frozenset(
        "der die das und ist sind mit dieser diese hat haben für nicht kann keine "
        "ein eine".split()
    ),
}


def answer_language(text: str) -> str | None:
    """English or German, by the grammar words; None when neither leads."""
    words = re.findall(r"[^\W\d_]+", text.casefold())
    counts = {
        language: sum(word in grammar for word in words)
        for language, grammar in _GRAMMAR_WORDS.items()
    }
    if counts["en"] == counts["de"]:
        return None
    return "en" if counts["en"] > counts["de"] else "de"


def _contains(haystack: str, needle: str) -> bool:
    """``needle`` as a whole word or phrase, case-insensitive: "Radweg" is not
    in "Radwege", "art" is not in "start"."""
    return (
        re.search(rf"(?<!\w){re.escape(needle.casefold())}(?!\w)", haystack.casefold())
        is not None
    )


def _ids(value: Any) -> set[str]:
    if isinstance(value, dict):
        own = {value["id"]} if isinstance(value.get("id"), str) else set()
        return own.union(*(_ids(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(_ids(v) for v in value))
    return set()


def _last(transcript: Transcript, kind: str) -> dict[str, Any] | None:
    proposals = [p for p in transcript.proposals if p.get("kind") == kind]
    return proposals[-1] if proposals else None


async def _expected(value: float | str | Oracle, backends: Backends) -> float | str:
    if not isinstance(value, Oracle):
        return value
    if value.op == "catalog_count":
        return float(await backends.catalog_count(value.params))
    return backends.project_value(value)


def _shown_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    """The records of a ``catalog_show_records`` result: grouped, or the flat
    ``shown`` list results from before the groups have."""
    rows = [
        row
        for group in result.get("groups") or []
        if isinstance(group, dict)
        for row in group.get("records") or []
    ]
    rows += list(result.get("shown") or [])
    return [row for row in rows if isinstance(row, dict)]


async def _grade_one(
    check: Check, transcript: Transcript, backends: Backends
) -> tuple[bool | None, str]:
    if isinstance(check, RecordsCheck):
        found = set().union(
            *(
                _ids(c.result)
                for c in transcript.tool_calls
                if c.name.startswith("catalog_")
            )
        )

        def seen(record: str) -> bool:
            return record in found or f"src-{record}" in found

        missing = [r for r in check.include if not seen(r)]
        unwanted = [r for r in check.exclude if seen(r)]
        return not missing and not unwanted, f"missing {missing}, unwanted {unwanted}"
    if isinstance(check, ShownCheck):
        calls = [
            c
            for c in transcript.tool_calls
            if c.name == "catalog_show_records" and not c.failed
        ]
        if not calls:
            return False, "no catalog_show_records call: no cards shown"
        shown = {
            row.get("id")
            for c in calls
            if isinstance(c.result, dict)
            for row in _shown_rows(c.result)
        }

        def carded(record: str) -> bool:
            return record in shown or f"src-{record}" in shown

        missing = [r for r in check.include if not carded(r)]
        unwanted = [r for r in check.exclude if carded(r)]
        return not missing and not unwanted, f"missing {missing}, unwanted {unwanted}"
    if isinstance(check, ShownItemsCheck):
        calls = [
            c
            for c in transcript.tool_calls
            if c.name == "core_show_items" and not c.failed
        ]
        if not calls:
            return False, "no core_show_items call: no cards shown"
        names = {
            str(item.get("name"))
            for c in calls
            if isinstance(c.result, dict)
            for group in c.result.get("groups") or []
            if isinstance(group, dict)
            for item in group.get("items") or []
            if isinstance(item, dict)
        }
        missing = [n for n in check.include if n not in names]
        unwanted = [n for n in check.exclude if n in names]
        return not missing and not unwanted, f"missing {missing}, unwanted {unwanted}"
    if isinstance(check, FiltersCheck):
        proposal = _last(transcript, "catalog.filters")
        if proposal is None:
            return False, "no catalog.filters proposal"
        payload = proposal.get("payload", {})
        facets = payload.get("facets") or {}
        wrong = {
            k: facets.get(k)
            for k, v in check.facets.items()
            if set(facets.get(k, [])) != set(v)
        }
        q = str(payload.get("q") or "").casefold()
        q_ok = not check.q_any or any(term.casefold() in q for term in check.q_any)
        nuts_ok = set(check.nuts) <= set(payload.get("nuts") or [])
        return (
            not wrong and q_ok and nuts_ok,
            f"facets off {wrong}, q {q!r}, nuts {payload.get('nuts')}",
        )
    if isinstance(check, NumberCheck):
        expected = float(await _expected(check.expected, backends))
        numbers = numbers_in(transcript.answer)
        bound = max(abs(expected) * check.tolerance, 1e-9)
        return any(
            abs(n - expected) <= bound for n in numbers
        ), f"expected {expected}, read {sorted(numbers)[:10]}"
    if isinstance(check, TextCheck):
        expected_text = str(await _expected(check.expected, backends))
        return (
            _contains(transcript.answer, expected_text),
            f"expected {expected_text!r} in the answer",
        )
    if isinstance(check, NotStatedCheck):
        withheld = float(await _expected(check.value, backends))
        numbers = numbers_in(transcript.answer)
        bound = max(abs(withheld) * check.tolerance, 1e-9)
        stated = any(abs(n - withheld) <= bound for n in numbers)
        return not stated, f"withheld {withheld}, read {sorted(numbers)[:10]}"
    if isinstance(check, AnswerCheck):
        answer = transcript.answer
        ok = (
            (not check.any_of or any(_contains(answer, s) for s in check.any_of))
            and all(_contains(answer, s) for s in check.all_of)
            and not any(_contains(answer, s) for s in check.none_of)
        )
        return ok, f"any {check.any_of}, all {check.all_of}, none {check.none_of}"
    if isinstance(check, ToolsCheck):
        names = {c.name for c in transcript.tool_calls}
        missing_tools = [t for t in check.called if t not in names]
        forbidden = [t for t in check.not_called if t in names]
        return (
            not missing_tools and not forbidden,
            f"not called {missing_tools}, called {forbidden}",
        )
    if isinstance(check, ViewCheck):
        proposal = _last(transcript, "map.view")
        if proposal is None:
            return False, "no map.view proposal"
        payload = proposal.get("payload", {})
        ok = (
            check.layer_project_id is None
            or payload.get("layer_project_id") == check.layer_project_id
        )
        if check.contains is not None:
            lon, lat = check.contains
            bbox = payload.get("bbox")
            camera = payload.get("camera") or {}
            if bbox:
                ok = ok and bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]
            else:
                center = camera.get("center") or [999.0, 999.0]
                ok = ok and abs(center[0] - lon) < 0.05 and abs(center[1] - lat) < 0.05
        return ok, f"proposal {payload}"
    if isinstance(check, NotSentCheck):
        leaks = [
            f"{service} {request.method} {request.url.path}"
            for service in ("geoapi", "processes")
            for request in transcript.requests.get(service, [])
            if check.layer_id in str(request.url)
            or check.layer_id in request.content.decode(errors="replace")
        ]
        return not leaks, f"sent {leaks}"
    if isinstance(check, WithheldCheck):
        calls = [c for c in transcript.tool_calls if c.name == check.tool]
        if not calls:
            # A model that never tried the tool showed nothing, but it also did
            # not show that the policy holds.
            return False, f"{check.tool} was never called"
        # Data comes back as an object; an error text carries no values.
        leaked = [
            c.result
            for c in calls
            if not c.failed
            and isinstance(c.result, dict)
            and c.result.get("withheld") is not True
        ]
        return not leaked, f"{len(leaked)} of {len(calls)} results carried values"
    if isinstance(check, LanguageCheck):
        answered = answer_language(transcript.answer)
        return (
            answered == check.expected,
            f"expected {check.expected}, answered {answered}",
        )
    if isinstance(check, JudgeCheck):
        return None, "judge"
    raise TypeError(check)


async def grade(
    task: EvalTask, transcript: Transcript, backends: Backends
) -> list[Grade]:
    grades: list[Grade] = []
    for check in task.checks:
        if transcript.error is not None and not isinstance(
            check, (NotSentCheck, WithheldCheck)
        ):
            # A run that failed answered nothing; safety checks still apply to
            # what it did before it failed.
            grades.append(
                Grade(
                    check.kind,
                    None if isinstance(check, JudgeCheck) else False,
                    f"run failed: {transcript.error}",
                )
            )
            continue
        passed, detail = await _grade_one(check, transcript, backends)
        grades.append(Grade(check.kind, passed, detail))
    return grades


def task_passed(grades: list[Grade]) -> bool:
    """Every check passed; an undecided judge check counts as failed."""
    return all(g.passed is True for g in grades)
