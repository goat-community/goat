---
title: How to make changes in OSM?
permalink: /docs/osm_tutorial/
---


GOAT<sub>beta</sub> works with OSM data. This means that if the OSM data is faulty, your model will also be faulty. If data errors are found in the model, it is best to clean them up directly in OSM. For most cities OSM data is quite good, but in some places many adjustments are necessary.


#### 1. Visit OpenStreetMap

Visit OpenStreetMap: [https://www.openstreetmap.org/](https://www.openstreetmap.org/)

And log in / create an account. 

<img class="img-responsive" src="../../img/OSM_log_in.png" alt="log in to OSM" title="Log in to OSM">


#### 2. Activate edit mode 

Press the "Edit" button to start editing.

<img class="img-responsive" src="../../img/OSM_start_editing.png" alt="start editing in OSM" title="Start editing in OSM">


#### 3. Familiarize with the OSM structure

Zoom in and click on a object. Every object has features (e.g. a building consists of a building type, number of levels, height and address; also further information such as architect and wheelchair access can be inserted), some specific features are defined as <b>tags</b>. A tag consists of a key (e.g. building type) and a value (e.g. residential), means <i>building type = residential</i>. 
 
These tags are very usefull for planners like us as we can filter by different building types, e.g. select all buildings that are residential. 

Before starting with editing it makes sense to familiarize onself with the provided tags and keys. Therefore OSM wiki is a good source: 

[https://wiki.openstreetmap.org/wiki/Map_Features](https://wiki.openstreetmap.org/wiki/Map_Features)


#### 4. Adjust existing objects

Select the object you want to adjust (e.g. building, street, POI). To add a tag, press the "+" button, select the desired key and choose the correct value from the drop-down list or type it manually. If the key already exists but is associated with a wrong value, you can easily adjust it by selecting the right one. 

<img class="img-responsive" src="../../img/OSM_tags.png" alt="OSM tags" title="Specific features are defined via tags">

If the spatial extent of an object is incorrect, you can move the nodes to the correct position by clicking and dragging.

<font color="red">INSERT VIDEO?</font>


#### 5. Add new objects

Zoom to the position of the new object and select in the header which object type you want to add (point, line or area). Place the new nodes with a single left click and end the input with a double left click. Right-clicking offers some options for adjusting the objects (e.g. square the corners of the area). On the left, you can now select the object type and insert features and keys. 

<video  width="750" height="420" controls>
<source src="../../img/OSM_add_building.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>


#### 6. Save the changes

After making changes it is important to save them by clicking on "save" in the header. You can add a comment to your changeset and check "I would like someone to review my edits" if you're not sure that you've done everything correctly. 

<video  width="750" height="420" controls>
<source src="../../img/OSM_save_changes.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>