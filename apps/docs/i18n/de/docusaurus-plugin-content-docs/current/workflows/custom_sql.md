---
description: "Schreiben Sie im Knoten Benutzerdefiniertes SQL Abfragen auf bis zu drei verbundene Eingaben (input_1 bis input_3), mit räumlichen Funktionen und Variablen."
---

# Benutzerdefiniertes SQL

:::warning Erweiterte Funktion
Dies ist eine erweiterte Funktion, die für Benutzer mit SQL-Kenntnissen gedacht ist. Falsche Abfragen können dazu führen, dass Workflows fehlschlagen oder unerwartete Ergebnisse liefern. Wenn Sie Hilfe beim Schreiben von SQL-Abfragen benötigen, können Sie KI-Assistenten verwenden, um Code zu generieren und zu erklären.
:::

Das Werkzeug **Benutzerdefiniertes SQL** ermöglicht es Ihnen, benutzerdefinierte SQL-Abfragen für Datenanalysen direkt innerhalb Ihrer Workflows zu schreiben. Diese mächtige Funktion ermöglicht erweiterte Datenverarbeitung, die über GOATs eingebaute Werkzeuge hinausgeht.

## Übersicht

Das Werkzeug Benutzerdefiniertes SQL verbindet sich mit GOATs DuckDB Backend und gibt Ihnen direkten Zugriff auf die Abfrage Ihrer Datensätze mit SQL-Syntax. Sie können:

- Komplexe analytische Abfragen ausführen
- Mehrere Datensätze verknüpfen
- Aggregationen und statistische Berechnungen durchführen  
- Abgeleitete Datensätze mit benutzerdefinierter Logik erstellen
- Auf erweiterte räumliche Funktionen zugreifen

## Verwendung von Benutzerdefiniertes SQL

### Hinzufügen des Werkzeugs

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Suchen Sie im Tab <strong>Werkzeuge</strong> des rechten Panels unter <strong>Datenmanagement</strong> das Werkzeug <strong>Benutzerdefiniertes SQL</strong> und ziehen Sie es auf Ihre Workflow-Leinwand.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Verbinden Sie bis zu drei Datensatz- oder Werkzeug-Knoten, um Datenquellen für Ihre Abfrage bereitzustellen. Sie werden unter <strong>Verbundene Eingaben</strong> aufgeführt.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Klicken Sie auf den Knoten Benutzerdefiniertes SQL, um das <strong>Konfigurations-Panel</strong> rechts zu öffnen.</div>
</div>

### Schreiben von SQL-Abfragen

Klicken Sie im Abschnitt **SQL-Abfrage** des Konfigurations-Panels auf **SQL-Abfrage schreiben** (bzw. **SQL-Abfrage bearbeiten**, sobald eine Abfrage vorhanden ist), um den **SQL-Editor** zu öffnen, und schreiben Sie Ihre Abfrage in das Eingabefeld oben:

```sql
SELECT
  h.*,
  p.population_density
FROM input_1 h
JOIN input_2 p ON ST_Intersects(h.geometry, p.geometry)
WHERE p.population_density > 1000
```

Der Editor schreibt SQL-Schlüsselwörter automatisch groß und schlägt während der Eingabe Tabellen- und Spaltennamen vor; mit `Tab` übernehmen Sie einen Vorschlag. Im Tab **Aufbau** unter dem Editor wählen Sie links **Tabellen**, **Operatoren** oder eine Funktionskategorie und klicken in der mittleren Liste auf einen Eintrag, um ihn an der Cursorposition einzufügen; eine Spalte wird mit ihrem Tabellennamen eingefügt, zum Beispiel `input_1.height`. Das Panel **Hilfe** rechts beschreibt den Eintrag unter dem Mauszeiger.

Wenn die Abfrage fertig ist, klicken Sie auf **Anwenden**, um sie im Knoten zu speichern. Die Abfrage wird dann im Abschnitt **SQL-Abfrage** angezeigt; klicken Sie darauf, um den Editor erneut zu öffnen.

#### Eingabe-Referenzen

- **input_1, input_2, input_3**: Referenzieren Sie Ihre verbundenen Datensätze mit diesen Tabellennamen
- Die Nummer entspricht der Verbindungsreihenfolge am Knoten
- Sie können bis zu 3 Eingabedatensätze pro Knoten Benutzerdefiniertes SQL verbinden

#### Zusätzliche Layer

Neben den verbundenen Eingaben können Sie bis zu zwei weitere Layer abfragen, ohne sie auf der Leinwand zu verbinden. Klicken Sie unter **Zusätzliche Layer** auf **Layer hinzufügen** und wählen Sie **Aus Projekt** oder **Meine Datensätze**. Jeder hinzugefügte Layer wird über seinen **Tabellenalias** referenziert (standardmäßig `extra_1` und `extra_2`), den Sie ändern können; ein Alias darf nur Buchstaben, Ziffern und Unterstriche enthalten.

