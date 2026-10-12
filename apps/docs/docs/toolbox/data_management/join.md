---
description: "Join attributes from a Join Layer to a Target Layer by matching field values, a spatial relationship or both, with inner or left join and optional statistics."
sidebar_position: 1
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Join Features

This tool allows you to **combine data from two layers based on attribute matching or spatial relationships**. The result is a new layer containing the Target Layer's geometry and attributes, enriched with attributes from the Join Layer.

## 1. Explanation

Joining is the process of attaching fields from one layer (Join Layer) to another layer (Target Layer).

**GOAT supports three join methods:**

- **Attribute**: match features based on a common field (e.g., matching a zip code in both layers).
- **Spatial**: match features based on their geometric relationship (e.g., features that intersect).
- **Spatial and Attribute**: requires both a spatial overlap and a matching attribute.

<Tabs>
<TabItem value="attribute" label="Attribute Join" default className="tabItemBox">

An Attribute Join links two layers by comparing values in a shared field. Every feature in the Target Layer is matched against features in the Join Layer where the field values are equal.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/toolbox/data_management/join/attribute_join_basic.png').default} alt="Basic Attribute Join" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

### Join Type

The `Join Type` controls which features appear in the output:

- **Inner Join**: only features with a match in both layers are kept. Features without a match are dropped.
- **Left Join**: all features from the Target Layer are kept. Features without a match receive `NULL` for the joined fields.

### One-to-One

When each target feature matches at most one feature in the Join Layer, the result has the same number of rows as the Target Layer.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/toolbox/data_management/join/attribute_join_one_to_one.webp').default} alt="One-to-One Join: Inner Join vs Left Join" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

### One-to-Many

When one target feature matches multiple features in the Join Layer, the result contains one row per match: the target geometry is repeated for each matching record.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/toolbox/data_management/join/attribute_join_one_to_many.webp').default} alt="One-to-Many Join: Inner Join vs Left Join" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

</TabItem>

<TabItem value="spatial" label="Spatial Join" className="tabItemBox">

A Spatial Join links features based on their geometric relationship, so no shared field is needed. Each feature in the Target Layer is matched to features in the Join Layer that satisfy the selected spatial relationship.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: "32px", marginBottom: "32px" }}>
  <img src={require('/img/toolbox/data_management/join/spatial_relationships.webp').default} alt="Spatial Relationship Types" style={{ maxHeight: "auto", maxWidth: "70%", objectFit: "cover"}}/>
</div>

**Available spatial relationships:**

| Relationship | Description |
|---|---|
| `Intersects` | Target and join features share any geometry (point, line, or area). |
| `Overlaps` | Features partially overlap but neither is fully inside the other. |
| `Completely Contains` | Target feature fully contains the join feature. |
| `Covers` | Target feature fully contains the join feature. |
| `Disjoint` | Features have no spatial relationship: they do not touch or overlap. |
| `Touches` | Features share a boundary but do not overlap. |
| `Within Distance` | Features are within a specified distance of each other. |
| `Identical To` | Features have exactly the same geometry. |
| `Completely Within` | Target feature is fully inside the join feature. |
| `Covered By` | Target feature is covered by the join feature. |

</TabItem>

<TabItem value="spatial_attribute" label="Spatial and Attribute Join" className="tabItemBox">

This method requires **both** a spatial relationship and a matching attribute value to be satisfied. A feature is only joined if it meets both conditions simultaneously. Use this when location alone is not enough, for example when matching buildings that are within a district **and** share the same land-use classification.

In this example, population data is joined to Berlin districts using both conditions. Matching on the `namgem` attribute alone could incorrectly assign population values from a city like Potsdam if the name matches. Adding a spatial condition (`Intersects`) ensures only points that lie inside the correct district and share the same `namgem` value are joined.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/toolbox/data_management/join/spatial_attribute_join.webp').default} alt="Spatial and Attribute Join Example" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

</TabItem>
</Tabs>

## 2. Example use cases

### Attribute Join
- Add population data to district areas (matching on district ID).
- Combine survey results with census boundaries (matching on tract ID).

### Spatial Join
- Count the number of schools within each city district.
- Find which municipality each point of interest belongs to.
- Sum the total length of roads within a park boundary.

### Spatial and Attribute Join
- Match buildings within a flood zone that also share the same building type.

## 3. How to use the tool?

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click on <code>Toolbox</code> <img src={require('/img/icons/toolbox.png').default} alt="Toolbox" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. Under <code>Data Management</code>, click on <code>Join Features</code>.</div>
</div>

### Select Layers

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Select your <code>Target Layer</code>: the main layer whose geometry you want to keep.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Select your <code>Join Layer</code>: the layer containing the fields you want to add.</div>
</div>

### Match Method

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Under <code>Match Method</code>, enable <code>Attribute Match</code>, <code>Spatial Match</code>, or both.</div>
</div>

<Tabs>
<TabItem value="attribute" label="Attribute" default className="tabItemBox">

Under <code>Attribute Relationship</code>, click <code>+ Add Match Field</code>, then select the <code>Target Field</code> and the <code>Join Field</code>: the shared field used to match features between the two layers.

</TabItem>

<TabItem value="spatial" label="Spatial" className="tabItemBox">

Under <code>Spatial Match</code>, select the <code>Spatial Relationship</code>. If selecting <code>Within Distance</code>, specify the distance and unit.

</TabItem>

<TabItem value="spatial_attribute" label="Spatial and Attribute" className="tabItemBox">

Configure both <code>Spatial Match</code> (select the spatial relationship) and <code>Attribute Relationship</code> (click <code>+ Add Match Field</code>, then select the matching fields). Both conditions must be met for a feature to be joined.

</TabItem>
</Tabs>

### Join Options

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Select the <code>Join Type</code>: <code>Inner Join</code> (keep only matched features) or <code>Left Join</code> (keep all target features, unmatched get NULL).</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Select the <code>Match Handling</code>: <code>One to One</code> or <code>One to Many</code>.</div>
</div>


<div class="step">
  <div class="step-number">7</div>
  <div class="content">
  Optionally, enable <code>Add Join Fields</code> to select which fields from the Join Layer to include in the output, and/or enable <code>Calculate Statistics</code> to compute aggregated values when multiple Join Layer records match a single Target Layer feature. When <code>Calculate Statistics</code> is enabled, configure the statistic:
  <ul>
    <li><code>Select operation</code>: <code>Count</code>, <code>Sum</code>, <code>Min</code>, <code>Max</code>, <code>Mean</code>, or <code>Standard Deviation</code>.</li>
    <li><code>Select field</code>: choose the numeric field from the Join Layer to aggregate (hidden when operation is <code>Count</code>).</li>
    <li><code>Result column name</code> (optional): name for the output column. Leave empty to use the default name (e.g. <code>count</code> or <code>fieldname_operation</code>).</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Click <code>Run</code> to execute the join. The result layer will be added to the map.</div>
</div>
