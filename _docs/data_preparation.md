---
title: Data Preparation
permalink: /docs/data_preparation/
---


<b>Necessary shapefile<b>

study_area.shp

There is one folder (your-GOAT-directory/app/database/data) in which you can organize the data you want to load into the database. 
The setup-script will search for shapefiles in this directory and upload all of them into your database. The only file that is essential for setting up GOAT is a shapefile defining your study area. Other data is optional, however especially landuse data or custom population data can improve data quality.
As high-resolution population data is one of most important data source for GOAT there are three different ways for you to feed the data into the system. Depending on your data availability you can pick one approach in the `your-GOAT-directory/app/database/goat_config.yaml`.

##### Population disaggregation

<b>Custom data<b>

landuse.shp (optional)

Two SQL-scripts do the job for you:

The script `your-GOAT-directory/app/database/data_preparation/SQL/buildings_residential.sql` will extract all the residential buildings from the planet_osm_polygon-table (this table contains all OSM-polygons in you study area and will be created automatically). As OSM data is of varying quality and tagging-schemes are not always consistent there are several attributes on which this extraction can be done. In addition a custom landuse-table can help to select only residential buildings. You can customize the settings for this extraction in the table variable_container either before the setup (the creation settings of the variable_container can be found in `your-GOAT-directory/app/database/data_preparation/SQL/create_tables.sql`) but also afterwards by directly changing the table variable_container to tune your disaggregation. 

There is a second script `your-GOAT-directory/app/database/data_preparation/SQL/population_disaggregation.sql` actually disaggregates the population data from the boundaries you added with your study_area to the individual buildings. As the population disaggregation is based on OpenStreetMap data, it relies on relatively complete OSM-buildings footprints. In addition, especially in areas with heterogenous building levels it is recommended to check if buildings levels are mapped properly. If there are no buildings levels mapped a default value, which can be defined by you in the database table `variable_container` will be used. 

In general it is highly recommended to check for the data quality in your study area. If you are unhappy with the data quality it is highl recommended to improve the local OSM dataset. Very often with some little mapping effort you can improve data quality essentially. The setup of GOAT allows you to update the data after successful mapping. 


##### Census extrapolation 

<b>Custom data<b>

census.shp

landuse.shp (optional)

In the case you have census data in your study area but you know the data is outdated. GOAT has an script `your-GOAT-directory/app/database/data_preparation/SQL/census.sql` that allows you to update the census grids based on current population numbers in your whole study area. The script checks for areas where new development took place and estimates based on average gross living area how many residents live in the affected grids. You can also customize the same in the `variable_container`. This procedure also makes use of the extracted residential buildings as described in the population dissagregation.

##### Custom high-resolution population data 

<b>Custom data<b>

population.shp

If you have population data as point source you can upload the same into the database.


##### Filename conventions

The automated way the scripts process the data make it necessary that the your custom data is labelled correctly. It is important that the filename and certain attributes are labelled as in the following examples. It is possible to import shapefiles with additional columns however the folowing conventions must be followed.

<img class="img-responsive" src="../../img/shapefile_study_area.png" alt="how your study area shapefile has to be for GOAT" title="Shapefile study area">

<b>Name the file <font color="red">study_area.shp</font> and make sure the columns <font color="red">sum_pop</font> and <font color="red">name</font> are existing!<b>

<img class="img-responsive" src="../../img/shapefile_landuse.png" alt="how your landuse shapefile has to be for GOAT" title="Shapefile landuse">

<b>Name the file <font color="red">landuse.shp</font> and make sure the column <font color="red">landuse</font> is existing!<b>

<img class="img-responsive" src="../../img/shapefile_census.png" alt="how your census shapefile has to be for GOAT" title="Shapefile census">

<b>Name the file <font color="red">census.shp</font> and make sure the column <font color="red">pop</font> is existing!<b>

<img class="img-responsive" src="../../img/shapefile_population.png" alt="how your population shapefile has to be for GOAT" title="Shapefile population">

<b>Name the file <font color="red">population.shp</font> and make sure the column <font color="red">population</font> is existing!<b>


You can furthermore permanently upload additional data into your database with the command-line tools shp2pgsql or others.

