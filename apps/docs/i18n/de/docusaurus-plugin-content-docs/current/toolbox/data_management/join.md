---
description: "Hängen Sie Felder eines Join-Layers über Attribute, räumliche Beziehung oder beides an einen Ziel-Layer an, als Inner oder Left Join, optional mit Statistiken."
sidebar_position: 1
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Objekte verbinden

Dieses Werkzeug ermöglicht es Ihnen, **Daten aus zwei Layern basierend auf Attributabgleichen oder räumlichen Beziehungen zu kombinieren**. Das Ergebnis ist ein neuer Layer, der die Geometrie und Attribute des Ziel-Layers enthält, angereichert mit Attributen des Join-Layers.

## 1. Erklärung

Das Verknüpfen ist der Prozess des Anhängens von Feldern aus einem Layer (Join-Layer) an einen anderen Layer (Ziel-Layer).

**GOAT unterstützt drei Verknüpfungsmethoden:**

- **Attributiv**: Abgleich von Features basierend auf einem gemeinsamen Feld (z. B. Postleitzahl in beiden Layern).
- **Räumlich**: Abgleich von Features basierend auf ihrer geometrischen Beziehung (z. B. Features, die sich schneiden).
- **Räumlich und Attributiv**: Erfordert sowohl eine räumliche Überschneidung als auch ein passendes Attribut.

<Tabs>
<TabItem value="attribute" label="Attribut-Verknüpfung" default className="tabItemBox">

Eine attributive Verknüpfung verbindet zwei Layer durch den Vergleich von Werten in einem gemeinsamen Feld. Jedes Feature im Ziel-Layer wird mit Features im Join-Layer abgeglichen, bei denen die Feldwerte übereinstimmen.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/toolbox/data_management/join/attribute_join_basic_de.png').default} alt="Einfache attributive Verknüpfung" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

### Verbindungstyp

Der `Verbindungstyp` bestimmt, welche Features in der Ausgabe erscheinen:

- **Inner Join**: nur Features mit einer Übereinstimmung in beiden Layern werden behalten. Features ohne Übereinstimmung werden entfernt.
- **Left Join**: alle Features des Ziel-Layers werden behalten. Features ohne Übereinstimmung erhalten `NULL` für die verknüpften Felder.

### Eins zu Eins

Wenn jedes Ziel-Feature höchstens einem Feature im Join-Layer entspricht, enthält das Ergebnis die gleiche Anzahl von Zeilen wie der Ziel-Layer.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/toolbox/data_management/join/attribute_join_one_to_one_de.webp').default} alt="Eins-zu-Eins-Verknüpfung: Inner Join vs. Left Join" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

### Eins zu Viele

Wenn ein Ziel-Feature mehreren Features im Join-Layer entspricht, enthält das Ergebnis eine Zeile pro Übereinstimmung: Die Ziel-Geometrie wird für jeden passenden Datensatz wiederholt.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/toolbox/data_management/join/attribute_join_one_to_many_de.webp').default} alt="Eins-zu-Viele-Verknüpfung: Inner Join vs. Left Join" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

</TabItem>

<TabItem value="spatial" label="Räumliche Verknüpfung" className="tabItemBox">

Eine räumliche Verknüpfung verbindet Features basierend auf ihrer geometrischen Beziehung, ein gemeinsames Feld ist daher nicht erforderlich. Jedes Feature im Ziel-Layer wird mit Features im Join-Layer abgeglichen, die die ausgewählte räumliche Beziehung erfüllen.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: "32px", marginBottom: "32px" }}>
  <img src={require('/img/toolbox/data_management/join/spatial_relationships_de.webp').default} alt="Arten räumlicher Beziehungen" style={{ maxHeight: "auto", maxWidth: "70%", objectFit: "cover"}}/>
</div>

**Verfügbare räumliche Beziehungen:**

| Beziehung | Beschreibung |
|---|---|
| `Schneidet` | Ziel- und Join-Features teilen beliebige Geometrie (Punkt, Linie oder Fläche). |
| `Überlappt` | Features überlappen sich teilweise, keines ist vollständig im anderen enthalten. |
| `Enthält vollständig` | Ziel-Feature enthält das Join-Feature vollständig. |
| `Bedeckend` | Ziel-Feature enthält das Join-Feature vollständig. |
| `Disjunkt` | Features haben keine räumliche Beziehung: Sie berühren oder überlappen sich nicht. |
| `Berührt` | Features teilen eine Grenze, überlappen sich jedoch nicht. |
| `In einer Entfernung von` | Features liegen innerhalb einer festgelegten Entfernung voneinander. |
| `Identisch mit` | Features haben exakt dieselbe Geometrie. |
| `Vollständig innerhalb von` | Ziel-Feature liegt vollständig innerhalb des Join-Features. |
| `Bedeckt` | Ziel-Feature wird vom Join-Feature bedeckt. |

</TabItem>

<TabItem value="spatial_attribute" label="Räumliche und Attribut-Verknüpfung" className="tabItemBox">

Diese Methode erfordert **sowohl** eine räumliche Beziehung als auch einen übereinstimmenden Attributwert. Ein Feature wird nur verknüpft, wenn beide Bedingungen gleichzeitig erfüllt sind. Verwenden Sie dies, wenn der Standort allein nicht ausreicht, z. B. für Gebäude innerhalb eines Bezirks, die zusätzlich dieselbe Nutzungsklassifikation aufweisen.

