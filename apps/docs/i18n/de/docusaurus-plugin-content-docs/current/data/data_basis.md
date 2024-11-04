---
sidebar_position: 2
---

# Eingebaute Datensätze


### Daten als elementare Grundlage für Analysen

Bei Plan4Better verstehen wir, dass Daten die treibende Kraft hinter unsere Analysen sind und daher unser wertvollstes Gut darstellen. Um fundierte Erkenntnisse auf der Grundlage qualitativ hochwertiger Informationen zu liefern, integriert unsere WebGIS-Plattform GOAT eine Vielzahl unterschiedlicher räumlicher und nicht-räumlicher Datensätze aus diversen Quellen. Die Verarbeitung uneinheitlicher Daten mit unterschiedlicher Genauigkeit kann jedoch eine Herausforderung sein. Daher setzen wir Techniken wie effiziente Datenintegration, Disaggregation und Fusionsworkflows ein, um diese Hürden zu meistern.

### Datenerhebung und Datenaufbereitung

Der Datenerhebungsprozess beginnt mit der Identifizierung relevanter Datenquellen und dem Sammeln der Daten, idealerweise aus Open-Data-Portalen oder öffentlich zugänglichen Initiativen. Abhängig von der Datenquelle werden verschiedene Formate wie Shapefiles und GeoJSON verwendet. Es ist daher entscheidend, die Daten in ein einheitliches Schema und Format zu konvertieren, um Konsistenz und Vergleichbarkeit zu gewährleisten.

Datenintegration und -Fusion werden angewandt, um verschiedene Datensätze zusammenzuführen und an den lokalen Kontext anzupassen. Validierungsprozesse stellen die Genauigkeit und Zuverlässigkeit der Daten sicher. Wir sind stets offen, zusätzliche Datensätze und Quellen bei Bedarf zu integrieren.

Bei Plan4Better aktualisieren wir unsere Daten mindestens einmal jährlich. Für sich rasch verändernde Daten wie z.B. Points of Interest (POIs) und ÖPNV-Daten sind häufigere Aktualisierungen möglich. Die folgende Abbildung veranschaulicht die Hauptdatentypen, die wir verwenden Im darauffolgenden Abschnitt werden die einzelnen Typen näher beschreiben.

![GOAT data basis](/img/data/data_basis/original_files/data_en_blue.png "GOAT data basis")

### Datensätze im Katalog

Die folgenden Datensätze sind im Katalog verfügbar. Sie werden als Feature Layers verwaltet und enthalten räumlichen Merkmale (Punkte, Linien oder Polygone) oder nicht-räumliche Daten (in Tabellenform). Sie können für Analysen und Visualisierungen zu Ihren Projekten hinzugefügt werden. Auch wenn dies keine vollständige Liste der verfügbaren Layer ist, gibt die folgende Übersicht eine Einführung in die wichtigsten Datentypen.

::::note

Dieser Abschnitt enthält technische Details zu den im Katalog verfügbaren Datensätzen. Für eine allgemeine Übersicht und Hinweise zum Hinzufügen von Datensätzen zu Ihren Projekten besuchen Sie bitte den [Katalog](../workspace/catalog).

::::

#### Points of Interest (POIs)
Standorte von häufig genutzten Einrichtungen und Anlaufpunkten, die für die Erreichbarkeitsplanung wichtig sind.

- *Features:*
    - ÖPNV-Haltestellen
	- Einkaufszentren
	- Standorte für Tourismus & Freizeit
	- Gastronomiebetriebe
	- Gesundheitseinrichtungen
	- Bildungseinrichtungen

