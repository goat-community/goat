---
description: "Ermitteln Sie aus GTFS-Daten die durchschnittlichen ÖV-Abfahrten pro Stunde je Haltepunkt für Tag und Zeitfenster, gesamt und je Verkehrsmittel."
sidebar_position: 8
---


# Anzahl Abfahrten Haltepunkte

Dieser Indikator zeigt die **durchschnittliche Anzahl der Abfahrten öffentlicher Verkehrsmittel** pro Stunde für jeden Haltepunkt des öffentlichen Verkehrs an.

<div style={{ display: 'flex', justifyContent: 'center' }}>
<iframe  width="674" height="378" src="https://www.youtube.com/embed/psnuUksG7W4?si=dhLw5Gp0ThYHFd5l&amp;start=46" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

## 1. Erklärung

**Anzahl Abfahrten Haltepunkte** zeigt die **durchschnittliche Anzahl der Abfahrten pro Stunde für ein ausgewähltes Zeitintervall an jedem Haltepunkt des öffentlichen Verkehrs**. Sie können die Summe für alle Verkehrsmittel anzeigen oder sich auf ein bestimmtes Verkehrsmittel konzentrieren (z.B. Bus, Straßenbahn, U-Bahn, Bahn).

Dieser Indikator ist die Grundlage für die [ÖV-Güteklassen](./oev_gueteklassen.md) und ist nützlich für **Schwachstellenanalysen von [lokalen Verkehrsplänen](https://www.plan4better.de/de/glossar/nahverkehrsplan)** (siehe unter anderem [Richtlinie für die Nahverkehrsplanung in Bayern](https://www.demografie-leitfaden-bayern.de/index.html)).

:::info

Die Berechnung der Anzahl Abfahrten ist für Gebiete verfügbar, in denen [GTFS-Daten](https://www.plan4better.de/de/glossar/gtfs) des öffentlichen Verkehrs in GOAT integriert sind. Derzeit unterstützte Regionen umfassen **Deutschland, die Schweiz und die Region Haut-Rhin in Frankreich**. Wenn Sie Analysen außerhalb dieser Regionen benötigen, können Sie [ein eigenes ÖPNV-Netz importieren](../../data/builtin_datasets.md#eigenes-öpnv-netz) oder uns gerne [kontaktieren](https://plan4better.de/de/contact/), damit wir das für Sie übernehmen.

:::

## 2. Anwendungsbeispiele

- Welche Stationen in der Stadt dienen als Hauptknotenpunkte?
- Welche Stationen haben im Vergleich zu anderen niedrige Serviceraten?
- Wie variiert die Qualität des öffentlichen Verkehrs zu unterschiedlichen Zeiten der Woche oder des Tages?

## 3. Wie benutzt man den Indikator?

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie auf <code>Werkzeuge</code> <img src={require('/img/icons/toolbox.png').default} alt="Options" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Unter <code>Erreichbarkeitsindikatoren</code> wählen Sie <code>Anzahl Abfahrten Haltepunkte</code>, um das Einstellungsmenü zu öffnen.</div>
</div>

### Berechnungszeit

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie <code>Tag</code>, <code>Startzeit</code> und <code>Endzeit</code> für Ihre Analyse.</div>
</div>

### Konfiguration

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Wählen Sie das <code>Referenzgebiet</code>: einen Polygon-Layer, der das Untersuchungsgebiet definiert.</div>
</div>

### Ergebnis-Layer

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Legen Sie den <code>Name der Ergebnislayer</code> für den Ausgabe-Layer fest.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Klicken Sie auf <code>Ausführen</code>, um die Berechnung zu starten.</div>
</div>

### Ergebnisse

Nach Abschluss der Berechnung wird ein neuer Layer namens <b>"Anzahl Abfahrten Haltepunkte"</b> zur Karte hinzugefügt.

Klicken Sie auf Haltepunkte, um Details anzuzeigen, einschließlich **Name des Haltepunkts**, **Gesamtanzahl der Abfahrten** und **Abfahrten pro Verkehrsmittel**.



:::tip Tipp

Falls Sie an einem bestimmten Verkehrsmittel interessiert sind, z.B. nur Busse, können Sie das [attributbasierte Styling](../../map/layer_style/style/attribute_based_styling) verwenden, um die Punktfarbe basierend auf der gewünschten Spalte anzupassen.

:::

## 4. Technische Details

Ähnlich den Public Transport Quality Classes <i>(Deutsch: ÖV-Güteklassen)</i>, wird dieser Indikator basierend auf **GTFS-Daten** berechnet (siehe [Netz-Datensätze](../../data/builtin_datasets)). Basierend auf dem ausgewählten Tag und Zeitfenster wird die durchschnittliche Anzahl der Abfahrten pro Stunde (unabhängig von der Richtung) berechnet.

## 5. Referenzen

Shkurti, Majk (2022). [Spatio-temporal public transport accessibility analysis and benchmarking in an interactive WebGIS](https://www.researchgate.net/publication/365790691_Spatio-temporal_public_transport_accessibility_analysis_and_benchmarking_in_an_interactive_WebGIS)
