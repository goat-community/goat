---
sidebar_position: 1
---

# Dataset Types

Users can access datasets in the **Catalog Explorer** and through the **Dataset Explorer**. The datasets found in the [Catalog](../workspace/Catalog) are provided and maintained by Plan4Better. If you add an external dataset via URL, upload a dataset from your local computer or create a layer in GOAT, they will be visible in the Dataset Explorer.

**Adding Datasets**

![GOAT data types](/img/data/data_basis/original_files/dataset_types.png "Dataset Types")


:::info External Datasets

Unlike other datasets, external datasets are sourced from **third-party services** via the link you provide. These datasets can either be [Features](#1-features) or [Rasters](#2-rasters), each serving distinct purposes. *External feature layers* will be fetched into GOAT and stored there, meanwhile *external raster layers* will be fetched live (to overlay on the map) but not stored.
<p>
</p>
The following external datasets are supported in GOAT: Web Map Service (WMS), Web Map Tile Service (WMTS), Web Feature Service (WFS), XYZ Tiles.

:::

## Type of Datasets

### 1. Features

#### 1.1 Spatial Features
Feature datasets serve as a dynamic repository of **spatial features**, such as points, lines, or polygons - they contaian spatially referenced geogrpahic features. Users can upload and utilize data from **Shapefiles**, **Geopackages**, **GeoJSON**, and **KML** files or add **WFS** link from an external URL. Feature datasets can be visualized on the map, [styled](../category/layer-styling), and used for analyses with any tools from the [toolbox](../category/toolbox). Furthermore, feature datasets can serve as a data basis for the [scenario creation](../scenarios).

<p> </p>
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/data/spatial.png').default} alt="Home Interface Overview in GOAT" style={{ maxHeight: "750px", maxWidth: "750px", objectFit: "cover"}}/>
</div>
<p> </p>

Within the GOAT framework, there are two different types of feature datasets, to address different aspects of geospatial functionality:

- **Feature Dataset Standard:** This is the primary feature type that is automatically selected when a user uploads a file. It supports a range of formats including GeoJSON, GPKG, KML, and ZIP files. This dataset serves as the foundation for basic geospatial operations within GOAT.

- **Feature Dataset Tool:** This dataset includes all datasets that have been produced using the tools available in GOAT.


#### 1.2. Non-spatial datasets
**Tables** are **non-spatial datasets**, which differ from the geospatial datasets due to their lack of geographic reference points, therefore they cannot be visualized on the map. These datasets can be used for selected analysis and data management processes. Users can import table datasets in widely used formats such as **CSV** (Comma-Separated Values) and **XLSX** (Microsoft Excel Open XML Spreadsheet). 

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/data/table.png').default} alt="Home Interface Overview in GOAT" style={{ maxHeight: "750px", maxWidth: "750px", objectFit: "cover"}}/>
</div>
<p> </p>

### 2. Rasters

:::info Note

You cannot edit or run analyses on raster layers.

:::

Raster datasets are provided by external sources such as **WMS** (Web Map Service) or **WMTS** (Web Map Tile Service). Therewith, a wide range of georeferenced map images, such as topographic maps, can be obtained from external servers and integrated into GOAT. While these images can be incorporated as static maps, it is important to note that they do not support analytical functions.


:::tip Note

The styling of these external image datasets is dependent on the external service providing the WMS (e.g. service from GeoServer https://wm&#8203;s.websitehai.com/geoserver/ows?SERVICE=WMS&) or WMTS. 
Consequently, the visual presentation of the map imagery, including elements such as color schemes and representation of geographic features, cannot be changed within the GOAT framework.

:::
<p> </p>
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/data/raster.png').default} alt="Home Interface Overview in GOAT" style={{ maxHeight: "750px", maxWidth: "750px", objectFit: "cover"}}/>
</div>
<p> </p>

**WMS (Web Map Service)**
This type of layer supports zooming and panning and it is ideal for basemaps, but the output is always a static image and gets loaded slower.

**WMTS (Web Map Tile Service)**
WMTS layers have pre-rendered, fixed sized tiles therefore it loads quickly, and you can zoom in and pan them quickly and smoothly. It is ideal for basemaps on big areas and best to use when you want to have consistent map-style.


**XYZ Tiles**
This type of layer offers fast and efficient map zooming and panning because the tile is defined by their longitude (X), latitude (Y) and zoom level (Z) coordinates. It’s most often used when you need a fast-loading map that has the same performance on different zoom levels.

|   | WMS | WMTS and XYZ Tiles |
|----|-------------|--------------|
| **Type of URL in GOAT**    | Capabilites URL | Capabilites (only WMTS), Direct URL |
| **Data output** | Dynamic map images | Pre-rendered, cached map tiles |
| **Structure** | No tiles - images are generated on-the-fly | Structured tiles based on grid |
| **Performance** | Slower (images generated per request) | Faster (tiles are cached) |
| **Customization** | Limited | Limited |
| **Scalability** |Less scalable | Highly scalable |
|**Zoom level** | Variable, set by request parameters | Fixed zoom level, predetermined by the server |




:::info INFO
You can find out which data types are supported by GOAT under [**Attribute Types**](../data/data_types).
:::