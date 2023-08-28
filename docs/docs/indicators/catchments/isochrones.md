---
sidebar_position: 2
---

# Single-Isochrones

Single-Isochrones are **catchment areas** that are **calculated on the real transport network**. This accessibility indicator shows how far a person can travel from a selected starting point within a given travel time.

## 1. Explanation

**Single-Isochrones** show how far a person can travel from a selected starting point within a given travel time. In contrary to the [buffer](buffer/), which creates a straight line circle, the isochrone calculation routes on the real transport network. Therefor, the user can select the ``routing mode`` (_Walking_, _Bike_, _Pedelec_, _Transit_ or _Car_). 

Isochrones can be used as an **accessibility indicator** in one specific location. The isochrone area gives insights into the network connectivity. Furthermore, the isochrone can be intersected with further spatial data sets, such as population and POI data. Therewith it can be assessed how many people or POIs can be reached from a certain starting point.  



**TODO: insert image of isochrone**



:::tip Tip

Want to perform isochrones from multiple starting points? See [Multi-Isochrones](multi-isochrones/).

:::




## 2. Which planning questions can be answered? 

Among others, isochrones can be used to answer the following planning questions:

* How many supermarkets can be reached from a certain point in a 10-minute walk?
* How many people can access a public transport station within 5 minutes of cycling?
* How many people can reach a specific location within 20 minutes by public transport?
* How big is the catchment area of a school by car vs. by public transport? How many students live within these catchment areas? 

## 3. How to use the indicator?

### Video Tutorial
<iframe class="embed-responsive-item" src="https://player.vimeo.com/video/754209613" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen data-uk-responsive width="700" height="400"></iframe>

### Step-by-step guideline

1. Pick for which ``routing`` mode you would like to calculate an isochrone. 

TODO: Insert Swizzle (Walking, Cycling/Pedelec, Public Transport, Car)

#### Walking

Considering all paths accessible by foot.

Default walking speed: 5km/h

<img src="https://plan4better.de/images/docs/technical_documentation/isochrone/walking_en.webp" width="1000px" alt="isochrone walking settings" style={{width: "1000px", height: "150px", maxHeight: "100px", maxWidth: "300px", objectFit: "contain"}}/> 

Further information: **TODO: add link to routing/walking**

#### Cycling Standard

Considering all paths accessible by bicycle.

Default cycling speed: 15km/h Depending on the surface, smoothness and slope of the different street segments, the cycling speed is adjusted accordingly (further information >> **TODO: add paper link**).

<img src="https://plan4better.de/images/docs/technical_documentation/isochrone/standard_en.webp" width="1000px" alt="isochrone cycling settings" style={{width: "300px", height: "150px", maxHeight: "100px", maxWidth: "300px", objectFit: "contain"}}/> 

#### Pedelec

Same as the cycling standard profile, but with an increased cycling speed of 23 km/h.
For Pedelecs, slopes are considered with a lower impedance than for standard bicycles.

<img src="https://plan4better.de/images/docs/technical_documentation/isochrone/pedelec_en.webp" width="1000px" alt="isochrone pedelec settings" style={{width: "1000px", height: "150px", maxHeight: "100px", maxWidth: "300px", objectFit: "contain"}}/> 

Further information: **TODO: add link to routing/cycling**


#### Transit

In this routing mode, users can compute intermodal accessibility centered around public transport. The following settings can be adjusted:

-	The ``weekday`` (Monday to Sunday)
-	Time period (``from time`` and ``to time``) (0h to 24h)
-	``Access Mode`` (How the user accesses the station, e.g., Walk, Bicycle),
-	``Egress Mode`` (How the user exists the station e.g., Walk, Bicycle) 
-	``Transit Modes`` (Bus, Tram, Metro and/or Rail).

<img src="https://plan4better.de/images/docs/technical_documentation/isochrone/transit_en.webp" width="1000px" alt="isochrone transit settings" style={{width: "1000px", height: "350px", maxHeight: "350px", maxWidth: "300px", objectFit: "contain"}}/> 