#### Geometrie und Einheiten

Jeder Layer speichert seine Geometrie in einer Spalte namens `geometry`, als geografische Länge und Breite in WGS 84 (EPSG:4326). Räumliche Funktionen messen daher in Grad: `ST_Distance(a.geometry, b.geometry)` liefert Grad, keine Meter. Für Meter und Quadratmeter transformieren Sie die Geometrie zuerst in ein projiziertes Koordinatensystem, zum Beispiel UTM-Zone 32N, die den größten Teil Deutschlands abdeckt:

```sql
ST_Transform(geometry, 'EPSG:4326', 'EPSG:25832', always_xy := true)
```

Für andere Regionen verwenden Sie die UTM-Zone des Gebiets. Geben Sie die ursprüngliche Spalte `geometry` zurück oder transformieren Sie das Ergebnis zurück nach EPSG:4326, damit es an der richtigen Stelle auf der Karte erscheint.

#### Verfügbare Funktionen

Das Werkzeug Benutzerdefiniertes SQL unterstützt Standard-SQL-Funktionen plus räumliche Operationen:

**Räumliche Funktionen:**
- `ST_Intersects()` - Prüft, ob sich Geometrien überschneiden
- `ST_Within()` - Testet, ob eine Geometrie innerhalb einer anderen liegt
- `ST_DWithin()` - Prüft, ob Geometrien höchstens eine bestimmte Entfernung voneinander haben
- `ST_Distance()` - Berechnet Entfernungen zwischen Geometrien
- `ST_Buffer()` - Erstellt Puffer um Geometrien
- `ST_Area()` - Berechnet Geometriefläche
- `ST_Length()` - Berechnet Linienlänge
- `ST_Transform()` - Transformiert Geometrien in ein anderes Koordinatensystem

