---
description: "Show or hide a layer's legend, add a caption below the layer name and replace the values of color scale steps with custom legend labels such as Low or High."
sidebar_position: 5
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


# Legend

**Legends help users understand the symbology and meaning of your map layers.** GOAT automatically displays legends for all visible layers, but you can customize their appearance and add descriptive captions to make your maps more informative.

## How to manage layer legends

<div class="step">
  <div class="step-number">1</div>
  <div class="content">In the <code>Layers</code> panel, click your layer. Its settings panel opens on the right with the <code>Style</code> tab selected. Open the <code>Legend</code> section at the bottom of this tab.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Options</code>, toggle the <code>Show</code> checkbox to <strong>enable or disable the legend display</strong></div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">While <code>Show</code> is enabled, you can fill in the <code>Caption</code> field <strong>explaining the layer's content</strong>. The caption will appear below the layer name in the legend list</div>
</div>

<p></p>
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/map/styling/legend.webp').default} alt="Legend configuration with caption settings" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div>

## Custom legend labels for color steps

When using attribute-based styling with a color scale (any classification method, including <code>Custom Breaks</code> and <code>Custom Ordinal</code>), you can add a custom label to each color step. These labels replace the raw data values in the map legend with human-readable descriptions.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">In the <code>Style</code> section of the <code>Style</code> tab, click the options icon <img src={require('/img/icons/options.png').default} alt="Options Icon" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> next to <code>Fill Color</code> or <code>Stroke Color</code>. With a field selected in <code>Color based on</code>, click the <code>Color scale</code> selector to open the classification panel. See [Attribute-based Styling](./style/attribute_based_styling).</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Below each color step row you will see a text input with the placeholder <code>Legend label</code>. Type a custom label, for example <code>Low</code>, <code>Medium</code>, or <code>High</code>, to replace the numeric value in the legend.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Leave the field empty to show the default value in the legend. Click <code>Apply</code> to save your labels.</div>
</div>

## Best practices

- **Use clear, descriptive captions** that explain what the layer represents
- **Keep captions concise** but informative
- **Disable legends** for layers that don't need visual explanation (e.g., reference layers)
- **Review legend visibility** to avoid cluttering the map interface
