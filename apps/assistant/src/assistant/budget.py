"""When an answer stops searching and writes up what it found.

A run has hard limits (``run_max_tool_calls``, ``run_max_tokens``); a run that
hits one fails and the user gets nothing of what it found. So shortly before
either is reached, the model's next call gets no tools and is told to answer
with what it has.
"""

from dataclasses import dataclass

from pydantic_ai.usage import RunUsage

#: Tool calls kept in reserve: a model may call several tools in one step.
#: At most a sixth of the limit, so a small limit still leaves some to use.
TOOL_CALL_RESERVE = 5
#: The next call may be this many times the average call so far: each one
#: carries the results of the calls before it.
NEXT_CALL_FACTOR = 2


@dataclass(frozen=True)
class RunBudget:
    max_tokens: int
    max_tool_calls: int

    def spent(self, usage: RunUsage) -> bool:
        """Time to answer: few tool calls left, or the next model call might
        not fit in the tokens left."""
        reserve = min(TOOL_CALL_RESERVE, self.max_tool_calls // 6)
        if usage.tool_calls >= self.max_tool_calls - reserve:
            return True
        if usage.requests == 0:
            return False
        per_call = usage.total_tokens / usage.requests
        return usage.total_tokens + NEXT_CALL_FACTOR * per_call > self.max_tokens
