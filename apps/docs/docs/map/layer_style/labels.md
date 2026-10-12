---
description: "Label map features with an attribute field and set the size, color, placement, offset and overlap of the labels, plus a halo color and width for readability."
sidebar_position: 3
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


# Labels

**Labels allow you to display text on your map features based on any attribute field.** This makes your maps more informative and easier to interpret by showing key information directly on the features.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/map/styling/labels.webp').default} alt="Labels displayed on map features" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div>

## How to add and configure labels

### General settings

<div class="step">
  <div class="step-number">1</div>
  <div class="content">In the <code>Layers</code> panel, click your layer. Its settings panel opens on the right with the tabs <code>Style</code>, <code>Filter</code> and <code>Metadata</code>, and the <code>Style</code> tab selected. Open the <code>Labels</code> section of this tab.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">On <code>Label by</code> choose the <strong>attribute field</strong> (text or number) whose values you want to display as labels. The <code>Label Settings</code> appear below once a field is selected.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <Video src={require('/img/map/styling/label_by.mp4').default} alt="Selecting label attribute field" style={{ maxHeight: "auto", maxWidth: "500px", objectFit: "cover"}}/>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Under <code>Label Settings</code>, on <code>Size</code>, set the <strong>label size</strong> using the slider (1-100) or enter the value manually</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">On <code>Color</code> choose a <strong>label color</strong> using the <code>Color Picker</code> or select from the <code>Preset Colors</code></div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Set the <code>Placement</code> to define <strong>where labels appear relative to features</strong> (<code>Center</code>, <code>Top</code>, <code>Bottom</code>, <code>Left</code>, <code>Right</code> or the corner positions such as <code>Top Left</code>; for line layers <code>Center</code>, <code>Above</code> or <code>Below</code>)</div>
</div>

### Advanced settings

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Click the options icon <img src={require('/img/icons/options.png').default} alt="Options" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> next to <code>Label Settings</code> to show the <code>Advanced Options</code></div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Adjust <code>Offset X</code> and <code>Offset Y</code> to fine-tune <strong>label position</strong> by moving horizontally or vertically</div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Configure the <code>Allow overlap</code> checkbox: <strong>Enable to show all labels</strong> (may cause visual clutter) or <strong>disable it to hide labels that would overlap others</strong>, especially at lower zoom levels (cleaner appearance)</div>
</div>

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Add a <code>Halo color</code> to create a <strong>colored outline around text </strong> for better readability on busy backgrounds</div>
</div>

<div class="step">
  <div class="step-number">10</div>
  <div class="content">Set the <code>Halo width</code> to control <strong>outline thickness</strong> (maximum is one-quarter of font size)</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <Video src={require('/img/map/styling/labels_overlap.mp4').default} alt="Label overlap and halo effects" style={{ maxHeight: "auto", maxWidth: "500px", objectFit: "cover"}}/>
</div>

## Best practices

- Use **smaller fonts for dense layers** to reduce visual clutter
- Add **halos with contrasting colors** (light halos on dark maps, dark halos on light maps) to improve text readability
- Keep **overlap disabled by default for cleaner appearance**, though some labels may be hidden in crowded areas
- **Test your label settings at different zoom levels** to ensure they remain readable and useful across all scales
