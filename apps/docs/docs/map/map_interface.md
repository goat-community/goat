---
description: "Find your way around the Map interface: the upper bar, the Layers panel, search, toolbox and measurement tools, the style and filter panel, and map navigation."
sidebar_position: 1
---

# Map Interface

**Opening a project will take you to the Map Interface**. Here, you can create, organize, and style layers, visualize spatial data, and harness all of GOAT's powerful spatial analysis capabilities.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/interface/map_interface.webp').default} alt="Map Interface Overview" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

### Upper Bar

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/interface/upper_bar.webp').default} alt="Upper bar interface elements" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

#### Left Side
- <code>Project menu</code>: <strong>Click to return</strong> to the home page, edit project metadata, delete the project, lock the map extent, report an issue, or read the privacy policy.
- <code>Project Name</code>: <strong>Double-click to edit</strong> the project name.
- <code>Last Saved</code>: <strong>Shows the timestamp</strong> of the last saved change.

#### Right Side
- <code>Project mode toggle</code>: <strong>Switch between</strong> the Map, Workflows, Layouts and Dashboard interfaces.
- <code>Share Project</code>: <strong>Manage the sharing options</strong>.
- <code>Documentation</code>: <strong>Access the GOAT documentation</strong>.
- <code>Job Status</code>: <strong>View the status</strong> of ongoing and completed tasks.
- <code>User profile</code>: <strong>Access account settings</strong> and log out.


### Panels & tools

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/interface/right-left_panels.webp').default} alt="recent datasets" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

#### Layers Panel

The Layers Panel on the left side of the map interface provides **access to all project layers**. From here, users can manage their data by **adding new layers** with <code>+ Add layer</code> and **organizing them** using <img src={require('/img/icons/layer.png').default} alt="Group layers" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/><code>Group layers</code> to create logical collections of related datasets.

#### Tools
The tools are located on the right side of the Layers Panel:

- <img src={require('/img/icons/magnifying-glass.png').default} alt="Address and coordinates search" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> <code> Search button</code>: <strong>Search for addresses</strong> or coordinates to quickly navigate to a specific location on the map. 

- <img src={require('/img/icons/toolbox.png').default} alt="Toolbox" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> <code>Toolbox</code>: <strong>Access to the Toolbox</strong>. Read more in [Toolbox](../category/toolbox).


-  <img src={require('/img/icons/ruler-horizontal.png').default} alt="Measurements" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> <code>Measurements</code>: Users can <strong>measure distances and areas</strong>, such as routes, lines and polygons.
  
#### Editing and Tools Panel

When selecting a layer from the Layers Panel, the Editing Panel appears on the right side of the map interface. This panel provides access to various options:

- <code>Style</code>: <strong>Customize the visual appearance</strong> of the selected layer by changing colors, opacity, and other styling options. Read more in [Layer Styling](../category/layer-design).

- <code>Filter</code>: <strong>Apply filters</strong> to the selected layer to display only specific features based on attribute values. Read more in [Layer Filtering](filter).

- <code>Metadata</code>: <strong>View and edit metadata information</strong> for the selected layer. 
  
### Map Navigation

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/interface/map_navigation.webp').default} alt="recent datasets" style={{ maxHeight: "auto", maxWidth: "90%", objectFit: "cover"}}/>
</div> 

<p></p>



- <img src={require('/img/icons/plus.png').default} alt="Zoom In" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> <code>Zoom In</code> 

- <img src={require('/img/icons/minus.png').default} alt="Zoom out" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> <code>Zoom Out</code> 
  
- <img src={require('/img/icons/fullscreen.png').default} alt="Fullscreen" style={{ maxHeight: "16px", maxWidth: "16px", objectFit: "cover"}}/> <code>Fullscreen</code> 

-  <img src={require('/img/icons/map.png').default} alt="Base map" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> <code>Base map</code>: <strong>Choose between</strong> the available base map options. Click <code>+ Add a new basemap</code> at the bottom of the panel to add a custom basemap. Under the <code>Basemap</code> tab, select the type (<code>Vector</code> or <code>Raster</code>), enter the <strong>Basemap URL</strong>, a <strong>Title</strong>, and optionally a description and thumbnail URL. Alternatively, use the <code>Single Color</code> tab to set a solid color as the map background. Click <code>Add basemap</code> to save.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/map/basemap/add_basemap.webp').default} alt="Add custom basemap in GOAT" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

