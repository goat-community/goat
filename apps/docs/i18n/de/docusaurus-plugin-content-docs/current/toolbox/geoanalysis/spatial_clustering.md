---
description: "Gruppieren Sie bis zu 2.000 Punkte in eine feste Zahl von Zonen, per K-Means oder als Ausgeglichene Zonen, die nach Anzahl oder Feldwert gleich groß werden."
sidebar_position: 6
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Räumliches Clustering

Das Werkzeug Räumliches Clustering **erstellt geclusterte Zonen durch Gruppierung nahegelegener Features in eine angegebene Anzahl räumlicher Cluster**.

<!-- TODO: Add YouTube video embed when available
<div style={{ display: 'flex', justifyContent: 'center' }}>
<iframe width="674" height="378" src="VIDEO_URL" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>
-->

## 1. Erklärung

Das Werkzeug Räumliches Clustering gruppiert eine Menge räumlicher Features in eine angegebene Anzahl räumlicher Zonen. Es bietet zwei Clustering-Methoden:

- **K-Means**: Eine schnelle, geometriebasierte Methode, die Features nach Nähe zu Clusterzentren gruppiert. Diese Methode zielt nicht darauf ab, gleich große Zonen bereitzustellen.

- **Ausgeglichene Zonen**: Ein genetischer Algorithmus, der Zonen mit **annähernd gleicher Größe** erstellt, entweder nach Anzahl der Features oder nach einem numerischen Feldwert. Diese Methode unterstützt auch **Kompaktheitseinschränkungen**, um die räumliche Ausdehnung jeder Zone zu begrenzen.

<!-- TODO: Add illustration showing K-means vs Balanced zones
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
<img src={require('/img/toolbox/geoanalysis/clustering_zones/clustering_comparison.png').default} alt="K-Means vs Balanced Zones" style={{ maxHeight: "400px", maxWidth: "auto"}}/>
</div>
-->

:::info

Das Werkzeug für räumliches Clustering ist derzeit **auf Punkt-Features beschränkt**. Es unterstützt maximal **2.000 Punkte**. Für größere Datensätze sollten Sie Ihre Daten vor der Ausführung des Werkzeugs filtern oder eine Stichprobe nehmen.
:::

:::info
- Die Methode **Ausgeglichene Zonen** verwendet einen genetischen Algorithmus, der **nicht deterministisch** ist. Verschiedene Läufe können leicht unterschiedliche Zonenkonfigurationen erzeugen.
- Die Ausführungszeit für **Ausgeglichene Zonen** kann je nach Anzahl der Punkte und gewünschten Cluster erheblich variieren. Sie ist im Allgemeinen langsamer als K-Means und kann je nach Datensatzkomplexität zwischen **1 Minute und 3 Minuten** dauern.
:::

## 2. Anwendungsfälle

- Aufteilung von Verkaufsgebieten in ausgeglichene Zonen basierend auf Kundenstandorten und Umsatz.

- Gruppierung von Bevölkerungsstandorten in Gebiete mit gleicher Bevölkerungsgröße.

- Gruppierung potenzieller Carsharing-Stationen in Servicebereiche.

## 3. Vorgehensweise

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie auf <code>Werkzeuge</code> <img src={require('/img/icons/toolbox.png').default} alt="Optionen" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie im Menü <code>Geoanalyse</code> auf <code>Räumliches Clustering</code>.</div>
</div>

### Eingabe

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie Ihren <code>Eingabe-Layer</code> aus dem Dropdown-Menü. Dies muss ein <b>Punkt-Layer</b> sein, der die zu clusternden Features enthält.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Legen Sie die <code>Anzahl der Cluster</code> fest, also die Anzahl der zu erstellenden Zonen (Standard: 10).</div>
</div>

### Konfiguration

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Wählen Sie den <code>Cluster-Typ</code>.</div>
</div>

<Tabs>

<TabItem value="kmean" label="K-Means" default className="tabItemBox">

**K-Means** gruppiert Features nach Nähe zu Clusterzentren. Es ist schnell und eignet sich, wenn Sie eine schnelle räumliche Gruppierung ohne strenge Größenbalance benötigen.

Für K-Means ist keine zusätzliche Konfiguration erforderlich.

</TabItem>

<TabItem value="equal_size" label="Ausgeglichene Zonen" className="tabItemBox">

**Ausgeglichene Zonen** verwendet einen genetischen Algorithmus, um Zonen mit gleicher oder annähernd gleicher Größe zu erstellen. Diese Methode ist langsamer, liefert aber ausgewogenere Ergebnisse.

Zusätzliche Konfigurationsoptionen werden verfügbar:

</TabItem>

