---
description: "Nutzen Sie die Widgets Filter, Tabelle, Zahlen und Rich Text im Dashboard, um Layer nach Feldern zu filtern, Daten zu gruppieren und Statistiken anzuzeigen."
sidebar_position: 2
---


# Daten

**Dieser Abschnitt enthält Widgets, die Ihnen helfen, mit Ihren Daten zu interagieren und sie zu analysieren**: **Filter**, **Tabelle**, **Zahlen** und **Rich Text**.

## Filter

Dieses Widget ist ein interaktives Element, das **es Benutzern ermöglicht, Daten auf dem konfigurierten Layer basierend auf dem ausgewählten Attributfeld zu filtern**. Betrachter können dies als **Zuschneide-Werkzeug auf den Karten** verwenden.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Ziehen Sie das <code>Filter</code> Widget per Drag & Drop auf ein Panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Wählen Sie Ihren <code>Layer</code> und wählen Sie das <code>Feld</code>, <b>nach dem Sie filtern möchten</b>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Fügen Sie optional einen <code>Platzhalter</code>-Text hinzu, der vor der Anwendung des Filters erscheint.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Aktivieren oder deaktivieren Sie <code>Kreuzfilter</code>, um <b>dieses Widget mit anderen Daten-Widgets interagieren zu lassen</b>. Wenn aktiviert, wird das Filtern von Daten in einem Widget automatisch alle anderen verbundenen Widgets auf Ihrem Dashboard aktualisieren.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Aktivieren oder deaktivieren Sie die Option <code>Zoomen zur Auswahl</code>, wodurch die <b>Kartenansicht automatisch zu den gefilterten Daten geschwenkt wird</b>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Aktivieren Sie <code>Filtern per Kartenklick</code>, damit Betrachter den Filter durch Klicken auf ein Feature direkt in der Karte setzen können. Beim Klick auf ein Feature wird dessen Wert für das konfigurierte Feld als Filter übernommen. Wenn <code>Mehrfachauswahl erlauben</code> aktiviert ist, kann durch Klicken ein Wert ein- oder ausgeschlossen werden. Nicht verfügbar für das Layout <code>Bereich</code>.</div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_filter.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Tabelle

Das Tabellen-Widget **zeigt Daten eines Layers als scrollbare Tabelle**. Sie können rohe Datensätze anzeigen, Daten gruppiert aggregieren oder eine eigene SQL-Abfrage schreiben.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Ziehen Sie das <code>Tabelle</code>-Widget per Drag & Drop auf ein Panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Unter <code>Info</code> fügen Sie einen <code>Titel</code> und eine optionale <code>Beschreibung</code> hinzu.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Unter <code>Daten</code> wählen Sie Ihren <code>Layer</code> aus.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Wählen Sie die <code>Datenquelle</code>:
  <ul>
    <li><code>Dashboard-Konfiguration</code>: Spalten und Gruppierung visuell konfigurieren</li>
    <li><code>SQL-Abfrage</code>: eigene SQL-Abfrage gegen den Layer schreiben</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">
  Im Modus <b>Dashboard-Konfiguration</b> wählen Sie den <code>Modus</code>:
  <ul>
    <li><code>Records</code>: zeigt alle Zeilen an. Mit <code>Visible fields</code> wählen Sie, welche Spalten angezeigt werden.</li>
    <li><code>Grouped</code>: aggregiert Daten nach Feld. Definieren Sie eine oder mehrere <code>Wertspalten</code> (jeweils mit einer Statistik: Count, Sum, Mean, Median, Min, Max), ein <code>Gruppierungsfeld</code> und optional ein <code>Secondary group-by field</code>. Klicken Sie auf <code>+ Add column</code>, um weitere Wertspalten hinzuzufügen.</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Im Modus <b>SQL-Abfrage</b> klicken Sie auf <code>Write SQL Query</code> (oder <code>Edit SQL Query</code>), um den SQL-Editor zu öffnen.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Im Modus Dashboard-Konfiguration verwenden Sie <code>Sortieren nach</code> und <code>Aufsteigend sortieren</code>, um die Standard-Zeilenreihenfolge festzulegen. Betrachter können die Tabelle auch interaktiv sortieren, indem sie auf eine Spaltenüberschrift klicken: Der erste Klick sortiert aufsteigend, ein zweiter Klick absteigend und ein dritter Klick hebt die Sortierung auf. Ein Pfeilsymbol in der Überschrift zeigt die aktive Sortierrichtung an.</div>
