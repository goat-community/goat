---
name: build-a-workflow
description: Build a new workflow, a chain of analysis steps in the project's Workflows mode, from what the user describes. For example "build a workflow that finds the areas within 15 minutes on foot of the schools and counts the residents there", a 15-minute city check, a heatmap of access, joining attributes from one layer to another, or counting things near places.
---

# Build a workflow

You build one new workflow in the open project and hand it to the user. You never
start it (the user clicks Run in Workflows mode), and you never change or delete a
workflow that exists. On a page without the workflow tools (the catalog, home,
layouts, dashboards), tell the user to open the project's Map or Workflows page to
build it there.

## Steps

1. **Understand the goal.** What is reached from where, how (walking, bicycle,
   pedelec, car, public transport), how far (minutes or meters), in which place, and
   what the result should show. Ask, as your instructions say, only when the goal
   itself is unclear.
2. **Look for a template.** Call workflow_find_templates once, with the analysis in
   a few words. German and English words in one query are fine: it searches the
   whole query, then up to four of its words of three or more characters on their
   own. When it finds fewer than twenty, `other_templates` lists the other
   workflow templates the user can use as well, up to twenty in all. When no
   template holds those words, it lists the workflow templates the user can use
   instead, up to twenty. Its `note` says what the lists hold: their names and
   descriptions are often in another language than the query, and a hit can be
   weak, so judge from all of them whether one fits. A second call in the same
   answer returns the first call's result, so do not search again. When one
   fits, use it: templates are tested.
   Only workflow templates can be used. Find a project layer for each of its
   inputs with needs_binding as in steps 3 and 4, then call
   workflow_create_from_template with
   `bindings`: each input's `key`, as `inputs` of workflow_find_templates gives it,
   and the layer_project_id. A binding takes no filter: when the only layer with
   the data an input needs covers far more than the place (its `extent` or
   `feature_count`), build a draft with `filter.area` instead of using the
   template. An input with needs_binding that you leave
   unbound stays open for the user and comes back in `open_issues`. Then answer
   (step 7).
3. **Find the data.** project_get_layers lists the project's layers. For a
   dataset no project layer holds, search the catalog for it once: find the place
   with catalog_find_region, then one catalog_search with its nuts and the topic's
   German and English words in q, separated by commas (`toilette,wc,toilet`).
   That search decides: do not search for that dataset again with other words.
   For each dataset the workflow needs:
   - exactly one layer fits: use it;
   - several fit, or none fits but the search found fitting catalog datasets: it
     is unclear;
   - nothing fits anywhere: leave the step open (layer null), labelled for what is
     missing. The user chooses its layer in the editor, so it needs no card.

   Ask about all unclear datasets in one ask_user card, one question per dataset,
   as soon as the candidates are clear. Do not read each candidate's record with
   catalog_get_record before asking: read one only for the dataset you will use,
   once the user picked it, or when the fields decide which candidate fits. The
   card's options, at most four: the fitting project layers (value: the
   layer_project_id as text), fitting catalog datasets (value: the catalog id;
   description: "Adds it to the project"), and "Leave it open" (no value).
   Recommend the best fit. Then end your answer.
4. **After the answer.** Add each catalog dataset the user picked with
   project_add_catalog_layer and its catalog id, and use the layer_project_ids it
   returns (a bundle adds several layers). A dataset the user only named in their
   text, or wrote into the card's free-text field, is not picked: ask with the
   card. "Leave it open" means layer null. A new layer's data is copied in the
   background; until then the check does not judge its fields, and
   project_get_fields may not read them either: take them from the columns
   catalog_get_record lists for that dataset, for a bundle the `columns` of the
   member you use. It lists at most 60 columns of a layer. When the field you need
   is not listed and the list may be cut (`columns_truncated` on a member, or 60
   columns listed), leave that dataset step open, labelled with the dataset's
   name, so the user chooses the layer once its copy is ready. When the list is
   complete, the dataset has no such field: tell the user, or offer another
   dataset.
5. **Pick the tools.** workflow_tools lists the tools and their layer inputs. Read
   the settings of the ones you use with one workflow_describe_tool call. Use only
   the tools, inputs and settings these list. A step they do not list, such as a
   custom SQL step, does not go into your draft; the user can add it in the editor
   later. recipes.md has the common chains: load it with skills_load (name
   build-a-workflow, file recipes.md).
6. **Write, check, fix.** Write the draft, check it with workflow_check_draft, fix
   every issue you can (Reading issues) and check again, at most three times. Then
   create it with workflow_create. The same draft created again returns the first
   result; a changed draft would be a second workflow.
7. **Answer** in a few sentences: what the workflow does, each step left open and
   what the user chooses there (the open issues), what the notes say (an area
   stored as a box, layers a template added), and that the user starts it with Run.
   The workflow card opens it.

## The draft

```json
{
  "name": "Schools: residents within 15 minutes on foot",
  "steps": [
    {"id": "schools", "kind": "dataset", "label": "Schools", "layer": 12,
     "filter": {"area": "DE212", "where": [{"field": "schulart", "op": "=", "value": "Grundschule"}]}},
    {"id": "residents", "kind": "dataset", "layer": 13},
    {"id": "walk", "kind": "tool", "tool": "catchment_area_v2", "label": "15 minutes on foot",
     "settings": {"routing_mode": "walking", "cost_type": "time", "max_cost": 15, "steps": 1}},
    {"id": "count", "kind": "tool", "tool": "aggregate_polygon", "label": "Residents",
     "settings": {"area_type": "polygon", "weighted_by_intersecting_area": true,
                  "column_statistics": [{"operation": "sum", "field": "einwohner"}]}},
    {"id": "save", "kind": "export", "name": "Residents within 15 minutes of schools"}
  ],
  "connections": [
    {"from": "schools", "to": "walk", "input": "starting_points"},
    {"from": "walk", "to": "count", "input": "area_layer_id"},
    {"from": "residents", "to": "count", "input": "source_layer_id"},
    {"from": "count", "to": "save"}
  ],
  "variables": []
}
```