</Tabs>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Wenn Sie <b>Ausgeglichene Zonen</b> verwenden, wählen Sie die <code>Größenmethode</code>: <i>Anzahl</i> für gleiche Feature-Anzahlen pro Zone oder <i>Feldwert</i>, um nach einem numerischen Attribut auszugleichen.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Wenn Sie <b>Feldwert</b> verwenden, wählen Sie das <code>Größenfeld</code>: ein numerisches Feld aus Ihrem Eingabe-Layer, das als Ausgleichsgewichtung verwendet wird.</div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Aktivieren Sie optional <code>Zonengebiet begrenzen</code>, um eine Kompaktheitseinschränkung hinzuzufügen. Wenn aktiviert, konfigurieren Sie die <code>Max. Distanz</code>, um die maximale Entfernung zwischen zwei Features im selben Cluster zu begrenzen.</div>
</div>

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Klicken Sie auf <code>Ausführen</code>, um die Berechnung zu starten.</div>
</div>

### Ergebnisse

Sobald die Berechnung abgeschlossen ist, werden **zwei Ergebnis-Layer** zur Karte hinzugefügt:

1. **Features-Layer**: Die ursprünglichen Eingabe-Features, denen jeweils eine `cluster_id` zugewiesen wurde.
2. **Zusammenfassungs-Layer**: Ein Multigeometrie-Feature pro Zone mit Zonenstatistiken (Größe, maximale Distanz zwischen Features).


<div style={{ display: 'flex', justifyContent: 'center' }}>
<img src={require('/img/toolbox/geoanalysis/spatial_clustering/clustering.webp').default} alt="Spatial Clustering Ergebnis in GOAT" style={{ maxHeight: "auto", maxWidth: "80%"}}/>
</div>

:::tip Tipp

Möchten Sie visuell ansprechende Karten erstellen, die eine klare Geschichte erzählen? Erfahren Sie, wie Sie Farben, Legenden und Stile in unserem Abschnitt [Styling](../../map/layer_style/style/styling) anpassen können.

:::

## 4. Technische Details

### K-Means Clustering

Der K-Means-Algorithmus arbeitet iterativ:

1. **Initialisierung**: *k* anfängliche Zentroide werden unter Verwendung einer Furthest-Point-Strategie für eine bessere Verteilung ausgewählt.
2. **Zuordnung**: Jedes Feature wird basierend auf der euklidischen Distanz (in projizierten Koordinaten) dem nächstgelegenen Zentroid zugeordnet.
3. **Aktualisierung**: Zentroide werden als mittlere Position aller zugeordneten Features neu berechnet.
4. **Wiederholung** bis die Zentroide konvergieren oder die maximale Anzahl an Iterationen erreicht ist.

### Ausgeglichene Zonen

Die Methode Ausgeglichene Zonen verwendet einen **genetischen Algorithmus**, um optimale räumliche Gruppierungen zu finden:

1. Eine anfängliche Population von Lösungen wird erstellt, wobei K-Means als Startpunkt verwendet wird, plus zufällige Variationen.
2. Für jede Lösung wird ein **Startpunkt (Seed)** für jeden Cluster extrahiert und **Zonen wachsen gelassen** durch räumliche Nachbarn, um alle Features den Clustern zuzuweisen. Durch das Wachstum nicht zugewiesene Features werden dem **kleinsten umliegenden Cluster** zugewiesen. Die Rand-Features großer Cluster können dann kleineren Zonen **neu zugewiesen** werden.
3. Jede Lösung wird anhand eines **Fitness-Scores** bewertet.
4. Die besten Lösungen werden über mehrere Generationen hinweg kombiniert und mutiert, um das Ergebnis schrittweise zu verbessern.
5. Der Algorithmus stoppt, wenn keine weitere Verbesserung gefunden wird oder die maximale Anzahl an Generationen erreicht ist.

Der Algorithmus verwendet **räumliche Nachbarschaftsgraphen**, um zusammenhängendes Zonenwachstum sicherzustellen: Features werden Zonen durch ihre räumlichen Nachbarn zugewiesen, was kompakte und verbundene Cluster fördert.


#### Fitness-Funktion:
Jede Lösungskandidat wird bewertet basierend auf:
- **Größenvarianz**: Wie gleichmäßig die Zonen dimensioniert sind (primäres Ziel).
- **Kompaktheitsstrafe** (optional): Bestraft Zonen, bei denen der maximale Distanzschwellenwert überschritten wird.


Alle Einschränkungen (gleiche Größe, Kompaktheit) sind **weiche Einschränkungen**: Der Algorithmus optimiert darauf hin, erzwingt sie jedoch nicht als harte Grenzen.

#### Algorithmus-Parameter:

| Parameter | Wert | Beschreibung |
|-----------|-------|-------------|
| Populationsgröße | 40–50 | Anzahl der Lösungskandidaten pro Generation |
| Generationen | 40–50 | Maximale Anzahl an Evolutionszyklen |
| Mutationsrate | 0,1 | Wahrscheinlichkeit der Änderung des Cluster-Startpunkts |
| Crossover-Rate | 0,7 | Wahrscheinlichkeit der Kombination von Elternlösungen |
| Elitismus | Top 10% | Die besten Lösungen bleiben über Generationen erhalten |
**Adaptive Parameter:** Für größere Datensätze (>500 Features) werden die Populationsgröße und die Anzahl der Generationen automatisch reduziert, um angemessene Rechenzeiten beizubehalten.
