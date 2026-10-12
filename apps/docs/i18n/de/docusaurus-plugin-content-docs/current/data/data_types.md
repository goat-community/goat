---
sidebar_position: 2
sidebar_label: Feldtypen
description: "Die Feldtypen in GOAT, von Text, Zahl, Boolesch und Datum über automatische laufende Nummern und UUIDs bis zu berechneter Fläche, Umfang, Länge und Formel, dazu Zahlenformat und zulässige Werte."
---

# Feldtypen

Jede Spalte in einem Feature-Datensatz oder einer Tabelle hat einen **Feldtyp**. Er bestimmt, wie GOAT die Werte speichert, wie sie angezeigt werden und welche Werkzeuge die Spalte verwenden können. Diese Seite erklärt die Feldtypen, die GOAT unterstützt.

## Speicherung räumlicher Daten

GOAT trennt die **Metadaten** eines Datensatzes von den **Daten** selbst:

- **Metadaten**: Name, Beschreibung, Felddefinitionen, Gestaltung und Freigabeeinstellungen des Datensatzes. Diese liegen in einer **PostgreSQL**-Datenbank.
- **Daten**: die Geometrien und Attributwerte. Sie werden in **DuckLake** gespeichert, einem analytischen Speicher auf Basis von Parquet-Dateien im Objektspeicher. Dadurch kann GOAT auch große Datensätze schnell abfragen und analysieren.

Alle Geometrien werden im Koordinatenbezugssystem **EPSG:4326** gespeichert (Längen- und Breitengrad in Grad). Gemessen wird jedoch nicht in Grad: **Fläche**-, **Umfang**- und **Länge**-Spalten werden auf der gekrümmten Erdoberfläche berechnet, sodass ihre Werte echte Meter sind und auch über große Gebiete hinweg genau bleiben.

Einen umfassenderen Überblick, wie die Plattform zusammenspielt, gibt die Seite [Architektur](../nerdy_content/architecture) (nur auf Englisch).

## Unterstützte Feldtypen

| Feldtyp | Was er enthält | Beispiele |
|---------|----------------|-----------|
| **Text** | Beliebigen Text | Straßennamen, Kategorien, Beschreibungen |
| **Zahl** | Ganze Zahlen oder Dezimalzahlen | `1`, `-5`, `3.14`, `45.67` |
| **Boolesch** | Wahr- oder Falsch-Werte | `true`, `false` |
| **Datum** | Einen Zeitpunkt | `2024-01-15 14:30:00` |
| **Laufende Nummer** | Eine fortlaufende Nummer, die GOAT jedem Feature vergibt | `1`, `2`, `3` |
| **UUID (eindeutige Kennung)** | Eine eindeutige Kennung, die GOAT jedem Feature vergibt | `0625b5a7-50e1-4cfa-8392-7b0852e0d980` |
| **Fläche** | Die Fläche eines Polygons | `1,25 ha`, `340 m²` |
| **Umfang** | Die Umrisslänge eines Polygons | `820 m` |
| **Länge** | Die Länge einer Linie | `1,4 km` |
| **Formel** | Einen aus anderen Spalten berechneten Wert | `population / area` |

### Spalten, die Sie selbst befüllen

**Text**, **Zahl**, **Boolesch** und **Datum** enthalten die Werte, die Sie eingeben oder importieren. Sie können sie jederzeit zu einem Datensatz hinzufügen, und es sind die Typen, die beim Anlegen eines neuen Datensatzes zur Verfügung stehen.

Eine **Zahl**-Spalte lässt sich für die Anzeige formatieren. Die Formatierung ändert nur, wie der Wert in GOAT aussieht. Der gespeicherte Wert bleibt unverändert, und Werkzeuge rechnen weiterhin mit der vollständigen Zahl.

| Einstellung | Wirkung auf `1234567.891` |
|-------------|---------------------------|
| **Nachkommastellen** | `2` rundet die Anzeige auf `1234567,89`; `auto` überlässt GOAT die Wahl |
| **Tausendertrennzeichen anzeigen** | `1.234.567,891` |
| **Große Zahlen abkürzen** | `1,2 Mio.` |
| **Vorzeichen immer anzeigen** | `+1234567,891`, damit positive Werte genauso deutlich gekennzeichnet sind wie negative |

