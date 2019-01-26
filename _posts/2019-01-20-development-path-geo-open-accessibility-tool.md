---
layout: post
title:  "Development path of Geo Open Accessibility Tool(GOAT)"
author: Elias Pajares
---


I am happy to let you know that Geo Open Accessibility Tool (GOAT) is by far where want it to be as highlighted in my other previous post. Apart from the on-going professionalization which are seen as crucial to provide a truly useful and stable accessibility instrument, additional features will be implemented on a regular basis.
The main objective we have been focusing on in the past months was making the interactive network modification and the user interface better. We spared very little time for coming up with new features. However, there are some new envisioned and edge cutting features which will bring GOAT to the status where the first version (GOAT 1.0) will be released. 

So far, GOAT is still very much a personal project as funding for this first stable release has not been secured yet. Consequently, time for the first ground-breaking release of GOAT for production purposes remains undefined. Our current estimated time for the full development of this tool is between 1-2 years. Nonetheless I feel it’s important to communicate the potential features that GOAT will have in future and further show direction which this tool will take. In the course of development, some GOAT features will be added and others probably removed. 
GOAT is an open source project and therefore targets a very strong interaction with its users. To this end, I am very open to ideas and suggestions from the community at large. Just get in touch!

<table class="table table-striped table-hover ">
  <thead>
    <tr>
      <th>Feature</th>
      <th>Description</th>
      <th>Time horizon</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Routing performance</td>
      <td>The pgRouting library shines with its flexibility, however this comes with 
      the cost of relatively long query times for the calculation of the shortest path and the isochrones. New features such as multi-isochrones rely on a more efficient calculations. Although pgRouting is not tuned per default for high-performance, with good network preparation and improved SQL-queries the performance can increased substantially. It will also be checked if database clusters or the calculation on multiple cores can improve the performance.</td>
      <td>>At the moment it is already worked on improving the performance, however with cycling as new mode and the implementation of new accessibility indicators, this will be an ongoing challenge.</td>
    </tr>
    <tr>
      <td>Column content</td>
      <td>Column content</td>
      <td>Column content</td>
    </tr>
    <tr class="info">
      <td>Column content</td>
      <td>Column content</td>
      <td>Column content</td>
    </tr>
    <tr class="success">
      <td>Column content</td>
      <td>Column content</td>
      <td>Column content</td>
    </tr>
    <tr class="danger">
      <td>Column content</td>
      <td>Column content</td>
      <td>Column content</td>
    </tr>
    <tr class="warning">
      <td>Column content</td>
      <td>Column content</td>
      <td>Column content</td>
    </tr>
    <tr class="active">
      <td>Column content</td>
      <td>Column content</td>
      <td>Column content</td>
    </tr>
  </tbody>
</table>

(There will be a table with the new possible features here)
Our goal is to make GOAT the most user friendly tool for accessibility planning thus major improvements in performance, accuracy and data quality are highly targeted. The focus is on improved data fusion concepts and stronger engagement in the OpenStreetMap (OSM) community.
For those who have tested GOAT, you might have realized that the demo app is only available for the city of Munich currently. This is because our institution (TUM) is located in Munich. This is also where I began the development of this tool. In future, this tool will be expanded to other German municipalities and the world. 

As much as GOAT allows its setup to be installed on its own server by anybody, many still want to be able to use GOAT immediately especially on their areas of study.  The reason for not extending coverage to other fields of study is related to the claims I have on the extent of data quality and the resources available at my disposal for additional server space. From my perspective cross-checks, OpenStreetMap data can be of varying quality especially when used in a production environment with other data sources or where local knowledge is necessary. Activity in the local OSM community is also essential.

To this date, I can only be in a position to provide the services of GOAT within the boundaries of the city of Munich. However, in the coming months I can think of extending this to some other counties in the metropolitan regions of Munich. This is exclusive of new locations. 
I would also be very open to launch GOAT in other cities worldwide as an initiative to foster meaningful cooperation with others. If you miss GOAT in your city and you are interested in becoming part of the community just get in touch and we could develop strategies to make this possible!


- As highlighted in my previous post GOAT is by far not where we want to be
- besides an ongoing professionalization which is targeted to the overall project, new features are planned and will be implemented constantly
- the focus the months before this release, was mainly on improving the interactive network modification and the userinterface
- however there was little time invested in completely new features
- but there are envisioned edgecutting new features for GOAT, which shall bring GOAT to the status that GOAT 1.0 can be released 
- as funding for this first stable release is not secured and GOAT so far is still very much a personal project it is still undefined when this groundbreaking first release for production will be finished
- at the moment it is estimated that the needed development will need between one and two years
- I however see it as important to already communicate the potential features GOAT will have in the future and to show the direction 
- some features might be added additionally other probably removed 
- as this is an open source project and in general a very strong interaction with possible users is targeted I am also very open to discuss and consider input from the community. Just get in touch! 


- (There will be a table with the possible new features)

- besides the extensions highlighted major improvements in performance, accuracy and data quality are targeted
- The focus therefore is on improved data fusion concepts and also a stronger engagement in the OSM community
- everybody who has tested GOAT realized that the demo app is currently only available for the city of Munich, as our institution is located in Munich it is self-explaining that I started here, however an extension to other German municipalities and other places in the world is envisioned 
- although GOAT can be setup by everybody on it own server with his or hers study area many still want to be able to use GOAT right a way
- reasons for not covering other study areas are mainly related to the claims I have on the data quality but also on the ressources available for additional server space
- as OSM data can be of varying quality to use it in a production environment from my perspective cross-checks with other data source or the local knowledge are necessary
- furthermore I see activity in the local OSM-community as essential
- to the date I can only provide this within the city boundaries of Munich, in the coming months I can imagine to extent this to some other counties in metropolitan region of munich, however not yet to completely new places.
- However I would be very open to launch GOAT in other cities worldwide as part of cooperation with others. If you miss GOAT in your city and you are interested in becoming part of the community just get in touch and we could develop strategies to make this possible!