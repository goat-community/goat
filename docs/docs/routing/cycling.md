---
sidebar_position: 2
---

# Cycling

##### Routing algorithms - Walking and Cycling:

The routing for walking and cycling is based on a custom implementation of the widely used Dijkstra algorithm. In the implementation, the routing network is dynamically created and therefore allows the computation of scenarios. 

While the routing network is saved in the PostgreSQL/PostGIS database, the routing is done in Python using the just-in-time compiler Numba.


