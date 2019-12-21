---
title: Heatmap
permalink: /docs/heatmap/
---

GOAT allows you to calculate and visualize gravity-based accessibility measures, which are visualized as heatmaps. Based on pre-calculated travel times the heatmap is computed dynamically based on the selection of the user. A hexagonal grid is used for visualization.

<img class="img-responsive" src="../../img/heatmap.png" title="Heatmap for groceries">

#### 1. Calculation
The calculation of the heatmap is based on the calculation of the potential accessibility of opportunities in zone i to all other zones (n). 
The measure has the following form (Geurs and Van Wee 2004):
<img class="img-responsive" src="../../img/potential_accessibility_measures.png">


As cost of travel C<sub>ij</sub> travel times between i and j are used. Travel times are computed in seconds. As cut-off value 15 minutes is used for the mode walking, this means that destination that are further away then 15 minutes walking time are not considered in the calculation of the index.
The sensitivity parameter defines how accessibility changes with increasing travel time. As the sensitivity parameter is decisive when measuring accessibility, GOAT allows you to adjust them. The following graphs show the influence of the sensitivity parameter on accessibility. 

<table><tr>
<td> <img class="img-responsive" src="../../img/sensitivity_index.png" title="Sensitivty index β= -0.003" style="width: 300px;"/> </td>
<td> <img class="img-responsive" src="../../img/sensitivity_index2.png" title="Sensitivty index β= -0.002" style="width: 300px;"/> </td>
</tr></table>

#### 2. Classification
In order to classify the accessibility levels that were computed for each grid cell, a classification based on quintiles is used. 

#### 3. Example of calculation
##### 3.1 Calculation travel times
The following example illustrates how the gravity-based heatmap is computed.
The travel times are calculated for each grid cell to the concerning destination on the street network. 


<img class="img-responsive" src="../../img/grid_groceries.png" title="Accessibility to groceries" style="width: 600px;"/> 

For one grid cell the calculation could be done as in the following examples:

Uniform sensitivity parameter:
<img class="img-responsive" src="../../img/accessiblity_uniform_sensitivity-index.png" style="width: 500px;">
Varying sensitivity parameter for Hypermarket:
<img class="img-responsive" src="../../img/accessiblity_different_sensitivity-indices.png" style="width: 500px;">

##### 3.2 Calculation with uniform sensitivity parameter
In the first case we want to calculate the accessibility to groceries in 15min (β= -0.002).
This means the sensitivity parameter is the same for every category of grocery. 

<img class="img-responsive" src="../../img/uniform_sensitivity.png" title="Accessibility to groceries in 15min with uniform sensitivity index">

##### 3.3 Calculation with different sensitivity indices
In the second case we calculate the accessibility to groceries in 15min (β= -0.001 and 
β= -0.002). This means the sensitivity parameter depends on the categories of grocery. For this example, we used β= -0.001 for the type of grocery hypermarket and β= -0.002 for discount supermarket und supermarket.

<img class="img-responsive" src="../../img/different_sensitivity.png" title="Accessibility to groceries in 15min with different sensitivity indices" >


If both examples are compared significant changes in accessibility can be observed, as in the second example the sensitivity parameter is chosen in favor of hypermarkets. 


