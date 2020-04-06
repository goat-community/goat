---
title: Making changes in OSM
permalink: /docs/osm_tutorial/
---


GOAT works with OSM data. This means that if the OSM data is faulty, your model will also be faulty. If data errors are found in the model, it is best to clean them up directly in OSM. For most cities OSM data is quite good, but in some places many adjustments are necessary.

There are many different ways to edit OSM data. You can do the editing directly in the browser, e.g. with the embedded iD editor, or use external editor tools like [JOSM](https://josm.openstreetmap.de/). This documentation shows the basic steps of editing OSM data with the iD Editor. 


#### 1. Visit OpenStreetMap

Visit OpenStreetMap: [https://www.openstreetmap.org/](https://www.openstreetmap.org/)

And log in / create an account. 

<img class="img-responsive" src="../../img/OSM_log_in.png" alt="log in to OSM" title="Log in to OSM">


#### 2. Activate edit mode 

Press the "Edit" button to start editing.

<img class="img-responsive" src="../../img/OSM_start_editing.png" alt="start editing in OSM" title="Start editing in OSM">


#### 3. Familiarize with the OSM structure

Zoom in and click on an object. Every object has features (e.g. a building consists of a building type, number of levels, height and address; also further information such as architect and wheelchair access can be inserted), some specific features are defined as <b>tags</b>. A tag consists of a key (e.g. building type) and a value (e.g. residential), means <i>building type = residential</i>. 
 
By using these tags semantical-rich data is produced which is of special value for planners. As it allows for the analysis of different functions in space e.g. select all buildings that are residential.

Before starting with editing it makes sense to familiarize yourself with the provided tags and keys. Therefore the OSM wiki is a very important reference:

[https://wiki.openstreetmap.org/wiki/Map_Features](https://wiki.openstreetmap.org/wiki/Map_Features)


#### 4. Adjust existing objects

Select the object you want to adjust (e.g. building, street, POI). To add a tag, press the "+" button, select the desired key and choose the correct value from the drop-down list or type it manually. If the key already exists but is associated with a wrong value, you can easily adjust it by selecting the right one. 

<img class="img-responsive" src="../../img/OSM_tags.png" alt="OSM tags" title="Specific features are defined via tags">

If the spatial extent of an object is incorrect, you can move the nodes to the correct position by clicking and dragging.


#### 5. Add new objects

Zoom to the position of the new object and select in the header which object type you want to add (point, line or area). Place the new nodes with a single left click and end the input with a double left click. Right-clicking offers some options for adjusting the objects (e.g. square the corners of the area). On the left, you can now select the object type and insert features and keys. 

<p align="left">
<div class="embed-responsive embed-responsive-16by9">
  <iframe class="embed-responsive-item" src="https://player.vimeo.com/video/333129999" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>
</div>
</p>


#### 6. Save the changes

After making changes it is important to save them by clicking on "save" in the header. You can add a comment to your changeset and check "I would like someone to review my edits" if you're not sure that you've done everything correctly. 

<p align="left">
<div class="embed-responsive embed-responsive-16by9">
  <iframe class="embed-responsive-item" src="https://player.vimeo.com/video/333130694" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>
</div>
</p>

For a more detailed tutorial see here: [https://learnosm.org/en/](https://learnosm.org/en/)

#### Possibilities for groups

<b>MapRoulette<b>

[MapRoulette](https://maproulette.org/) is an online platform or tool that can be used to create mapping-related tasks in Open Street Map. It is also directly linked to OSM or its editor and everyone with an Open Street Map account also has access to these challenges. On MapRoulette, tasks exist worldwide from simple ones like adding a property to something more complex as in this work like checking and drawing buildings for residential areas. 
<td> <img class="img-responsive" src="../../img/Maproulette.JPG" title="Sample task in MapRoulette"> </td>
The challenges are primarily aimed at local processors who have better knowledge or access to the data. However, everyone can often help, by means of aerial photos. For the fulfillment of the tasks, points can be collected which can be compared with others. For example, tasks can be created with an Overpass Turbo query. E.g. all residential areas in Matosinhos:
<td> <img class="img-responsive" src="../../img/Overpass.JPG" title="Example query in Overpass-Turbo"> </td>

<b>Mapping Party<b>

Another sociable method is to map in a group, often referred to as a "mapping party". With this one either undertakes a common tour through the area to be recorded in order to collect GPS data or one meets at a suitable location and records the data with the help of the abovementioned methods. Since mapping can be a bit monotonous in the long run, it is much more entertaining in a group, especially with snacks and drinks. Ideally, everyone should have an OSM account and their own computer or laptop. To prevent several people working on the same area, [MapRoulette](https://maproulette.org/), for example, can be used for better coordination.