Further information: **TODO: add link to routing/transit**

#### Car
TODO

Further information: **TODO: add link to routing/transit**

--- end of swizzle --- 

1. Place the ``starting point`` on the map. 

<img src="/img/docs/indicators/catchments/Isochrone/original_files/starting_point.png" width="1000px" alt="isochrone starting point" style={{width: "1000px", height: "250px", maxHeight: "10px", maxWidth: "100px", objectFit: "cover"}}/> 

TODO: check image

3. ... to be continued ... 

4. result table .. 

5. intersect isochrone with POI data ... 



#### 1 Walking accessibility to supermarkets

##### 1.1 Planning question

How many supermarkets can be reached from a certain point in 10 minutes walking?

##### 1.2 Step-by-Step guide

1. Display all supermarkets by enabling the amenity "Supermarket" in the Thematic Data Filter under the category "Shop".

[comment]:<img src="/images/tutorials/Isochrone/amenity_supermarket_en.webp" alt="amenity supermarket" style="max-height:400px;"/>

2. Zoom in into the area where you want to calculate the isochrone.

3. Select the the routing profile and the desired walking speed.

[comment]:<img src="/images/tutorials/Isochrone/Isochrone_1.2_select_eng.webp"  alt="choose isochrone range" style="max-height:175px;"/>

4. Place the starting point for the isochrone.

[comment]:<img src="/images/tutorials/Isochrone/starting_point_isochrone_en.webp"  alt="set starting point" style="max-height:150px;"/>

5. After the calculation has been carried out, a window with the results opens automatically. From this window you can see the number of supermarkets that can be reached within 10 minutes.

[comment]:<img src="/images/tutorials/Isochrone/results_supermarkets_en.webp"  alt="results"/>

6.	 In the result window that opens, the results can be analyzed by the use of different graphs. Therewith it can be seen how the supermarkets are spacial distributed. 

[comment]:<img src="/images/tutorials/Isochrone/results_supermarkets_2_en.webp"  alt="results"/>

#### 2 Accessibility by bike

##### 2.1 Planning question

How many people can reach the train station within 5 minutes by bike?

##### 2.2 Step-by-Step guide

1. Change the routing mode to "cycling" and choose the desired speed.
   
[comment]:<img src="/images/tutorials/Isochrone/Isochrone_2.2_select_eng.webp"  alt="Routing mode cycling" style="max-height:220px;"/>

2. Place the starting point for the isochrone calculation on the station.

[comment]:<img src="/images/tutorials/Isochrone/starting_point_isochrone_en.webp"  alt="set starting point" style="max-height:150px;"/>

3. After the calculation has been carried out, a window with the results opens automatically. From this window you can see the population that can reach the train station within 10 minutes of cycling.

[comment]:<img src="/images/tutorials/Isochrone/Isochrone_2.3_10minutes_eng.webp"  alt="result"/>

4. The travel time can interactively be adjusted to 5 minutes by moving the slider. 
   
[comment]:<img src="/images/tutorials/Isochrone/Isochrone_2.3_5minutes_eng.webp"  alt="result"/>

5. Besides the table, the population count can be visualized in a graph.

[comment]:<img src="/images/tutorials/Isochrone/Isochrone_2.result_different_graph_Eng.webp"  alt="download" style="max-height:300px;"/>

6. By clicking on the download button you can download the isochrones as GeoJSON, Shapefile or XML and the result table as Excel file.

[comment]:<img src="/images/tutorials/Isochrone/Isochrone_2.4_export_eng.webp"  alt="download" style="max-height:230px;"/>


#### 3 Accessibility by public transport

##### 3.1 Planning question

How many people can access a specific location within 20min by rail-based public transport (tram, underground, train)?

##### 3.2 Step-by-Step guide

