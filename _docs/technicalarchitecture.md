---
title: Technical Architecture
permalink: /docs/technicalarchitecture/
---

#### Structure and Environment

- GOAT is technically spoken a WebGIS-application, accordingly it makes use of diverse software, libraries and programming languages. 
- the classical server-client architecture of web application make this necessary
- the core of the application is an PostgreSQL/PostGIS database, which acts as data store and the place where most of the calculations (especially ressource intensive) are done. 
- the routing and the calculation of the isochrone are done completely on the database
- accordingly most of the spatial operations are done in Spatial SQL, but also with the procedural programming language Pl/pgSQL and Python as Pl/Python

<img class="img-responsive" src="../../img/libraries_used.png" alt="Libraries Used">

- for sharing geospatial data with the web Geoserver is used, geoserver communicates directly with the database and serves this data to the web
- the standardized services WFS and WMS are used for that
- for more customizable interaction with the geospatial data, also a NodeJS server is used
- for the development and also for the production Geoserver and NodeJS run in Docker containers
- in the front-end this data is retrieved by the commonly used webstack (HTML,CSS, Javascript) with the help of the Openlayers library
- all of the software have in common that they are open source and have a strong worldwide community
- the setup is tested on a Ubuntu 18.04 machine, but as all the software is available for other operating systems, with customization in the setup the application can be installed also on other Linux distros, Windows and Mac
- for the development the setup is designed with the help of a VM controlled by Vagrant, accordingly for testing purpose, local use and development GOAT can be installed effortless on every OS

#### Data

- GOAT practically can use all sort of data, however the data prepartion at the moment focuses on the use of OpenStreetMap (OSM) data 
- as most widely known open geospatial data source, standardized data schema and its ubiquitous availability it was decided to use OSM as main data source
- however also other data can be inserted into the database and used for the analysis, the automatic setup already supports custom landuse data and population data 
- for the data preparation a combination of SQL and Python scripts are used
- besides the extraction of POIS, public transport stop and landuse, the setup allows to disaggregate population data with the use of administrative data, landuse data and OSM data
- for this disaggregation GOAT can process administrative data in varying resolution, in general the better the OSM building data and the finer the administrative data the better the result of the disaggregation
- as OSM is an open geospatial dataset the quality of the data and accordingly the analyses depend on the activity of the local OSM community
- however this also allows and invites every person and entity interested in using tools like GOAT to improve the local OSM-data

