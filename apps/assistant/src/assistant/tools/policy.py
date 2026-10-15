"""The data policy (spec §4.7), applied to every tool flagged ``returns_data``.

Standard sends what the user can see, size-capped. Restricted sends field names
and types, counts, min/max, histograms (class breaks) and the distinct values of
fields with at most ``LOW_CARDINALITY_LIMIT`` of them; never rows, features,
geometries, or aggregates outside that list (mean, standard deviation, sums).

A data tool's output model says how it is reduced, with a ``restricted()``
method. An output without one is withheld entirely: a new data tool that forgot
its Restricted form fails closed, not open.
"""

from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel

from assistant.llm.types import DataPolicy

LOW_CARDINALITY_LIMIT = 50

RESTRICTED_REASON = (
    "Withheld: the organization's data policy (Restricted) does not allow sending "
    "this to the AI."
)


class Withheld(BaseModel):
    withheld: Literal[True] = True
    reason: str = RESTRICTED_REASON


@runtime_checkable
class Restrictable(Protocol):
    def restricted(self) -> BaseModel: ...


def apply_policy(policy: DataPolicy, result: BaseModel) -> BaseModel:
    if policy == "standard":
        return result
    if isinstance(result, Restrictable):
        reduced = result.restricted()
        # A reduction that hands back the very object it was given reduced
        # nothing: fail closed.
        return Withheld() if reduced is result else reduced
    return Withheld()
