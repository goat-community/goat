---
description: "Create buffer zones at one or more distances around points, lines or polygons, optionally merging overlapping buffers into one polygon per distance."
sidebar_position: 1
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';



# Buffer

This tool allows you to **create zones around points, lines, or polygons with a specified distance**.

<div style={{ display: 'flex', justifyContent: 'center' }}>
<iframe width="674" height="378" src="https://www.youtube.com/embed/Yboi3CwOLPM?si=FuSPRmK6zTB-GVJ1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

## 1. Explanation

A buffer is a tool used to **delineate the catchment area around a specific point, line, or polygon illustrating the extent of influence or reach from that feature.** Users can define the ``distance`` of the buffer, thereby customizing the radius of the area covered.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

  <img src={require('/img/toolbox/geoprocessing/buffer/buffer_types.png').default} alt="Buffer Types" style={{ maxHeight: "400px", maxWidth: "400px", objectFit: "cover"}}/>

</div> 

## 2. Example use cases 

- Analyze population within 500m of train stations
- Count shops accessible within 1000m of bus stops


## 3. How to use the tool?


<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click on <code>Tools</code> <img src={require('/img/icons/toolbox.png').default} alt="Options" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under the <code>Geoprocessing</code> menu, click on <code>Buffer</code>.</div>
</div>

### Input

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Select the <code>Input layer</code> around whose features you want to create the buffers. Point, line and polygon layers can be used.</div>
</div>

### Configuration

The <code>Configuration</code> section becomes available as soon as an input layer is selected.

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Choose the <code>Distance Source</code>:
    <ul>
      <li><b>Constant</b> (default): the same distances are used for all features. Enter them in <code>Buffer Distances</code>, separated by commas (e.g. <code>100, 200, 300</code>). GOAT creates <b>one buffer per feature and per distance</b>.</li>
      <li><b>Field</b>: every feature gets its own distance. Select the numeric <code>Distance Field</code> of the input layer that contains the distance. Features with an empty value or a value of 0 are skipped.</li>
    </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Select the <code>Distance Units</code> of the distances: <b>Meters</b> (default), <b>Kilometers</b>, <b>Feet</b>, <b>Miles</b>, <b>Nautical Miles</b> or <b>Yards</b>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">
  Configure <code>Merge overlapping buffers</code>:
    <ul>
      <li><b>Disabled</b> (default): GOAT creates a separate buffer around each input feature. The buffers keep the attributes of their input feature.</li>
      <li><b>Enabled</b>: GOAT <b>merges all buffers of the same distance into one polygon</b>. The result contains one polygon per distance; the attributes of the input features are not kept. This is useful if you want to see the total area covered at each distance.</li>
    </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">If you <b>enabled Merge overlapping buffers</b>, the <code>Polygon Difference</code> switch appears. When you enable it, GOAT subtracts each smaller distance from the next larger one, so the result consists of <b>rings that do not overlap</b>. This only has an effect with the <b>Constant</b> distance source and at least two buffer distances.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/toolbox/geoprocessing/buffer/polygon_union_difference.webp').default} alt="Buffers without merging, merged, and merged with polygon difference" style={{ maxHeight: "auto", maxWidth: "60%", objectFit: "cover"}}/>
</div> 

<p></p>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">
  Optionally, click the options icon <img src={require('/img/icons/options.png').default} alt="Options" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> in the <code>Configuration</code> header to show further settings for the buffer shape:
    <ul>
      <li><code>Curve Smoothness</code>: number of segments used to approximate a quarter circle (default <b>8</b>). Higher values give smoother edges but take longer to calculate.</li>
      <li><code>Cap Style</code>: shape of the buffer at the ends of lines: <b>CAP ROUND</b> (default), <b>CAP FLAT</b> or <b>CAP SQUARE</b>.</li>
      <li><code>Join Style</code>: shape of the buffer at corners: <b>JOIN ROUND</b> (default), <b>JOIN MITRE</b> or <b>JOIN BEVEL</b>.</li>
      <li><code>Mitre Limit</code>: only shown for <b>JOIN MITRE</b>; limits how far pointed corners extend (default <b>1</b>).</li>
    </ul>
  </div>
</div>

### Results

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Optionally, change the <code>Result layer name</code> (default: <b>Buffer</b>).</div>
</div>

<div class="step">
  <div class="step-number">10</div>
  <div class="content">Click on <code>Run</code>. This starts the calculation of the buffer. As soon as it is finished, the resulting polygon layer is added to your map.</div>
</div>

The result layer contains the column <code>buffer_distance</code>. With the <b>Constant</b> distance source, it holds the distance in meters, and the buffers are colored by distance. With the <b>Field</b> distance source, it holds the value of the distance field.

<p></p>

:::tip Tip

Want to style your buffers and create nice-looking maps? See [Styling](../../map/layer_style/style/styling.md).

:::
