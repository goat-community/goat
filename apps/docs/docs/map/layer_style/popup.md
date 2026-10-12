---
description: "Show feature details in a popup on click or hover, built from field list, text, image, button, badge and divider blocks or custom HTML with field placeholders."
sidebar_position: 4
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


# Popup

**Popups display relevant information when users interact with map features.** This keeps your map clean while providing detailed information on demand. You can choose when to show the popup, add content blocks, and control how everything is presented.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/map/styling/popup.webp').default} alt="Popup displaying feature information" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div>

## How to configure popups

<div class="step">
  <div class="step-number">1</div>
  <div class="content">In the <code>Layers</code> panel, click your layer. Its settings panel opens on the right with the tabs <code>Style</code>, <code>Filter</code> and <code>Metadata</code>, and the <code>Style</code> tab selected. Open the <code>Popup</code> section of this tab and enable the <code>Popup</code> toggle.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Set <code>Show popup on</code>: <code>On click</code>, <code>Only on hover</code>, or <code>On click and on hover</code>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Under <code>Content</code>, keep <code>Simple</code> selected and click <code>+ Add block</code> to add content blocks. Available block types: <code>Text</code>, <code>Field list</code>, <code>Image</code>, <code>Button</code>, <code>Badge</code>, <code>Divider</code>. Click a block in the list to edit it, drag it to reorder, or click the trash icon to remove it. The eye icon (<code>Show preview</code>) shows a preview popup on the map.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">For a <code>Field list</code> block: choose <code>Table</code> or <code>List</code> as <code>Layout</code>, click <code>+ Add attribute</code> to select which fields to display (or <code>Add all fields</code>), and optionally set <code>Collapse after</code> to limit the number of visible rows.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">
  Under <code>Appearance</code>, configure the following options:
  <ul>
    <li><code>Layout</code>: choose <code>Popup</code> or <code>Pinned</code>; for <code>Pinned</code>, choose the corner under <code>Anchor</code></li>
    <li><code>Width</code>: set a fixed width in px, or leave as <code>Auto</code></li>
    <li><code>Max height</code>: set a maximum height in px to enable scrolling for long content</li>
    <li><code>Header</code>: choose <code>Standard</code>, <code>Compact</code>, or <code>None</code></li>
    <li><code>Highlight active feature</code>: toggle to highlight the selected feature on the map</li>
  </ul>
  </div>
</div>

## HTML mode

For full control over the popup design, switch from **Simple** to **HTML** mode under `Content`. This lets you write custom HTML and CSS to create rich, branded popups, with images, styled cards, custom fonts, and dynamic field values.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Under <code>Content</code>, click <code>HTML</code> in the <code>Simple</code> / <code>HTML</code> toggle. The first time, GOAT converts your existing blocks into HTML.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">On the <code>Custom HTML</code> card, click <code>Edit…</code> to open the <code>Custom HTML</code> editor and write your custom markup. The editor shows a live preview next to your code and the <code>Appearance</code> options on the right. Click <code>Save</code> to apply your changes.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Use <code>{"{{field_name}}"}</code> placeholders to inject feature attribute values dynamically into your HTML. Type <code>{"{{"}</code> to get field suggestions, or pick a field under <code>Insert Field</code>.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/map/styling/popup_html.webp').default} alt="Custom HTML popup in GOAT" style={{ maxHeight: "auto", maxWidth: "100%"}}/>
</div>

## Best practices

- **Choose relevant fields** that provide meaningful context to users
- **Use clear, descriptive names** instead of technical field names
- **Limit the number of fields** to avoid overwhelming users with information
- **Use collapse** to keep popups compact when showing many attributes
