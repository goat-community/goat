---
sidebar_position: 4
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


# Filter

The **Filter** can be used to limit the data that is visible on the map. You can thereby either filter by **logical expression** (e.g. only visualizing supermarkets with a certain name) or by **spatial expression** (e.g. only showing points within a specific bounding box).

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

  <img src={require('/img/map/filter/filter_clicking.gif').default} alt="Filter tool in GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>

</div> 

## 1. Explanation


The **Filter** <img src={require('/img/map/filter/filter_icon.png').default} alt="Filter Icon" style={{ maxHeight: "20px", maxWidth: "20px"}}/> allows users to **display only certain elements** from a larger dataset based on specific criteria. This tool helps to visualize selected elements from a large geospatial dataset and there with allows users to focus on the information that is most relevant to their needs.

Logic and spatial expressions can be added based on the attributes of **point layers** and **polygon layers** with different types of data (`number` and `string`).

:::info

The **filter operation does not alter the original data**. It can be used on any layer to constrain the data used for visualization and analysis, without changing the underlying dataset. If reset, all original data associated with the layer will once again be visible.

:::



## 2. Example use cases
- Show all cities in Germany that have more than 50.000 inhabitants.
- Show all carsharing stations of a certain operator.
- Show the regions that have more than one airport.


## 3. How to use the filter?

### Single Expression Filtering

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Select the layer to which you want to apply the filter. </div>
</div>

<div class="step">
  <div class="step-number">2</div>

  <div class="content">Click on <code>Filter</code> <img src={require('/img/map/filter/filter_icon.png').default} alt="Filter Icon" style={{ maxHeight: "20px", maxWidth: "20px"}}/>. </div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/filter/filter.png').default} alt="Filter tool in GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

<p></p>
<div class="step">
  <div class="step-number">3</div>
  <div class="content">The <code>Active Layer</code> shows the currently selected layer on which the filter will be applied.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Click on <code>+ Add Expression</code>.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Select if you like to filter based on a <b>Logical Expression</b> or a <b>Spatial Expression</b>. 
  </div>
</div>

<Tabs>
  <TabItem value="Logical expression" label="Logical expression" default className="tabItemBox">

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Select the <code>Field</code>, i.e. the attribute which you like to use for the filtering.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Select the concrete <code>Operator</code> that you want to apply. 
  <i> Note: the available options vary based on the data type of the attribute selected in Step 6.</i>
  </div>
</div>

The **Filter Expressions** available for `number` (numerical data) and `string` (text data) are given below:

| Expressions for `number` | Expressions for `string` |
| -------|----|
| is  | is |
| is not  | is not |
| includes  | includes  |
| excludes  |  excludes |
| is at least  | starts with |
| is less than | ends with |
| is at most | contains the text |
| is greater than | doesn't contain the text |
| is between | is empty string |
|  | is not empty string |


:::tip Hint
For the expressions **"includes"** and **"excludes"**, multiple values can be selected.
:::

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Set your filter criteria. The map will automatically update with your filtered data and the filter icon will appear on the filtered layer.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/filter/filter_atlayer.webp').default} alt="Filter Result in GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 
</TabItem>

<TabItem value="Spatial expression" label="Spatial expression" default className="tabItemBox">
<div class="step">
  <div class="step-number">6</div>
  <div class="content">Select the <code>intersection method</code>, i.e. the method used for the spatial boundary.</div>
</div>

<Tabs>
  <TabItem value="Map extent" label="Map extent" default className="tabItemBox">
<div class="step">
  <div class="step-number">7</div>
  <div class="content"> The layer is automatically cropped to the current map extension.<p> To change the filter, zoom in or out of the map, choose the appropriate view, and refresh the map extension with the button.</p></div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/filter/Map_extend.gif').default} alt="Attribute Selection" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>

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

If you wish, you can **combine multiple filters** for multi-expression filtering. To do this, simply repeat steps 4-8 above for each additional expression. In the <code>Logic Operator</code> field, you can choose between the **AND** and **OR** logic combinations.  
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

  <img src={require('/img/map/filter/filter-results.png').default} alt="Logic Operators" style={{ maxHeight: "300px", maxWidth: "300px", objectFit: "cover"}}/>

</div> 

If you select **AND**, only items for which all the filter expressions are true will be displayed. If you choose **OR**, items will be shown if any of the filter terms are true. 

:::tip NOTE
Multi-expression filtering should be applied carefully and logically to achieve the best result.
:::

### Delete Expressions and Filters


You can either **remove single expressions** from the filter by clicking on the three dots <img src={require('/img/map/filter/3dots_horizontal.png').default} alt="Options" style={{ maxHeight: "25px", maxWidth: "25px", objectFit: "cover"}}/> next to the expression and then click on `Delete`.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/filter/filter_delete.webp').default} alt="Delete" style={{ maxHeight: "300px", maxWidth: "300px", objectFit: "cover"}}/>

</div> 

Or you can **remove the whole filter** by clicking on `Clear Filter` at the bottom of the Filter menu. 

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

  <img src={require('/img/map/filter/clear_filter.webp').default} alt="Clear Filters" style={{ maxHeight: "300px", maxWidth: "300px", objectFit: "cover"}}/>

</div> 




