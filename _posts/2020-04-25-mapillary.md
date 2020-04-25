---
layout: post
title:  "Covering Fürstenfeldbruck with Mapillary"
author: Santiago German Linares Ramirez
---

Data, Data and more Data! While working in the [mFund project](https://www.bmvi.de/SharedDocs/DE/Artikel/DG/mfund-projekte/GOAT.html) to bring GOAT’s feature to the municipality Fürstenfeldbruck, we have been looking for available information from many sources to accomplish the objectives. As always, OpenStreetMap has been a great source of information, but still a lot of details are missing. Here comes Mapillary, the easy way to describe it is “the Google Street View of open source”. People from all over the world have captured imagery from their cars, bikes or just by walking millions of kilometers of city streets, roads, pedestrian and bicycle-paths to have an up-to-date source of what is going on in the streets. But that is not everything, Mapillary’s magic is in their machine-generated map feature, so they can automatically detect different objects from the images (traffic signs, fire hydrant, lane markings, bicycle racks, etc.) and estimate their position on the map. Since in Fürstenfeldbruck only few parts of the road network were captured beforehand, we decided to go outside and take the pictures ourselves. This screenshot shows our coverage: 

<img class="img-responsive" src="../../../../../img/mapillary_ffb.png" alt="Fürstenfeldbruck Area and pictured links" title="Fürstenfeldbruck Area and pictured links"/>  
<i> Figure 1. Fürstenfeldbruck Area and pictured links</i>

To learn how to work with Mapillary, we made some tests in Munich before going to Fürstenfeldbruck. During the test, we tried different kinds of cameras, holding devices to attach the phone/GoPro to the bicycle, settings for recording and different features from the app. Challenging is especially the high battery consumption and the high memory requirements for storing all images. The best set-up proved to be a GoPro for the pictures connected to a mobile phone for recording the GPS track and orientation (north - south), additionally equipped with a power bank.

<img class="img-responsive" src="../../../../../img/mapillary_bike.jpg" alt="Bicycle with the GoPro in the S-Bahn on our way to Fürstenfeldbruck" title="Bicycle with the GoPro in the S-Bahn on our way to Fürstenfeldbruck"/>  
<i>Figure 2. Bicycle with the GoPro in the S-Bahn on our way to Fürstenfeldbruck</i>

So far, within the area, we have pictured 210 km in 8 days. Compared with the working time considered in the planning stage (5 days for 240 km), the real working time was around 2:30 hours per day (limited through the duration of the battery) and the average cycling speed is about 10 km/h because it is necessary to cross the same streets several times. There are very few areas and footpaths remaining but most of the streets are now covered. To face lower picture rate, we organized a group day where 4 members from the GOAT community went together to picture nearby villages. To organize this task, Mapillary has a feature called "Capture projects". With this feature, the user defines the general area that he wants to cover as a shape, in our case Fürstenfeldbruck. Then, the shape is divided in subareas, each of them are called tasks and are assigned to the “drivers” that are members of the group (Figure 3). Before we went to the city, everybody downloaded an app called "Mapillary Driver", here each of the drivers can see to which area they are assigned and for which streets pictures are missing, in that way it is very easy to complete all the tasks. 

<img class="img-responsive" src="../../../../../img/mapillary_tasks.png" alt="Fürstenfeldbruck area divided by tasks and the assignment to each driver" title="Fürstenfeldbruck area divided by tasks and the assignment to each driver"/>   
<i>Figure 3. Fürstenfeldbruck area divided by tasks and the assignment to each driver</i>

By doing this fieldwork, we are providing and improving the data available to develop GOAT’s features in Fürstenfeldbruck, but at the same time we are very happy to share the data with everybody out there. The information provided by the pictures and the machine-generation tools from Mapillary help to develop the data for better calculations. And the possibility to see up-to-date images makes it easy to remotely analyze the street. 

 <p align="left">
<div class="embed-responsive embed-responsive-16by9">
  <iframe class="embed-responsive-item" src="https://player.vimeo.com/video/411741106?texttrack=en&autoplay=1&loop=1&autopause=0" allow="autoplay; fullscreen" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>
</div>
</p>
<i>Figure 4. The Mapillary images can be viewed directly in GOAT now</i>

This allows to verify details such as the quality of sidewalks or cycle paths; land use, as the pictures below where it is possible to identify residential areas with 30 zone or calmed roads, commercial areas to analyze parking distribution or footpaths and the quality of the road surface; schools, health buildings, points of interest and even possibility to find bicycle racks.

<img class="img-responsive" src="../../../../../img/mapillary_sequences.png" alt="Captured sequences" title="Captured sequences"/>   
<i>Figure 5. Captured sequences within different landuse areas</i>

Mapillary data was used to improve the quality of OpenStreetMap data. Like shown in the picture below Mapillary photos can easily and directly be used when editing in OSM. The taken photos in Fürstenfeldbruck area are showed as green dots. 

<img class="img-responsive" src="../../../../../img/mapillary_osm.png" alt="Using Mapillary pictures to improve OSM data" title="Using Mapillary pictures to improve OSM data"/>   
<i>Figure 6. Using Mapillary pictures to improve OSM data</i>

We used the data so far mainly to complete the attributes of the street network in OpenStreetMap. Based on the Mapillary photos many relevant attributes could be collected that are important to provide a more realistic cycling routing. As an example, it is possible to identify the type of surface (paved, unpaved, asphalt, concrete, paving stones, …) or smoothness (excellent, good, intermediate, bad, ...) of a road or path. It is also possible to identify if a road is designed for bicycles and pedestrians and much more... 

We will keep on collected more imagery and fine tune our used methodology to build better map data for all!

