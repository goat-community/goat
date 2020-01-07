---
title: Population Extrapolation
permalink: /docs/population/
---

#### Residential buildings

Script: `your-GOAT-directory/app/data_preparation/SQL/buildings_residential.sql`

This script identifies all residential buildings at a specified location based on land use data and buildings data. Attributes of the buildings are additionally used. However, as always the accuracy depends largely on the data quality of your custom and OSM data.

The scripts allows you to customize the filters that identify residential buildings. The default values are customized to the City of Munich, therefore it is important to double-check them if you are in another context. The following filters can be adjusted in the `goat-config.yaml`:

- <b>custom_landuse_no_residents</b>: if you have a custom landuse-layer you can define landuse categories that are not residential
- <b>osm_landuse_no_residents</b>: <i>osm-tag landuse</i> that is not for residents, this filter is combined in case you have custom landuse data
- <b>building_types_potentially_residential</b>: <i>osm-tag building</i> that should not be excluded – <font color="red">Note: many buildings are just called building=yes</font>
- <b>building_types_residential</b>: <i>osm-tag building</i> that are for sure residential e.g. building=residential (to know more about the building types visit [https://wiki.openstreetmap.org/wiki/Key:building](https://wiki.openstreetmap.org/wiki/Key:building))
- <b>tourism_no_residents</b>: <i>osm-tag tourism</i> that has no residents (to know more about the key tourism visit [https://wiki.openstreetmap.org/wiki/Tourism](https://wiki.openstreetmap.org/wiki/Tourism) )
- <b>amenity_no_residents</b>: <i>osm-tag amenity</i> that has no residents (to know more about the amenities visit [https://wiki.openstreetmap.org/wiki/Key:amenity](https://wiki.openstreetmap.org/wiki/Key:amenity))
- <b>minimum_building_size_residential</b>: all buildings that have a smaller size than this are excluded (very often garages etc.)

the script furthermore extracts building levels for the residential buildings, in case no building levels are in the osm-attributes (unfortunately this is usually the case) a default value for the building levels can be adjusted in the `goat-config.yaml`.

<span style="color:red">Note: these building levels are used for the census extrapolation or the population disaggregation.</span>

The output of this function is a table called <span style="color:blue">buildings_residential</span>. It should contain only residential buildings. But as always the accuracy very much depends on the data quality.
<td> <img class="img-responsive" src="../../img/buildings_residential.png" title="Residential buildings"> </td>

The script buildings_residential.sql is the basis for the census extrapolation. 

#### Census extrapolation
<b>Custom data<b>

census.shp

landuse.shp (optional)

fixed_population.shp (optional)

Script: `your-GOAT-directory/app/data_preparation/SQL/census.sql`

In the case you have census data in your study area but you know the data is outdated. GOAT has an script `your-GOAT-directory/app/data_preparation/SQL/census.sql` that allows you to update the census grids based on current population numbers in your whole study area, which you provided in the layer-table `study_area`. A prerequisite is that your population numbers for your `study_area` are more recent, than your census data. Currently the script does only work if the population numbers have increased in the timespan that is lying between the reference year of the census data and the reference year of the administrative boundaries of your `study_area`. 

The script checks for areas where new development took place and estimates based on average gross living area how many residents live in the affected grids. The same can be customized in the `goat-config.yaml`. This procedure also makes use of the extracted residential buildings as described in `your-GOAT-directory\app\data_preparation\SQL\buildings_residential.sql`

This script is designed in a way that allows to iteratively improve the results. It is recommended to simply run the setup of GOAT and check for the quality of the population data. There will be following tables if the script was running successfully: 

<b><span style="color:red">buildings_to_map</span>: all buildings of <font color="blue">buildings_residential</font> that are located within a grid cell in which no population from the census is documented.<b> 

This means that the scripts assumes that these buildings were built after the census and should be reviewed if they are mapped correctly. The building type, building levels and land use of the area are of particular importance. It is recommended to map this information directly in the OSM database (See [making changes in OSM](/docs/osm_tutorial/)). When updating GOAT you can get your most recent changes in OpenStreetMap. 

<b><span style="color:brown">census_split_new_development</span>: all grid cells where new residential development took place.<b>

The script is following simplistic rules and assigns new population to places based on the building volume (area x number of floors) it happens that there are assign very high population numbers to big buildings. Often this is correct, however in case of e.g. Villas in the forest this could be wrong. Therefore, you have the possibility to upload a layer where you are able to fix the population numbers for certain buildings. You can simply create a shapefile with the structure of `your-GOAT-directory/app/database/data/fixed_populatipon.shp` mentioned in [Data Preparation](https://www.open-accessibility.org/docs/data_preparation/).
The result of the this process is an updated census grid that is used for further processing. 

<b><span style="color:green">population</span>: the population numbers from the updated census grids is distributed to the associated buildings based on there build-up area, if a building has several addresses the population is equally split between the addresses.<b> 

Currently in this step that involves all buildings the number of building levels is not included as this information is very often not available for all buildings, however in case of small population grid (e.g. Germany 100mx100m) it can be assumed that the buildings in one grid cell have a very similiar number of levels.
For grid cells for which no population was recorded in the census, the additional population moved between the census and now into the `study_area` (calculated from the difference between the census data and the up to date population data stored in the table `study_area`), is distributed proportionally among all new residential building units. Negative population data means there is no population ascertained in this building. 


This script delivers the following output:
<td> <img class="img-responsive" src="../../img/census.png" title="Output of the script"> </td>