---
description: "Zeigen Sie Layer-Daten in den Widgets Kategorien, Histogramm und Kreisdiagramm: Statistik, Feld und Gruppierung wählen, Farben und Auswahlverhalten festlegen."
sidebar_position: 3
---


# Diagramme

**Stellen Sie Ihre Daten in einem visuellen Format mit verschiedenen Diagrammtypen dar: Kategorien, Histogramm und Kreisdiagramm.** 

## Kategorien

Das Kategorien-Widget ermöglicht es Ihnen, die Verteilung eines kategorischen Feldes aus einem ausgewählten Layer zu visualisieren, indem es statistische Analysen berechnet und **Gruppen nach dem ausgewählten Feld** generiert.

<div class="step">
  <div class="step-number">1</div>
  <div class="content"><b>Ziehen Sie</b> das <code>Layer</code> Widget per <b>Drag & Drop</b> auf ein Panel und wählen Sie Ihren <code>Layer</code> aus.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Unter <code>Info</code> fügen Sie einen <code>Titel</code> und eine optionale <code>Beschreibung</code> für das Widget hinzu.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie die <code>statistische Methode</code>, die Sie anwenden möchten. Es kann <code>Anzahl</code>, <code>Summe</code>, <code>Min</code>, <code>Max</code> sein oder Sie fügen Ihren eigenen [`Ausdruck`](../expressions) hinzu.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Wählen Sie das <code>Feld</code> aus, <b>auf das die Statistik angewendet werden soll</b>. <i>Summe, Min und Max können nur auf numerische Felder angewendet werden.</i></div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Unter <code>Gruppieren nach Feld</code> wählen Sie das Feld aus, <b>nach dem Ihre Ergebnisse gruppiert werden sollen</b>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">
  Unter <code>Stil</code> konfigurieren Sie das Erscheinungsbild des Diagramms:
  <ul>
    <li><code>Grundfarbe</code>: legt die Standard-Balkenfarbe fest</li>
    <li>
      <code>Wertbasierte Darstellung</code>: wenn aktiviert, werden Balken basierend auf dem ausgewählten Darstellungsfeld eingefärbt. Weitere Optionen erscheinen:
      <ul>
        <li><code>Darstellungsfeld</code>: wählen Sie <code>Statistikfeld</code> (Farbe nach Wert) oder <code>Gruppierungsfeld</code> (eine Farbe pro Kategorie)</li>
        <li><code>Farbskala</code>: Klassifizierungsmethode (z.B. [Quantil](https://www.plan4better.de/de/glossar/quantilklassifizierung)); nur sichtbar wenn Darstellungsfeld auf Statistikfeld gesetzt ist</li>
        <li><code>Palette</code>: Farbpalette für das Diagramm</li>
        <li><code>Reihenfolge (n/n)</code>: listet alle Kategorienwerte auf. Mit <code>Alle hinzufügen</code> / <code>Alle entfernen</code> Kategorien ein- oder ausschließen. Ziehen Sie das ⋮⋮-Symbol zum Neuanordnen. Über das ⋮-Menü können einzelne Einträge <code>Umbenennen</code> oder <code>Entfernen</code> werden.</li>
      </ul>
    </li>
    <li><code>Auswahlfarbe</code>: Farbe zum Hervorheben eines ausgewählten Balkens; nur sichtbar wenn <code>Auswahlverhalten</code> auf <code>Hervorheben</code> gesetzt ist</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">
  Unter <code>Optionen</code>:
  <ul>
    <li><code>Auswahlverhalten</code>: wählen Sie <code>Filtern</code>, um alle verbundenen Widgets beim Klick auf einen Balken zu filtern, oder <code>Hervorheben</code>, um den ausgewählten Balken hervorzuheben, ohne zu filtern</li>
    <li><code>Nach Kartenausschnitt filtern</code>: nur Daten innerhalb der aktuellen Kartenansicht anzeigen</li>
    <li><code>Zahlenformat</code>: Zahlenformat aus der Dropdown-Liste festlegen</li>
  </ul>
  </div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_categories.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

<p></p>

## Histogramm

Das Histogramm-Widget ermöglicht es Ihnen, die **Verteilung eines numerischen Feldes aus einem ausgewählten Layer durch `Anzahl`** zu visualisieren.

<div class="step">
  <div class="step-number">1</div>
  <div class="content"><b>Ziehen Sie</b> das <code>Layer</code> Widget per <b>Drag & Drop</b> auf ein Panel und wählen Sie Ihren <code>Layer</code> aus.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Unter <code>Info</code> fügen Sie einen <code>Titel</code> und eine optionale <code>Beschreibung</code> für das Widget hinzu.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie das <code>numerische Feld</code>, das Sie visualisieren möchten. Die angewendete statistische Methode wird <code>Anzahl</code> sein. </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Unter <code>Stil</code> konfigurieren Sie das Erscheinungsbild des Diagramms:
  <ul>
    <li><code>Grundfarbe</code>: legt die Standard-Balkenfarbe fest</li>
    <li><code>Hover-Farbe</code>: Farbe beim Hover über einen Balken</li>
    <li><code>Anzahl Klassen</code>: Anzahl der Histogramm-Klassen (1–20, Standard 10)</li>
    <li><code>X-Achsenwerte</code>: benutzerdefinierte Achsenwerte für die X-Achse (mit Enter oder Komma eingeben)</li>
    <li><code>Anzeigename des Feldes</code>: optionaler benutzerdefinierter Name für das im Diagramm angezeigte Feld</li>
    <li><code>Auswahlfarbe</code>: Farbe für den ausgewählten Bereich; nur sichtbar wenn <code>Auswahlverhalten</code> auf <code>Hervorheben</code> gesetzt ist</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">
  Unter <code>Optionen</code>:
  <ul>
    <li><code>Auswahlverhalten</code>: wählen Sie <code>Filtern</code>, um alle verbundenen Widgets beim Klick auf einen Balken zu filtern, oder <code>Hervorheben</code>, um den ausgewählten Bereich hervorzuheben, ohne zu filtern</li>
    <li><code>Nach Kartenausschnitt filtern</code>: nur Daten innerhalb der aktuellen Kartenansicht anzeigen</li>
    <li><code>Zahlenformat</code>: Zahlenformat aus der Dropdown-Liste festlegen</li>
  </ul>
  </div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_histogram.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 


## Kreisdiagramm

Das Kreisdiagramm-Widget ermöglicht es Ihnen, **die Verteilung eines Feldes** aus einem ausgewählten Layer zu visualisieren.

<div class="step">
  <div class="step-number">1</div>
  <div class="content"><b>Ziehen Sie</b> das <code>Layer</code> Widget per <b>Drag & Drop</b> auf ein Panel und wählen Sie Ihren <code>Layer</code> aus.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Unter <code>Info</code> fügen Sie einen <code>Titel</code> und eine optionale <code>Beschreibung</code> für das Widget hinzu.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie die <code>statistische Methode</code>, die Sie anwenden möchten. Es kann <code>Anzahl</code>, <code>Summe</code>, <code>Min</code>, <code>Max</code> sein oder Sie fügen Ihren eigenen [`Ausdruck`](../expressions) hinzu.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Wählen Sie das <code>Feld</code> aus, <b>auf das die Statistik angewendet werden soll</b>. <i>Summe, Min und Max können nur auf numerische Felder angewendet werden.</i></div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Wählen Sie das <code>Feld</code> aus, nach dem Ihre Ergebnisse <b>gruppiert werden sollen</b>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">
  Unter <code>Stil</code> konfigurieren Sie das Erscheinungsbild des Diagramms:
  <ul>
    <li><code>Diagrammtyp</code>: wählen Sie <code>Donut</code>, <code>Kreis</code> oder <code>Halbkreis</code></li>
    <li><code>Beschriftungsgröße</code>: wählen Sie <code>S</code>, <code>M</code> oder <code>L</code></li>
    <li><code>Layout</code>: wählen Sie <code>Aktives Segment im Zentrum</code> (zeigt den Prozentsatz des aktiven Segments in der Mitte), <code>Alle Labels außerhalb</code> oder <code>Legende</code></li>
    <li><code>Palette</code> und <code>Reihenfolge (n/n)</code>: Farbpalette und angezeigte Kategorien verwalten. Mit <code>Alle hinzufügen</code> / <code>Alle entfernen</code> Kategorien ein- oder ausschließen. Ziehen Sie zum Neuanordnen. Über das ⋮-Menü können einzelne Einträge <code>Umbenennen</code> oder <code>Entfernen</code> werden.</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">
  Unter <code>Optionen</code>:
  <ul>
    <li><code>Nach Kartenausschnitt filtern</code>: zeigt nur Daten innerhalb der aktuellen Kartenansicht an</li>
  </ul>
  </div>
</div>

::::info
Ergebnisse werden in **Prozent** visualisiert.
::::


<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_pie_chart.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 


::::tip

Wo **statistische Methoden angewendet werden können**, sind *Anzahl, Summe, Min, Max und [Ausdruck](../expressions)* die verfügbaren Optionen. Schauen Sie sich unsere **[Ausdrücke-Dokumentation](../expressions)** für weitere Informationen an.
::::