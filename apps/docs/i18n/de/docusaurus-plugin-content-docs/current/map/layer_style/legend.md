---
description: "Blenden Sie die Legende eines Layers ein oder aus, fügen Sie einen Untertitel hinzu und ersetzen Sie Werte der Farbstufen durch eigene Legendenbezeichnungen."
sidebar_position: 5
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';



# Legende

**Legenden helfen Benutzern, die Symbologie und Bedeutung Ihrer Kartenlayer zu verstehen.** GOAT zeigt automatisch Legenden für alle sichtbaren Layer an, aber Sie können ihr Aussehen anpassen und beschreibende Beschriftungen hinzufügen, um Ihre Karten informativer zu machen.


## Wie man Layer-Legenden verwaltet

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie im <code>Layer</code>-Panel auf Ihren Layer. Rechts öffnet sich das Einstellungs-Panel des Layers; der Tab <code>Stil</code> ist ausgewählt. Öffnen Sie unten in diesem Tab den Bereich <code>Legende</code>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Aktivieren oder deaktivieren Sie unter <code>Optionen</code> das Kontrollkästchen <code>Anzeigen</code>, um <strong>die Legendenanzeige zu aktivieren oder zu deaktivieren</strong>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Solange <code>Anzeigen</code> aktiviert ist, können Sie das Feld <code>Untertitel</code> ausfüllen, das <strong>den Inhalt des Layers erklärt</strong>. Der Untertitel erscheint unter dem Layer-Namen in der Legendenliste.</div>
</div>

<p></p>
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/map/styling/legend_de.webp').default} alt="Legendenkonfiguration mit Untertiteleinstellungen" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div>


## Benutzerdefinierte Legendenbezeichnungen für Farbstufen

Bei der attributbasierten Darstellung mit einer Farbskala (jede Klassifizierungsmethode, einschließlich <code>Benutzerdefinierte Schritte</code> und <code>Benutzerdefinierte Ordinalskala</code>) können Sie jeder Farbstufe eine eigene Bezeichnung hinzufügen. Diese Bezeichnungen ersetzen die Rohdatenwerte in der Kartenlegende durch lesbare Beschreibungen.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie im Bereich <code>Stil</code> des Tabs <code>Stil</code> neben <code>Füllfarbe</code> oder <code>Strichfarbe</code> auf das Optionen-Symbol <img src={require('/img/icons/options.png').default} alt="Optionen-Symbol" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. Ist unter <code>Farbe basierend auf</code> ein Feld ausgewählt, klicken Sie auf die Auswahl <code>Farbskala</code>, um das Klassifizierungsfenster zu öffnen. Siehe [Attributbasiertes Styling](./style/attribute_based_styling).</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Unterhalb jeder Farbstufen-Zeile sehen Sie ein Textfeld mit dem Platzhalter <code>Legendenbezeichnung</code>. Geben Sie eine eigene Bezeichnung ein, z. B. <code>Niedrig</code>, <code>Mittel</code> oder <code>Hoch</code>, um den numerischen Wert in der Legende zu ersetzen.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Lassen Sie das Feld leer, um den Standardwert in der Legende anzuzeigen. Klicken Sie auf <code>Anwenden</code>, um Ihre Bezeichnungen zu speichern.</div>
</div>

## Bewährte Praktiken

- **Verwenden Sie klare, beschreibende Untertitel**, die erklären, was der Layer darstellt
- **Halten Sie Untertitel prägnant**, aber informativ
- **Deaktivieren Sie Legenden** für Layer, die keine visuelle Erklärung benötigen (z.B. Referenzlayer)
- **Überprüfen Sie die Legendensichtbarkeit**, um eine Überfrachtung der Kartenoberfläche zu vermeiden
