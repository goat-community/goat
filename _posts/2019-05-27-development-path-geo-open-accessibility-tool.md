---
layout: post
title:  "Development path of GOAT"
author: Elias Pajares
---

Geo Open Accessibility Tool (GOAT) is by far not where it should be. Apart from the on-going professionalization which is seen as crucial to provide a truly useful and stable accessibility instrument, additional features will be implemented on a regular basis.
The main objective we have been focusing on in the past months was making the interactive network modification and the setup process better. Little time was spent for coming up with new features. However, there are some new envisioned and edge cutting features which will bring GOAT to the status where the first version (GOAT 1.0) will be released.

So far, GOAT is still very much a personal project as funding for this first stable release has not been secured. Consequently, the date for the first ground-breaking release of GOAT for production purposes remains undefined. Our current estimated time is between 1 and 2 years. Nonetheless I feel it’s important to communicate the potential features that GOAT will have in future and further show directions which this instrument will take. In the course of development, some GOAT features will be added and others probably removed. 

The following table gives a glimpse on the fields of development, it has to be underlined that this list is not complete, especially smaller features and features related to the user experience are not listed.

<table class="table table-striped table-hover ">
  <thead>
    <tr>
      <th>Feature</th>
      <th>Description</th>
      <th>Open tasks</th>
    </tr>
  </thead>
  <tbody>
    <tr class="success">
      <td><b>Routing performance</b></td>
      <td>The pgRouting library shines with its flexibility, though this comes with 
      the cost of relatively long query times for the calculation of the shortest path and the isochrones. New features such as multi-isochrones rely on more efficient calculations. Although pgRouting is not tuned per default for high-performance, with good network preparation and improved SQL-queries the performance can be boosted. It will also be examined if database clusters or the calculation on multiple cores can improve the performance.</td>
      <td>At the moment work already started to improve the performance. However with cycling as new mode and the implementation of new accessibility indicators, this will be an ongoing challenge.</td>
    </tr>
    <tr class="success">
      <td><b>Calculation multi-isochrones</b></td>
      <td>Currently the user has only the possibility to calculate one isochrone by clicking on the map. A new feature shall allow for the calculation at several origins. As origin certain amenities can be selected and the isochrones will be visualized all at once. This could allow to answer questions like: What is the share of residents having access to schools in 10 minutes?</td>
      <td>This new feature goes hand in hand with the targeted performance boost of the pgRouting functions. SQL-functionality is also already partly finished, only the implementation into the front-end was not started yet.</td>
    </tr>
    <tr class="success">
      <td><b>Modification POIs</b></td>
      <td>This feature can be seen as first step to allow users to model the effect of land-use changes. It is targeted to develop an experimental feature that let's the user draw, modify and delete POIs. As with the interactive network changes the user will be able to perform an accessibility analysis considering these land-use changes. Interesting scenarios could be calculated like: How does walking accessibility change if amenities are better distributed in space?</td>
      <td>At the moment little interaction with POIs is possible, therefore first some features (e.g. POIs clustering) have to be implemented that allow a more interactive and visually appealing way to interact with the POIs layer.</td>
    </tr>
    <tr class="warning">
      <td><b>Individualization walking</b></td>
      <td>Modelling better the individual component of accessibility is one of the core aims of GOAT. There is especially seen the need to customize the routing functionality to better model the challenges mobility-impaired people face on a daily basis. Accordingly it should be possible to model accessibility also for the elderly and disabled people. In addition the routing functionality will be refined to better model time losses at intersections, inclines and other barriers.</td>
      <td>From the theoretical side there was already done significant effort (e.g. excellent bachelor thesis at TUM). Though further empiric findings need to be done to better understand how especially barriers influence the walking speed of different person groups.</td>
    </tr>
    <tr class="warning">
      <td><b>New mode cycling</b></td>
      <td>Modelling cycling is one of the most demanded features. However the challenge to have a realistic routing functionality has to be underlined. It is targeted to model cycling for different user groups and conditions. Groundwork in this aspect was done in a great study project at TUM. The results from the latter will be further refined and integrated into the overall architecture.</td>
      <td>Part of the back-end functionality is already finished, but the front-end and especially the integration into the interactive network modification functionality still require significant resources. Nevertheless, an experimental version of the feature will be released soon.</td>
    </tr>
    <tr class="danger">
      <td><b>Dynamic recalculation heatmap</b></td>
      <td>The used heatmap builds on precalculated travel times. While this is great for performance it comes with the costs that the calculation is not dynamic. With the current architecture and resources a dynamic recalculation is not possible in an acceptable query time. There have to be found ways to allow also a dynamic recalculation for this indicator.</td>
      <td>A precondition for this feature is a significant performance boost of the routing functions. After this has been achieved the heatmap functionality has to be further refined and adapted to allow scenario building.</td>
    </tr>
    <tr class="danger">
      <td><b>Full land-use modification</b></td>
      <td>It is targeted to give the user the ability to fully manipulate land-use data, besides adding new POIs the user should be able to upload own building data, allocate population and jobs (and a lot more). This feature is seen as essential part to use GOAT as tool to help in developing urban development plans.</td>
      <td>The described feature requires significant effort as in the front-end and the back-end extensive development have to be done. In addition a very high user experience are the precondition for the feature.</td>
    </tr>

  </tbody>
</table>

To this end, I am very open to ideas and suggestions from the community at large. GOAT is an open source project and therefore targets a very strong interaction with its users. Just get in touch!

Besides the listed improvements one main focus is on improved data fusion concepts and stronger engagement in the OpenStreetMap (OSM) community.
For those who have tested GOAT, you might have realized that the demo app is currently only available for the city of Munich. As much as GOAT can be installed by everybody on it own server, many still want to be able to use GOAT immediately especially in their study area.

The reason for not extending coverage to other places is related to the claims I have on data quality and the resources available at my disposal for additional server space. From my perspective as OSM data can be of varying quality cross-checks with local knowledge and other data source are essential when the data is used in a production environment. 

To this date, I can only be in a position to provide the services of GOAT within the boundaries of the city of Munich. However, in the coming months I can imagine to extend the online-version of GOAT to some other counties in the metropolitan regions of Munich.

I would also be very open to launch GOAT in other cities worldwide as an initiative to foster meaningful cooperation with others. If you miss GOAT in your city and you are interested in becoming part of the community just get in touch and we could develop strategies to make this possible!