- Step kinds: dataset, tool, export. Step ids: letters, digits, `-` and `_`, unique.
- dataset: `layer` is a layer_project_id from project_get_layers, or null for a step
  left open; an open step needs a `label` naming what is missing and takes no
  filter. `filter.area` is a nuts_id from catalog_find_region and keeps the
  features inside that region: use it when a dataset covers more than the place
  asked about, project layers included. project_get_layers shows a layer's
  `extent` (west, south, east, north) and its `feature_count` when known: a
  layer whose extent or feature count is far larger than the place gets
  `filter.area`. `filter.where` keeps the features matching every condition,
  each `{field, op, value}` with op one of `=`, `!=`, `<`, `<=`, `>`, `>=`, `in`
  (a list) or `contains` (text), on fields from project_get_fields, which you
  read only for the layers the workflow uses. A layer's own filter on the map is
  not part of the workflow: restate it in `where` when it matters.
- tool: `tool` is an id from workflow_tools; `settings` by name, as
  workflow_describe_tool lists them; leave out settings whose default fits. A
  layer reaches a tool only through a connection: never name one of the tool's
  layer inputs in `settings`; a draft that does is refused.
- export: `name` is the name the result is saved as. Every result the user wants
  to keep ends in an export.
- connections: `from`, `to`, and `input`, the tool's layer input (layer_inputs); no
  input into an export; one connection per input.
- The workflow's `name`, the step labels and the export names are in the
  language of the user's message, as your answer is, also when the project's
  layers are named in another language; the names of layers stay as they are.
- A setting with `visible_when` counts only when its condition holds: set the
  settings it depends on. Names starting with `_` in a condition are facts the
  editor knows, such as that the project has a street network. A setting shown
  only with `show_advanced = true` needs `show_advanced: true` too.
- `default_hint` is the value a setting takes from other settings when it is left
  out, in the editor and in a run (`5 if routing_mode = "walking", else 15 if
  ...`). When the step relies on a number it gives, set that number (or the
  user's) explicitly, so the step shows it; a field list (`every field of ...`)
  stays left out.
- A field setting (`reads_layer`) takes a field of the layer connected to that
  input: from project_get_fields for a dataset (catalog_get_record for one still
  being copied, step 4), or a field the step before produces. Never guess a field
  name. While that layer is still to be chosen (a step left open, or a step that
  reads from one), leave the field out: the check cannot read the fields of an
  open layer, so a guessed name passes now and fails once the user picks a layer
  with other field names, while a field left out stays open for the user.
- Statistics (`column_statistics`, `field_statistics`): set every item's
  `operation`, which never depends on the layer; an empty `column_statistics`
  stops workflow_create. Its `field` follows the rule above, for example
  `[{"operation": "sum"}]` while the layer is open; `count` needs no field.
- Heatmaps take up to three opportunity layers on `opportunity_layer_1_id`,
  `opportunity_layer_2_id` and `opportunity_layer_3_id`; the settings of each
  (`per_opportunity`) are written as `opportunity_<N>_<name>`, for example
  `opportunity_1_max_cost`.
- Never invent a tool, an input, a setting, a value or a layer.

## Reading issues

workflow_check_draft answers with the `issues`, how many of them stop
workflow_create (`blocking`) and how many the user resolves by choosing the layers
of the steps left open (`open`). workflow_create is refused while one blocks. Each
issue names its steps by your ids (`steps`), and a one-step issue's message starts
with the step's name.

- `layer_not_chosen`: a dataset step without a layer. Fine when you left it open on
  purpose; otherwise choose its layer.
- `input_not_connected`, `opportunity_not_connected`: connect a step to that input.
- `connection_to_unknown_input`: use an input from layer_inputs.
- `setting_required`: fill it from the user's request, or ask.
- `setting_invalid`: the value does not fit; read the setting again with
  workflow_describe_tool. On a step that reads from a step left open it can be a
  field left out on purpose, which stays open.
- `field_not_in_layer`, `filter_field_not_in_layer`: use a field the layer has
  (project_get_fields).
- `field_maybe_missing`: a warning; the step before may not produce that field:
  compare with what that step outputs.
- `too_many_destinations`: the heatmap's opportunity layers without a filter have
  more features than it takes. Give their dataset steps `filter.area` for the
  place asked about, or a `where`, and check again. When an If step may skip the
  heatmap, it is a warning and does not stop workflow_create.
- `export_name_missing`: give the export a name.
- `loop`: a step reads from itself through others; remove a connection.
- `layer_not_readable`: the user cannot read that layer; choose another or leave
  the step open.
- `step_not_connected`: a warning; connect the step or leave it out.
- An error instead of a result (a value the check refuses, a tool workflow_tools
  does not list, a layer input in `settings`, a layer the user cannot read or that
  is not in the project) comes again for the same draft: change the draft.
- A check that could not run says so (`checked` false). The same draft stays
  unchecked in this answer, so do not check it again: go on with workflow_create,
  which checks again and refuses while no check can run. That refusal may be tried
  once more.
