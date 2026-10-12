---
description: "Veröffentlichen Sie ein Projekt, damit alle die Karte ohne GOAT-Konto sehen, teilen Sie es per URL oder iframe und sperren Sie die Kartenausdehnung, oder machen Sie einen Datensatz für alle GOAT-Nutzer öffentlich."
sidebar_position: 2
---

# Öffentliches Teilen

In GOAT können Sie zwei Arten von Inhalten öffentlich machen: ein **Projekt**, damit jeder seine Karte ohne GOAT-Konto ansehen kann, und einen **Datensatz**, damit alle angemeldeten GOAT-Nutzer ihn verwenden können. Diese Seite behandelt beides.

## Ein Projekt im Web veröffentlichen

Sie können ein **Projekt veröffentlichen, sodass jeder seine Karte ohne GOAT-Konto ansehen kann**. Das eignet sich ideal, um räumliche Analysen zu präsentieren, Einblicke zu teilen oder interaktive Karten auf externen Plattformen einzubetten.

Beim Veröffentlichen entsteht eine **Momentaufnahme** des Projekts: Die öffentliche Seite zeigt das Projekt so, wie es zum Zeitpunkt der Veröffentlichung war, während das Projekt selbst an seinem Platz bleibt und seine Zugriffsrechte behält. Besucher sehen das Projekt so, wie es im [Dashboard](../builder/builder_interface) angeordnet ist.

::::info
Öffentliches Teilen ist nur zum Ansehen. Wenn andere die Karte **bearbeiten** sollen, teilen Sie sie in den Tabs <code>Personen</code> und <code>Teams</code> des Dialogs <code>Teilen</code>. Siehe [Teams & Mitglieder](../sharing).
::::

### Wie teile ich eine Karte öffentlich?

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/sharing/public_tab_published_de.webp').default} alt="Der Tab Öffentlich vor und nach dem Veröffentlichen eines Projekts" style={{ maxHeight: "auto", maxWidth: "100%", objectFit: "contain"}}/>
</div>
<p> </p>

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie oben rechts in der Karte auf <code>Teilen</code>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Öffnen Sie den Tab <code>Öffentlich</code>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Klicken Sie auf <code>Im Web veröffentlichen</code>.</div>
</div>

Nun können Sie:

- <code>Link kopieren</code> unter <code>Adresse</code>: <b>Teilen Sie den Direktlink</b>, damit andere die Karte im Browser öffnen können.

- <code>Kopieren</code> neben <code>Code einbetten</code> unter <code>Einbetten</code>: <b>Betten Sie die Karte</b> als iframe in Websites oder Tools ein, die HTML und iframes unterstützen.

### Weitere Einstellungen im Tab „Öffentlich“

Sobald das Projekt veröffentlicht ist, bietet der Tab <code>Öffentlich</code> außerdem diese Einstellungen:

- <code>Adresse</code>: Wenn Ihre Organisation eine eigene Domain eingerichtet hat, wählen Sie hier, ob die Karte über diese Domain oder über die <code>GOAT-Standarddomain</code> bereitgestellt wird. Ohne eigene Domain zeigt dieser Abschnitt nur den Link. Eigene Domains richten Sie unter [Einstellungen](../workspace/settings) ein.

