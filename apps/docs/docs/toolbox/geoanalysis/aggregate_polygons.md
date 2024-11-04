---
sidebar_position: 3
---

import thematicIcon from "/img/toolbox/data_management/join/toolbox.webp";
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


# Aggregate Polygons

The **Aggregate Polygon** tool performs statistical analysis of polygons, e.g. count, sum, min, or max, and **aggregates the information on polygons**.

## 1. Explanation

With the Aggregate Polygons tool, data can be combined or aggregated between different polygon layers based on their **spatial relationships**. These spatial relationships are calculated using different **statistical approaches**. This technique is useful for analyzing and visualizing how different geographical entities interact, making them easier to analyze and interpret.

The example below shows the geometry of the *Source Layer* remains the same, while its attribute table will be enriched by aggregating information from the *Area of Aggregation*.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/toolbox/geoanalysis/aggregate_polygons/polygon_aggregation.png').default} alt="Polygon Aggregation" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 


## 2. Example use cases

- Visualizing the number of parks per city district.
- Calculating the mean building size in an area.
- Aggregating population numbers on a hexagonal grid and calculating population densities.

## 3. How to use the tool?


<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click on <code>Toolbox</code> <img src={thematicIcon} alt="toolbox" style={{width: "25px"}}/>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under the <code>Geoanalysis</code> menu, click on <code>Aggregate Polygons</code>.</div>
</div>



<img src={require('/img/toolbox/geoanalysis/aggregate_polygons/aggregate_polygons.png').default} alt="Polygon Aggregation Tool in GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>

### Layer to aggregate

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Select your <code>Source Layer</code>, which contains the data you like to aggregate.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Select on which <code> Area Type</code> you like to aggregate the source layer. You can choose between <b>Polygon</b> or <b>H3 grid</b>.</div>
</div>

<Tabs>
  <TabItem value="Polygon" label="Polygon" default className="tabItemBox">

 #### Polygon

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Select the <code>Area Layer</code> which contains the polygons on which you like to aggregate your point data.</div>
</div>


  </TabItem>
  <TabItem value="H3 Grid" label="H3 Grid" className="tabItemBox">

 #### H3 Grid

 <div class="step">
  <div class="step-number">5</div>
  <div class="content">Select the <code>H3 Grid Resolution</code>. You can choose resolutions between <b>3</b> (average edge length of 69km) and <b>10</b> (average edge length of 70m).</div>
</div>

:::tip NOTE

To learn more about the H3 grid, you can visit the [Glossary](../../further_reading/glossary#H3-grid).

:::

  </TabItem>
</Tabs>

### Statistics

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Select the <code> Statistic Method</code> and <code>Field Statistics</code> (the field in the source layer that is used to group the aggregation.).</div>
</div>

Available **Statistics Methods** are listed in the following. The available methods depend on the data type of the chosen attribute:

| Method | Type | Description |
| -------|------| ------------|
| Count  | `string`,`number`    | Counts the number of non-null values in the selected column|
| Sum    | `number`   | Calculates the sum of all the numbers in the selected column|
| Mean   | `number`   | Calculates the average (mean) value of all numeric values in the selected column|
| Median | `number`   | Yields the middle value in the selected column's sorted list of numeric values|
| Min    | `number`   | Yields the minimum value of the selected column|
| Max    | `number`   | Yields the maximum value of the selected column|


<div class="step">
  <div class="step-number">7</div>
  <div class="content">If you wish, you can enable the <b>Weighted by Intersection Area</b> by clicking on the <b>options button</b> <img src={require('/img/map/styling/options_icon.png').default} alt="Options Icon" style={{ maxHeight: "25px", maxWidth: "25px", objectFit: "cover"}}/>. Therewith, aggregated values are weighted by the share of the intersection area between the <i>Source Layer</i> and the <i>Aggregation Layer</i>.</div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Click on <code>Run</code>.</div>
</div>

:::tip Hint

Depending on the size of the datasets, the calculation might take some minutes. The [status bar](../../workspace/home#status-bar) shows the current progress.

:::

### Results

<div class="step">
  <div class="step-number">9</div>
  <div class="content">As soon as the calculation process is finished, the resulting layer <b>"Aggregation Polygon"</b> will be added to the map. The result layer will consist of the information of the source layer and an <b>additional column</b> showing the results from the <b>statistical operation</b>. You can see the table by clicking on the polygon on the map.</div>
</div>

<img src={require('/img/toolbox/geoanalysis/aggregate_polygons/aggregate_polygons_result.png').default} alt="Polygon Aggregation Result in GOAT" style={{ maxHeight: "auto", maxWidth: "auto"}}/>

:::tip Tip
Want to style your result layer and create nice-looking maps? See [Styling](../../map/layer_style/styling).
:::

