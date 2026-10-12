---
description: "Calculate the average public transport departures per hour at each platform for a chosen day and time window, in total and per mode, from GTFS data."
sidebar_position: 8
---

# Trip Count Platform

This indicator displays the **average number of public transport departures** per hour for each public transport platform.

<div style={{ display: 'flex', justifyContent: 'center' }}>
<iframe width="560" height="315" src="https://www.youtube.com/embed/2oRxWow9LBQ?si=IYvAqZcpSO02yDaA&amp;start=46" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

## 1. Explanation

The **Trip Count Platform** shows the **average number of departures per hour for a selected time interval at each public transport platform**. You can view the sum for all modes or focus on a specific mode (e.g., bus, tram, metro, rail).

This indicator is the foundation for the [ÖV-Güteklassen](./oev_gueteklassen.md) and is useful for **weak point analyses of [local transport plans](https://www.plan4better.de/en/glossary/local-public-transport-plan)** (see, among others, [Guideline for Local Transport Planning in Bavaria](https://www.demografie-leitfaden-bayern.de/index.html)).

:::info

Trip Count Platform computation is available for areas where public transport [GTFS data](https://www.plan4better.de/en/glossary/gtfs) is integrated into GOAT. Currently supported regions include **Germany, Switzerland, and the Haut-Rhin region of France**. If you need analyses beyond these regions, you can [import your own public transport network](../../data/builtin_datasets.md#your-own-public-transport-network) or [contact us](https://plan4better.de/en/contact/) and we will do it for you.

:::

## 2. Example use cases

- Which stations in the city serve as main hubs?
- Which stations have low service rates in comparison to others?
- How does the public transport quality vary over different times of the week or day?

## 3. How to use the indicator?

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Click on <code>Toolbox</code> <img src={require('/img/icons/toolbox.png').default} alt="Options" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Under <code>Accessibility Indicators</code>, select <code>Trip Count Platform</code> to open the settings menu.</div>
</div>

### Calculation Time

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Choose the <code>Day</code>, <code>Start Time</code>, and <code>End Time</code> for your analysis.</div>
</div>

### Configuration

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Select the <code>Reference Area Layer</code>: a polygon layer defining the study area boundary.</div>
</div>


### Result Layer

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Set the <code>Result layer name</code> for the output layer.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Click <code>Run</code> to start the calculation.</div>
</div>

### Results

When the calculation is finished, a new layer called <b>"Trip Count Platform"</b> will be added to the map.

Click on platforms to view details including **platform name**, **total departure count**, and **departure counts per mode**.

<div style={{ display: 'flex', justifyContent: 'center' }}>

</div>

<p></p>

:::tip Hint

If you are interested in one specific mode, e.g. only busses, you can use the [attribute-based styling](../../map/layer_style/style/attribute_based_styling.md) to adjust the point color based on that desired column.

:::

## 4. Technical details

Similar to the Public Transport Quality Classes <i>(German: ÖV-Güteklassen)</i>, this indicator is calculated based on **GTFS data** (see [Network Datasets](../../data/builtin_datasets)). Based on the selected day and time window, the average number of departures per hour (regardless of direction) is calculated.

## 5. References

Shkurti, Majk (2022). [Spatio-temporal public transport accessibility analysis and benchmarking in an interactive WebGIS](https://www.researchgate.net/publication/365790691_Spatio-temporal_public_transport_accessibility_analysis_and_benchmarking_in_an_interactive_WebGIS)
