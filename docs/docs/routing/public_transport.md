---
sidebar_position: 3
---

# Public Transport

##### Routing algorithms - Public Transport:

Since public transport isochrone requires a combination of different data types (sidewalks, bikeways, public transport schedules, etc.) it has more complexity than the other isochrone modes.

The data used is a combination of GTFS and OSM data through the R5 engine(Rapid Realistic Routing on Real-world and Reimagined networks). The routing results are intersected with population and POI’s from the GOAT database. R5 is the routing engine for Conveyal, a web-based system that allows users to create transportation scenarios and evaluate them in terms of cumulative opportunities and accessibility indicators. The figure on the below represents the grid interpolation with travel time cost from the R5 engine:

<img src="\images\docs\technical_documentation\isochrone\r5_en.webp" alt="r5 isochrone" style="max-height:350px;"/>

As a result, the grid will include accessibility information for all the amenities for each minute of the travel-time window.

<img src="\images\docs\technical_documentation\isochrone\grid_en.webp" alt="r5 isochrone" style="max-height:150px;"/>

The resolution of the grid cells depends on the Web Mercator zoom levels. Meanwhile, the resolution is a trade-off between performance and accuracy. Different zoom levels are implemented for walking/cycling and public transport. To consider the fact that walking and cycling is requiring analyses focusing on the local level. Generally speaking, higher resolutions are producing high-resolution results but are paired with longer computation times.