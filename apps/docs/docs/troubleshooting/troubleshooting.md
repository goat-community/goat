---
sidebar_position: 10
slug: /troubleshooting
---

# Troubleshooting

When using GOAT, you might face issues for some specific tasks you want to perform. These issues are generally due to computation constraints in GOAT. Computational limits are essential for maintaining server stability and efficiency, ensuring reliable performance. Learning to understand and fix these problems will help you move forward with your analysis. This page is here to guide you through common errors, making it easier to solve them and keep progressing with GOAT. 
## Job failures
When you run an analysis in a project, the task is referred to as a **job** in the software. An error message stating **job failure** indicates that the task could not be executed. To learn more about the reason for the failure, please check the [status bar](workspace/home#status-bar). You can find bellow common job failure and suggestion to solve them.

* Analyses cannot exceed two minutes in length, and there is a limit on the number of features that can be analyzed. 
<div style={{ display: "flex", alignItems: "center" }}>
  <img 
    src={require('/img/troubleshooting/arrow-right.png').default} 
    alt="Layers" 
    style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover", marginRight: "8px" }} 
  />
  <span>
    <strong>You can use the  <a href="map/filter">Filter</a> to split your analysis into smaller layers.</strong>
  </span>
</div>

 ![Filtering to compute larger areas](/img/troubleshooting/filtering.jpg "Filtering to compute larger areas")

* For gravity analysis, GOAT does not accept higher sensitivities than 1,000,000.
<div style={{ display: "flex", alignItems: "center" }}>
  <img 
    src={require('/img/troubleshooting/arrow-right.png').default} 
    alt="Layers" 
    style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover", marginRight: "8px" }} 
  />
  <span>
    <strong>You can use the suggested sensitivities in GOAT as a reference.</strong>
  </span>
</div>

* Starting points of a routing indicator like catchement area or public transport nearby should be closer than 100m from the road network. 
<div style={{ display: "flex", alignItems: "center" }}>
  <img 
    src={require('/img/troubleshooting/arrow-right.png').default} 
    alt="Layers" 
    style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover", marginRight: "8px" }} 
  />
  <span>
    <strong>You can visualize the network either directly with the base map of by visualizing the street network layer in scenarios</strong>
  </span>
</div>

 ![Routing start point](/img/troubleshooting/routing_start.jpeg "Routing start point")

* If you calculate an indicator but the result is empty, no output is provided and a job failure occurs. For example, if you calulates public transport trip count in an area and a type period where no trip is performed; the job fails with the error: **The Layer is None**
<div style={{ display: "flex", alignItems: "center" }}>
  <img 
    src={require('/img/troubleshooting/arrow-right.png').default} 
    alt="Layers" 
    style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover", marginRight: "8px" }} 
  />
  <span>
    <strong>You can try expanding the spatial or temporal range of your analysis.</strong>
  </span>
</div>


## Error upload datasets

* If you try to upload a dataset type that is not coverted by GOAT, an error arise. See authorized [dataset types](data/dataset_types)

