---
description: "Führen Sie zwei oder mehr Layer zu einem zusammen: gleichnamige Felder werden vereint, übrige bleiben erhalten, optional mit Quellspalte und Multi-Geometrien."
sidebar_position: 2
---

# Zusammenführen (Merge)

Mit diesem Werkzeug können Sie **zwei oder mehr Layer zu einem einzigen Ausgabe-Layer zusammenführen**. Die Objekte aller Eingabe-Layer werden in einem Datensatz gestapelt. Standardmäßig werden Felder mit gleichem Namen zusammengeführt, während eingabespezifische Felder im Ergebnis erhalten bleiben.

## 1. Erklärung

Beim Zusammenführen werden Objekte aus mehreren Layern in einem Layer vereint. Im Gegensatz zur Verbindung (Join) ist kein Abgleich erforderlich: Alle Objekte aller Eingabe-Layer werden einfach kombiniert. Dies ist hilfreich, wenn Sie denselben Datentyp auf mehrere Layer aufgeteilt haben und damit als einheitlichen Datensatz arbeiten möchten.

**Wichtige Verhaltensweisen:**
- Objekte aller Eingabe-Layer sind im Ergebnis enthalten.
- Felder mit gleichem Namen werden in eine Spalte zusammengeführt.
- Felder, die nur in einem Eingabe-Layer vorhanden sind, werden mit `NULL`-Werten für Objekte aus anderen Layern übernommen.

## 2. Anwendungsbeispiele

- Gebäudegrundrisse aus mehreren Gemeinden zu einem Layer zusammenführen.
- Erhebungsergebnisse aus separaten Dateien in einem Datensatz stapeln.
- Straßennetz-Layer aus verschiedenen Datenquellen zusammenführen.

## 3. Verwendung des Werkzeugs

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie auf den <code>Toolbox</code> <img src={require('/img/icons/toolbox.png').default} alt="Toolbox" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. Klicken Sie unter <code>Datenmanagement</code> auf <code>Zusammenführen (Merge)</code>.</div>
</div>

### Eingabe-Layer auswählen

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Wählen Sie unter <code>Eingabe</code> Ihren ersten <code>Eingabe-Layer</code> aus dem Dropdown aus.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Klicken Sie auf <code>+ Hinzufügen Input Path</code>, um einen oder mehrere weitere Layer hinzuzufügen.</div>
</div>

### Merge-Optionen

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Öffnen Sie <code>Merge-Optionen</code> und konfigurieren Sie die folgenden Schalter:
  <ul>
    <li><code>Add Source Column</code>: fügt dem Ergebnis eine Spalte hinzu, die angibt, aus welchem Eingabe-Layer ein Objekt stammt.</li>
    <li><code>Validate Geometry Types</code>: prüft vor dem Zusammenführen, ob alle Eingabe-Layer denselben Geometrietyp aufweisen.</li>
    <li><code>Promote To Multi</code>: konvertiert einteilige Geometrien in mehrteilige (z. B. Polygon → MultiPolygon), um die Kompatibilität zwischen den Eingaben sicherzustellen.</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Klicken Sie auf <code>Ausführen</code>, um das Zusammenführen zu starten. Der Ergebnis-Layer wird der Karte hinzugefügt.</div>
</div>
