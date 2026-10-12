---
description: "Style fill, stroke, stroke width, markers or point radius by a data field, using color palettes and classification methods such as quantile or custom breaks."
sidebar_position: 2
---

# Attribute-based Styling

**You can style layers based on data attributes to easily identify differences and trends.** Each visualization aspect (Fill Color, Stroke Color, Stroke Width, Custom Marker, and Point Settings) can be styled by any field in your layer's data.

<iframe width="100%" height="500" src="https://www.youtube.com/embed/cLIPMCOu4FQ?si=aydSJN_Pf0fusO9x" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## How to apply attribute-based styling

<div class="step">
  <div class="step-number">1</div>
  <div class="content">In the <code>Layers</code> panel, click your layer. Its settings panel opens on the right with the tabs <code>Style</code>, <code>Filter</code> and <code>Metadata</code>, and the <code>Style</code> tab selected. The styling options are in the <code>Style</code> section of this tab.</div>
</div>

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="fill-color" label="Fill Color" default>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">On <code>Fill Color</code>, click the options icon <img src={require('/img/icons/options.png').default} alt="Options Icon" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> and the <code>Advanced Options</code> will appear.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Color based on</code>, select the <strong>text or number field to style by</strong>.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Now you can go up to <code>Palette</code>, and choose a <strong>color palette</strong> or keep the default. Learn more in the <a href="#color-palette">Color Palette</a> section below.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Click <code>Color scale</code> and choose your <strong>data classification method</strong>. See all methods in the <a href="#data-classification-methods">Data Classification</a> section.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">At the bottom of the <code>Color scale</code> panel, toggle <code>No data</code> to assign a color to features where the selected field has no value. The default color is grey (<code>#CCCCCC</code>). Click the color swatch to change it.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <Video src={require('/img/map/styling/attribute-based-fill-color.mp4').default} alt="Fill Color Styling" style={{ maxHeight: "auto", maxWidth: "20%", objectFit: "cover"}}/>

</div>

</TabItem>
<TabItem value="stroke-color" label="Stroke Color">

<div class="step">
  <div class="step-number">2</div>
  <div class="content">On <code>Stroke Color</code> (labelled <code>Color</code> for line layers), click the options icon <img src={require('/img/icons/options.png').default} alt="Options Icon" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> and the <code>Advanced Options</code> will appear.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Color based on</code>, select the <strong>text or number field to style by</strong>.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Now you can go up to <code>Palette</code>, and choose a <strong>color palette</strong> or keep the default. Learn more in the <a href="#color-palette">Color Palette</a> section below.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Click <code>Color scale</code> and choose your <strong>data classification method</strong>. See all methods in the <a href="#data-classification-methods">Data Classification</a> section.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">At the bottom of the <code>Color scale</code> panel, toggle <code>No data</code> to assign a color to features where the selected field has no value. The default color is grey (<code>#CCCCCC</code>). Click the color swatch to change it.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <Video src={require('/img/map/styling/attribute-based-stroke-color.mp4').default} alt="Stroke Color Styling" style={{ maxHeight: "auto", maxWidth: "20%", objectFit: "cover"}}/>

</div>

</TabItem>
<TabItem value="custom-marker" label="Custom Marker">

<div class="step">
  <div class="step-number">2</div>
  <div class="content">On <code>Custom Marker</code>, enable the toggle and click the options icon <img src={require('/img/icons/options.png').default} alt="Options Icon" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. The <code>Advanced Options</code> will appear.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Marker based on</code>, select the <strong>text field to style by</strong>.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Click <code>Ordinal Markers</code> and choose the marker for each category value: pick from the <code>Library</code> or upload your own under <code>Custom</code>.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Under <code>Marker Settings</code>, adjust the <code>Size</code> slider to set the base marker size, and use <code>Placement</code> to control where the icon is anchored relative to the map point (<code>Center</code>, <code>Top</code>, <code>Bottom</code>, <code>Left</code>, <code>Right</code> or a corner position such as <code>Top Left</code>).</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Enable <code>Allow overlap</code> to prevent markers from being hidden when they overlap on the map.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Optionally, click the options icon <img src={require('/img/icons/options.png').default} alt="Options Icon" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> next to <code>Marker Settings</code> to show its <code>Advanced Options</code> and set <code>Marker size based on</code> to a numeric field to vary the marker size per feature. See the <a href="#point-settings">Point Settings</a> tab for details on size classification.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <Video src={require('/img/map/styling/attribute-based-custom-marker.mp4').default} alt="Custom Marker Styling" style={{ maxHeight: "auto", maxWidth: "40%", objectFit: "cover"}}/>

</div>

</TabItem>
<TabItem value="stroke-width" label="Stroke Width">

<div class="step">
  <div class="step-number">2</div>
  <div class="content">On <code>Stroke Width</code>, click the options icon <img src={require('/img/icons/options.png').default} alt="Options Icon" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> and the <code>Advanced Options</code> will appear.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Stroke based on</code>, select the <strong>numeric field</strong> to drive the stroke width.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Click <code>Size scale</code> to open the classification panel. Choose a <strong>classification method</strong> and set the number of <strong>Steps</strong> (2–10). Each step shows a width preview alongside the value range.</div>
</div>

:::note
Stroke Width attribute-based styling applies to **lines, polygons, and points**.
:::

</TabItem>
<TabItem value="point-settings" label="Point Settings">

