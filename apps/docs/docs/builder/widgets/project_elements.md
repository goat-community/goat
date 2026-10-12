---
description: "Round off a dashboard with Text, Divider, Image, Tabs and Links widgets: format text, separate sections, group widgets into tabs and add links or popups."
sidebar_position: 4
---

# Project Elements

This section of widgets offer **extra elements to make your dashboard rounded**: **Text**, **Divider**, **Image**, **Tabs**, and **Links**.

## Text

Add text to your dashboard. You can **customize it with the appearing buttons**:

- You can use different **headings, lists,** or **code blocks.**
- Add **bold**, *italic*, <u>underline</u>, strikethrough (~~Lorem ipsum~~), subscript (X<sub>1</sub>) or superscript (X<sup>1</sup>) to your text.
- Change the **alignment, add links,** adjust the **letter color** or **add highlight.**

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_text.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Divider

The divider widget adds a **horizontal line** to your dashboard, which can be used to visually separate different sections or elements within the dashboard.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_divider.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Image

**Upload an image from your computer** to your dashboard. Under `Info` you can add a `Description` shown below the image and an `Alternative text` for accessibility. Enable `Padding` under Options to add inner spacing around the image.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/builder/builder_image.webp').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Tabs

The Tabs widget **groups other widgets in the same panel into tabbed views**, letting viewers switch between them without scrolling.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Drag and drop the <code>Tabs</code> widget on a panel. Add other widgets to the same panel first so they are available to assign.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Info</code>, add a <code>Title</code> for the widget.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">
  Under <code>Tabs & Widgets</code>, each tab is listed with its name and widget count. Click a tab to expand it:
  <ul>
    <li>Use the <code>Add widget to this tab...</code> dropdown to assign widgets from the same panel. Each widget can only be assigned to one tab at a time.</li>
    <li>Drag the dotted icon to reorder assigned widgets. Use the ⋮ menu to remove a widget from the tab.</li>
    <li>Click the delete icon on a tab to remove it (available when more than one tab exists).</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Click the <code>+</code> button to add a new tab.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Enable <code>Full width</code> to make the tab bar span the full panel width.</div>
</div>

## Links

The Links widget **displays a row of labelled links or popup triggers**, useful for navigation, references, or inline information.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Drag and drop the <code>Links</code> widget on a panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Info</code>, add a <code>Title</code> and optional <code>Description</code>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">
  Under <code>Links</code>, each item has a <code>URL</code> / <code>Popup</code> toggle:
  <ul>
    <li><code>URL</code>: enter a <code>Label</code> and a destination URL.</li>
    <li><code>Popup</code>: enter a <code>Label</code> and click <code>Configure popup</code> to set the <code>Popup type</code> (<code>Tooltip</code>, <code>Popup</code>, or <code>Dialog</code>), <code>Popup placement</code>, <code>Size</code> (<code>Small</code>, <code>Medium</code>, or <code>Large</code>), and the popup content (Markdown supported).</li>
  </ul>
  Drag items to reorder them. Click the × icon to delete a link.
  </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Click <code>Add Link</code> to add another item.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">
  Under <code>Options</code>:
  <ul>
    <li><code>Separator</code>: visual divider between links (<code>Vertical line</code>, <code>Dot</code>, or <code>Dash</code>).</li>
    <li><code>Secondary text</code>: additional text shown alongside the links (e.g. a copyright notice).</li>
  </ul>
  </div>
</div>

::::tip
Check out our **[Gallery](https://www.plan4better.de/en/gallery)** for further dashboard inspirations.
::::

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_viewer_dashboard.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div>