1. Set the routing mode to “Transit” and choose the calculation options (weekday, time, access mode and egress mode) as desired. In the “Transit Modes” section, you can select which public transportation options shall be considered for the calculation. In this example, we focus on rail-based public transport (tram, underground and train). To get some additional information on the public transport network, you can activate the public transport background map. 

[comment]:<img src="/images/tutorials/Isochrone/isochrone_3.1public_en.webp"  alt="change_routing_mode" style="max-height:400px;"/>

2. Click "Isochrone Single" and zoom in the area where you want to calculate the isochrone.

[comment]:<img src="/images/tutorials/Isochrone/isochrone_3.2public_en.webp"  alt="choose isochrone" style="max-height:400px;"/>

3. Place the starting point for the isochrone.

[comment]:<img src="/images/tutorials/Isochrone/isochrone_3.3public_en.webp"  alt="choose starting point" style="max-height:400px;"/>

4. After the calculation has been carried out, a window with the results opens automatically. From this window you can see how many people can access a specific location within 20min by rail-based public transport. You can also change the travel time by using the slider.

[comment]:<img src="/images/tutorials/Isochrone/isochrone_3.4public_en.webp"  alt="result" style="max-height:400px;"/>

5. You can also view the population graph with travel time by clicking the graph button indicated by the blue box.

[comment]:<img src="/images/tutorials/Isochrone/isochrone_3.5public_en.webp"  alt="result-graph" style="max-height:400px;"/>


## 4. Technical details

Isochrones are isolines connecting all points that can be reached from a specific starting point within a certain time interval. Depending on the chosen travel mode, the according transport networks are used for the [routing > TODO: Insert Link](/../routing).

The isochrone shapes are dynamically created in the front end based on a travel time grid. Therefore, isochrones can be created fast and for different intervals on the fly.

### Visualization 

The isochrone shape is derived from the routing grid using the [Marching square contour line algorithm](https://en.wikipedia.org/wiki/Marching_squares "Wikipedia: Marching Squares"), a computer graphics algorithm that can generate two-dimensional contour lines from a rectangular array of values ([de Queiroz Neto et al. 2016](isochrones#6-resources)). This algorithm transforms the grid from a 2D array to a shape to visualize or analyzed. An illustration of 2D image processing is shown in the figure. 

<img src="https://plan4better.de/images/docs/technical_documentation/isochrone/wiki.webp" width="1000px" alt="marching square" style={{width: "1000px", height: "400px", maxHeight: "400px", maxWidth: "400px", objectFit: "contain"}}/> 

## 5. Further readings

(Links to tutorials)  
Links to videos  
Related docs  

If you want to learn more detailed examples of how the isochrone can be used within GOAT, you can access [the tutorials](../../tutorials/isochrone/) and [video sections](../../videos/) on the website.

## 6. Resources

J. F. de Queiroz Neto, E. M. d. Santos, and C. A. Vidal. “MSKDE - Using
Marching Squares to Quickly Make High Quality Crime Hotspot Maps”. en.
In: 2016 29th SIBGRAPI Conference on Graphics, Patterns and Images (SIBGRAPI).
Sao Paulo, Brazil: IEEE, Oct. 2016, pp. 305–312. isbn: 978-1-5090-3568-7. doi:
10.1109/SIBGRAPI.2016.049. url: https://ieeexplore.ieee.org/document/
7813048/

https://fr.wikipedia.org/wiki/Marching_squares#/media/Fichier:Marching_Squares_Isoline.svg

Majk Shkurti, "Spatio-temporal public transport accessibility analysis and benchmarking in an interactive WebGIS", Sep 2022. url: https://www.researchgate.net/publication/365790691_Spatio-temporal_public_transport_accessibility_analysis_and_benchmarking_in_an_interactive_WebGIS

Matthew Wigginton Conway,Andrew Byrd,Marco Van Der Linden. "Evidence-Based Transit and Land Use Sketch Planning Using Interactive Accessibility Methods on Combined Schedule and Headway-Based Networks", 2017. url: https://journals.sagepub.com/doi/10.3141/2653-06

