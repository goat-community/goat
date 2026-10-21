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
beside the dock), or Add to an editable open project, which adds on the click with an Undo notice; the model adds a
catalog dataset of its own choosing only with `project_add_catalog_layer`, after the user picked it in a card, and a
workflow template it uses brings the datasets the template ships (Write tools and Templates, below). The thumbnail,
owner and last change are read by the web app when the card is shown, with
the user's session, not taken from the tool result: thumbnail links expire, and names of colleagues need not go to the
model provider. For the same reason `core_find` gives an owner's name only where the search matched the owner (the
user typed it) and says "you" for the user's own items. A search result row carries one line of description,
type, publisher, years and a rounded bbox, and only the first page brings facet counts (each facet's most
frequent values), because every later model call of the answer resends them; `catalog_get_record` and
`catalog_describe` have the rest. A search that finds nothing brings a note instead of its empty facet lists: what an
empty result means and when to stop, since a model given only the empty lists searched on with other words until
the answer's budget was gone and could not build the workflow it was asked for. For the same reason, after
`FRUITLESS_SEARCHES` catalog searches in a row of one answer found nothing (`catalog_search` and
`catalog_suggest_terms`, the tools with `ToolSpec.found_nothing`), the answer's next catalog searches are refused
without running (`assistant/tools/toolset.py`); a search that finds something starts the count again, so an answer
can still look for several datasets.

**Asking the user.** `ask_user` shows a card in the dock on every page: up to four questions answered together, two
to four options each, and a free-text field the card adds by itself. It is a general mechanism, not tied to
workflows. The card is a `data-ask` part named by its card id, `ask-` and an id the tool mints (`tools/ask.py`), not
the provider's tool call id, which some providers number per response and so repeat in a later answer; the tool's
stored result carries the card id, by which `asks.AskHistory` finds the card again. After a card the run offers no
more tools, so the answer ends there. The user's answer is the next run's message (`RunMessage.answer`): it is
checked against the stored card before anything is stored (a card is answered once), kept with the user message and
returned as that message's `metadata.answer`, and given to the model with the values the card attached
(`asks.answer_lines`, in a block of its own after the user's text, `prompt.with_note`). The card never carries its
option values, such as a layer or a catalog id, to the web: the card part leaves them out (`asks.card_data`), so do
the stream and the transcript of the `ask_user` call (`asks.public_args`), and the stored rows keep them. An id the
model then passes to another tool is streamed with that call, as any argument is. The card is not on `/mcp`: its
clients cannot show one.

**Write tools.** Next to read tools and proposals there is a third risk class, `write` (`ToolSpec.risk` in
`tools/runtime.py`): tools that create a workflow in the open project or add a catalog dataset to it. They create;
nothing changes or deletes what exists (changing workflows waits for their version history). They belong to the
workflows pack (`tools/workflows.py`), which is offered on the Map and Workflows pages only and never on `/mcp`.
Every write goes into the project of the page: no write tool takes a project id, so text inside a dataset, a template
or a tool description cannot make the assistant write into another project. The user's rights apply, since every call
carries their token: a viewer is told they can view the project but not create workflows or add datasets in it, and
the instructions tell the model not to try again (core answers 401 for missing rights as well as 403). A write called
again with the same arguments anywhere in the conversation returns its first result: each run starts with the
conversation's earlier write results (`toolset.earlier_writes`, from the stored parts, which also keep the calls of
an answer cancelled afterwards), and writes run one at a time, so an identical twin in the same response finds the
first one's result. A retry or a "try again" with the same arguments thus never creates a second workflow (a changed
draft is a new call); only a write that returned counts, so one that failed can be tried again. The audit row of a
write keeps what it created (the `created` column of `assistant.tool_call`, from the result's `created()`); if
reading that fails, it is logged and the call still answers, since what was created exists. A catalog dataset the
model chooses is added only when the user picked it in a card: `asks.user_chose` reads the stored card and answer,
never the model's words, and a typed reply is no pick; the datasets a workflow template ships come with the template
instead (Templates, below). Consent is only as good as the card's labels: the model writes them and the option values
stay hidden, so the user agrees to what a label and its description say; a pick adds one public catalog dataset to
the page's project, where it is visible and can be removed.

**Building a workflow.** The model is shown only the tools of the user's toolbox (`offered` in
`tools/workflow_tools.py`: `GET /processes` for the user, without the tools hidden from the toolbox, such as custom
SQL), and the check and the create refuse a draft naming any other tool: processes describes, checks and runs every
tool it knows, the hidden ones and beta tools for a user outside the beta included. The model writes one draft for
the whole workflow. A pure function turns the draft into the editor's config (`to_config` in `workflows/draft.py`:
ids derived from the draft's and a salt, the editor's handles and dataset filter format, a layout and a stored
viewport, since the editor opens a workflow at its stored view), so the check, the create and the editor read the
same config. Every call converts the draft once with a fresh salt: the create saves the config it has just checked,
and two workflows made from one draft share no node id, which goatlib finds an export's result layer by. The check is
the editor's own (`POST /workflows/check` on processes) plus the assistant's check of filter fields
(`filter_field_issues` in `workflows/issues.py`, which does not judge a layer geoapi lists no fields for yet, such as
a catalog dataset just added); its issues come back in the draft's ids, the message of a one-step issue starting with
the step's name (`draft_issues`). It needs the user's toolbox and the tools' process descriptions, for the steps'
titles, the layer inputs and the field settings: without them a draft is unchecked and `workflow_create` refuses.
Processes' 400 or 422 on a draft goes back to the model as an error to fix; only when processes cannot be reached or
fails is a draft left unchecked.
The model can tell a dataset that covers far more than the place asked about, which then gets an area filter:
`project_get_layers` gives each layer's extent, rounded, and, for a catalog dataset, the feature count its copy
recorded (core keeps no count for other layers, and counting each layer on every call would read whole tables). A
heatmap whose destinations exceed what it takes is processes' `too_many_destinations`, which blocks the create like
any other error, unless an If step may skip the heatmap: then it is a warning, which blocks nothing. A template's
inputs are bound without a filter, so the skill binds them only to layers that fit the place and drafts the workflow
with an area filter otherwise; the check of the template's workflow (Templates, below) catches such a binding only
where it would stop a run.
Only readable layers of the page's project reach processes, as for the project tools: a locked layer is refused
before anything is sent, and a tool step's settings may not name one of its layer inputs, because layers reach tools
only through connections and a layer set as a setting would pass by the step's `layer`, the connections and the
refusal of a locked layer. That rule needs the descriptions too, and a draft without them is never created (`prepare`
and `check` in `tools/workflows.py`). A workflow is created only when every issue that would stop a run is one the
user resolves by choosing the layers of the steps left open, on such a step or a step downstream of it: no layer
chosen, a required field setting whose layer is still to be chosen, or a setting the tool rejects where it reads such
a layer (the input itself, a field setting or a list whose items read it, the settings of an opportunity on that
handle, and the opportunities as a whole while every connected one reads such a layer, since processes then cannot
say which one an error belongs to). A rejection of such a step as a whole, naming no setting, stays open too,
whatever its cause, since the check does not name one. Everything else blocks, a rejected setting that reads no such
layer among them (`split_issues`, fed by `layer_settings`). Nothing starts a run: the user clicks Run.

