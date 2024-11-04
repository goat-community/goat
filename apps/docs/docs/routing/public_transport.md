---
sidebar_position: 3

---

# Public Transport

The **Public Transport Routing** in GOAT is essential for performing analyses that include public transport trips.

## 1. Objectives

Public transport routing facilitates **intermodal analysis** by integrating access and egress modes, such as walking or biking to and from the station. This is more complex than the other routing modes as it requires the merging of different datasets (such as sidewalks & bike lanes, public transport stops & schedules, etc.) and calculation approaches.

Public transport routing is used for many indicators in GOAT, such as [Catchment Areas](../toolbox/accessibility_indicators/catchments) and [Heatmaps](../toolbox/accessibility_indicators/connectivity).

Moreover, with [Scenarios on the Street Network](../scenarios#4-street-network---edges), a **flexible routing algorithm** adapts to scenario changes in accessibility analyses in GOAT.

### Configurable Options for Analyses

- `weekday`: Choose from Weekday, Saturday, or Sunday.
- `start time` and `end time`: Specify the analysis time window.



## 2. Data

### Transit Data

Utilizes data in **[GTFS](https://developers.google.com/transit/gtfs)** (General Transit Feed Specification) for static public transport network information (stops, routes, schedules, transfers).


### Street Data

Incorporates street-level information from  **[OpenStreetMap](https://wiki.openstreetmap.org/)** to support multi-modal routing and real-world path connections (includes sidewalks, bike paths, and crosswalks).


## 3. Technical Details

Public transport routing is performed using the **[R5 Routing Engine](https://github.com/conveyal/r5)** (_Rapid Realistic Routing on Real-world and Reimagined networks_). R5 is the routing engine from **[Conveyal](https://conveyal.com/)**, a web-based platform that allows users to create transportation scenarios and evaluate them in terms of cumulative opportunities and accessibility indicators.


### Routing Options

#### Modes
`bus` `tram` `rail` `subway` `ferry` `cable_car` `gondola` `funicular`

#### Access and Egress Modes

- **Access Mode:** How users get to a transit stop from their starting location (`walk` `bicycle` `car`).
- **Egress Mode:** How users proceed to their destination from a transit stop (`walk` `bicycle`).


#### Other (Default Configurations)

The following default configurations are used while performing public transport routing. They are not currently user-configurable.

- **Decay function type:** logistic
- **Standard deviation:** 12 minutes
- **Width:** 10 minutes
- **Walk speed:** 1.39 km/h
- **Maximum walk time:** 20 minutes
- **Bike speed:** 4.166666666666667 km/h
- **Maximum bike time:** 20 minutes
- **Bike traffic stress:** 4
- **Maximum rides:** 4
- **Zoom level:** 9
- **Percentiles:** 5
- **Monte Carlo draws:** 200