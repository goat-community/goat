---
description: "Filter a layer or table by attribute with logical expressions or by map extent, combine expressions with AND or OR, and save the result as a new layer."
sidebar_position: 5
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


# Filter

**Filter limits data visibility on your map** using logical expressions (e.g., supermarkets with specific names) or spatial expressions (e.g., points within a bounding box). **The filter allows you to focus on relevant information without altering original data.** It works with **point, line and polygon layers** and with **tables** containing `number`, `string`, `datetime`, and `boolean` data types. 

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/map/filter/filter_clicking.mp4').default} alt="Filter tool in GOAT" style={{ maxHeight: "auto", maxWidth: "80%", objectFit: "cover"}}/>
</div> 

## How to use the filter

### Single Expression Filtering

<div class="step">
  <div class="step-number">1</div>
  <div class="content">In the <code>Layers</code> panel, click your layer. Its settings panel opens on the right with the tabs <code>Style</code>, <code>Filter</code> and <code>Metadata</code>. Select the <code>Filter</code> tab. For a table, the panel has only the tabs <code>Filter</code> and <code>Metadata</code> and opens on <code>Filter</code>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Click <code>+ Add Expression</code> to <strong>add a new filter expression</strong>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Choose <code>Logical Expression</code> or <code>Spatial Expression</code> to <strong>define your filter type</strong>. For a table, a <code>Logical Expression</code> is added directly.</div>
</div>

<Tabs>
  <TabItem value="Logical expression" label="Logical expression" default className="tabItemBox">

<div class="step">
  <div class="step-number">4</div>
  <div class="content">In <code>Select field</code>, choose the attribute to <strong>filter by</strong>.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">In <code>Select operator</code>, choose the operator. Available options vary by data type (<code>number</code>, <code>string</code>, <code>datetime</code>, and <code>boolean</code>).</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

| Expressions for `number` | Expressions for `string` |
| -------|----|
| Is  | Is |
| Is not  | Is not |
| Includes  | Includes  |
| Excludes  |  Excludes |
| Is blank | Is blank |
| Is not blank | Is not blank |
| Is at least  | Starts with |
| Is less than | Ends with |
| Is at most | Contains the text |
| Is greater than | Does not contain the text |
| Is between | Is empty string |
|  | Is not empty string |

</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

| Expressions for `datetime` | Expressions for `boolean` |
| -------|----|
| Is on | Is true |
| Is not on | Is false |
| Is before | Is blank |
| Is after | Is not blank |
| In the last |  |
| Not in the last |  |
| Is between |  |
| Is not between |  |

</div>

:::tip Hint
For `datetime` fields, choose a date from the **date picker** (`Select date`). **"Is between"** uses two dates (**From** and **To**), and **"In the last"** takes a **Number of days**. For `boolean` fields, the operator already sets the condition, so no value is needed.
:::


:::tip Hint
For the expressions **"Includes"** and **"Excludes"**, multiple values can be selected.
:::

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Set your filter criteria in <code>Select Value</code>, <code>Select values</code> or <code>Enter value</code>, depending on the operator. As soon as the expression is complete, the map updates automatically and the layer shows a filter icon in the <code>Layers</code> panel.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/filter/filter_atlayer.webp').default} alt="Filter Result in GOAT" style={{ maxHeight: "auto", maxWidth: "80%", objectFit: "cover"}}/>
</div> 
</TabItem>

<TabItem value="Spatial expression" label="Spatial expression" default className="tabItemBox">
<div class="step">
  <div class="step-number">4</div>
  <div class="content">In <code>Select intersection method</code>, choose the <strong>spatial boundary</strong>.</div>
</div>

<Tabs>
  <TabItem value="Map extent" label="Map extent" default className="tabItemBox">

With <code>Map Extent</code>, the layer <strong>automatically crops to the current map extent</strong>. To change the filter, zoom in/out and click the refresh icon (<code>Use current map extent</code>).

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <Video src={require('/img/map/filter/Map_extend.mp4').default} alt="Attribute Selection" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>

</div> 
</TabItem>

<TabItem value="Boundary" label="Boundary" default className="tabItemBox">

:::info coming soon

This feature is currently under development. 🧑🏻‍💻

:::
</TabItem>
</Tabs>

</TabItem>
</Tabs>

### Multiple Expressions Filtering

**Combine multiple filters** by repeating steps 2-6 for each expression. As soon as there are two or more expressions, <code>Filter results</code> appears above them. In <code>Filter results</code>, choose **Match all filters** (AND) or **Match at least one filter** (OR) to **control how filters interact**.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/filter/filter-results.webp').default} alt="Logic Operators" style={{ maxHeight: "auto", maxWidth: "30%", objectFit: "cover"}}/>
</div>

### Delete Expressions and Filters

**Remove single expressions**: Click on the <code>More Options</code> <img src={require('/img/icons/3dots-horizontal.png').default} alt="Options" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> menu next to the expression, then click <code>Delete</code> to **remove the expression**.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/filter/filter_delete_clear.webp').default} alt="Delete expression and clear filters" style={{ maxHeight: "auto", maxWidth: "30%", objectFit: "cover"}}/>
</div>

**Remove whole filter**: Click <code>Clear Filter</code> at the bottom of the <code>Filter</code> tab to **remove all filters**.

### Save as new layer

Once the filter is applied, click <code>Save as new layer</code> at the bottom of the <code>Filter</code> tab to **save the filtered result as a new dataset** in your workspace. This allows you to work with the filtered data independently.

