---
description: "Combine two or more layers into one output layer: same-named fields are merged, unique fields kept, with options for a source column and multi-part geometries."
sidebar_position: 2
---

# Merge

This tool allows you to **combine two or more layers into a single output layer**. Features from all input layers are stacked into one dataset. By default, fields with the same name are mapped together, while fields unique to individual inputs are retained in the output.

## 1. Explanation

Merging stacks features from multiple layers into one layer. Unlike a join, no matching is required: all features from all input layers are simply combined. This is useful when you have the same type of data split across multiple layers and want to work with it as a single dataset.

**Key behaviour:**
- Features from all input layers are included in the output.
- Fields with the same name across layers are merged into one column.
- Fields that only exist in one input layer are retained with `NULL` for features from other layers.

## 2. Example use cases

- Combine building footprints from multiple municipalities into one layer.
- Stack survey results collected in separate files into a single dataset.
- Merge road network layers from different data sources.

## 3. How to use the tool

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click on <code>Toolbox</code> <img src={require('/img/icons/toolbox.png').default} alt="Toolbox" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. Under <code>Data Management</code>, click on <code>Merge</code>.</div>
</div>

### Select Input Layers

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Input</code>, select your first <code>Input Layer</code> from the dropdown.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Click <code>+ Add Input Path</code> to add one or more additional layers to merge.</div>
</div>

### Merge Options

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Expand <code>Merge Options</code> and configure the following toggles:
  <ul>
    <li><code>Add Source Column</code>: adds a column to the output indicating which input layer each feature came from.</li>
    <li><code>Validate Geometry Types</code>: checks that all input layers share the same geometry type before merging.</li>
    <li><code>Promote To Multi</code>: converts single-part geometries to multi-part (e.g. Polygon → MultiPolygon) to ensure compatibility across inputs.</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Click <code>Run</code> to execute the merge. The result layer will be added to the map.</div>
</div>