- <code>Messung</code>: Hier legen Sie fest, ob Besuche der öffentlichen Seite gezählt werden. Was Sie sehen, hängt von Ihrer Organisation ab:
    - Hat sie noch **keine Analytics-Instanz**, zeigt dieser Abschnitt <code>Keine Analytics-Instanzen konfiguriert</code> und wo Sie eine hinzufügen. Das Einrichten ist unter [Analytics](../workspace/settings#analytics) beschrieben.
    - Hat sie **eine oder mehrere Instanzen**, wählen Sie eine, um Besuche zu zählen, oder <code>Kein Tracking</code>. Sobald Sie eine Instanz wählen, lässt sich der Schalter <code>Cookie-Einwilligungsbanner</code> darunter verwenden (bei <code>Kein Tracking</code> ist er ausgegraut und zeigt <code>Nicht erforderlich — es wird nichts erfasst</code>): Lassen Sie ihn an, um Besucher zu fragen, bevor das Tracking startet. Schalten Sie ihn aus, zeigt GOAT eine Warnung, denn ohne Einwilligung ist Tracking in Deutschland und den meisten EU-Ländern nicht mit der DSGVO vereinbar.

### Kartenausdehnung anpassen

Um zu steuern, wie weit Nutzer die Karte verschieben und herauszoomen können, können Sie die Kartenausdehnung sperren.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <Video src={require('/img/sharing/sharing_lock_extent.mp4').default} alt="Öffentliches Teilen in GOAT" style={{ maxHeight: "750px", maxWidth: "750px", objectFit: "cover"}}/>
</div>
<p> </p>

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Verschieben und zoomen Sie die Karte so, dass sie den <b>größten Bereich</b> zeigt, den Nutzer sehen können sollen.</div>
</div>
<div class="step">
  <div class="step-number">2</div>
  <div class="content">Öffnen Sie das GOAT-Menü, indem Sie oben links auf das GOAT-Logo klicken.</div>
</div>
<div class="step">
  <div class="step-number">3</div>
  <div class="content">Klicken Sie auf <code>Kartenausdehnung sperren</code>. Die Karte lässt sich nun nicht mehr über diesen Bereich hinaus verschieben oder herauszoomen. Um die Sperre aufzuheben, klicken Sie im selben Menü auf <code>Kartenansicht entsperren</code>.</div>
</div>

Um stattdessen die Zoomstufen zu begrenzen, nutzen Sie <code>Zoom-Grenzen</code> in den [Einstellungen](../builder/settings) des Dashboards.

::::info
Wenn Ihre Karte bereits veröffentlicht ist, **müssen Sie sie erneut veröffentlichen**, damit die Änderungen wirksam werden. Der Link bleibt gleich.
::::

### Öffentliche Karte aktualisieren (erneut veröffentlichen)

Die öffentliche Seite übernimmt spätere Änderungen am Projekt nicht automatisch. So aktualisieren Sie sie mit Ihren neuesten Änderungen:

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie oben rechts auf <code>Teilen</code>.</div>
</div>
<div class="step">
  <div class="step-number">2</div>
  <div class="content">Öffnen Sie den Tab <code>Öffentlich</code>.</div>
</div>
<div class="step">
  <div class="step-number">3</div>
  <div class="content">Klicken Sie auf <code>Aktualisieren</code>. Die Momentaufnahme wird durch den aktuellen Stand des Projekts ersetzt; der Link bleibt gleich, sodass auch eingebettete Karten die neue Version zeigen.</div>
</div>

### Veröffentlichung aufheben

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie oben rechts auf <code>Teilen</code> und öffnen Sie den Tab <code>Öffentlich</code>.</div>
</div>
<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie unter <code>Offline nehmen</code> auf <code>Veröffentlichung aufheben</code>. Der Link funktioniert dann für niemanden mehr, auch nicht in eingebetteten Karten. Sie können jederzeit erneut veröffentlichen.</div>
</div>

## Einen Datensatz öffentlich machen

Als Eigentümer eines Datensatzes können Sie ihn **für alle GOAT-Nutzer öffentlich** machen. Dabei entsteht kein öffentlicher Link und keine Momentaufnahme: Der Datensatz wird nur für andere angemeldete GOAT-Nutzer geöffnet.

<div class="step">
   <div class="step-number">1</div>
   <div class="content">Öffnen Sie das <code>Weitere Optionen</code>-Menü <img src={require('/img/icons/3dots.png').default} alt="Weitere Optionen" style={{ maxHeight: '20px', maxWidth: '20px'}}/> des Datensatzes, wählen Sie <code>Teilen</code>, öffnen Sie den Tab <code>Öffentlich</code> und aktivieren Sie <code>Öffentlich für alle GOAT-Nutzer</code>.</div>
</div>

Sobald er öffentlich ist, kann **jeder angemeldete GOAT-Nutzer, in jeder Organisation, den Datensatz ansehen und zu seinen Projekten hinzufügen**. Er wird nirgends aufgelistet; man erreicht ihn über die Projekte und Vorlagen, die ihn enthalten, und die Bearbeitungsrechte ändern sich nicht. Wenn ein öffentlicher Datensatz mit einer Vorlage mitgeliefert wird, wird er mit einem **öffentlich-Badge** angezeigt.
