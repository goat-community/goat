---
title: Routing Profiles
permalink: /docs/routing_profiles/
---

Depending on the data precision in the study area and the purpose of the GOAT version, different routing profiles are available. 

TO BE CONTINUED

As GOAT is designed for active mobility, the following OSM road types are exluded from the routing: 
    class_id: 
    0:
    101:
    102:
    103:
    104: trunk
    105: trunk_link
    106: primary
    107: primary_link
    501:
    502:
    503:
    504:
    701: "islands"
    801:

categories_no_foot & categories_no_bicycle: ["use_sidepath","no"]

#### Walking
<b>Standard<b>

Default routing profile for walking, considering all path accessible by foot. 

Default walking speed: 5km/h

<b>Elderly<b>

Same as the standard routing profile, but with a reduced walking speed of 3 km/h. 

<b>Safe-night<b>

The idea behind this routing profile is to model changes in accessibility over time. Some paths, for example through green areas, are pretty attractive during the day, but as soon as the sun goes down and these paths are not illuminated, they become unattractive to the user. With this safe-night routing option, deficiencies in the illuminated path-network can be found and paths that have an important connection function but are not illuminated can be identified.

Therefore, the safe-routing excludes all non-illuminated paths. As there are two options to map the illuminance in OSM (by mapping the street lamps or by assigning the tag "lit" to the road sequence) both have to be considered in order to classify which road segments are illuminated and which are not. First, the way attributes are checked. Since the tag "lit" is not always specified, but the information of the other tags allows conclusions about the lighting situation, the paths are classified according to the following scheme:


<img class="img-responsive" src="../../img/classification_schema_illumination.png" alt="Classification schema illuminance" title="Classification schema illuminance"/> 

This scheme was designed on the basis of usual standards in Germany. As these may be different in other countries, all those conditions can be adjusted in the variable container of the file `goat_config.yaml`. 

After checking the way attributes, a 15m-buffer was created around all mapped street lamps. All streets that intersect with the streetlamp buffer and did not have the tag "lit" assigned, are also classified as lit.

Via the "Illuminance" layer (to be found in the Street Level Quality layers) the lighting conditions of the paths can be displayed. 

This routing profile is only enabled for study areas with very good data about the illuminance. 


#### Cycling
<b>Standard<b>

Default routing profile for walking, considering all path accessible by bike. 

Default cycling speed: 15km/h

Steigungsprofile

<b>Pedelec<b>

Same as the standard routing profile, but with an increased cycling speed of 20 km/h. 

Verändertes Steigungsprofil

#### Wheelchair

Based on the walking routing, but considers only barrier-free paths. 

TO BE CONTINUED