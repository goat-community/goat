---
description: "Publish a project so anyone can view the map without a GOAT account, share it by URL or iframe, lock the map extent and republish after changes, or make a dataset public to all GOAT users."
sidebar_position: 2
---

# Public Sharing

In GOAT you can make two kinds of content public: a **project**, so anyone can open its map without a GOAT account, and a **dataset**, so all signed-in GOAT users can use it. This page covers both.

## Publishing a Project to the Web

You can **publish a project so anyone can view its map without a GOAT account**. This is ideal for showcasing spatial analysis, sharing insights, or embedding interactive maps on external platforms.

Publishing creates a **snapshot** of the project: the public page shows the project as it was when you published it, while the project itself stays where it is and keeps its access rights. Visitors see the project as it is laid out in the [Dashboard](../builder/builder_interface).

::::info
Public sharing is view-only. If you want others to **edit the map**, share it on the <code>People</code> and <code>Teams</code> tabs of the <code>Share</code> dialog. See [Teams & Members](../sharing).
::::

### How to Share a Map Publicly? 

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/sharing/public_tab_published.webp').default} alt="The Public tab before and after publishing a project" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "contain"}}/>
</div>
<p></p>

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click <code>Share</code> in the upper-right corner of the map.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Open the <code>Public</code> tab.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Click <code>Publish to web</code>.</div>
</div>

Now you can:

- <code>Copy link</code> under <code>Address</code>: <b>Share the direct link</b> so others can open the map in their browser.

- <code>Copy</code> next to <code>Embed Code</code> under <code>Embed</code>: <b>Embed the map</b> as an iframe in websites or tools that support HTML and iframes.

### Other Settings on the Public Tab

Once the project is published, the <code>Public</code> tab also offers these settings:

- <code>Address</code>: If your organization has set up a custom domain, choose here whether the map is served from it or from the <code>GOAT default domain</code>. Without a custom domain, this section only shows the link. Custom domains are set up under [Settings](../workspace/settings).

- <code>Measurement</code>: Here you decide whether visits to the public page are counted. What you see depends on your organization:
    - If it has **no analytics instance** yet, this section shows <code>No analytics instances configured</code> and where to add one. Setting one up is described under [Analytics](../workspace/settings#analytics).
    - If it **has one or more instances**, pick one to count visits, or choose <code>No tracking</code>. Once you pick an instance, the <code>Cookie consent banner</code> switch below it can be used (with <code>No tracking</code> it is greyed out and reads <code>Not needed — nothing is tracked</code>): leave it on to ask visitors before tracking starts. If you turn it off, GOAT shows a warning, because tracking people without their consent is not allowed under GDPR in Germany and most of the EU.

### Adjusting Map Extent

To control how far users can pan and zoom out, you can lock the map extent.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/sharing/sharing_lock_extent.mp4').default} alt="Public Sharing on GOAT" style={{ maxHeight: "auto", maxWidth: "80%", objectFit: "cover"}}/>
</div>
<p> </p>

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Pan and zoom the map so that it shows the <b>largest area</b> users should be able to see.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Open the GOAT menu by clicking the GOAT logo in the upper-left corner.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Click <code>Lock map extent</code>. The map can no longer be panned or zoomed out beyond this area. To remove the limit, click <code>Unlock map view</code> in the same menu.</div>
</div>

To limit the zoom levels instead, use <code>Zoom limits</code> in the Dashboard [Settings](../builder/settings).

::::info
If your map is already published, **you’ll need to republish it** for the changes to take effect. The link will remain the same.
::::

### Updating a Public Map (Republish)

The public page does not follow later changes to the project. To update it with your latest changes:

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click <code>Share</code> in the upper-right corner.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Open the <code>Public</code> tab.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Click <code>Republish</code>. The snapshot is replaced with the current state of the project; the link stays the same, so embedded maps show the new version as well.</div>
</div>

### Unpublishing a Map

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click <code>Share</code> in the upper-right corner and open the <code>Public</code> tab.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Take it offline</code>, click <code>Unpublish</code>. The link stops working for everyone, including embedded maps. You can publish again at any time.</div>
</div>

## Making a Dataset Public

As a dataset's owner, you can **make it public to all GOAT users**. This does not create a public link or a snapshot: it only opens the dataset to other signed-in GOAT users.

<div class="step">
   <div class="step-number">1</div>
   <div class="content">Open the dataset's <code>More Options</code> <img src={require('/img/icons/3dots.png').default} alt="More options" style={{ maxHeight: '20px', maxWidth: '20px'}}/> menu, choose <code>Share</code>, open the <code>Public</code> tab and turn on <code>Public to all GOAT users</code>.</div>
</div>

Once public, **every signed-in GOAT user, in any organization, can view the dataset and add it to their projects**. It is not listed anywhere; people reach it through the projects and templates that include it, and editing rights do not change. When a public dataset ships with a template, it is shown with a **public badge**.
