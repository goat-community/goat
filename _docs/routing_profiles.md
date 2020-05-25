---
title: Routing Profiles
permalink: /docs/routing_profiles/
---

As GOAT is designed for active mobility, roads that are only designed for cars (e.g. highways) are exluded from the routing. Depending on the data precision in the study area and the purpose of the GOAT version, different routing profiles are available. 

When setting up your own GOAT version, the available routing profiles and according default speeds can be adjusted in the `app-config.json` file.

#### Walking
<b>Standard<b>

Default routing profile for walking, considering all path accessible by foot. 

Default walking speed: 5km/h 

<b>Elderly<b>

Same as the standard routing profile, but with a reduced walking speed of 3 km/h. 

<b>Safe-night<b>

The safe-routing excludes all non-illuminated paths. The idea behind this routing profile is to model changes in accessibility over time. Some paths, for example through green areas, are pretty attractive during the day, but as soon as the sun goes down and these paths are not illuminated, they become unattractive to the user. With this safe-night routing option, deficiencies in the illuminated path-network can be found and paths that have an important connection function but are not illuminated can be identified.

As there are two options to map the illuminance in OSM (by mapping the street lamps or by assigning the tag "lit" to the road sequence) both have to be considered in order to classify which road segments are illuminated and which are not. First, the way attributes are checked. Since the tag "lit" is not always specified, but the information of the other tags allows conclusions about the lighting situation, the paths are classified according to the following scheme:


<img class="img-responsive" src="../../img/classification_schema_illumination.png" alt="Classification schema illuminance" title="Classification schema illuminance"/> 

This scheme was designed on the basis of usual standards in Germany. As these may be different in other countries, all those conditions can be adjusted in the variable container of the file `goat_config.yaml`. 

After checking the way attributes, a 15m-buffer was created around all mapped street lamps. All streets that intersect with the streetlamp buffer and did not have the tag "lit" assigned, are also classified as lit.

Via the layer "Illuminance" (to be found in the Street Level Quality layers), the lighting conditions of the paths can be displayed. 

This routing profile is only enabled for study areas with very good data about the illuminance. 


#### Cycling
<b>Standard<b>

Default routing profile for cycling, considering all path accessible by bicycle. 

Default cycling speed: 15km/h

Depending on the surface, smoothness and slope of the different street segments, the cycling speed is adjusted accordlingly. The  impedance factors used for this are defined in the file `goat_config.yaml`.

<b>Pedelec<b>

Same as the standard routing profile, but with an increased cycling speed of 23 km/h. 

For Pedelecs, slopes are considered with a lower impedance than for Standard bicyles. 

#### Wheelchair

The wheelchair-routing is based on the walking routing, but considers only barrier-free paths. Stairs, unpaved paths and paths with high slopes are excluded from the routing.

Via the layer "Wheelchair Usability" (to be found in the Street Level Quality layers), the conditions regarding the freedom from barriers of the paths can be displayed. 

This routing profile helps to find deficits in the barrier-free network of a city. In view of demographic change, freedom from barriers is becoming increasingly important. In addition, a high percentage of the population is temporarily mobility impaired (e.g. by pushing a baby carriage or carrying heavy luggage). All these people and needs must be taken into account when planning infrastructure for active mobility. 

