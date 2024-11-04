---
sidebar_position: 3
---

# Datasets

On the **Datasets** page, data can be **uploaded, managed, and shared**. The page provides users with an organized view of their datasets, categorized by personal datasets, team datasets, and datasets that are shared with the whole organization. Furthermore, datasets can be organized in **folders**, **filtered**, and **sorted** based on their name, creation date, or their last update. Datasets can also be **deleted**, **downloaded** and their **metadata** edited. 

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/datasets_general.png').default} alt="Datasets Page in Workspace of GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

In the Workspace you have the option to upload a dataset or add it via an external link.

## Upload data

GOAT supports the upload of **GeoPackage, GeoJSON, Shapefile, KML, CSV**, and **XLSX** files. Follow these steps to upload a dataset via the Workspace:

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Navigate to the <b>"Datasets"</b> page via the sidebar.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Click on <code>+ Add Dataset</code> and select <code>Dataset Upload</code>. </div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Select the file from your local device.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Select the <b>Destination Folder</b> and define the <b>Name</b> of your new dataset. Furthermore, you can add a <b>Description</b> if you like.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Check the information and click on <code>Upload</code>.</div>
</div>

## External data

 The following external datasets are supported in GOAT: **Web Feature Service (WFS), Web Map Service (WMS), Web Map Tile Service (WMTS), XYZ Tiles**. Follow these steps to add an external dataset via the Workspace:

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Navigate to the <b>"Datasets"</b> page via the sidebar.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Click on <code>+ Add Dataset</code> and select <code>Dataset External</code>. </div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Add the URL the file.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Select the layer you'd like to add and click on <code>Next</code>.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Select the <b>Destination Folder</b> and define the <b>Name</b> of your new dataset. Furthermore, you can add a <b>Description</b> if you like.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Check the information and click on <code>Save</code>.</div>
</div>

:::tip tip

You can also upload datasets directly in the [Map](../map/layers).

:::


## Filter datasets

Datasets can be sorted based on the [dataset type](../data/dataset_types "What are the dataset types?"), i.e. *features, tables, external imagery*, and *external vector tiles*. Simply click on the filter icon <img src={require('/img/map/filter/filter_icon.png').default} alt="Filter Icon" style={{ maxHeight: "20px", maxWidth: "20px"}}/> to choose the desired dataset type for filtering.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/dataset_filter.gif').default} alt="Datasets filtering in Workspace of GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Managing datasets
By clicking on the three dots <img src={require('/img/map/filter/3dots.png').default} alt="Options" style={{ maxHeight: "25px", maxWidth: "25px", objectFit: "cover"}}/> , you can view and edit the metadata of datasets, move a dataset into another folder, download it, share the dataset with other people, or delete it.
<img src={require('/img/workspace/datasets/managing_datasets.gif').default} alt="Options" style={{ maxHeight: "300px", maxWidth: "300px"}}/>


## See metadata of the datasets

The **metadata** of datasets can be viewed and edited by clicking on <code>Info</code> under the three dots <img src={require('/img/map/filter/3dots.png').default} alt="Options" style={{ maxHeight: "25px", maxWidth: "25px", objectFit: "cover"}}/> or by clicking directly on the dataset. This grants access to a detailed **summary** of the data, the **attribute table**, and a **map preview with a legend**.
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/metadata.gif').default} alt="Metadata of the datasets in Workspace of GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 


## Create folders

To organize your data, you can create new folders within the workspace. Therefore, click on the ``folder icon`` <img src={require('/img/workspace/datasets/folder_icon.png').default} alt="Folder Icon" style={{ maxHeight: "25px", maxWidth: "25px"}}/> and define the name of the new folder.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/new_folder.gif').default} alt="Create new folders in Workspace of GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 


## Move datasets to folders

To move a dataset into a folder, click on three dots <img src={require('/img/map/filter/3dots.png').default} alt="Options" style={{ maxHeight: "25px", maxWidth: "25px"}}/> and select **"Move to folder"**. From the dropdown menu, choose the folder to which you want to move your dataset.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/move_to_folder.gif').default} alt="Move your datasets to the folders in Workspace of GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 
