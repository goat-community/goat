---
sidebar_position: 3
---

import thematicIcon from "/img/toolbox/data_management/join/toolbox.webp";
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


# Polygone aggregieren

Das **Polygone aggregieren**-Werkzeug führt statistische Analysen von Polygonen durch, z.B. Anzahl, Summe, Minimum oder Maximum, und **aggregiert die Informationen auf Polygonen**.

## 1. Erklärung

Mit dem Polygone aggregieren-Werkzeug können Daten zwischen verschiedenen Polygon-Layern basierend auf ihren **räumlichen Beziehungen** kombiniert oder aggregiert werden. Diese räumlichen Beziehungen werden mithilfe verschiedener **statistischer Ansätze** berechnet. Diese Technik ist nützlich, um zu analysieren und zu visualisieren, wie verschiedene geografische Entitäten interagieren, was die Analyse und Interpretation erleichtert.

Das untenstehende Beispiel zeigt, dass die Geometrie der *Referenz-Layer* gleich bleibt, während ihre Attributtabelle durch die Aggregation von Informationen aus der *Aggregationsfläche* erweitert wird.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/toolbox/geoanalysis/aggregate_polygons/polygon_aggregation.png').default} alt="Polygon Aggregation" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## 2. Anwendungsbeispiele

- Visualisierung der Anzahl von Parks pro Stadtteil.
- Berechnung der durchschnittlichen Gebäudegröße in einem Gebiet.
- Aggregation der Bevölkerungszahlen auf einem sechseckigen Raster und Berechnung der Bevölkerungsdichten.

## 3. Wie benutzt man das Werkzeug?

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie auf <code>Werkzeuge</code> <img src={thematicIcon} alt="toolbox" style={{width: "25px"}}/>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Wählen Sie im Menü <code>Geoanalyse</code> aus und drücken auf <code>Polygone aggregieren</code>.</div>
</div>

<img src={require('/img/toolbox/geoanalysis/aggregate_polygons/aggregate_polygons.png').default} alt="Polygon Aggregation Tool in GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>

### Layer zum Aggregieren

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie einen <code>Referenz-Layer</code>, der die Daten enthält, die Sie aggregieren möchten.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Wählen Sie, auf welche <code>Form</code> Sie die Referenz-Layer aggregieren möchten. Sie können zwischen <b>Polygon</b> oder <b>H3-Raster</b> wählen.</div>
</div>

<Tabs>
  <TabItem value="Polygon" label="Polygon" default className="tabItemBox">

 #### Polygon

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Wählen Sie den <code>Polyon-Layer</code>, der die Polygone enthält, auf denen Sie Ihre Punktdaten aggregieren möchten.</div>
</div>

  </TabItem>
  <TabItem value="H3 Grid" label="H3-Raster" className="tabItemBox">

 #### H3-Raster

 <div class="step">
  <div class="step-number">5</div>
  <div class="content">Wählen Sie <code>H3-Raster</code>. Sie können zwischen Auflösungen von <b>3</b> (durchschnittliche Kantenlänge von 69 km) und <b>10</b> (durchschnittliche Kantenlänge von 70 m) wählen.</div>
</div>

:::tip Tipp

Um mehr über das H3-Raster zu erfahren, können Sie das [Glossar](../../further_reading/glossary#H3-grid) besuchen.

:::

  </TabItem>
</Tabs>

### Statistiken

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Wählen Sie die <code>Statistische Methode</code> und <code>Feld Statistik</code> (das Feld in dem Referenz-Layer, das zur Gruppierung der Aggregation verwendet wird).</div>
</div>

Die verfügbaren **Statistischen Methoden** sind im Folgenden aufgeführt. Die verfügbaren Methoden hängen vom Datentyp des ausgewählten Attributs ab:

| Methode | Typ | Beschreibung |
| -------|------| ------------|
| Anzahl | `string`,`number`    | Zählt die Anzahl der Nicht-Null-Werte in der ausgewählten Spalte|
| Summe  | `number`   | Berechnet die Summe aller Zahlen in der ausgewählten Spalte|
| Mittelwert | `number`   | Berechnet den Durchschnitt (Mittelwert) aller numerischen Werte in der ausgewählten Spalte|
| Median | `number`   | Gibt den Mittelwert in der sortierten Liste der numerischen Werte der ausgewählten Spalte zurück|
| Min    | `number`   | Gibt den Minimalwert der ausgewählten Spalte zurück|
| Max    | `number`   | Gibt den Maximalwert der ausgewählten Spalte zurück|

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Wenn Sie möchten, können Sie die Option <b>Gewichtet nach Verschneidungsfläche</b> aktivieren, indem Sie auf <b>Erweiterte Eigenschaften</b> <img src={require('/img/map/styling/options_icon.png').default} alt="Options Icon" style={{ maxHeight: "25px", maxWidth: "25px", objectFit: "cover"}}/> klicken. Dadurch werden aggregierte Werte nach dem Anteil der Schnittfläche zwischen dem <i>Referenz-Layer</i> und dem <i>Aggregations-Layer</i> gewichtet.</div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Drücken Sie nun auf <code>Ausführen</code>.</div>
</div>

:::tip Tipp

Abhängig von der Größe der Datensätze kann die Berechnung einige Minuten dauern. Die [Statusleiste](../../workspace/home#status-bar) zeigt den aktuellen Fortschritt an.

:::

### Ergebnisse

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Sobald der Berechnungsprozess abgeschlossen ist, wird der resultierende Layer <b>"Aggregation Polygon"</b> der Karte hinzugefügt. Der Ergebnis-Layer besteht aus den Informationen des Referenz-Layers und einer <b>zusätzlichen Spalte</b>, die die Ergebnisse der <b>statistischen Operation</b> anzeigt. Sie können die Tabelle sehen, indem Sie das Polygon auf der Karte anklicken.</div>
</div>

<img src={require('/img/toolbox/geoanalysis/aggregate_polygons/aggregate_polygons_result.png').default} alt="Polygon Aggregation Result in GOAT" style={{ maxHeight: "auto", maxWidth: "auto"}}/>

:::tip Tipp
Möchten Sie Ihren Ergebnislayer bearbeiten und ansprechende Karten erstellen? Dies können Sie unter [Layer Design](../../map/layer_style/styling).
:::

