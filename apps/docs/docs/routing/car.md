---
sidebar_position: 4

---

# Car

The **Car Routing** is used for all analyses in GOAT that contain car trips.


## 1. Objectives

Car routing is used for many indicators in GOAT, such as [Catchment Areas](../toolbox/accessibility_indicators/catchments) and [Heatmaps](../toolbox/accessibility_indicators/connectivity). 

As GOAT also allows the creation of [Scenarios on the Street Network](../scenarios#4-street-network---edges), a **custom routing algorithm** is needed that also reflects the changes of the scenario in the accessibility analyses. For the mode of the car, we thereby **only consider paths that are suitable for driving**.

## 2. Data

### Routing Network

Data from the  **[Overture Maps Foundation](https://overturemaps.org/)**  is used as a routing network in GOAT. It includes the transportation infrastructure with **edges**  (for any continuous path not bisected by another) and **nodes**  (for any point where two distinct paths intersect), representing real-world networks.


## 3. Technical Details

### Data Pre-processing

The following steps are performed on the data to enable  **quick**  and  **accurate**  routing for cars:

1.  **Attribute Parsing:**  Categorizing attributes of edges (street `class` and `surface`).
2.  **Geospatial Indexing:**  Utilizing  **[Uber's H3 grid-based](../further_reading/glossary#h3-grid)**  indexing for efficient routing.
3.  **Extracting Restrictions:**  Identifying one-way access restrictions in addition to speed limits for both directions of the edge (`maxspeed_forward` and `maxspeed_backward`).

### Routing Process Steps

#### Sub-network Extraction

1.  **Buffer Region:**  Based on user-origin, travel time, and maximum potential driving speed.
2.  **Edge Filtering:**  Include only relevant edges for driving.

For car routing, the edges of the following street classes are considered:

`motorway`, `primary`, `secondary`, `tertiary`, `residential`, `living_street`, `trunk`, `parking_aisle`, `driveway`, `alley` and `track`.
    
You can find further information on this classification in the [Overture Wiki](https://docs.overturemaps.org/schema/reference/transportation/segment).

#### Artificial Edge Creation

User-provided origin points are typically located a short distance away from the street network. To account for the additional time (or cost) of driving from the origin to its nearest street (e.g. using an unmarked driveway), artificial (or simulated) edges are created.


#### Edge Cost Computation

For all edges in the sub-network, a cost value (represented as time) is calculated based on path length and driving speed.

Cost function for car:

`cost_forward = length / maxspeed_forward`

`cost_reverse = length / maxspeed_backward`

When calculating `cost_reverse`, if an edge contains a one-way restriction and therefore must not be traversed in the reverse direction, it is given a very large cost. This prevents the routing algorithm from considering such edges for routing in the reverse direction.

:::info Note
GOAT's routing algorithm does not currently take into account **historic traffic patterns** for car routing. This feature is currently under development. 🧑🏻‍💻
:::

#### Network Propagation

To compute the shortest path from the origin point to various destinations, a custom implementation of the well-known [Dijkstra Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) is used.


<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/routing/walk/dijkstra.gif').default}  alt="Dijkstra Algorithm" style={{ width: "auto", height: "auto", objectFit: "cover"}}/>
<p style={{ textAlign: 'center' }}>GIF: <a href="https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm">Dijkstra Algorithm</a></p>
</div>

The implementation has a time complexity of *O(ElogV)*, is written in **Python**, and uses the just-in-time compiler **Numba**.
