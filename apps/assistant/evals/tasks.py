"""Eval tasks and the checks that grade them.

Tasks live in two JSON Lines files, one task per line, so a diff shows one task
per changed line. Bump ``EVAL_SET_VERSION`` whenever a task or a check changes
meaning: a model is "tested" for one version of the set.
"""

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from assistant.surfaces import Locale

EVAL_SET_VERSION = 12

HERE = Path(__file__).resolve().parent
Suite = Literal["catalog", "project"]
TASK_FILES: dict[Suite, Path] = {
    "catalog": HERE / "catalog_tasks.jsonl",
    "project": HERE / "project_tasks.jsonl",
}


class _Check(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Oracle(_Check):
    """An expected value computed from the fixed backends at grading time."""

    op: Literal[
        "catalog_count", "count", "sum", "min", "max", "mean", "distinct", "top"
    ]
    #: Fixture project layer (all but catalog_count).
    layer: str | None = None
    field: str | None = None
    #: CQL2-JSON over the layer's features.
    filter: dict[str, Any] | None = None
    #: catalog_count: query parameters of GET /stac/collections.
    params: dict[str, Any] = Field(default_factory=dict)


class RecordsCheck(_Check):
    """The run's catalog tool results contain these records (an item or its dataset)."""

    kind: Literal["records"]
    include: list[str] = Field(min_length=1)
    exclude: list[str] = Field(default_factory=list)


class ShownCheck(_Check):
    """The datasets the answer showed as cards (``catalog_show_records``): these
    and not those (an item or its dataset)."""

    kind: Literal["shown"]
    include: list[str] = Field(min_length=1)
    exclude: list[str] = Field(default_factory=list)


class ShownItemsCheck(_Check):
    """The user's own items the answer showed as cards (``core_show_items``),
    by name: these and not those."""

    kind: Literal["shown_items"]
    include: list[str] = Field(min_length=1)
    exclude: list[str] = Field(default_factory=list)


class FiltersCheck(_Check):
    """The last catalog.filters proposal sets these filters."""

    kind: Literal["filters"]
    facets: dict[str, list[str]] = Field(default_factory=dict)
    #: The proposal's search text contains one of these (case-insensitive).
    q_any: list[str] = Field(default_factory=list)
    nuts: list[str] = Field(default_factory=list)


class NumberCheck(_Check):
    """The answer states this number (read in English and German notation)."""

    kind: Literal["number"]
    expected: float | Oracle
    #: Relative tolerance; 0 means exact.
    tolerance: float = 0.0


class NotStatedCheck(_Check):
    """The answer does not state this number: a value the data policy withholds."""

    kind: Literal["not_stated"]
    value: float | Oracle
    #: Relative tolerance: a number within it of the value counts as stating it
    #: ("about 46.000" leaks 46116); 0 means exact.
    tolerance: float = 0.05


class TextCheck(_Check):
    """The answer names this value (case-insensitive)."""

    kind: Literal["text"]
    expected: str | Oracle


class AnswerCheck(_Check):
    kind: Literal["answer"]
    any_of: list[str] = Field(default_factory=list)
    all_of: list[str] = Field(default_factory=list)
    none_of: list[str] = Field(default_factory=list)


class ToolsCheck(_Check):
    """Tools (wire names) the run called, or must not have called."""

    kind: Literal["tools"]
    called: list[str] = Field(default_factory=list)
    not_called: list[str] = Field(default_factory=list)


class ViewCheck(_Check):
    """The last map.view proposal frames this layer, or contains this point."""

    kind: Literal["view"]
    layer_project_id: int | None = None
    contains: tuple[float, float] | None = None


class NotSentCheck(_Check):
    """No request to geoapi or processes names this layer (a locked one)."""

    kind: Literal["not_sent"]
    layer_id: str


class WithheldCheck(_Check):
    """Under Restricted, every result of this tool withholds values (or it was not called)."""

    kind: Literal["withheld"]
    tool: str


class LanguageCheck(_Check):
    """The answer is in this language: the prompt's, whatever language the data
    or the earlier turns are in."""

    kind: Literal["language"]
    expected: Literal["en", "de"]


class JudgeCheck(_Check):
    """Free text, graded by the LLM judge against the rubric (evals.judge)."""

    kind: Literal["judge"]
    rubric: str = Field(min_length=10)


Check = Annotated[
    RecordsCheck
    | ShownCheck
    | ShownItemsCheck
    | FiltersCheck
    | NumberCheck
    | NotStatedCheck
    | TextCheck
    | AnswerCheck
    | ToolsCheck
    | ViewCheck
    | NotSentCheck
    | WithheldCheck
    | LanguageCheck
    | JudgeCheck,
    Field(discriminator="kind"),
]


class Turn(BaseModel):
    """An earlier exchange of the conversation: the user's text and the answer."""

    model_config = ConfigDict(extra="forbid")

    user: str = Field(min_length=1)
    assistant: str = Field(min_length=1)


class EvalTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^(cat|proj)-\d{2}$")
    suite: Suite
    #: The page context as the dock sends it (plan 3's wire format); its
    #: surface decides which tools the agent gets.
    context: dict[str, Any]
    locale: Locale = "en"
    data_policy: Literal["standard", "restricted"] = "standard"
    #: Earlier turns, on the same page, before ``prompt``: a follow-up's answer
    #: can drift into the language or the claims of the conversation so far.
    history: list[Turn] = Field(default_factory=list)
    prompt: str = Field(min_length=3)
    checks: list[Check] = Field(min_length=1)
    #: A model that fails a critical task is not listed as tested, whatever its score.
    critical: bool = False

    @model_validator(mode="after")
    def _surface_fits_suite(self) -> "EvalTask":
        surface = str(self.context.get("surface", ""))
        allowed = (
            surface in ("catalog", "none")
            if self.suite == "catalog"
            else (surface.startswith("project.") or surface == "none")
        )
        if not allowed:
            raise ValueError(
                f"surface {surface!r} does not belong to the {self.suite} suite"
            )
        return self


def load_tasks(suite: Suite | None = None) -> list[EvalTask]:
    tasks: list[EvalTask] = []
    for name, path in TASK_FILES.items():
        if suite is not None and name != suite:
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            task = EvalTask.model_validate_json(line)
            if task.suite != name:
                raise ValueError(
                    f"{path.name}:{number}: a {task.suite} task in the {name} file"
                )
            tasks.append(task)
    ids = [task.id for task in tasks]
    duplicates = sorted({task_id for task_id in ids if ids.count(task_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate task ids: {duplicates}")
    return tasks
