---
description: "Add Filter, Table, Numbers and Rich Text widgets to a dashboard to filter a layer by field, list or group its records, compute statistics and show live values."
sidebar_position: 2
---

# Data

**This section contains widgets that help you interact with and analyze your data**: **Filter**, **Table**, **Numbers**, and **Rich Text**.

## Filter

This widget is an interactive element, which **allows the user to filter the data on the configured layer based on the selected attribute field**. Viewers can use this as a **cropping tool on the maps**.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Drag and drop the <code>Filter</code> widget on a panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Select your <code>layer</code> and choose the <code>field</code> <b>you want to filter by</b>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Optionally add a <code>Placeholder</code> text which appears before the filtering is applied.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Enable or disable <code>Cross filter</code> to make this <b>widget interact with other data widgets</b>. When enabled, filtering data in one widget will automatically update all other connected widgets on your dashboard.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Enable or disable the option <code>Zoom to selection</code>, which will <b>automatically pan the map view to the filtered data</b>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Enable <code>Filter by map click</code> to let viewers set the filter by clicking a feature directly on the map. When a feature is clicked, its value for the configured field is applied as the filter. If <code>Allow multiple selection</code> is enabled, clicking a feature toggles it in or out of the active selection. Not available for the <code>Range</code> layout.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_filter.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Table

The Table widget **displays data from a layer as a scrollable table**. You can show raw records, aggregate grouped data, or write a custom SQL query.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Drag and drop the <code>Table</code> widget on a panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Info</code>, add a <code>Title</code> and optional <code>Description</code>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Under <code>Data</code>, select your <code>layer</code>.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Choose the <code>Data source</code>:
  <ul>
    <li><code>Dashboard setup</code>: configure columns and grouping visually</li>
    <li><code>SQL query</code>: write a custom SQL query against the layer</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">
  In <b>Dashboard setup</b> mode, choose the <code>Mode</code>:
  <ul>
    <li><code>Records</code>: shows all rows. Use <code>Visible fields</code> to select which columns to display.</li>
    <li><code>Grouped</code>: aggregates data by field. Define one or more <code>Value columns</code> (each with a statistic: Count, Sum, Mean, Median, Min, Max), a <code>Group-by field</code>, and optionally a <code>Secondary group-by field</code>. Click <code>+ Add column</code> to add more value columns.</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">In <b>SQL query</b> mode, click <code>Write SQL Query</code> (or <code>Edit SQL Query</code>) to open the SQL editor.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">In Dashboard setup mode, use <code>Sort by</code> and <code>Sort ascending</code> to set the default row order. Viewers can also sort interactively by clicking any column header: the first click sorts ascending, a second click sorts descending, and a third click removes the sort. An arrow icon in the header shows the active sort direction.</div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">
  Under <code>Layout</code>, configure the table appearance:
  <ul>
    <li><code>Sticky header</code>: keeps the column header visible while scrolling</li>
    <li><code>Show totals</code>: shows a totals row at the bottom</li>
    <li><code>Display mode</code> (<code>Flat</code> / <code>Collapsible</code>): available when a secondary group-by field is set or in SQL mode. In <code>Collapsible</code> mode, you can also enable <code>Start expanded</code> and <code>Show subtotals</code>.</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Under <code>Style</code>, set the <code>Header Color</code>.</div>
</div>

<div class="step">
  <div class="step-number">10</div>
  <div class="content">
  Under <code>Options</code>:
  <ul>
    <li><code>Filter viewport</code>: only includes rows within the current map view</li>
    <li><code>Rows shown</code>: number of rows loaded initially and per scroll chunk (1–20)</li>
  </ul>
  </div>
</div>

## Numbers

Choose from different statistic methods to be computed on a layer.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Drag and drop the <code>Numbers</code> widget on a panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Select your <code>layer</code>. </div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Choose the <code>statistic method</code> you want to apply. It can be <code>Count</code>, <code>Sum</code>, <code>Min</code>, <code>Max</code>, or add your own [<code>Expression</code>](../expressions). </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Choose the <code>field</code> <b>onto which the statistics should be applied</b>. <i>Sum, min, and max can only be applied to numeric fields.</i></div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Enable or disable <code>Filter viewport</code>, which <b>makes only the data within the current map view visible</b>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Set the <code>Number format</code> from the dropdown list. The default number format is dynamic based on the language of the interface.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_number.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Rich Text

The Rich Text widget **displays formatted text with optional dynamic values** from layer statistics. Use it to add context, descriptions, or live-updating numbers to your dashboard.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Drag and drop the <code>Rich Text</code> widget on a panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Type and format your text directly in the widget editor.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Under <code>Variables</code>, click <code>Add Variable</code> to define a named variable (e.g. <code>var_1</code>) linked to a layer field and statistic operation. Use <code>Insert Variable</code> in the editor toolbar to embed the variable in your text.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Under <code>Options</code>:
  <ul>
    <li><code>Filter viewport</code>: variable values update to reflect only data within the current map view</li>
    <li><code>Hide when no filter</code>: hides the widget when no filter is active. When disabled, set a <code>Fallback text</code> to show instead.</li>
  </ul>
  </div>
</div>