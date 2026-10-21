"""``ask_user`` (spec §5.1): a card of questions in the dock, on every page.

The card reaches the dock as a ``data-ask`` part whose id is the card id:
``ask-`` and an id the tool mints for the card, never the provider's tool call
id, which some providers number per response and so repeat in a later answer.
After it, the run offers no more tools (``RunDeps.asked``), so the model ends
its answer; the user's choices come with their next message. Not on MCP: its
clients cannot show it.
"""

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel
from pydantic_ai.exceptions import ToolFailed

from assistant.asks import CARD_PREFIX, AskUserInput, card_data
from assistant.surfaces import SURFACES
from assistant.tools.runtime import ToolEnv, ToolSpec

ASKED_NOTE = (
    "The card is shown to the user. End your answer now, without asking the same "
    "in text; their choices come with their next message."
)


class AskShown(BaseModel):
    card_id: str
    status: Literal["asked"] = "asked"
    note: str = ASKED_NOTE


async def _ask(env: ToolEnv, args: AskUserInput) -> AskShown:
    if env.emit_data is None:
        raise ToolFailed(
            "Questions with a card can only be asked in the GOAT assistant."
        )
    card_id = CARD_PREFIX + uuid4().hex
    await env.emit_data("ask", card_data(card_id, args), part_id=card_id)
    return AskShown(card_id=card_id)


ASK_USER: ToolSpec[AskUserInput, AskShown] = ToolSpec(
    name="ask.user",
    description=(
        "Ask the user with a card when they have to choose: which dataset fits, "
        "which variant they mean. Up to four questions in one card, answered "
        "together; each has two to four options with a short label, a one-line "
        "description and optionally a value (an id you need back, never shown). "
        "The card adds a free-text field itself. After it, end your answer."
    ),
    input_model=AskUserInput,
    output_model=AskShown,
    run=_ask,
    surfaces=frozenset(SURFACES),
    returns_data=False,
)
