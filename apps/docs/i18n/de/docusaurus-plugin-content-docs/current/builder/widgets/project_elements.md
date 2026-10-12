---
description: "Runden Sie Ihr Dashboard mit den Widgets Text, Trennlinie, Bild, Tabs und Links ab: Text formatieren, Abschnitte trennen, Widgets in Tabs gruppieren."
sidebar_position: 4
---



# Projektelemente

Dieser Abschnitt bietet zusätzliche Widgets, **um Ihr Dashboard abzurunden**: **Text**, **Trennlinie**, **Bild**, **Tabs** und **Links**. Ziehen Sie das Widget per Drag & Drop auf ein Panel.


### Text

Fügen Sie Text zu Ihrem Dashboard hinzu. Sie können ihn mit den erscheinenden Schaltflächen anpassen:

- Gestalten Sie Ihren Text mit verschiedenen **Überschriften**, **Listen** oder **Code-Blöcken.**
- Fügen Sie **fett**, *kursiv*, <u>unterstrichen</u>, durchgestrichen (~~Lorem ipsum~~), tiefgestellt (X<sub>1</sub>) oder hochgestellt (X<sup>1</sup>) zu Ihrem Text hinzu.
- Ändern Sie die **Ausrichtung**, **fügen Sie Links hinzu**, passen Sie die **Buchstabenfarbe** an oder **fügen Sie Hervorhebungen hinzu**.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_text.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

### Trennlinie

Das Widget Trennlinie **fügt eine horizontale Linie zu Ihrem Dashboard hinzu**, die verwendet werden kann, um verschiedene Abschnitte oder Elemente innerhalb des Dashboards visuell zu trennen.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_divider.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 


### Bild

**Laden Sie ein Bild** von Ihrem Computer in Ihr Dashboard hoch. Unter `Info` können Sie eine `Beschreibung` hinzufügen, die unterhalb des Bildes angezeigt wird, sowie einen `Alternativer Text` für die Barrierefreiheit. Aktivieren Sie `Innenabstand` unter Optionen, um einen inneren Abstand um das Bild hinzuzufügen.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/builder/builder_image.webp').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div>

## Tabs

Das Tabs-Widget **gruppiert andere Widgets desselben Panels in Tab-Ansichten**, sodass Betrachter zwischen ihnen wechseln können, ohne zu scrollen.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Ziehen Sie das <code>Tabs</code>-Widget per Drag & Drop auf ein Panel. Fügen Sie zuerst andere Widgets zum selben Panel hinzu, damit sie zur Zuweisung verfügbar sind.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Unter <code>Info</code> fügen Sie einen <code>Titel</code> für das Widget hinzu.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">
  Unter <code>Tabs & Widgets</code> wird jeder Tab mit seinem Namen und der Widget-Anzahl aufgelistet. Klicken Sie auf einen Tab, um ihn zu erweitern:
  <ul>
    <li>Verwenden Sie das Dropdown <code>Widget zu diesem Tab hinzufügen...</code>, um Widgets aus demselben Panel zuzuweisen. Jedes Widget kann jeweils nur einem Tab zugewiesen werden.</li>
    <li>Ziehen Sie das gepunktete Symbol, um zugewiesene Widgets neu anzuordnen. Verwenden Sie das ⋮-Menü, um ein Widget aus dem Tab zu entfernen.</li>
    <li>Klicken Sie auf das Löschen-Symbol eines Tabs, um ihn zu entfernen (verfügbar, wenn mehr als ein Tab vorhanden ist).</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Klicken Sie auf die <code>+</code>-Schaltfläche, um einen neuen Tab hinzuzufügen.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Aktivieren Sie <code>Volle Breite</code>, damit die Tab-Leiste die gesamte Panel-Breite einnimmt.</div>
</div>

## Links

Das Links-Widget **zeigt eine Reihe von beschrifteten Links oder Popup-Auslösern** an, nützlich für Navigation, Referenzen oder kontextbezogene Informationen.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Ziehen Sie das <code>Links</code>-Widget per Drag & Drop auf ein Panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Unter <code>Info</code> fügen Sie einen <code>Titel</code> und eine optionale <code>Beschreibung</code> hinzu.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">
  Unter <code>Links</code> hat jedes Element einen <code>URL</code> / <code>Popup</code>-Schalter:
  <ul>
    <li><code>URL</code>: geben Sie eine <code>Bezeichnung</code> und eine Ziel-URL ein.</li>
    <li><code>Popup</code>: geben Sie eine <code>Bezeichnung</code> ein und klicken Sie auf <code>Popup konfigurieren</code>, um <code>Popup-Typ</code> (<code>Tooltip</code>, <code>Popup</code> oder <code>Dialog</code>), <code>Popup-Platzierung</code>, <code>Größe</code> (<code>Klein</code>, <code>Mittel</code> oder <code>Groß</code>) und den Popup-Inhalt (Markdown unterstützt) festzulegen.</li>
  </ul>
  Ziehen Sie Elemente, um sie neu anzuordnen. Klicken Sie auf das ×-Symbol, um einen Link zu löschen.
  </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Klicken Sie auf <code>Link hinzufügen</code>, um ein weiteres Element hinzuzufügen.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">
  Unter <code>Optionen</code>:
  <ul>
    <li><code>Trennzeichen</code>: visueller Trenner zwischen Links (<code>Vertikaler Strich</code>, <code>Punkt</code> oder <code>Strich</code>).</li>
    <li><code>Zusatztext</code>: zusätzlicher Text neben den Links (z.B. ein Copyright-Hinweis).</li>
  </ul>
  </div>
</div>

<p></p>

:::tip

Schauen Sie sich unsere **[Galerie](https://www.plan4better.de/en/gallery)** für weitere Dashboard-Inspirationen an.

:::
<p></p>
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_viewer_dashboard.mp4').default} alt="recent datasets" style={{ maxHeight: "auto", maxWidth: "80%", objectFit: "cover"}}/>
</div> 