- *Quellen:*
    [Overture Maps Foundation](https://overturemaps.org/), [Open Street Map (OSM)](https://wiki.openstreetmap.org/), staatliche Behörden, Krankenkassen und Einzelhandelsunternehmen. Bei Bedarf führen wir zusätzliche Datenerhebungen vor Ort durch.

#### Bevölkerung und Gebäude
Bevölkerungsdaten werden oft auf Mikroniveau (z. B. Anzahl der Bewohner eines Gebäudes) bereitgestellt und aus Landkreis, Gemeinde- und Zensusdaten disaggregiert. Dieser Prozess berücksichtigt auch Flächennutzungsinformationen zur Verbesserung der Genauigkeit.

- *Features:*
    - Bevölkerung auf Gebäudeebene - Einwohnerzahl für Landkreise & Gemeinden (Deutschland)
    - Bevölkerung auf lokaler Ebene - Zensus 2022 (Deutschland)
    - Bevölkerung auf europäischer NUTS-3-Ebene (Nomenclature of Territorial Units for Statistics)

- *Quellen:*
    Die Bevölkerungsdaten stammen aus Quellen wie dem [Zensus 2022](https://ergebnisse.zensus2022.de/datenbank/online/), sowie den einzelnen Landkreisen und Gemeinden, während Gebäudedaten in Form von 3D-Stadtmodellen (DGM) der Bundesländer bereitgestellt werden.


#### Verwaltungsgrenzen
Gebiete unter der Zuständigkeit von Regierungs- oder Verwaltungsorganen.

- *Features:*
    - Gemeinden
    - Landkreise
    - Bundesländer
    - Postleitzahlengebiete

- *Quellen:*
    Die [Bundesanstalt für Kartographie und Geodäsie (BKG)](https://www.bkg.bund.de/) und [Open Street Map (OSM)](https://wiki.openstreetmap.org/).

### Netzwerkdatensätze für Routing

Dies sind die Netzwerke, die von GOAT für die Analyse von Routing-Indikatoren zur Erreichbarkeit verwendet werden.

::::info

Während aktuell fest integrierte Netzwerke für ÖPNV- und Straßennetz-Routing genutzt werden, wird es Nutzern zukünftig möglich sein, eigene Netzwerke für Routing-Analysen hochzuladen. Wenn Sie an dieser Funktion interessiert sind, zögern Sie nicht, uns zu [kontaktieren](https://plan4better.de/de/contact/ "Contact Support").

::::

#### Öffentliches Verkehrsnetz
Umfangreiche Daten zum öffentlichen Verkehrsnetz für verschiedene Verkehrsmittel wie Busse, Straßenbahnen, U-Bahnen, Züge und Fähren. Diese werden von GOAT für das [Routing des Öffentlichen Verkehrs](../routing/public_transport) genutzt.

![Netzwerk des öffentlichen Verkehrs](/img/data/data_basis/pt_network_banner.png "Public Transport Network")

- *Features:*
    - Haltestellen (Name, Standort, Typ, Zugänglichkeitsinformationen)
    - Linien (Name, Diensttyp, Zugänglichkeitsinformationen)
    - Fahrten (angefahrene Haltestellen, Abfahrtszeiten)
    - Fahrpläne (Betriebstage, Taktfrequenz)
    - Umstiege & Geschossigkeit (Umsteigevorgaben, Bahnhofstopologie)
    - Linienverläufe (geografische Darstellung der Routen)

- *Quellen:*
    [DELFI](https://www.delfi.de/) für deutschlandweite ÖPNV-Netzwerke und [Open Street Map (OSM)](https://wiki.openstreetmap.org/) für straßenbezogene Informationen, die multimodales Routing ermöglichen und Zugangsinformationen zu Bahnhöfen bieten.

- *Vorbereitung:*
    - Die Daten werden im GTFS (General Transit Feed Specification)-Format erfasst.
    - Haltestellen werden überprüft und korrigiert, um genaue Station-interne- und Bus- und Bahnsteige-Beziehungen zu gewährleisten.
    - Trassen werden überprüft und angepasst, um genaue Diensttypen und Verkehrsarten zu gewährleisten.
    - Das Netzwerk wird optimiert, um für jede Linie nur das häufigste Fahrtmuster zu berücksichtigen.
    - GOAT ermöglicht ÖPNV-Analysen für beliebige Zeitintervalle und drei Wochentagstypen (**Wochentag**, **Samstag**, and **Sonntag**) wobei ein **Dienstag** typischerweise als Referenztag für den Wochentag dient.

#### Straßennetz und Topografie
Umfangreiche Straßennetzdaten, die reale Transportnetzwerke und deren Komponenten repräsentieren: Straßen, Autobahnen, Kreuzungen und spezielle Wege. Diese werden von GOAT für die verschiedenen Routing Berechnungen herangezogen: [Fußgänger](../routing/walking), [Fahrrad](../routing/bicycle), [Pedelec](../routing/bicycle), and [PKW](../routing/car) routing.

![Wege Netzwerk](/img/data/data_basis/street_network_banner.png "Street Network")

- *Quellen:*
    - Vektoren (jeder durchgehende Weg, der nicht durch einen anderen unterbrochen wird)
    - Verbindungen oder Knotenpunkte (jeder Punkt, an dem zwei unterschiedliche Wege aufeinandertreffen)

- *Sources:*
    [Overture Maps Foundation](https://overturemaps.org/) für europaweite Straßennetzdaten und digitale Höhenmodelle (DEM), die wichtige topografische Informationen (Oberflächengradient) von [Copernicus](https://www.copernicus.eu/de) erfassen.

- *Vorbereitung:*
    - Die Daten werden im Geoparquet-Format aus dem ["Transportation theme"](https://docs.overturemaps.org/guides/transportation/) von Overture Maps erfasst.
    - Digitale Höhenmodelle (DEM) für die Region Europa werden erfasst und verarbeitet.
    - Straßenbschnitte und Knoten des Straßennetzwerks werden anhand des  [Uber's H3 grid-based](../further_reading/glossary#h3-grid) Systems indexiert und verarbeitet.
    - Oberflächen- und Steigungsimpedanz werden für jedes Segment unter Verwendung von DEM-Daten berechnet.
    - Verschiedene Attribute jedes Segments werden analysiert, um Straßenklassen, Abbiege- und Einbahnstraßenbeschränkungen sowie Geschwindigkeitsbegrenzungen zu identifizieren.
    - Die modalspezifische Geschwindigkeitsbegrenzung pro Straßentyp wird zur Interpolation von Geschwindigkeitsbegrenzungen verwendet, wo diese nicht definiert ist.