</div>

<div class="step">
  <div class="step-number">8</div>
  <div class="content">
  Unter <code>Layout</code> konfigurieren Sie das Erscheinungsbild der Tabelle:
  <ul>
    <li><code>Sticky header</code>: Spaltenüberschrift beim Scrollen sichtbar halten</li>
    <li><code>Show totals</code>: Summenzeile am Ende der Tabelle anzeigen</li>
    <li><code>Display mode</code> (<code>Flat</code> / <code>Collapsible</code>): verfügbar wenn ein sekundäres Gruppierungsfeld gesetzt ist oder im SQL-Modus. Im Modus <code>Collapsible</code> können Sie zusätzlich <code>Start expanded</code> und <code>Show subtotals</code> aktivieren.</li>
  </ul>
  </div>
</div>

<div class="step">
  <div class="step-number">9</div>
  <div class="content">Unter <code>Stil</code> legen Sie die <code>Header Color</code> fest.</div>
</div>

<div class="step">
  <div class="step-number">10</div>
  <div class="content">
  Unter <code>Optionen</code>:
  <ul>
    <li><code>Nach Kartenausschnitt filtern</code>: nur Zeilen innerhalb der aktuellen Kartenansicht berücksichtigen</li>
    <li><code>Angezeigte Zeilen</code>: Anzahl der initial geladenen Zeilen und Nachladegröße beim Scrollen (1–20)</li>
  </ul>
  </div>
</div>

## Zahlen

Wählen Sie aus verschiedenen statistischen Methoden, die auf einem Layer berechnet werden sollen.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Ziehen Sie das <code>Zahlen</code> Widget per Drag & Drop auf ein Panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Wählen Sie Ihren <code>Layer</code> aus. </div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie die <code>statistische Methode</code>, die Sie anwenden möchten. Es kann <code>Anzahl</code>, <code>Summe</code>, <code>Min</code>, <code>Max</code> sein oder Sie fügen Ihren eigenen [<code>Ausdruck</code>](../expressions) hinzu. </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Wählen Sie das <code>Feld</code> aus, <b>auf das die Statistik angewendet werden soll</b>. <i>Summe, Min und Max können nur auf numerische Felder angewendet werden.</i></div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Aktivieren oder deaktivieren Sie die Option <code>Nach Kartenausschnitt filtern</code>, wodurch <b>nur die Daten innerhalb der aktuellen Kartenansicht sichtbar werden</b>.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Legen Sie das <code>Zahlenformat</code> aus der Dropdown-Liste fest. Das Standardformat richtet sich nach der Sprache der Oberfläche.</div>
</div>


<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/builder/builder_number.mp4').default} alt="recent datasets" style={{ maxHeight: "500px", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Rich Text

Das Rich-Text-Widget **zeigt formatierten Text mit optionalen dynamischen Werten** aus Layer-Statistiken. Verwenden Sie es, um Kontext, Beschreibungen oder live-aktualisierende Kennzahlen zu Ihrem Dashboard hinzuzufügen.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Ziehen Sie das <code>Rich Text</code>-Widget per Drag & Drop auf ein Panel.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Tippen und formatieren Sie Ihren Text direkt im Widget-Editor.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Unter <code>Variablen</code> klicken Sie auf <code>Variable hinzufügen</code>, um eine benannte Variable (z.B. <code>var_1</code>) zu definieren, die mit einem Layer-Feld und einer Statistikoperation verknüpft ist. Verwenden Sie <code>Variable einfügen</code> in der Editor-Symbolleiste, um die Variable in Ihren Text einzufügen.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">
  Unter <code>Optionen</code>:
  <ul>
    <li><code>Nach Kartenausschnitt filtern</code>: Variablenwerte aktualisieren sich auf Daten innerhalb der aktuellen Kartenansicht</li>
    <li><code>Ausblenden ohne Filter</code>: blendet das Widget aus, wenn kein Filter aktiv ist. Wenn deaktiviert, legen Sie einen <code>Fallback-Text</code> fest, der stattdessen angezeigt wird.</li>
  </ul>
  </div>
</div>