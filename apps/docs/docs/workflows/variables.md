---
description: "Define String or Number workflow variables with default values, insert them into tool parameter fields, and set their values when running from the Map view."
---

# Variables

**Workflow Variables** allow you to define reusable values that can be set at run time without editing the workflow. Use them to make your analysis flexible and shareable: collaborators can run the same workflow with different parameters without touching the workflow structure.

Variables use the syntax `{{@variable_name}}` and can be inserted into most tool parameter fields.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/workflows/variables.webp').default} alt="Workflow Variables" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div>

## Variable Types

| Type | Use for |
|---|---|
| **String** | Text values: names, labels, filter criteria |
| **Number** | Numeric values: distances, thresholds, counts |

## Creating Variables

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click the <code>{"{}"}</code> <strong>Variables</strong> icon in the toolbar at the bottom of the canvas to open the Variables dialog.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Click <strong>Add Variable</strong>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Enter a <strong>Name</strong>. Names must start with a letter or underscore and contain only letters, digits, and underscores, no spaces (e.g. <code>buffer_distance</code>, not <code>buffer distance</code>).</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Select a <strong>Type</strong>: <code>String</code> or <code>Number</code>.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Optionally enter a <strong>Default</strong> value.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Optionally enter a <strong>Label</strong>. The label is what people see instead of the technical name, wherever they pick the variable or set its value (e.g. <code>Maximum grouping distance</code> for <code>max_grouping_distance</code>). Expressions and SQL keep using the name. To add help text, click the speech bubble icon next to the variable, type a <strong>Description</strong> (up to 500 characters) and click beside the box to keep it; <code>Esc</code> discards the change. A filled icon shows that a variable has a description, and hovering over it shows the text.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Click <strong>Done</strong> to save. To delete a variable, click the delete icon next to it.</div>
</div>

## Using Variables in Tool Parameters

Click the <code>{"{}"}</code> icon inside any compatible parameter field and select the variable you want to insert. Once inserted, the field displays the variable reference (e.g. <code>{"{{@variable_name}}"}</code>) highlighted in green, indicating the field is driven by a variable.

A variable with a label is listed by its label, with its reference next to it, and its description appears when you hover over it. A field that holds a labelled variable shows the label below it. When you type <code>{"{{@"}</code> in a field, the suggestions match both names and labels; in the SQL editor they match names and show each label next to its name.

:::tip
Use descriptive names that clearly explain the parameter's purpose: `buffer_distance` instead of `dist`, `poi_type` instead of `type`.
:::

## Running Workflows with Variables from the Map View

Workflows with variables can be run directly from the Map view without opening the workflow editor.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Open the <code>Toolbox</code> and click the <strong>Workflows</strong> tab.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Click on a workflow from the list to open it.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">A <strong>Variables</strong> section appears showing all variables defined in the workflow. Set the values you want to use for this run. Each field is titled with the variable's label (or its name, if it has none), and its description is shown below the field.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Click <strong>Run</strong>. The workflow executes with the values you entered. Click <strong>Reset</strong> to restore the default values.</div>
</div>

:::info
The values you enter here only apply to this run. Next time you open the workflow, the default values are restored.
:::
