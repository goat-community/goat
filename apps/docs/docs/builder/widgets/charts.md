---
description: "Chart layer data with the Categories, Histogram and Pie chart widgets: pick a statistic, field and grouping, style the colors and set the click response."
sidebar_position: 3
---

# Charts

**Display your data in a visual format using different types of charts**: **Categories**, **Histogram**, and **Pie chart**. 

## Categories

The categories widget allows you to visualize the distribution of a categorical field from a selected layer by computing statistical analyses and generating **groups by the selected field.**

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Drag and drop the <code>Categories</code> widget on a panel and <b>select your </b><code>layer</code>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Info</code>, add a <code>Title</code> and optional <code>Description</code> for the widget.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Choose the <code>statistic method</code> <b>you want to apply</b>. It can be <code>Count</code>, <code>Sum</code>, <code>Min</code>, <code>Max</code>, or add your own [`Expression`](../expressions).</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Choose the <code>field</code> <b>onto which the statistics should be applied</b>. <i>Sum, min, and max can only be applied to numeric fields.</i></div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">On <code>Group by field</code>, select the field you want your <b>results to be grouped by</b>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">
  Under <code>Style</code>, configure the chart appearance:
  <ul>
    <li><code>Base Color</code>: sets the default bar color</li>
    <li>
      <code>Value-based styling</code>: when enabled, bars are colored based on the selected styling field. Additional options appear:
      <ul>
        <li><code>Styling field</code>: choose <code>Statistics field</code> (color by computed value) or <code>Group-by field</code> (one color per category)</li>
        <li><code>Color scale</code>: classification method (e.g. [Quantile](https://www.plan4better.de/en/glossary/quantile-classification)); shown when Styling field is set to Statistics field</li>
        <li><code>Palette</code>: color palette for the chart</li>
        <li><code>Order (n/n)</code>: lists all category values. Use <code>Add all</code> / <code>Remove all</code> to include or exclude categories. Drag the ⋮⋮ handle to reorder. Use the ⋮ menu to <code>Rename</code> or <code>Remove</code> individual items.</li>
      </ul>
    </li>
    <li><code>Selection Color</code>: color used to highlight a selected bar; only visible when <code>Selection Response</code> is set to <code>Highlight</code></li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">
  Under <code>Options</code>:
  <ul>
    <li><code>Selection Response</code>: choose <code>Filter</code> to filter all connected widgets when a bar is clicked, or <code>Highlight</code> to highlight the selected bar without filtering</li>
    <li><code>Filter viewport</code>: makes only the data within the current map view visible</li>
    <li><code>Number format</code>: set the number format from the dropdown list</li>
  </ul>
  </div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_categories.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Histogram

The histogram widget allows you to visualize the **distribution of a numeric field from a selected layer by `count`**.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Drag and drop the <code>Histogram</code> widget on a panel and <b>select your <code>layer</code></b>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Info</code>, add a <code>Title</code> and optional <code>Description</code> for the widget.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Choose the <code>numeric field</code> which you <b>want to visualize</b>. The statistical method applied will be <code>count</code>.  </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Under <code>Style</code>, configure the chart appearance:
  <ul>
    <li><code>Base Color</code>: sets the default bar color</li>
    <li><code>Hover Color</code>: color shown when hovering over a bar</li>
    <li><code>Number of Bins</code>: number of histogram buckets (1–20, default 10)</li>
    <li><code>X-axis ticks</code>: add custom tick values for the X-axis (enter with Enter or comma)</li>
    <li><code>Field Display Name</code>: optional custom label for the field shown in the chart</li>
    <li><code>Selection Color</code>: color for the selected portion; only visible when <code>Selection Response</code> is set to <code>Highlight</code></li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">
  Under <code>Options</code>:
  <ul>
    <li><code>Selection Response</code>: choose <code>Filter</code> to filter all connected widgets when a bar is clicked, or <code>Highlight</code> to highlight the selected portion without filtering</li>
    <li><code>Filter viewport</code>: makes only the data within the current map view visible</li>
    <li><code>Number format</code>: set the number format from the dropdown list</li>
  </ul>
  </div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_histogram.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Pie chart

Pie chart widget allows you to **visualize the distribution of a field** from a selected layer.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Drag and drop the <code>Pie chart</code> widget on a panel and <b>select your </b><code>layer</code>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Info</code>, add a <code>Title</code> and optional <code>Description</code> for the widget.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Choose the <code>statistic method</code> <b>you want to apply</b>. It can be <code>Count</code>, <code>Sum</code>, <code>Min</code>, <code>Max</code>, or add your own [`Expression`](../expressions).</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Choose the <code>field</code> onto which the statistics should be applied. <i>Sum, min, and max can only be applied to numeric fields.</i></div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Select the <code>field</code> you want your results to be <code>grouped by</code>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">
  Under <code>Style</code>, configure the chart appearance:
  <ul>
    <li><code>Chart type</code>: choose <code>Donut</code>, <code>Pie</code>, or <code>Half donut</code></li>
    <li><code>Label size</code>: choose <code>S</code>, <code>M</code>, or <code>L</code></li>
    <li><code>Layout</code>: choose <code>Center active</code> (shows the active slice's percentage in the center), <code>All labels outside</code>, or <code>Legend</code></li>
    <li><code>Palette</code> and <code>Order (n/n)</code>: set the color palette and manage which categories are shown. Use <code>Add all</code> / <code>Remove all</code> to include or exclude items. Drag to reorder. Use the ⋮ menu to <code>Rename</code> or <code>Remove</code> individual items.</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">
  Under <code>Options</code>:
  <ul>
    <li><code>Filter viewport</code>: shows only data within the current map view</li>
  </ul>
  </div>
</div>



::::info
Results will be visualized in **percentage**.
::::


<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_pie_chart.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

::::tip
Where **statistical methods can be applied**, *count, sum, min, max and [expression](../expressions)* are the available options. Check out our **[Expressions documentation](../expressions)** for more information.
::::