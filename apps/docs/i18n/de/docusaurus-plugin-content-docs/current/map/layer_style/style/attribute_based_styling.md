---
description: "Gestalten Sie Füll- und Strichfarbe, Strichbreite, Marker oder Punktradius nach einem Datenfeld, mit Farbpaletten und Klassifizierungen wie Quantil."
sidebar_position: 2
---

# Attributbasiertes Styling

**Sie können Layer basierend auf Daten-Attributen gestalten, um Unterschiede und Trends leicht zu identifizieren.** Jeder Visualisierungsaspekt (Füllfarbe, Strichfarbe, Strichbreite, Benutzerdefiniertes Symbol und Punkteinstellungen) kann nach jedem Feld in den Daten Ihres Layers gestaltet werden.

<iframe width="100%" height="500" src="https://www.youtube.com/embed/cLIPMCOu4FQ?si=aydSJN_Pf0fusO9x" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Wie man attributbasiertes Styling anwendet

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie im <code>Layer</code>-Panel auf Ihren Layer. Rechts öffnet sich das Einstellungs-Panel des Layers mit den Tabs <code>Stil</code>, <code>Filtern</code> und <code>Metadaten</code>; der Tab <code>Stil</code> ist ausgewählt. Die Styling-Optionen finden Sie dort im Bereich <code>Stil</code>.</div>
</div>

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="fill-color" label="Füllfarbe" default>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie neben <code>Füllfarbe</code> auf das Optionen-Symbol <img src={require('/img/icons/options.png').default} alt="Optionen-Symbol" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>; der Bereich <code>Erweiterte Optionen</code> wird eingeblendet.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Farbe basierend auf</code> wählen Sie das <strong>Text- oder Zahlenfeld zum Stylen</strong> aus.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Jetzt können Sie zu <code>Palette</code> gehen und eine <strong>Farbpalette</strong> wählen oder die Standardpalette behalten. Erfahren Sie mehr im Abschnitt <a href="#farbpalette">Farbpalette</a> unten.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Klicken Sie auf <code>Farbskala</code> und wählen Sie Ihre <strong>Datenklassifizierungsmethode</strong>. Alle Methoden finden Sie im Abschnitt <a href="#datenklassifizierungsmethoden">Datenklassifizierungsmethoden</a>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Am Ende des <code>Farbskala</code>-Panels können Sie <code>Keine Daten</code> aktivieren, um Features, bei denen das gewählte Feld keinen Wert hat, eine Farbe zuzuweisen. Die Standardfarbe ist Grau (<code>#CCCCCC</code>). Klicken Sie auf das Farbfeld, um sie zu ändern.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <Video src={require('/img/map/styling/attribute-based-fill-color.mp4').default} alt="Füllfarbe Styling" style={{ maxHeight: "auto", maxWidth: "20%", objectFit: "cover"}}/>
</div>

</TabItem>
<TabItem value="stroke-color" label="Strichfarbe">

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie neben <code>Strichfarbe</code> (bei Linien-Layern mit <code>Farbe</code> beschriftet) auf das Optionen-Symbol <img src={require('/img/icons/options.png').default} alt="Optionen-Symbol" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>; der Bereich <code>Erweiterte Optionen</code> wird eingeblendet.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Farbe basierend auf</code> wählen Sie das <strong>Text- oder Zahlenfeld zum Stylen</strong> aus.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Jetzt können Sie zu <code>Palette</code> gehen und eine <strong>Farbpalette</strong> wählen oder die Standardpalette behalten. Erfahren Sie mehr im Abschnitt <a href="#farbpalette">Farbpalette</a> unten.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Klicken Sie auf <code>Farbskala</code> und wählen Sie Ihre <strong>Datenklassifizierungsmethode</strong>. Alle Methoden finden Sie im Abschnitt <a href="#datenklassifizierungsmethoden">Datenklassifizierungsmethoden</a>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Am Ende des <code>Farbskala</code>-Panels können Sie <code>Keine Daten</code> aktivieren, um Features, bei denen das gewählte Feld keinen Wert hat, eine Farbe zuzuweisen. Die Standardfarbe ist Grau (<code>#CCCCCC</code>). Klicken Sie auf das Farbfeld, um sie zu ändern.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <Video src={require('/img/map/styling/attribute-based-stroke-color.mp4').default} alt="Strichfarbe Styling" style={{ maxHeight: "auto", maxWidth: "20%", objectFit: "cover"}}/>
</div>

</TabItem>
<TabItem value="custom-marker" label="Benutzerdefiniertes Symbol">

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Aktivieren Sie bei <code>Benutzerdefiniertes Symbol</code> den Schalter und klicken Sie auf das Optionen-Symbol <img src={require('/img/icons/options.png').default} alt="Optionen-Symbol" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>; der Bereich <code>Erweiterte Optionen</code> wird eingeblendet.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Symbol basierend auf</code> wählen Sie das <strong>Textfeld zum Stylen</strong> aus.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Klicken Sie auf <code>Marker (Ordinal)</code> und wählen Sie den Marker für jeden Kategoriewert: aus der <code>Bibliothek</code> oder durch Hochladen eines eigenen Markers unter <code>Benutzerdefiniert</code>.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Unter <code>Marker-Einstellungen</code> passen Sie den <code>Größe</code>-Schieberegler an, um die Basisgröße des Markers festzulegen, und nutzen Sie <code>Position</code>, um die Verankerung des Icons relativ zum Kartenpunkt zu steuern (<code>Mitte</code>, <code>Oben</code>, <code>Unten</code>, <code>Links</code>, <code>Rechts</code> oder eine Eckposition wie <code>Oben Links</code>).</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Aktivieren Sie <code>Überlappung zulassen</code>, damit Marker nicht ausgeblendet werden, wenn sie sich auf der Karte überlappen.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Optional: Klicken Sie neben <code>Marker-Einstellungen</code> auf das Optionen-Symbol <img src={require('/img/icons/options.png').default} alt="Optionen-Symbol" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>, um den Bereich <code>Erweiterte Optionen</code> einzublenden, und setzen Sie <code>Markergröße basierend auf</code> auf ein numerisches Feld, um die Markergröße pro Feature zu variieren. Weitere Details zur Größenklassifizierung finden Sie im Tab <a href="#punkteinstellungen">Punkteinstellungen</a>.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <Video src={require('/img/map/styling/attribute-based-custom-marker.mp4').default} alt="Benutzerdefiniertes Symbol Styling" style={{ maxHeight: "auto", maxWidth: "40%", objectFit: "cover"}}/>
</div>

</TabItem>
<TabItem value="stroke-width" label="Strichbreite">

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie neben <code>Strichbreite</code> auf das Optionen-Symbol <img src={require('/img/icons/options.png').default} alt="Optionen-Symbol" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>; der Bereich <code>Erweiterte Optionen</code> wird eingeblendet.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Strich basierend auf</code> wählen Sie das <strong>numerische Feld</strong> aus, das die Strichbreite steuern soll.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Klicken Sie auf <code>Größenskala</code>, um das Klassifizierungsfenster zu öffnen. Wählen Sie eine <strong>Klassifizierungsmethode</strong> und legen Sie die Anzahl der <strong>Schritte</strong> fest (2–10). Jeder Schritt zeigt eine Breitenvorschau neben dem Wertebereich.</div>
</div>

:::note
Die attributbasierte Strichbreite gilt für **Linien, Polygone und Punkte**.
:::

</TabItem>
<TabItem value="point-settings" label="Punkteinstellungen">

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie neben <code>Punkteinstellungen</code> auf das Optionen-Symbol <img src={require('/img/icons/options.png').default} alt="Optionen-Symbol" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>; der Bereich <code>Erweiterte Optionen</code> wird eingeblendet.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">In <code>Radius basierend auf</code> wählen Sie das <strong>numerische Feld</strong> aus, das den Punktradius steuern soll.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Klicken Sie auf <code>Größenskala</code>, um das Klassifizierungsfenster zu öffnen. Wählen Sie eine <strong>Klassifizierungsmethode</strong> und legen Sie die Anzahl der <strong>Schritte</strong> fest (2–10). Jeder Schritt zeigt eine Größenvorschau neben dem Wertebereich. Es stehen dieselben Methoden wie bei der Farbklassifizierung zur Verfügung: [Quantil](https://www.plan4better.de/de/glossar/quantilklassifizierung), [Standardabweichung](https://www.plan4better.de/de/glossar/standardabweichung-klassifizierung), [Gleiches Intervall](https://www.plan4better.de/de/glossar/gleiche-intervalle), Heads und Tails, Benutzerdefinierte Schritte und Benutzerdefinierte Ordinalskala.</div>
</div>

:::note
Punkteinstellungen sind nur für **Punkt-Layer ohne Benutzerdefiniertes Symbol** verfügbar. Für Punkt-Layer mit einem Benutzerdefinierten Symbol verwenden Sie <code>Markergröße basierend auf</code> im Tab Benutzerdefiniertes Symbol.
:::

</TabItem>
</Tabs> 

## Farbpalette

Eine Palette ist ein Set von Farben, die Ihre Datenwerte oder Kategorien repräsentieren.

Sie können Ihre Palette anpassen, indem Sie den <code>Typ</code> und die <code>Schritte</code> auswählen, mit <code>Umgekehrt</code> die Farben umkehren oder <code>Benutzerdefiniert</code> für Ihren eigenen Farbbereich aktivieren.

GOAT bietet vier vordefinierte Palettentypen:

<p></p>

| Palettentyp  | Beispiel                                                                                                                                                     | Beschreibung                                                                                                                                                                                                                                  |
| :----------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Divergierend | <img src={require('/img/map/styling/diverging_palette.png').default} alt="divergierend" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/> | **Nützlich für Daten mit einem zentralen Mittelpunkt**, wie positive und negative Werte. Hilft dabei, Variationen um diesen Mittelpunkt klar zu zeigen.                                                                                       |
| Sequenziell  | <img src={require('/img/map/styling/sequential_palette.png').default} alt="sequenziell" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/> | **Ideal für Daten, die einer natürlichen Progression oder geordneten Sequenz folgen**, wie steigende oder sinkende Werte. Exzellent für die Visualisierung kontinuierlicher Daten, zeigt allmähliche Änderungen von einem Extrem zum anderen. |
|  Qualitativ  | <img src={require('/img/map/styling/qualitative_palette.png').default} alt="qualitativ" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/> | **Entwickelt für unterschiedliche Kategorien oder Klassen.** Hilft dabei, zwischen diskreten Kategorien zu unterscheiden, ohne Ordnung oder Wichtigkeit zu implizieren.                                                                       |
| Einzelner Farbton | <img src={require('/img/map/styling/singlehue_palette.png').default} alt="einzelner Farbton" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>    | **Verwendet verschiedene Schattierungen und Töne einer einzigen Farbe.** Erzeugt ein harmonisches Aussehen und ist effektiv für die Informationsübermittlung ohne die Ablenkung mehrerer Farben.                                              |

## Datenklassifizierungsmethoden

Die <code>Farbskala</code> bestimmt, wie Datenwerte auf Farben abgebildet werden. GOAT bietet sechs Datenklassifizierungsmethoden: **Quantil, Standardabweichung, Gleiches Intervall, Heads und Tails, Benutzerdefinierte Schritte und Benutzerdefinierte Ordinalskala.** Für Textfelder steht nur Benutzerdefinierte Ordinalskala zur Verfügung. Alle Methoden haben standardmäßig 7 Klassen, aber Sie können diese Anzahl nach Bedarf anpassen.

### Quantil

**Teilt Daten in Klassen mit gleichen Anzahlen von Features auf. Ideal für linear verteilte Daten**, erzeugt aber ungleiche Wertebereiche.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/styling/quantile.webp').default} alt="Quantil" style={{ maxHeight: "auto", maxWidth: "75%", objectFit: "cover"}}/>

</div>  

### Standardabweichung

**Klassifiziert Daten nach Abweichung vom Durchschnitt**. Zeigt **relative Streuung, Verteilung und Ausreißer statistisch**, benötigt aber normalverteilte Daten.
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/styling/standard_deviation.webp').default} alt="Standardabweichung" style={{ maxHeight: "auto", maxWidth: "75%", objectFit: "cover"}}/>

</div> 

### Gleiches Intervall

**Teilt Daten in gleich große Wertebereiche auf**. Funktioniert gut bei **gleichmäßig verteilten Daten, kann aber bei schiefen Daten irreführend sein** (einige Klassen können leer sein).
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/styling/equal_interval.webp').default} alt="Gleiches Intervall" style={{ maxHeight: "auto", maxWidth: "75%", objectFit: "cover"}}/>

</div> 

### Heads und Tails

**Behandelt schiefe Daten durch Hervorhebung von Extremen**. Fokussiert auf 'Köpfe' (sehr hohe Werte) und 'Schwänze' (sehr niedrige Werte). **Nützlich für Datensätze, bei denen Extreme am wichtigsten sind und zur Hervorhebung von Disparitäten.**

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/styling/heads_tails.webp').default} alt="Heads und Tails" style={{ maxHeight: "auto", maxWidth: "75%", objectFit: "cover"}}/>

</div> 

### Benutzerdefinierte Ordinalskala (für **Strings**)

**Sortiert und visualisiert String-Daten** wie Kategorien oder Labels. Da Strings keine natürliche Ordnung haben, **ermöglicht Benutzerdefinierte Ordinalskala Ihnen, Ihre eigenen Ordnungsregeln zu definieren** für maßgeschneiderte Sequenzen.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <img src={require('/img/map/styling/ordinal.webp').default} alt="Benutzerdefinierte Ordinalskala für Strings" style={{ maxHeight: "auto", maxWidth: "75%", objectFit: "cover"}}/>

</div>

<p></p>

Sie können mehr Schritte hinzufügen und mehrere String-Werte pro Gruppe aus dem <code>Dropdown-Menü</code> auswählen, das alle Werte aus Ihrem Datensatz auflistet.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

  <Video src={require('/img/map/styling/custom_ordinal.mp4').default} alt="Benutzerdefinierte Ordinalskala für Strings" style={{ maxHeight: "300px", maxWidth: "300px", objectFit: "cover"}}/>

</div> 

### Benutzerdefinierte Schritte (für **Zahlen**)

**Für numerische Daten mit benutzerdefinierten Breakpoints oder Schwellenwerten**. Bietet maßgeschneiderte Visualisierungen für spezifische Kontexte. **Hilft dabei, Konsistenz über Karten hinweg zu erhalten**. Gibt volle Kontrolle über Klassifizierungen, die mit realen Bedürfnissen übereinstimmen.


:::tip HINWEIS
Um Ihren Datensatz mit den Styling-Einstellungen in anderen Projekten zu verwenden, [speichern Sie Ihren Stil als Standard](./styling.md#stil-kopieren-und-einfügen).
:::