Entfernungen, Flächen, Längen und Puffergrößen gelten in den Einheiten des Koordinatensystems; siehe [Geometrie und Einheiten](#geometrie-und-einheiten).

**Analytische Funktionen:**
- `AVG()`, `SUM()`, `COUNT()` - Statistische Aggregationen
- `PERCENTILE_CONT()` - Berechnet Perzentile
- `ROW_NUMBER()`, `RANK()` - Fensterfunktionen
- `CASE WHEN` - Bedingte Logik

### Abfrage-Validierung

<div class="step">
  <div class="step-number">1</div>
  <div class="content"><strong>Automatische Prüfung</strong>: Kurz nachdem Sie aufhören zu tippen, wird die Abfrage gegen die Spalten ihrer Eingabetabellen geprüft. Ein grünes Häkchen in der oberen rechten Ecke des Editors zeigt an, dass die Abfrage gültig ist. Ist sie ungültig, erscheint ein rotes Kreuz, der Rahmen des Editors wird rot und die erste Fehlermeldung wird unter dem Editor angezeigt. <strong>Anwenden</strong> bleibt deaktiviert, bis der Fehler behoben ist.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content"><strong>Ergebnisvorschau</strong>: Wechseln Sie zum Tab <strong>Vorschau</strong>, um die Abfrage auszuführen und die ersten 10 Zeilen des Ergebnisses mit Name und Typ jeder Spalte zu sehen. Sind noch keine Eingabedaten verfügbar, zum Beispiel weil ein vorgelagertes Werkzeug noch nicht ausgeführt wurde, listet die Vorschau nur die Spalten auf, die die Abfrage zurückgeben wird.</div>
</div>

## Beispiele

### Grundlegende Filterung und Auswahl
```sql
-- Wohngebäude, die höher als 10 m sind
SELECT building_type, height, geometry
FROM input_1
WHERE building_type = 'residential'
  AND height > 10
```

### Räumliche Join-Analyse
```sql
-- Einrichtungen im Umkreis von 500 m um eine Haltestelle, mit der Entfernung in Metern
WITH a AS (
  SELECT name, amenity_type, geometry,
    ST_Transform(geometry, 'EPSG:4326', 'EPSG:25832', always_xy := true) AS geom_m
  FROM input_1
), t AS (
  SELECT stop_name,
    ST_Transform(geometry, 'EPSG:4326', 'EPSG:25832', always_xy := true) AS geom_m
  FROM input_2
)
SELECT
  a.name AS amenity_name,
  a.amenity_type,
  t.stop_name,
  ST_Distance(a.geom_m, t.geom_m) AS distance_m,
  a.geometry
FROM a
JOIN t ON ST_DWithin(a.geom_m, t.geom_m, 500)
ORDER BY distance_m
```

### Aggregation nach Gebiet
```sql
-- Anzahl der Punkte je Bezirk, auch für Bezirke ohne Punkte
SELECT
  admin.district_name,
  COUNT(points.geometry) AS point_count,
  ANY_VALUE(admin.geometry) AS geometry
FROM input_2 admin
LEFT JOIN input_1 points ON ST_Within(points.geometry, admin.geometry)
GROUP BY admin.district_name
```

## Bewährte Praktiken

:::tip Performance
- Verknüpfen Sie Tabellen über räumliche Prädikate wie `ST_Intersects()` oder `ST_Within()`, statt selbst jedes Zeilenpaar zu vergleichen
- Begrenzen Sie Ergebnisse während der Entwicklung mit `LIMIT 100`
- Testen Sie zuerst mit kleinen Datensätzen, dann skalieren Sie auf
:::

:::warning Datentypen
- Stellen Sie sicher, dass Geometriespalten ordnungsgemäß für räumliche Operationen formatiert sind
- Wandeln Sie Datentypen explizit um, wenn Sie verschiedene Datensätze verknüpfen
- Prüfen Sie auf NULL-Werte in kritischen Spalten
:::

### Abfrage-Optimierung

**Verwenden Sie räumliche Prädikate**: Verknüpfen Sie über räumliche Prädikate wie `ST_Intersects()`, `ST_Within()` oder `ST_DWithin()`, damit die Datenbank benachbarte Geometrien effizient zuordnen kann.

**Spaltenauswahl**: Wählen Sie nur die Spalten aus, die Sie benötigen, anstatt `SELECT *` zu verwenden.

**Ordnungsgemäße Joins**: Verwenden Sie geeignete Join-Typen (INNER, LEFT, RIGHT) basierend auf Ihren Analyseanforderungen.

### Fehlerbehandlung

Häufige Probleme und Lösungen:

- **Unbekannte Tabelle**: Stellen Sie sicher, dass Eingabedatensätze ordnungsgemäß verbunden sind und die Abfrage deren Tabellennamen verwendet (`input_1` bis `input_3` oder den **Tabellenalias** eines zusätzlichen Layers)
- **Unbekannte Spalte**: Überprüfen Sie Spaltennamen in Ihren Eingabedatensätzen; die Liste **Tabellen** im Tab **Aufbau** zeigt die Spalten jeder Tabelle
- **Geometriefehler**: Überprüfen Sie, ob Geometriespalten gültig und ordnungsgemäß formatiert sind
- **Only SELECT statements are allowed**: Schreiben Sie eine einzelne `SELECT`-Abfrage (optional beginnend mit `WITH`); Anweisungen, die Daten verändern, wie `CREATE`, `INSERT`, `UPDATE` oder `DELETE`, werden abgelehnt
- **Lang laufende Abfrage**: Teilen Sie komplexe Abfragen in kleinere Schritte auf

## Ausgabe und Integration

Das Werkzeug Benutzerdefiniertes SQL erstellt eine neue temporäre Ebene, die Ihre Abfrageergebnisse enthält und den Namen aus dem Feld **Name des Ergebnis-Layers** im Abschnitt **Ausgabe** erhält (Standard: `Custom SQL`). Nach einer erfolgreichen Ausführung zeigt das Konfigurations-Panel die **Dataset-Details** des Ergebnisses und diese **Aktionen**:

- **Tabelle**: Zeigt das Ergebnis in der Datenansicht unter der Leinwand
- **Karte**: Zeigt das Ergebnis auf einer Karte (nur für Ergebnisse mit Geometriespalte)
- **Datensatz speichern**: Speichert das Ergebnis als permanenten Datensatz

Außerdem können Sie:

- Die Ausgabe mit anderen Workflow-Werkzeugen für weitere Analysen verbinden
- Einen Knoten **Als Datensatz speichern** hinzufügen, um die Ergebnisse bei jeder Ausführung des Workflows als permanenten Datensatz zu speichern

:::info Variablen-Unterstützung
Abfragen in Benutzerdefiniertes SQL unterstützen [Workflow-Variablen](variables.md) mit der Syntax `{{@variable_name}}` für parametrisierte Abfragen. Tippen Sie `{{@` in den Editor, um eine Liste der Variablen des Workflows zu erhalten.
:::

## Einschränkungen

- Maximal 3 verbundene Eingaben und 2 zusätzliche Layer pro Knoten Benutzerdefiniertes SQL
- Nur eine einzelne `SELECT`-Anweisung ist erlaubt
- Ergebnisse ohne Geometriespalte werden als Tabelle erstellt und können nicht auf der Karte angezeigt werden
- Einige erweiterte DuckDB-Funktionen sind möglicherweise nicht verfügbar

Für komplexere Analyseanforderungen erwägen Sie die Verwendung mehrerer Knoten Benutzerdefiniertes SQL oder die Kombination mit anderen Workflow-Werkzeugen.
