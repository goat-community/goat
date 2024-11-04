---
sidebar_position: 1
---

import thematicIcon from "/img/toolbox/data_management/join/toolbox.webp";


# Join & Group

Füge Felder von einer Layer zu einer anderen hinzu und gruppiere sie, indem du ein übereinstimmendes Feld in beiden Layern verwendest.

## 1. Erklärung

Dieses Werkzeug erleichtert die Kombination von zwei Datensätzen. Durch die Definition von Beziehungen werden die Daten aus beiden Layern abgeglichen. Das resultierende Ergebnis ist eine neue Layer, die die Attribute des *Ziellayers* und eine neue Spalte enthält, die ein ausgewähltes Attribut des *Joinlayers* zusammenfasst.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

  <img src={require('/img/toolbox/data_management/join/join.png').default} alt="Join Schema" style={{ maxHeight: "400px", maxWidth: "200px", objectFit: "cover"}}/>

</div> 

GOAT verwendet die **"Inner Join"**-Operation, um einen Join zu berechnen, der Zeilen aus einem Ziel- und einem Join-Layer basierend auf einer verwandten Spalte zwischen ihnen kombiniert. Es werden nur Datensätze ausgewählt, die übereinstimmende Werte in beiden Tabellen haben. Das bedeutet, dass für jede Zeile im Ziellayer mindestens eine Zeile im Join-Layer vorhanden sein muss, um eine erfolgreiche Übereinstimmung zu erzielen. Alle nicht übereinstimmenden Zeilen werden nicht zurückgegeben.

## 2. Anwendungsbeispiele

- Zusammenfassung von Bevölkerungszahlen aus einer Tabelle in eine Feature-Layer von Postleitzahlengebieten (verwandte Spalte: Postleitzahlen).
- Zusammenführen und Aggregieren von Daten aus einer Haushaltsbefragung mit den Geometrien des Zensusgebiets (verwandte Spalte: Zensusgebiet).
- Join der Anzahl von Pendlern aus einer Tabelle in einen Feature-Layer mit den Stadtgrenzen (verwandte Spalte: Stadtname).

## 3. Wie benutzt man das Werkzeug?

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klickn Sie auf <code>Werkzeuge</code> <img src={thematicIcon} alt="toolbox" style={{width: "25px"}}/>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Wählen Sie im Menü <code>Datenmanagement</code> aus und drücken Sie auf <code>Join & Group</code>.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

  <img src={require('/img/toolbox/data_management/join/overview.png').default} alt="Join Tool in GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>

</div> 

<p> </p>

### Layer zum Join auswählen

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wähle deine <code>Ziellayer</code> (die primäre Tabelle oder Layer, denen du zusätzliche Daten hinzufügen möchtest). </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Wähle deine <code>Joinlayer</code> (die sekundäre Tabelle oder der Datensatz, der die Datensätze und Attribute enthält, die in den Ziellayer eingefügt werden sollen). </div>
</div>

### Übereinstimmende Felder

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Wähle das <code>Zielfeld</code> des Ziellayers, das du zum Abgleichen der Datensätze beider Layer verwenden möchtest.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Wähle das übereinstimmende Attribut des Joinlayers als <code>Joinfeld</code>. </div>
</div>

### Statistiken

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Wähle die <code>Statistische Methode</code>, die zum Join des Attributs verwendet werden soll. </div>
</div>

Du kannst zwischen mehreren statistischen Operationen wählen. Einige Methoden sind nur für bestimmte Datentypen verfügbar. Die folgende Liste bietet einen Überblick über die verfügbaren Methoden:

| Methode | Datentypen | Beschreibung |
| -------|------| ------------|
| Anzahl | `string`,`number`    | Zählt die Anzahl der Nicht-Null-Werte in der ausgewählten Spalte|
| Summe  | `number`   | Berechnet die Summe aller Zahlen in der ausgewählten Spalte|
| Mittelwert | `number`   | Berechnet den Durchschnitt (Mittelwert) aller numerischen Werte in der ausgewählten Spalte|
| Median | `number`   | Gibt den Mittelwert in der sortierten Liste der numerischen Werte der ausgewählten Spalte zurück|
| Min    | `number`   | Gibt den Minimalwert der ausgewählten Spalte zurück|
| Max    | `number`   | Gibt den Maximalwert der ausgewählten Spalte zurück|

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Wähle die <code>Feld Statistik</code>, für die du die statistische Operation anwenden möchtest.</div>
</div>

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Klicke auf <code>Ausführen</code>.</div>
</div>

### Ergebnisse

<div class="step">
  <div class="step-number">10</div>
  <div class="content">Der resultierende Layer<b>"Join"</b> wird dem Projekt sowie den <a href="../../workspace/datasets">Datensätzen</a> in deinem Workspace hinzugefügt. Dieser Layer besteht aus den Informationen des Ziellayers und einer <b>zusätzlichen Spalte</b>, die die Ergebnisse der <b>statistischen Operation</b> zeigt. Du kannst die Attribute sehen, indem du auf eines der Objekte in der Karte klickst.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

  <img src={require('/img/toolbox/data_management/join/result.png').default} alt="Join Result in GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>

</div> 

:::tip Tipp

Möchtest du das Aussehen des Ergebnislayer anpassen? Sieh dir das [attributbasierte Styling](../../map/layer_style/attribute_based_styling.md) an.

:::
