# assistant

GOAT's AI assistant service: conversations, detached agent runs and their event streams. Design:
`docs/superpowers/specs/2026-10-01-goat-ai-assistant-design.md`.

Run locally (port 8500): `ASSISTANT_DEFAULT_PROVIDER=test ASSISTANT_DEFAULT_MODEL=demo uv run uvicorn assistant.main:app --port 8500` from `apps/assistant`.
Without `ASSISTANT_DEFAULT_PROVIDER` the service has no default model and reports AI as unavailable.

`/mcp` is the MCP endpoint (Streamable HTTP, stateless, JSON responses): the read-only catalog tools
`catalog_search`, `catalog_describe`, `catalog_get_record`, `catalog_suggest_terms`, `catalog_find_region`. It
replaces the catalog
service's `/mcp`. `ASSISTANT_ENABLE_MCP` switches it, `ASSISTANT_MCP_ALLOWED_HOSTS` is its DNS-rebinding host
allow-list (`*` by default; name the real ingress host in production, as `host` and `host:*` if clients may send a
port). With `AUTH=True` it needs a GOAT bearer token. It takes `POST` only.
An MCP client that signs in through a Keycloak client of its own needs that client in `AUTH_ALLOWED_CLIENTS` when
the list is set: the assistant checks tokens as core does, and core checks them again when a tool passes one on.
Its tool-call audit rows belong to no conversation; the run sweeper deletes them after
`ASSISTANT_MCP_AUDIT_RETENTION_DAYS` (30 by default, at least 1).

Anything about GOAT data (dataset names, ids, counts, field values) comes only from tool results. Other questions
(history, places, planning terms) the model answers from its own knowledge; a detail a planner might rely on, such
as which district a quarter belongs to, is marked as general knowledge that was not checked against data.

Catalog searches filter places by NUTS region (`catalog_find_region`, then `nuts` on `catalog_search`), not by
the place name in the search text, which only matches datasets whose text names the place. NUTS names places in
their own languages, so `catalog_find_region` also knows each NUTS country by its English and German name. The dock shows a
dataset card only for what the answer recommends, named with `catalog_show_records`: an answer searches several
times, and its first hits are rarely the datasets it ends up recommending. The cards come in groups with a one-line
note each, so the answer's text keeps to the purpose, caveats and gaps instead of listing the datasets again.
`core_show_items` does the same for the user's own projects, datasets, bundles and project layers, and for a project's
workflows and print layouts (read with `project_get_workflows` and `project_get_layouts`). `core_find` finds all of
these by name, folder or owner in every space the user can open, shared folders included, through core's
`GET /content/search`, plus matching templates; a search of names alone missed what colleagues share with a team or
the organization. A question for data about a topic or place searches the datasets the user's organization already
has and the catalog in the same step, and the answer shows the organization's first: a planner first wants to know
"we have this already". `core_find` matches names, so a synonym the dataset is not named by misses it. Both tools take only
references; the server reads each one in core or the catalog with the user's sign-in, so a card never shows a name
the model made up or an item the user cannot open. Which buttons a card has is decided by the web app
(`apps/web/lib/assistant/itemActions.ts`), from the item's kind and the page, never by the model: a model reads text
other people wrote, and a button it chose could act on an instruction hidden in that text. Each card has at most one
button: Open a project, or a workflow or layout in its project's Workflows or Layouts view, Zoom to a layer of the open project (anything already in it has no preview, the real map is
beside the dock), or Add to an editable open project, which adds on the click with an Undo notice; the model can
never add anything itself. The thumbnail, owner and last change are read by the web app when the card is shown, with
the user's session, not taken from the tool result: thumbnail links expire, and names of colleagues need not go to the
model provider. For the same reason `core_find` gives an owner's name only where the search matched the owner (the
user typed it) and says "you" for the user's own items. A search result row carries one line of description,
type, publisher, years and a rounded bbox, and only the first page brings facet counts (each facet's most
frequent values), because every later model call of the answer resends them; `catalog_get_record` and
`catalog_describe` have the rest.

Prompt caching: every model call of an answer resends the instructions, tool definitions and the conversation so
far. OpenAI, Azure OpenAI, DeepSeek and Mistral cache that prefix by themselves; Claude (direct, Bedrock, Vertex) and
models behind OpenRouter that need it get explicit cache markers (`llm/providers.py`). The page note (language,
page, filters) travels in each user message (`prompt.with_note`), not in the instructions: it changes when the user
moves or filters, and anything that changed ahead of the conversation would make every call read it again. Cached tokens are recorded per run and shown in the
answer details.

Long conversations: because every call resends the conversation, earlier answers' search results and reasoning soon
made up most of each call, and an answer ran into `ASSISTANT_RUN_MAX_TOKENS` after a few searches. So before each call
earlier answers' long tool results go to the model as their counts and their reasoning is left out
(`assistant/history.py`); what the answers said and the cards they showed stay, and the stored history keeps
everything. And shortly before either run limit, the model's next call gets no tools and is told to answer with what
it found (`assistant/budget.py`), so a long search ends in an answer, not only in the limit error.

Behind a connection pooler in transaction mode, set `POSTGRES_TRANSACTION_POOLER`: the pool then prepares no
statements on the server. The assistant holds no session state in Postgres (its locks are per transaction, its
streams go through Redis), so nothing else changes.

Tests need the local Postgres and Redis from the repo's `compose.yaml`: `uv run pytest apps/assistant/tests`.

Evals (by hand, never in CI): see [evals/README.md](evals/README.md).