<div class="step">
  <div class="step-number">2</div>
  <div class="content">On <code>Point Settings</code>, click the options icon <img src={require('/img/icons/options.png').default} alt="Options Icon" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> and the <code>Advanced Options</code> will appear.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Radius based on</code>, select the <strong>numeric field</strong> to drive the point radius.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Click <code>Size scale</code> to open the classification panel. Choose a <strong>classification method</strong> and set the number of <strong>Steps</strong> (2–10). Each step shows a size preview alongside the value range. The same methods as color classification are available: [Quantile](https://www.plan4better.de/en/glossary/quantile-classification), [Standard Deviation](https://www.plan4better.de/en/glossary/standard-deviation-classification), [Equal Interval](https://www.plan4better.de/en/glossary/equal-interval-classification), Heads and Tails, Custom Breaks, and Custom Ordinal.</div>
</div>

:::note
Point Settings is only available for **point layers without a Custom Marker**. For point layers with a Custom Marker, use <code>Marker size based on</code> inside the Custom Marker tab.
:::

</TabItem>
</Tabs> 


## Color Palette

A palette is a set of colors representing your data values or categories.

You can customize your palette by selecting the <code>Type</code>, adjusting <code>Steps</code>, enabling <code>Reversed</code> to reverse the colors, or enabling <code>Custom</code> for your own color range.

GOAT offers four predefined palette types:

<p></p>

| Palette Type | Example                                                                                                                                                       | Description                                                                                                                                                                                                     |
| :----------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  Diverging   | <img src={require('/img/map/styling/diverging_palette.png').default} alt="diverging" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>     | **Useful for data with a central midpoint**, like positive and negative values. It helps show variations clearly around this midpoint.                                                                          |
|  Sequential  | <img src={require('/img/map/styling/sequential_palette.png').default} alt="sequential" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>   | **Ideal for data that follows a natural progression or ordered sequence**, like increasing or decreasing values. It excels at visualising continuous data, showing gradual changes from one extreme to another. |
| Qualitative  | <img src={require('/img/map/styling/qualitative_palette.png').default} alt="qualitative" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/> | **Designed for distinct categories or classes.** It helps distinguish between discrete categories without implying any order or importance.                                                                     |
|  Singlehue   | <img src={require('/img/map/styling/singlehue_palette.png').default} alt="singlehue" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>     | **Uses different shades and tones of a single color.** It creates a harmonious look and is effective for conveying information without the distraction of multiple colors.                                      |

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

<Video src={require('/img/map/styling/attribute-based-color-palettes.mp4').default} alt="Quantile" style={{ maxHeight: "auto", maxWidth: "75%", objectFit: "cover"}}/>

</div>  

## Data Classification Methods

The <code>Color scale</code> determines how data values map to colors. GOAT offers six data classification methods: **Quantile, Standard Deviation, Equal Interval, Heads and Tails, Custom Breaks, and Custom Ordinal.** For text fields, only Custom Ordinal is available. All the methods default to 7 classes, but you can adjust this number as needed.

### Quantile

**Divides data into classes with equal numbers of features**. **Ideal for linearly distributed data**, but creates uneven value ranges.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

<img src={require('/img/map/styling/quantile.webp').default} alt="Quantile" style={{ maxHeight: "auto", maxWidth: "60%", objectFit: "cover"}}/>

</div>  

### Standard Deviation

**Classifies data by deviation from the average**. Shows **relative dispersion, distribution, and outliers** statistically, but requires normally distributed data.
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/styling/standard_deviation.webp').default} alt="Standard Deviation" style={{ maxHeight: "auto", maxWidth: "60%", objectFit: "cover"}}/>

</div> 

### Equal Interval

**Divides data into equal-sized value ranges**. Works well for **evenly distributed data but can be misleading with skewed data** (some classes may be empty). 
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/styling/equal_interval.webp').default} alt="Equal Interval" style={{ maxHeight: "auto", maxWidth: "60%", objectFit: "cover"}}/>

</div> 

### Heads and Tails

**Handles skewed data by highlighting extremes**. Focuses on 'heads' (very high values) and 'tails' (very low values). **Useful for datasets where extremes matter most and for highlighting disparities**.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/styling/heads_tails.webp').default} alt="Heads and Tails" style={{ maxHeight: "auto", maxWidth: "60%", objectFit: "cover"}}/>

</div> 

### Custom Ordinal (for **strings**)

**Sorts and visualizes string data** like categories or labels. Since strings lack natural order, **Custom Ordinal lets you define your own ordering rules** for tailored sequences.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/styling/ordinal.webp').default} alt="Custom Ordinal for strings" style={{ maxHeight: "auto", maxWidth: "60%", objectFit: "cover"}}/>

</div>

<p></p>

You can add more steps and select multiple string values per group from the <code>dropdown menu</code>, which lists all values from your dataset.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <Video src={require('/img/map/styling/custom_ordinal.mp4').default} alt="Custom Ordinal for strings" style={{ maxHeight: "auto", maxWidth: "40%", objectFit: "cover"}}/>

</div> 

### Custom Breaks (for **numbers**)

**For numerical data with custom breakpoints or thresholds**. It provides tailored visualizations for specific contexts. **Helps maintain consistency across maps**. Gives full control over classifications aligned with real-world needs.


:::tip HINT
To reuse your dataset with the styling settings in other projects, [save your style as default](./styling.md#copy-and-paste-style).
:::