Dieselben Einstellungen stehen für **Fläche**-, **Umfang**- und **Länge**-Spalten zur Verfügung. Dort können Sie zusätzlich die **Einheit** wählen, in der der Wert angezeigt wird: `m²`, `ha` oder `km²` für Fläche und `m` oder `km` für Umfang und Länge. Bei `auto` wählt GOAT eine zum Wert passende Einheit.

GOAT zeigt dabei eine Live-Vorschau, sodass Sie das Ergebnis vor dem Speichern sehen.

### Spalten, die GOAT automatisch vergibt

Spalten vom Typ **Laufende Nummer** und **UUID (eindeutige Kennung)** befüllt GOAT selbst: Jedes Feature erhält seinen Wert beim Anlegen, egal ob Sie es auf der Karte zeichnen, in der Datentabelle eine Zeile hinzufügen oder es über die API hochladen. Den Wert können Sie weder eingeben noch ändern. Solange Sie ein Feature anlegen, zeigt das Feld <code>Wird automatisch vergeben</code>; nach dem Speichern erscheint der Wert. Beide Typen stehen beim Anlegen eines neuen Datensatzes und beim Bearbeiten der Felder eines bestehenden Datensatzes zur Verfügung.

- Eine **Laufende Nummer** zählt hoch: Jedes neue Feature erhält die nächste Nummer nach der höchsten bisher vergebenen. Mit <code>Beginnt bei</code> legen Sie die erste Nummer fest (Standard `1`), zum Beispiel `1000` für Vorhabennummern. Nummern werden nie erneut vergeben, auch nicht nach dem Löschen: Wird ein Feature gelöscht, bleibt eine Lücke, die Nummern der übrigen Features ändern sich nie, und das nächste neue Feature erhält immer eine noch nie vergebene Nummer, selbst wenn das gelöschte Feature die höchste hatte.
- Eine **UUID (eindeutige Kennung)** gibt jedem Feature eine zufällige Kennung, die auch über Datensätze hinweg eindeutig ist. Das ist nützlich, wenn die Daten mit anderen Systemen ausgetauscht werden.

Fügen Sie eine solche Spalte zu einem Datensatz hinzu, der bereits Features enthält, befüllt GOAT sie für alle auf einmal: Eine Laufende Nummer nummeriert sie ab <code>Beginnt bei</code> in der Reihenfolge, in der die Features angelegt wurden. Eine mit <code>Als neuen Layer speichern</code> erstellte Kopie behält die Werte und zählt nach der höchsten jemals im Original vergebenen Nummer weiter. Ein Datensatz aus einem importierten Projekt zählt ab seiner eigenen höchsten Nummer weiter.

Für Filter, Gestaltung und Popups ist eine Laufende Nummer eine Zahl und eine UUID ein Text.

#### Eine bestehende Zahl-Spalte in eine Laufende Nummer umwandeln

Haben Sie bisher Nummern von Hand in eine **Zahl**-Spalte eingetragen, kann GOAT die Nummerierung übernehmen, ohne die Spalte umzubenennen. Workflows, Filter und Dashboards, die sie verwenden, funktionieren weiter.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie in der Datentabelle auf <code>Felder bearbeiten</code> und wählen Sie die <strong>Zahl</strong>-Spalte aus.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Ändern Sie den <code>Feldtyp</code> auf <code>Laufende Nummer</code>. Optional legen Sie <code>Beginnt bei</code> fest: Diese Nummer gilt für Features, die noch keine Nummer haben, wenn sie höher als die bestehenden Nummern ist.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Klicken Sie auf <code>Speichern</code> und bestätigen Sie mit <code>Typ ändern</code>.</div>
</div>

Bestehende Werte bleiben, wie sie sind, und Features ohne Nummer erhalten eine. Neue Features bekommen die nächste Nummer nach der höchsten; Lücken werden nicht aufgefüllt. Kommt eine Nummer mehrfach vor oder ist ein Wert keine ganze Zahl, lehnt GOAT die Änderung ab und nennt den Grund: Bereinigen Sie diese Werte zuerst. Auf demselben Weg machen Sie aus einer Laufenden Nummer wieder eine <code>Zahl</code>; die Werte bleiben erhalten. Eine UUID lässt sich nicht aus einer bestehenden Spalte erzeugen.

### Spalten, die GOAT berechnet

