---
sidebar_position: 4
---

# Catalog

The **Data Catalog** is a comprehensive listing of all [geospatial datasets](../further_reading/glossary#geospatial-data) available for exploration and analysis. A wide range of datasets are provided by Plan4Better based on official open-data providers and other sources, ensuring that **reliable** data is immediately available to carry out analysis and visualization within your projects.

<div class="content"><img src={require('/img/workspace/catalog/home-catalog.png').default} alt="Data Catalog" style={{ maxHeight: "700px", maxWidth: "800px"}}/></div>

## Explore the catalog

Accessed from the [Workspace](../category/workspace) or via the [`+ Add layer`](../map/layers#add-layers) button in your GOAT project, you can search our collection of datasets by *keyword*, or by applying *spatial* and *non-spatial filters* for efficient discovery. You can also interactively preview datasets within our interface to assess content and quality, enabling visual exploration.

Our catalog features an extensive collection of datasets spanning different thematic areas, under different categories including:

- **Basemap:** Foundational map layer providing essential geographic features such as coastlines, rivers, and terrain, serving as a backdrop for additional data layers.

- **Imagery:** High-resolution visual data captured from satellites or aerial photography, offering detailed views of landscapes, urban areas, and infrastructure.

- **Boundary:** Spatial demarcations delineating administrative, political, or geographic boundaries, including country borders, state/province lines, and municipal districts.

- **Land-use:** Categorization of land areas based on their primary usage, including classifications such as residential, commercial, industrial, agricultural, and recreational zones.

- **Environment:** Data depicting natural features and phenomena, such as ecosystems, climate patterns, and ecological habitats.

- **People:** Demographic data related to human populations, such as population density, population distribution, age groups, and socio-economic characteristics.

- **Transportation:** Information on transportation networks and infrastructure, including roads, highways, railways, airports, ports, and public transport systems.

- **Places:** Points of interest and geographic landmarks such as schools, car-sharing locations, tourist attractions, and hospitals.

![Data Catalog in GOAT](/img/workspace/catalog/catalog_general.png "Data Catalog in GOAT")

Clicking on a dataset within the Catalog page will take you to the **metadata** section. Here, you can explore detailed information about the dataset, including its **description**, **[dataset type](../data/dataset_types)**, **geographical and language codes** (based on [ISO 3166-1 alpha-2](https://www.iso.org/iso-3166-country-codes.html)), **distributor name**, and **license details**. You can also preview the **dataset map** and associated data directly from the data page.

## Use catalog data in your GOAT project

<div class="step">
  <div class="step-number">1</div>
  <div class="content"> Under the <b>Layer</b> tab click <code> + Add Layer</code>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content"> Select <code>Catalog Explorer</code> and browse the <b>Data Catalog</b>.</div>
</div>

<div class="content"><img src={require('/img/workspace/catalog/map-catalog.png').default} alt="Catalog Explorer" style={{ maxHeight: "700px", maxWidth: "800px"}}/></div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content"> Select a <i>dataset</i> and click <code>Add Layer</code>.</div>
</div>

<div class="content"><img src={require('/img/workspace/catalog/add-layer.png').default} alt="Catalog Explorer" style={{ maxHeight: "700px", maxWidth: "800px"}}/></div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">After adding the layer, you can apply a <code><img src={require('/img/map/filter/filter_icon.png').default} alt="Filter Icon" style={{ maxHeight: "16px", maxWidth: "16px"}}/> Filter</code>. This allows large layers to be constrained to the specific geographic extent or attributes necessary for your analysis, thereby reducing complexity and speeding up analytical operations. </div>
</div>


:::tip HINT

To learn more about GOAT's advanced filtering capabilities, see the [Filter](../map/filter.md "Filter dataset") page.

:::