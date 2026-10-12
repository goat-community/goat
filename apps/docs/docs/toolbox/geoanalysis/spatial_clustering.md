---
description: "Group up to 2,000 points into a set number of zones with fast K-Means or Balanced Zones, a genetic algorithm that evens out zone size by count or field value."
sidebar_position: 6
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Spatial Clustering

The Spatial Clustering tool **creates clustered zones by grouping nearby features into a specified number of spatial clusters**.

<!-- TODO: Add YouTube video embed when available
<div style={{ display: 'flex', justifyContent: 'center' }}>
<iframe width="674" height="378" src="VIDEO_URL" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>
-->

## 1. Explanation

The Spatial Clustering tool groups a set of spatial features into a specified number of spatial zones. It offers two clustering methods:

- **K-Means**: A fast, geometry-based method that groups features by proximity to cluster centers. This method does not aim to provide equal-sized zones.

- **Balanced Zones**: A genetic algorithm that creates zones with **near-equal sizes**, either by feature count or by a numeric field value. This method also supports **compactness constraints** to limit the spatial spread of each zone.

<!-- TODO: Add illustration showing K-means vs Balanced zones
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
<img src={require('/img/toolbox/geoanalysis/clustering_zones/clustering_comparison.png').default} alt="K-Means vs Balanced Zones" style={{ maxHeight: "400px", maxWidth: "auto"}}/>
</div>
-->

:::info

The Spatial Clustering tool is currently **limited to point features only**. It only supports a maximum of **2,000 points**. For larger datasets, consider pre-filtering or sampling your data before running the tool.
:::

:::info
- The **Balanced Zones** method uses a genetic algorithm which is **non-deterministic**. Different runs may produce slightly different zone configurations.
- Execution time for **Balanced Zones** can vary significantly based on the number of points and desired clusters. It is generally slower than K-Means, taking anywhere from **1 Minute to 3 minutes** depending on dataset complexity.
:::

## 2. Example use cases

- Dividing sales territories into balanced zones based on customer locations and revenue.

- Grouping population locations into areas with equal population size.

- Grouping potential car-sharing stations into service areas.

## 3. How to use the tool?

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click on <code>Toolbox</code> <img src={require('/img/icons/toolbox.png').default} alt="Options" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under the <code>Geoanalysis</code> menu, click on <code>Spatial Clustering</code>.</div>
</div>

### Input

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Select your <code>Input Layer</code> from the drop-down menu. This must be a <b>point layer</b> containing the features you want to cluster.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Set the <code>Number of Clusters</code>: the number of zones to create (default: 10).</div>
</div>

### Configuration

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Select the <code>Cluster Type</code>.</div>
</div>

<Tabs>

<TabItem value="kmean" label="K-Means" default className="tabItemBox">

**K-Means** groups features by proximity to cluster centers. It is fast and suitable when you need a quick spatial grouping without strict size balancing.

No additional configuration is required for K-Means.

</TabItem>

<TabItem value="equal_size" label="Balanced Zones" className="tabItemBox">

**Balanced Zones** uses a genetic algorithm to create zones with equal or near-equal sizes. This method is slower but produces more balanced results.

Additional configuration options become available:

</TabItem>

</Tabs>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">If using <b>Balanced Zones</b>, select the <code>Size Method</code>: <i>Count</i> for equal features counts per zone, or <i>Field Value</i> to balance by a numeric attribute.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">If using <b>Field Value</b>, select the <code>Size Field</code>: a numeric field from your input layer to use as the balancing weight.</div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Optionally, enable <code>Limit Zone Area</code> to add a compactness constraint. When enabled, configure the <code>Max Distance</code> to limit the maximum distance between two features in the same cluster.</div>
</div>

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Click <code>Run</code> to start the calculation.</div>
</div>

### Results

Once the calculation is complete, **two result layers** will be added to the map:

1. **Features layer**: The original input features, each assigned a `cluster_id`.
2. **Summary layer**: One multigeometry feature per zone, with zone statistics (size, maximum distance between features).


<div style={{ display: 'flex', justifyContent: 'center' }}>
<img src={require('/img/toolbox/geoanalysis/spatial_clustering/clustering.webp').default} alt="Closest Average Heatmap Calculation Result in GOAT" style={{ maxHeight: "auto", maxWidth: "80%"}}/>
</div>

:::tip Tip

Want to create visually compelling maps that tell a clear story? Learn how to customize colors, legends, and styling in our [Styling section](../../map/layer_style/style/styling).

:::

## 4. Technical details

### K-Means Clustering

The K-Means algorithm works iteratively:

1. **Initialization**: *k* initial centroids are chosen using a furthest-point strategy for better spread.
2. **Assignment**: Each feature is assigned to the nearest centroid based on Euclidean distance (in projected coordinates).
3. **Update**: Centroids are recalculated as the mean position of all assigned features.
4. **Repeat** until centroids converge or the maximum number of iterations is reached.

### Balanced Zones 

The Balanced Zones method uses a **genetic algorithm** to find optimal spatial groupings:

1. An initial population of solutions is created using K-Means as a starting point, plus random variations.
2. For each solution, **extract seed** for each cluster and **grow zones** through spatial neighbors to assign all features to clusters. Features unassigned by growth are assigned to the **smallest surrounding cluster**. The frontier features of large clusters can then be **reassigned** to smaller zones.
3. Each solution is scored based on a **fitness score**.
4. The best solutions are combined and mutated across multiple generations to progressively improve the result.
5. The algorithm stops when no further improvement is found or the maximum number of generations is reached.

The algorithm uses **spatial neighbor graphs** to ensure contiguous zone growth: features are assigned to zones through their spatial neighbors, promoting compact and connected clusters.


#### Fitness function:
Each candidate solution is scored based on:
- **Size variance**: How evenly the zones are sized (primary objective).
- **Compactness penalty** (optional): Penalizes zones where the maximum distance threshold is exceeded.


All constraints (equal size, compactness) are **soft constraints**: the algorithm optimizes toward them but does not enforce them as hard limits.

#### Algorithm parameters:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Population size | 40–50 | Number of candidate solutions per generation |
| Generations | 40–50 | Maximum number of evolutionary cycles |
| Mutation rate | 0.1 | Probability of changing cluster seed location |
| Crossover rate | 0.7 | Probability of combining parent solutions |
| Elitism | Top 10% | Best solutions preserved across generations |
**Adaptive parameters:** For larger datasets (>500 features), the population size and generation count are automatically reduced to maintain reasonable computation times.