In diesem Beispiel werden Bevölkerungsdaten mit Berliner Stadtbezirken verknüpft. Ein rein attributiver Abgleich über das Feld `namgem` könnte fälschlicherweise Bevölkerungswerte einer Stadt wie Potsdam zuweisen, wenn der Name übereinstimmt. Durch die zusätzliche räumliche Bedingung (`Schneidet`) wird sichergestellt, dass nur Punkte verknüpft werden, die sich sowohl innerhalb des richtigen Bezirks befinden als auch denselben `namgem`-Wert aufweisen.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/toolbox/data_management/join/spatial_attribute_join_de.webp').default} alt="Räumliche und Attributive Verknüpfung Beispiel" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "cover"}}/>
</div>

</TabItem>
</Tabs>

## 2. Beispiel-Anwendungsfälle

### Attributive Verknüpfung
- Bevölkerungsdaten zu Postleitzahl-Gebieten hinzufügen (Abgleich über Postleitzahl).
- Umfragedaten mit Zensus-Bezirksgrenzen kombinieren (Abgleich über Bezirks-ID).

### Räumliche Verknüpfung
- Anzahl der Schulen in jedem Stadtbezirk zählen (Punkte in Polygonen).
- Die nächstgelegene Feuerwehrstation zu jedem Gebäude finden.
- Summierung der Gesamtlänge von Straßen innerhalb eines Parks.

### Räumliche und Attributive Verknüpfung
- Gebäude innerhalb einer Hochwasserzone abgleichen, die zudem denselben Gebäudetyp aufweisen.

## 3. Wie verwendet man das Werkzeug?

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie auf <code>Toolbox</code> <img src={require('/img/icons/toolbox.png').default} alt="Toolbox" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. Unter <code>Datenmanagement</code> klicken Sie auf <code>Objekte verbinden</code>.</div>
</div>

### Layer auswählen

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Wählen Sie Ihren <code>Ziel-Layer</code>: den Hauptlayer, dessen Geometrie Sie behalten möchten.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie Ihren <code>Join-Layer</code>: den Layer, der die Felder enthält, die Sie hinzufügen möchten.</div>
</div>

### Zuordnungsmethode

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Aktivieren Sie unter <code>Zuordnungsmethode</code> die gewünschte Methode: <code>Attribut-Zuordnung</code>, <code>Räumliche Zuordnung</code> oder beide.</div>
</div>

<Tabs>
<TabItem value="attribute" label="Attributiv" default className="tabItemBox">

Klicken Sie unter <code>Attributbeziehung</code> auf <code>Hinzufügen Zuordnungsfelder</code>, und wählen Sie dann das <code>Ziel-Feld</code> und das <code>Join-Feld</code>: das gemeinsame Feld, das zur Zuordnung von Features zwischen den beiden Layern verwendet wird.

</TabItem>

<TabItem value="spatial" label="Räumlich" className="tabItemBox">

Wählen Sie unter <code>Räumliche Beziehung</code> die gewünschte räumliche Beziehung aus. Bei Auswahl von <code>In einer Entfernung von</code> geben Sie die Entfernung und die Einheit an.

</TabItem>

<TabItem value="spatial_attribute" label="Räumlich und Attributiv" className="tabItemBox">

Konfigurieren Sie sowohl die <code>Räumliche Zuordnung</code> (räumliche Beziehung auswählen) als auch die <code>Attributbeziehung</code> (auf <code>Hinzufügen Zuordnungsfelder</code> klicken und Abgleichfelder auswählen). Beide Bedingungen müssen erfüllt sein, damit ein Feature verknüpft wird.

</TabItem>
</Tabs>

### Verknüpfungsoptionen

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Wählen Sie den <code>Verbindungstyp</code>: <code>Inner Join</code> (nur übereinstimmende Features behalten) oder <code>Left Join</code> (alle Ziel-Features behalten, nicht übereinstimmende erhalten NULL).</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Wählen Sie unter <code>Übereinstimmungen</code>: <code>Eins zu Eins</code> oder <code>Eins zu Viele</code>.</div>
</div>


<div class="step">
  <div class="step-number">7</div>
  <div class="content">
  Aktivieren Sie optional <code>Verknüpfungsfelder hinzufügen</code>, um festzulegen, welche Felder aus dem Join-Layer in die Ausgabe aufgenommen werden sollen, und/oder aktivieren Sie <code>Statistiken berechnen</code>, um aggregierte Werte zu berechnen, wenn mehrere Join-Layer-Datensätze einem einzelnen Ziel-Layer-Feature entsprechen. Wenn <code>Statistiken berechnen</code> aktiviert ist, konfigurieren Sie die Statistik:
  <ul>
    <li><code>Operation auswählen</code>: <code>Anzahl</code>, <code>Summe</code>, <code>Min</code>, <code>Max</code>, <code>Durchschnitt</code> oder <code>Standardabweichung</code>.</li>
    <li><code>Feld auswählen</code>: wählen Sie das numerische Feld aus dem Join-Layer, das aggregiert werden soll (ausgeblendet bei <code>Anzahl</code>).</li>
    <li><code>Name der Ergebnisspalte</code> (optional): Name für die Ausgabespalte. Leer lassen für Standardname (z. B. <code>count</code> oder <code>Feldname_Operation</code>).</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Klicken Sie auf <code>Ausführen</code>, um die Verknüpfung durchzuführen. Der Ergebnis-Layer wird der Karte hinzugefügt.</div>
</div>