**Templates.** `workflow_find_templates` searches the whole query and also its longer words (`MAX_SEARCH_WORDS` and
`MIN_SEARCH_WORD_CHARS` in `tools/workflows.py`), because core matches the whole query as one piece of a template's
name or description (`ILIKE`, no categories, no stemming, in the language the author wrote). Template texts are often
German while the user and the model write English, and a user can use only a few workflow templates, so when no search
finds one, the tool lists the workflow templates the user can use instead (`MAX_LISTED_TEMPLATES`, most recently
changed first, with a note saying whether these are all of them) and the model judges the fit from their names and
descriptions. When the searches find fewer than that, the other usable templates come beside the hits
(`other_templates`, up to `MAX_LISTED_TEMPLATES` in all, without repeating a hit), since a word can match a template
that fits worse than one written in the other language; the list is read in the same round trip as the searches, and
when only it fails, the hits come alone. It searches once per answer (`ToolSpec.once_per_answer`): every later call in
the same answer, whatever its words, gets the first call's result with a note instead of asking core, and runs alone,
so a twin in the same response finds that result too. A rephrased query searches the same names and descriptions,
while each call takes one of the answer's look-ups; a repeat still takes one, since the run budget counts every call
let run. Before a write the template is read, and only a workflow template is used (core would put a
layout template into the project's layouts). A binding must name one of the template's input keys: core ignores an
unknown key, which would leave that input open, and the corrected call would make a second workflow. The workflow a
template makes is checked before it exists: core's `POST /template/{id}/use/preview` answers with the config the use
would write with the same bindings, writing nothing, because a template's frozen config is not readable by its viewers
and binding it here would copy core's rules. That config goes through the draft's check and create gate
(`_check_template`, `config_graph`): a step without a layer is open like a draft step left open, so an input left
unbound stays open, and any other error refuses the use with the issues and what to do instead (`_refusal`): bind
another layer or draft with an area filter when the issue is on a bound input's step or downstream of it, such as
`too_many_destinations` for a bound layer that is too large; use another template or a draft otherwise, since no
binding fixes the template's own issues, and also when processes refuses the config itself. An unbound input the
check does not name (processes checks nothing in a workflow without a tool step) is named from the preview's
unresolved inputs. A step that reads an empty copy's dataset is open too, and its `layer_not_readable` is dropped
(`_empty_copy_steps`): core shares no empty copy's dataset, so the user cannot read it until the copy job points the
steps at their copy. Core's preview clears the tool settings that name that dataset by an entry (the use points them
at the copy's new entry), so a tool step it feeds that is still `layer_not_readable` names another layer, and blocks.
Using a template also links the datasets it ships into the project, catalog datasets among them, without a card; the
result's notes list the layers it added by layer_project_id and say when copies of its datasets are still being made.
Template text from other users is clipped before it reaches the model, step names and the check's messages about its
workflow included.

**Skills.** Built-in skills are instructions in the Agent Skills format: a folder per skill under `skills/` with a
`SKILL.md` (front matter with `name` and `description`, then the instructions) and Markdown reference files next to
it. Nothing in a skill is executed. All of them are read at import (`skills/__init__.py`), so a malformed skill stops
the service at startup naming its file; the instructions list each skill in one line after the fixed prompt (in the
cached prefix, `prompt.static_instructions`), and `skills_load` serves only what was read: a file name is looked up
among those files, never opened as a path. A loaded skill stays whole in the conversation's history
(`history.KEPT_TOOLS`), so it is not loaded again each turn. The first skill, `build-a-workflow`, carries GOAT's
common chains in `recipes.md`; its tests (`tests/test_build_a_workflow_skill.py`) check that every assistant tool it
names exists and that its example drafts use only tools, inputs, settings and choices found in process descriptions
captured from processes (`tests/fixtures/process_descriptions.json`).

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
everything. And before either run limit, the model's next call is told to answer with what it found and keeps only
`ask_user` (`assistant/budget.py`), so a long search ends in an answer, or in a card when the user has to choose, not
only in the limit error. `ASSISTANT_RUN_MAX_TOKENS` counts tokens read from the provider's cache at a tenth, roughly
what they cost: every call rereads the cached prefix, and counting it fully stopped answers on cheap rereads. The
budget and the hard limit count the same way. The step that answers offers other tools and instructions than the calls
before it, so the provider reads none of it from its cache, and a card's closing call misses again. So both are sized
at their whole context, read from the run's messages: the newest call's input and output plus the tool results the next
call sends. One more look-up is allowed only while, after it, both still fit with the run's largest step added; the card
only while both fit, and otherwise the step answers in text. Within a step, calls past the run's tool-call limit are
refused as they run, and every call let run counts toward that limit, failed ones too. A call a service failed twice
for (a 429 or 5xx answer, no answer in time, or none: `http.service_failed`) is refused on its next repeat without
asking the service again (`SERVICE_FAILED_TWICE` in `assistant/tools/toolset.py`); the first retry still runs, since a
service can fail for a moment. A 4xx answer does not count: it is the service's verdict on the call. A result that
would leave the answer step too little room is refused (`StepGuard`), which ends the run's look-ups (`answer_step` in
`assistant/tools/toolset.py`). The step's other calls go on, and where the answer step still fits after the run's
first call (which is not checked), the run answers with what it found instead of failing at a limit.

An answer also has to end in text. Pydantic AI asks again after a response without text or a tool call (only
reasoning, or nothing), with the same tools, and a model that gave one often gave the next alike until the run failed
on its output retries ("Exceeded maximum output retries"). It also takes any text that is not empty as the answer, so
an answer could end after its cards with a single space. Such an answer is asked for its text
(`agent.ends_with_text`); only the last retry's answer is taken as it is, since failing the run then would lose what
the user has already seen. And the second response of a run without a tool call or text beyond whitespace ends its
look-ups (`SILENT_RESPONSES` in `assistant/tools/toolset.py`): the next call is the answer step, told why
(`prompt.ANSWER_IN_TEXT`).

Behind a connection pooler in transaction mode, set `POSTGRES_TRANSACTION_POOLER`: the pool then prepares no
statements on the server. The assistant holds no session state in Postgres (its locks are per transaction, its
streams go through Redis), so nothing else changes.

Tests need the local Postgres and Redis from the repo's `compose.yaml`: `uv run pytest apps/assistant/tests`.

Evals (by hand, never in CI; the regression workflows they keep do run in CI): see [evals/README.md](evals/README.md).