**Fläche**, **Umfang**, **Länge** und **Formel** sind **berechnete** Spalten: GOAT leitet ihre Werte ab und hält sie aktuell, daher lassen sie sich nicht von Hand bearbeiten. Sie werden angeboten, wenn Sie die Felder eines bestehenden Datensatzes bearbeiten. Ein neuer Datensatz enthält noch keine Daten, aus denen sie berechnet werden könnten.

**Formel** lässt sich zu jedem Datensatz hinzufügen. Welche Messgrößen zur Verfügung stehen, hängt von der Geometrie Ihres Datensatzes ab, denn nicht jede Form lässt sich gleich messen:

- **Polygone**: Fläche und Umfang
- **Linien**: Länge
- **Punkte**: keine davon, da ein Punkt keine Ausdehnung hat
- **Tabellen** (ohne Geometrie): keine davon

Eine **Formel**-Spalte wird über einen Ausdruck definiert, den Sie im Formel-Editor schreiben. GOAT berechnet sie neu, sobald sich die zugrunde liegenden Daten ändern.

## Zulässige Werte einer Spalte einschränken

**Text**- und **Zahl**-Spalten können eine Liste **zulässiger Werte** führen. Alle, die den Datensatz bearbeiten, wählen dann aus dieser Liste, statt frei zu tippen. Das hält Kategorien einheitlich. Kein `bus stop`, `Bus Stop` und `bus_stop` mehr in derselben Spalte.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Öffnen Sie in der Datentabelle die <strong>Text</strong>- oder <strong>Zahl</strong>-Spalte, die Sie einschränken möchten: entweder über <code>Felder bearbeiten</code> und Auswahl aus der Liste, oder über das <img src={require('/img/icons/3dots.png').default} alt="Weitere Optionen" style={{ maxHeight: "16px", maxWidth: "16px", verticalAlign: "middle"}}/> Menü der Spaltenüberschrift und <code>Feld bearbeiten</code>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Geben Sie unter <code>Zulässige Werte</code> einen Wert ein und drücken Sie <code>Enter</code>. Wiederholen Sie das für jeden Wert, den Sie zulassen möchten.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Sobald die Liste mindestens einen Wert enthält, erscheint der Schalter <code>Andere Werte zulassen</code>. Aktivieren Sie ihn, wenn die Liste ein Vorschlag und keine Vorgabe sein soll.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Klicken Sie auf <code>Speichern</code>.</div>
</div>

Eine leere Liste lässt beliebige Werte zu. So beginnt jede Spalte.

:::info Reservierte Spaltennamen
Einige Namen verwendet GOAT intern; sie können nicht an eine Spalte vergeben werden, darunter `id`, `geometry` und `geom`. Geben Sie einen davon ein, markiert GOAT das Feld sofort und lässt das Speichern erst zu, wenn Sie den Namen ändern.
:::

## Feldtypen anzeigen

GOAT kennzeichnet jede Spalte mit einem kleinen **Feldtyp-Symbol**: `A` für Text, `123` für Zahl, `#` für Laufende Nummer, `ID` für UUID und ein Symbol für die übrigen Typen. Fahren Sie mit der Maus darüber, um den Namen des Feldtyps zu sehen.

Das Symbol erscheint überall dort, wo Spalten aufgelistet sind: in der Datentabelle, in der Feldliste der Layer-Einstellungen, in Spaltenfiltern und in den Feldauswahlen von Werkzeugen und Formel-Editor.

So sehen Sie es in der Datentabelle:

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie auf <img src={require('/img/icons/3dots.png').default} alt="Weitere Optionen" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> <code>Weitere Optionen</code> bei Ihrem Layer.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Wählen Sie <code>Daten anzeigen</code> aus dem Menü.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In der Datentabelle wird das Feldtyp-Symbol neben jedem Spaltennamen angezeigt.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/data/view_data_de.webp').default} alt="Weitere Optionen" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
  <p style={{ textAlign: 'center', fontStyle: 'italic', marginTop: '8px', color: '#666' }}>Die Option „Daten anzeigen“ aufrufen</p>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/data/data-table.webp').default} alt="Datentabelle mit Feldtypen" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
  <p style={{ textAlign: 'center', fontStyle: 'italic', marginTop: '8px', color: '#666' }}>Datentabelle mit dem Feldtyp neben jedem Spaltennamen</p>
</div>
