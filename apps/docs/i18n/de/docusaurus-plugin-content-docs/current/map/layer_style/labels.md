---
description: "Beschriften Sie Features nach einem Attributfeld und legen Sie Größe, Farbe, Platzierung, Offset und Überlappung sowie Halo-Farbe und Halo-Breite fest."
sidebar_position: 3
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';



# Beschriftungen

**Beschriftungen ermöglichen es, Text auf Ihren Karten-Features basierend auf jedem Attributfeld anzuzeigen.** Dies macht Ihre Karten informativer und leichter interpretierbar, indem wichtige Informationen direkt auf den Features angezeigt werden.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/map/styling/labels_de.webp').default} alt="Beschriftungen auf Karten-Features angezeigt" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div>


## Wie man Beschriftungen hinzufügt und konfiguriert

### Allgemeine Einstellungen


<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie im <code>Layer</code>-Panel auf Ihren Layer. Rechts öffnet sich das Einstellungs-Panel des Layers mit den Tabs <code>Stil</code>, <code>Filtern</code> und <code>Metadaten</code>; der Tab <code>Stil</code> ist ausgewählt. Öffnen Sie dort den Bereich <code>Beschriftungen</code>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Bei <code>Beschriftung nach</code> wählen Sie das <strong>Attributfeld</strong> (Text oder Zahl), dessen Werte Sie als Beschriftungen anzeigen möchten. Sobald ein Feld ausgewählt ist, erscheinen darunter die <code>Beschriftungseinstellungen</code>.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <Video src={require('/img/map/styling/label_by.mp4').default} alt="Auswahl des Beschriftungsattributfelds" style={{ maxHeight: "auto", maxWidth: "500px", objectFit: "cover"}}/>
</div>


<div class="step">
  <div class="step-number">3</div>
  <div class="content">Unter <code>Beschriftungseinstellungen</code> stellen Sie bei <code>Größe</code> die <strong>Beschriftungsgröße</strong> mit dem Schieberegler (1-100) ein oder geben Sie den Wert manuell ein.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Bei <code>Farbe</code> wählen Sie eine <strong>Beschriftungsfarbe</strong> mit dem <code>Farbwähler</code> oder aus den <code>Standardfarben</code>.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Stellen Sie die <code>Position</code> ein, um zu definieren, <strong>wo Beschriftungen relativ zu den Features erscheinen</strong> (<code>Mitte</code>, <code>Oben</code>, <code>Unten</code>, <code>Links</code>, <code>Rechts</code> oder die Eckpositionen wie <code>Oben Links</code>; bei Linien-Layern <code>Mitte</code>, <code>Oben</code> oder <code>Unten</code>).</div>
</div>


### Erweiterte Einstellungen

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Klicken Sie neben <code>Beschriftungseinstellungen</code> auf das Optionen-Symbol <img src={require('/img/icons/options.png').default} alt="Optionen" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>, um den Bereich <code>Erweiterte Optionen</code> einzublenden.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Passen Sie <code>Offset x</code> und <code>Offset y</code> an, um die <strong>Beschriftungsposition</strong> durch horizontale oder vertikale Bewegung feinzustellen.</div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">Konfigurieren Sie das Kontrollkästchen <code>Überlappung zulassen</code>: <strong>Aktivieren</strong> Sie es, um alle Beschriftungen zu zeigen (kann visuelles Durcheinander verursachen), oder <strong>deaktivieren</strong> Sie es, um Beschriftungen auszublenden, die andere überlappen würden, besonders bei niedrigeren Zoom-Stufen (saubereres Aussehen).</div>
</div>

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Fügen Sie eine <code>Halo-Farbe</code> hinzu, um einen <strong>farbigen Umriss</strong> um den Text zu erstellen für bessere Lesbarkeit auf belebten Hintergründen.</div>
</div>

<div class="step">
  <div class="step-number">10</div>
  <div class="content">Stellen Sie die <code>Halo-Breite</code> ein, um die <strong>Umrissdicke</strong> zu kontrollieren (Maximum ist ein Viertel der Schriftgröße).</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <Video src={require('/img/map/styling/labels_overlap.mp4').default} alt="Beschriftungsüberlappung und Halo-Effekte" style={{ maxHeight: "auto", maxWidth: "500px", objectFit: "cover"}}/>
</div>


## Bewährte Praktiken

- Verwenden Sie <strong>kleinere Schriftarten für dichte Layer</strong>, um visuelles Durcheinander zu reduzieren
- Fügen Sie <strong>Halos mit kontrastierenden Farben</strong> hinzu (helle Halos auf dunklen Karten, dunkle Halos auf hellen Karten), um die Textlesbarkeit zu verbessern
- Lassen Sie <strong>Überlappung standardmäßig deaktiviert für ein saubereres Aussehen</strong>, obwohl einige Beschriftungen in überfüllten Bereichen verborgen sein können
- <strong>Testen Sie Ihre Beschriftungseinstellungen bei verschiedenen Zoom-Stufen</strong>, um sicherzustellen, dass sie in allen Maßstäben lesbar und nützlich bleiben
