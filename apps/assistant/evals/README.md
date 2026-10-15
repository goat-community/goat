# GOAT eval set

33 catalog tasks and 18 project tasks that grade a model on what GOAT's assistant does (spec §12). The agent,
prompt, tools and limits are the production ones; the services behind the tools are fixed (decision E16): the
catalog app over its fixture catalog plus ten named rows, and canned answers for one fixture project
("Radverkehr Leipzig"). Checks are deterministic (expected records, filters, numbers, named values, tools, layers
never sent, values withheld); five free-text tasks go to an LLM judge.

It spends provider tokens, so it runs by hand, never in CI: `run` refuses when `CI` is set.

```bash
cd apps/assistant
uv run python -m evals list
# A candidate model (ASSISTANT_EVAL_API_KEY) judged by a different model (ASSISTANT_EVAL_JUDGE_API_KEY):
ASSISTANT_EVAL_API_KEY=<key> ASSISTANT_EVAL_JUDGE_API_KEY=<judge key> \
  uv run python -m evals run --provider openai_compatible \
  --model <model id> --base-url https://llm.example.org/v1 \
  --judge-provider <judge provider> --judge-model <judge model id>
# GOAT AI as ASSISTANT_DEFAULT_* configure it, judged by the same settings' model
# (fine for a look; promotion refuses a model that judged itself):
uv run python -m evals run
uv run python -m evals run --suite catalog --task cat-14 --no-judge   # a quick look
```

`run` always names its model: `--provider` and `--model`, or the instance's `ASSISTANT_DEFAULT_*`. Use a judge
that is not the model under test (`--judge-provider`, `--judge-model`, `--judge-base-url`, `--judge-region`):
`promote` refuses a run in which the model graded itself, and records the judge in the list entry.

`ASSISTANT_DEFAULT_API_KEY` is used only for GOAT AI's own provider and endpoint. Any other model or judge needs its
key in `ASSISTANT_EVAL_API_KEY` or `ASSISTANT_EVAL_JUDGE_API_KEY` (or the variable named by `--api-key-env` /
`--judge-api-key-env`); without it `run` refuses. Bedrock and Vertex AI use the SDK credential chain. Flags that
would be ignored (`--model` without `--provider`, `--judge-*` without `--judge-provider` or with `--no-judge`) are
an error. Promotion recomputes the score from the per-task records and needs a judge that is neither the test provider nor the model under test.

Each run writes `evals/results/<time>-<provider>-<model>.json` (not committed): per task the grades, the answer,
the tools called, tokens, the time to the first text and in total; a summary with the score per suite and the
critical tasks that failed.

**Tested models.** A model enters `src/assistant/llm/tested_models.json`, which the admin AI page reads, only
through `uv run python -m evals promote evals/results/<file>.json`. It refuses unless the run covered every
task of the current `EVAL_SET_VERSION`, every judge check was decided, no critical task failed, and the score
is at least 0.85 overall and 0.8 per suite. Commit the changed `tested_models.json`.

**Changing tasks.** One task per line in `catalog_tasks.jsonl` and `project_tasks.jsonl`. Bump
`EVAL_SET_VERSION` in `tasks.py` when a task or check changes meaning: models tested against an older version
keep their entry until re-run, and `promote` only accepts results of the current version.
