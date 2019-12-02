---
title: Technical Architecture
permalink: /docs/technicalarchitecture/
---

#### Structure and Environment

GOAT is a technically spoken a WebGIS-application. The architecture of GOAT involves various software including a number of libraries and programming languages.
The efficient interaction of software in GOAT is made possible by the popular classical server-client architecture of the web. 
Just like many applications today, GOAT has a database that allows efficient storage and organization of information. Information can therefore be accessed, managed and updated appropriately. 
As database PostgreSQL is used and the spatial extension PostGIS. Both together act as core of the application.

<img class="img-responsive" src="../../img/libraries_used.png" alt="mainy open source libraries are used" title="Libraries used">

Additionally, the underlying database allows ,with the help of the extension pgRouting, for routing and calculation of the isochrones. Most spatial operations in GOAT are done in Spatial SQL with the procedural programming language Pl/pgSQL and Python as Pl/Python.
Geoserver is used for sharing geospatial data with the web. The geoserver further communicates directly with the database and serves this data to the web. This is done with the standardized services WFS, WFS-T and WMS. Geoserver runs with Tomcat inside a Docker containers. 
In instances where more customizable interaction with the geospatial data is required, a NodeJS server is used. 

<img class="img-responsive" src="../../img/server_client_architecture.png" alt="Common server Server-Client Architecture" title="Server-Client-Architecture">

In the front-end, data is retrieved by the commonly used webstack (HTML, CSS, JavaScript) with the help of the Openlayers library. 
All software used in GOAT are open source and have a strong worldwide community acceptance and reputation. This setup was initially tested on an Ubuntu Server 18.04 machine but the same could be user on other Linux distros with a few customizations done to its setup.
The development setup is designed with the help of a VM which is controlled by Vagrant, for the purposes of development, testing and local use. This way, GOAT can be installed effortlessly into each and enjoyed on every operating system.


#### Data

GOAT can practically use all sorts of data, however, the current data operation technique focuses on the use of OpenStreetMap (OSM) data. OSM was used as the main source of data since it is the most widely known open geospatial data source. OSM is also a standardized data schema with ubiquitous availability. The automatic setup already supports custom landuse and population data hence other types of data can be effectively inserted into the database.

A combination of SQL and Python scripts are used for the preparation of data. Besides the extraction of POIS, public transport stop and landuse, the setup also allows for disaggregation of population data with the use of administrative, landuse and OSM data. During the disaggregation operation, GOAT can process administrative data in varying resolutions. Generally, the better the OSM building data and the administrative data, the better the result of the disaggregation.
OSM is an open geospatial dataset hence the quality of data and analyses depend on the activity of the local OSM community. Consequently, this allows and invites every person and entity interested in using tools like GOAT to improve the local OSM-data.
