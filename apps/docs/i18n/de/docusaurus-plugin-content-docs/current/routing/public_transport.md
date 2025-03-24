---
sidebar_position: 3

---

# Öffentliche Verkehrsmittel

Das **Verkehrsmittel ÖPNV** in GOAT ist essentiell für die Durchführung von Analysen, welche Fahrten mit öffentlichen Verkehrsmitteln beinhalten.

## 1. Zielsetzung

Das ÖPNV-Routing erleichtert die **intermodale Analyse** durch die Integration von Ein- und Ausstiegsmodi, wie z.B. zu Fuß oder mit dem Fahrrad zum und vom Bahnhof. Dies ist komplexer als die anderen Routing-Modi, da es die Zusammenführung verschiedener Datensätze (z. B. Bürgersteige und Radwege, Haltestellen und Fahrpläne des öffentlichen Verkehrs usw.) und Berechnungsansätze erfordert.

Das Routing im öffentlichen Verkehr wird in GOAT für Indikatoren wie [Einzugsgebiete](../toolbox/accessibility_indicators/catchments) verwendet.


## 2. Daten

### Transit-Daten

Verwendet Daten im Format **[GTFS](https://gtfs.org/)** (General Transit Feed Specification) für statische Informationen zum öffentlichen Verkehrsnetz (Haltestellen, Linien, Fahrpläne, Umsteigeverbindungen und mehr).


### Straßendaten

Integriert straßenbezogene Informationen aus **[OpenStreetMap](https://wiki.openstreetmap.org/)** zur Unterstützung multimodaler Routenführung und realistischer Wegeketten (einschließlich Gehwegen, Radwegen und Zebrastreifen).


## 3. Technische Einzelheiten

PDas Routing für den öffentlichen Verkehr wird mit der **[R5 Routing Engine](https://github.com/conveyal/r5)** (_Rapid Realistic Routing on Real-world and Reimagined networks_) durchgeführt. R5 ist die Routing-Engine von **[Conveyal](https://conveyal.com/)**, einer webbasierten Plattform, die es den Nutzern ermöglicht, Verkehrsszenarien zu erstellen und sie im Hinblick auf kumulative Möglichkeiten und Erreichbarkeitsindikatoren zu bewerten.


### Routing-Optionen

#### Modi

Analysen für die folgenden öffentlichen Verkehrsmodi werden derzeit von GOAT unterstützt. Wählen Sie einen oder mehrere aus – beachten Sie dabei, dass einige Modi nicht in allen Regionen verfügbar sind.

`Bus`, `Straßenbahn`, `Bahn`, `U-Bahn`, `Fähre`, `Seilbahn`, `Gondel`, `Standseilbahn`.

#### Reisezeitlimit

Die maximale Reisedauer, die beim Routing im öffentlichen Verkehr berücksichtigt wird. Aktuell wird ein Maximum von `90 Minuten` unterstützt. Dies beinhaltet auch die Zeit für den Zugang und Abgang zu bzw. von den ÖPNV-Haltestellen.

#### Tag

Der Wochentag, der beim Routing im öffentlichen Verkehr berücksichtigt wird. Wählen Sie zwischen `Werktag`, `Samstag` und `Sonntag`. Dies ist nützlich, um Unterschiede im Verkehrsangebot zwischen Werktagen und Wochenenden zu analysieren.

#### Start- und Endzeit

Ein Zeitfenster für das Routing im öffentlichen Verkehr. Es werden alle schnellstmöglichen Verbindungen innerhalb dieses Zeitfensters berücksichtigt, was z. B. zu einem möglichst großen Einzugsgebiet vom angegebenen Startpunkt führen kann.  
Eine Verbindung gilt als innerhalb des Zeitfensters liegend, **ausschließlich basierend auf ihrer Startzeit** – unabhängig von ihrer Endzeit oder Gesamtdauer.


#### Sonstiges (Standardkonfigurationen)

Die folgenden Standardkonfigurationen werden beim Routing für den öffentlichen Verkehr verwendet. Sie sind derzeit nicht vom Benutzer konfigurierbar.

- **Access Mode:** Zu Fuß
- **Egress Mode:** Zu Fuß
- **Abklingfunktionstyp:** Logistisch
- **Standardabweichung:** 12 Minuten
- **Breite:** 10 Minuten
- **Gehgeschwindigkeit:** 5 km/h
- **Maximale Gehzeit:** 20 Minuten
- **Fahrradgeschwindigkeit:** 15 km/h
- **Maximale Fahrradzeit:** 20 Minuten
- **Radverkehrsbelastung:** 4
- **Maximale Fahrten:** 4
- **Zoomstufe:** 9
- **Perzentile:** Ersten
- **Monte Carlo zieht:** 200