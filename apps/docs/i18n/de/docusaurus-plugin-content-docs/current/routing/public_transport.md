---
sidebar_position: 3

---

# Öffentliche Verkehrsmittel

Das **Verkehrsmittel ÖPNV** in GOAT ist essentiell für die Durchführung von Analysen, welche Fahrten mit öffentlichen Verkehrsmitteln beinhalten.

## 1. Zielsetzung

Das ÖPNV-Routing erleichtert die **intermodale Analyse** durch die Integration von Ein- und Ausstiegsmodi, wie z.B. zu Fuß oder mit dem Fahrrad zum und vom Bahnhof. Dies ist komplexer als die anderen Routing-Modi, da es die Zusammenführung verschiedener Datensätze (z. B. Bürgersteige und Radwege, Haltestellen und Fahrpläne des öffentlichen Verkehrs usw.) und Berechnungsansätze erfordert.

ÖPNV-Routing wird für viele Indikatoren in GOAT verwendet, wie z. B. [Einzugsgebiete](../toolbox/accessibility_indicators/catchments) und [Heatmaps](../toolbox/accessibility_indicators/connectivity).

Darüber hinaus passt sich mit [Szenarien für das Straßennetz](../Scenarios#4-straßennetz---kanten), ein **flexibler Routing-Algorithmus** an Szenarienänderungen bei Erreichbarkeitsanalysen in GOAT an.

### Konfigurierbare Optionen für Analysen

- `Wochentag`: Wählen Sie zwischen Wochentag, Samstag oder Sonntag.
- `Startzeit` und `Endzeit`: Geben Sie das Zeitfenster für die Analyse an.



## 2. Daten

### Transit-Daten

Verwendet Daten in **[GTFS](https://developers.google.com/transit/gtfs)** (General Transit Feed Specification) für statische Informationen zum öffentlichen Verkehrsnetz (Haltestellen, Routen, Fahrpläne, Umsteigeverbindungen).


### Straßendaten

Bezieht Informationen auf Straßenebene von  **[OpenStreetMap](https://wiki.openstreetmap.org/)** ein, um multimodales Routing und echte Wegeverbindungen zu unterstützen (einschließlich Bürgersteige, Radwege und Fußgängerüberwege).


## 3. Technische Einzelheiten

PDas Routing für den öffentlichen Verkehr wird mit der **[R5 Routing Engine](https://github.com/conveyal/r5)** (_Rapid Realistic Routing on Real-world and Reimagined networks_) durchgeführt. R5 ist die Routing-Engine von **[Conveyal](https://conveyal.com/)**, einer webbasierten Plattform, die es den Nutzern ermöglicht, Verkehrsszenarien zu erstellen und sie im Hinblick auf kumulative Möglichkeiten und Erreichbarkeitsindikatoren zu bewerten.


### Routing-Optionen

#### Modi
'Bus', 'Straßenbahn', 'Bahn', 'U-Bahn', 'Fähre', 'Seilbahn', 'Gondel', 'Standseilbahn'.

#### Zugangs- und Ausstiegsmodi

- **Zugangsmodus:** Wie die Nutzer von ihrem Ausgangsort zu einer Haltestelle gelangen (`zu Fuß` `Fahrrad` `Auto`).
- **Ausstiegsmodus:** Wie die Benutzer von einer Haltestelle zu ihrem Ziel gelangen (`zu Fuß` `Fahrrad`).


#### Sonstiges (Standardkonfigurationen)

Die folgenden Standardkonfigurationen werden beim Routing für den öffentlichen Verkehr verwendet. Sie sind derzeit nicht vom Benutzer konfigurierbar.

- **Abklingfunktionstyp:** logistisch
- **Standardabweichung:** 12 Minuten
- **Breite:** 10 Minuten
- **Gehgeschwindigkeit:** 1,39 km/h
- **Maximale Gehzeit:** 20 Minuten
- **Fahrradgeschwindigkeit:** 4,166666666666667 km/h
- **Maximale Fahrradzeit:** 20 Minuten
- **Radverkehrsbelastung:** 4
- **Maximale Fahrten:** 4
- **Zoomstufe:** 9
- **Perzentile:** 5
- **Monte Carlo zieht:** 200