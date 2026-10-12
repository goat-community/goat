---
description: "Erstellen Sie Puffer in einem oder mehreren Abständen um Punkte, Linien oder Polygone und führen Sie überlappende Puffer je Abstand optional zusammen."
sidebar_position: 1
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';



# Puffer

Dieses Werkzeug ermöglicht es Ihnen, **Zonen um Punkte, Linien oder Polygone mit einem bestimmten Abstand zu erstellen**.

<div style={{ display: 'flex', justifyContent: 'center' }}>
<iframe width="674" height="378" src="https://www.youtube.com/embed/Yboi3CwOLPM?si=FuSPRmK6zTB-GVJ1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

## 1. Erklärung

Ein Puffer ist ein Werkzeug, das verwendet wird, um **das Einzugsgebiet um einen bestimmten Punkt, eine Linie oder ein Polygon abzugrenzen und die Ausdehnung des Einflusses oder der Reichweite von diesem Feature zu veranschaulichen.** Benutzer können die ``Entfernung`` des Puffers definieren und damit den Radius des abgedeckten Bereichs anpassen.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

  <img src={require('/img/toolbox/geoprocessing/buffer/buffer_types.png').default} alt="Puffer-Typen" style={{ maxHeight: "400px", maxWidth: "400px", objectFit: "cover"}}/>

</div> 

## 2. Beispiel-Anwendungsfälle

- Analyse der Bevölkerung innerhalb von 500m um Bahnstationen
- Zählung der Geschäfte, die innerhalb von 1000m von Bushaltestellen erreichbar sind


## 3. Wie wird das Werkzeug verwendet?


<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie auf <code>Werkzeuge</code> <img src={require('/img/icons/toolbox.png').default} alt="Options" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie im Menü <code>Geoverarbeitung</code> auf <code>Puffer</code>.</div>
</div>

### Eingabe

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie den <code>Eingabe-Layer</code>, um dessen Objekte Sie die Puffer erstellen möchten. Es können Punkt-, Linien- und Polygon-Layer verwendet werden.</div>
</div>

### Konfiguration

Der Bereich <code>Konfiguration</code> wird verfügbar, sobald ein Eingabe-Layer ausgewählt ist.

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Wählen Sie die <code>Abstandsquelle</code>:
    <ul>
      <li><b>Konstant</b> (Standard): Für alle Objekte werden dieselben Abstände verwendet. Geben Sie diese unter <code>Pufferabstände</code> durch Kommas getrennt ein (z.B. <code>100, 200, 300</code>). GOAT erstellt <b>für jedes Objekt und jeden Abstand einen Puffer</b>.</li>
      <li><b>Feld</b>: Jedes Objekt erhält einen eigenen Abstand. Wählen Sie das numerische <code>Abstandsfeld</code> des Eingabe-Layers, das den Abstand enthält. Objekte mit leerem Wert oder dem Wert 0 werden übersprungen.</li>
    </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Wählen Sie die <code>Entfernungseinheit</code> der Abstände: <b>Meters</b> (Standard), <b>Kilometers</b>, <b>Feet</b>, <b>Miles</b>, <b>Nautical Miles</b> oder <b>Yards</b>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">
  Legen Sie <code>Überlappende Puffer zusammenführen</code> fest:
    <ul>
      <li><b>Deaktiviert</b> (Standard): GOAT erstellt um jedes Eingabeobjekt einen eigenen Puffer. Die Puffer behalten die Attribute ihres Eingabeobjekts.</li>
      <li><b>Aktiviert</b>: GOAT <b>führt alle Puffer mit demselben Abstand zu einem Polygon zusammen</b>. Das Ergebnis enthält ein Polygon je Abstand; die Attribute der Eingabeobjekte werden nicht übernommen. Dies ist nützlich, wenn Sie die insgesamt abgedeckte Fläche je Abstand sehen möchten.</li>
    </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Wenn Sie <b>Überlappende Puffer zusammenführen aktiviert haben</b>, erscheint der Schalter <code>Polygon Difference</code>. Wenn Sie ihn aktivieren, zieht GOAT jeden kleineren Abstand vom nächstgrößeren ab, sodass das Ergebnis aus <b>Ringen besteht, die sich nicht überlappen</b>. Dies wirkt sich nur bei der Abstandsquelle <b>Konstant</b> und mindestens zwei Pufferabständen aus.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

  <img src={require('/img/toolbox/geoprocessing/buffer/polygon_union_difference.webp').default} alt="Puffer ohne Zusammenführen, zusammengeführt und zusammengeführt mit Polygon Difference" style={{ maxHeight: "auto", maxWidth: "60%", objectFit: "cover"}}/>
</div> 

<p></p>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">
  Klicken Sie optional auf das Optionen-Symbol <img src={require('/img/icons/options.png').default} alt="Optionen" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> in der Kopfzeile von <code>Konfiguration</code>, um weitere Einstellungen für die Pufferform anzuzeigen:
    <ul>
      <li><code>Kurvenglättung</code>: Anzahl der Segmente, mit denen ein Viertelkreis angenähert wird (Standard <b>8</b>). Höhere Werte ergeben glattere Kanten, verlängern aber die Berechnung.</li>
      <li><code>Endkappenstil</code>: Form des Puffers an Linienenden: <b>CAP ROUND</b> (Standard), <b>CAP FLAT</b> oder <b>CAP SQUARE</b>.</li>
      <li><code>Verbindungsstil</code>: Form des Puffers an Ecken: <b>JOIN ROUND</b> (Standard), <b>JOIN MITRE</b> oder <b>JOIN BEVEL</b>.</li>
      <li><code>Gehrungsgrenze</code>: nur bei <b>JOIN MITRE</b> sichtbar; begrenzt, wie weit spitze Ecken hinausragen (Standard <b>1</b>).</li>
    </ul>
  </div>
</div>

### Ergebnisse

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Ändern Sie optional das Feld <code>Name der Ergebnislayer</code> (Standard: <b>Puffer</b>).</div>
</div>

<div class="step">
  <div class="step-number">10</div>
  <div class="content">Klicken Sie auf <code>Ausführen</code>. Dies startet die Berechnung des Puffers. Sobald sie abgeschlossen ist, wird der resultierende Polygon-Layer zu Ihrer Karte hinzugefügt.</div>
</div>

Der Ergebnis-Layer enthält die Spalte <code>buffer_distance</code>. Bei der Abstandsquelle <b>Konstant</b> enthält sie den Abstand in Metern, und die Puffer werden nach Abstand eingefärbt. Bei der Abstandsquelle <b>Feld</b> enthält sie den Wert des Abstandsfelds.

<p></p>

:::tip Tipp

Möchten Sie Ihre Puffer stylen und schön aussehende Karten erstellen? Siehe [Styling](../../map/layer_style/style/styling).

:::