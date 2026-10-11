---
description: "Browse project, workflow and layout templates on the Home page, filter them by kind and source, preview one and create a new project from it with Use template, and choose whether a template ships its datasets or gives every user their own copy."
sidebar_position: 4
---

# Start from a template

Templates let you **begin with something already set up** instead of a blank canvas. GOAT offers three kinds:

- **Project templates**: open a prepared project with styled layers, finished analyses, and a dashboard. A good starting point when you want a complete example to explore or adapt.
- **Workflow templates**: a ready-made analysis workflow where only your own data is missing. You supply the input layers and run it.
- **Layout templates**: print-ready page layouts, with the page size given in millimetres.

This page focuses on **project templates**. For the other two, see [Save a workflow as a template](../workflows/workflow_interface#3-how-to-use-the-workflow-interface) and the Layouts page.

## Browsing templates

On the **Home** page, the `Start from a template` row shows the available templates. You can:

- **Filter by kind**: `All templates`, `Project`, `Workflow`, or `Layout`.
- **Filter by source**: who the template came from (`Everyone`, `GOAT`, `Mine`, `Team`, or `Organization`).
- Click `All templates` to open the full template browser, where you can **search** templates and **preview** one before using it.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/getting_started/start_from_template.webp').default} alt="Start from a template row on the Home page" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

Templates from GOAT are also available under the `Templates` tab of the [Catalog](../workspace/catalog).

## Using a project template

<div class="step">
  <div class="step-number">1</div>
  <div class="content">On the <code>Home</code> page, find a project template in the <code>Start from a template</code> row, or open <code>All templates</code> and filter by <code>Project</code>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Select a template to <strong>preview</strong> what it contains.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Click <code>Use template</code>. GOAT creates a new project from the template, with its layers, analyses and dashboard already in place, and opens it.</div>
</div>

:::info
A project template opens as a **new project** you own. You can change it freely without affecting the template.
:::

## Datasets in a template

When you save a project as a template (`Save project as template…` in the **Project Menu**) or a workflow as a template, the `Inputs` table lists every dataset it uses. For each one you decide how the people who use the template get it:

- `Ship (read-only)`: everyone sees **your dataset** in their project. They can look at it and analyse it, but not change it, unless you also share it with them as editor. This is the default.
- `Copy for every user (with content)`: everyone who uses the template gets **their own copy** of the dataset, with all its features, columns, styling, dropdown fields and description. They can edit their copy freely.
- `Empty copy for every user`: like a copy, but **without features**: the same columns, geometry type and styling, ready for each user to enter their own data, for example planned projects in a training.

A raster dataset, or one read from an external service, has no features to copy, so it can only be shipped. In a workflow template you can also switch a dataset off so that the template asks for a layer when it is used.

When someone uses the template, GOAT first creates the project or workflow with your dataset and then makes their copies in the background; you can follow them under [Job status](../workspace/workspace_interface.md#job-status). Until a copy is ready, the dataset is shown read-only. Once it is ready, it takes the place of your dataset everywhere in their project: on the map, in the dashboard and in workflows.

:::info
A copy is made from your dataset **as it is when the template is used**. Changes you make to your dataset afterwards do not reach copies that already exist, and changes others make to their copy never reach your dataset. Everyone who may use the template must be able to read the datasets it ships or copies with content: sharing the template shares them as viewer. An empty copy only takes the columns, geometry type and styling, so your dataset itself stays private: it is not shared and never becomes public.
:::

