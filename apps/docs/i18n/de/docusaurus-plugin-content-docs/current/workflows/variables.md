---
description: "Legen Sie Variablen vom Typ Text oder Zahl mit Standardwert an, fügen Sie sie in Werkzeugparameter ein und setzen Sie Werte beim Start aus der Kartenansicht."
---

# Variablen

**Workflow-Variablen** ermöglichen es Ihnen, wiederverwendbare Werte zu definieren, die zur Laufzeit gesetzt werden können, ohne den Workflow zu bearbeiten. Nutzen Sie sie, um Ihre Analyse flexibel und teilbar zu machen: Mitarbeitende können denselben Workflow mit anderen Parametern ausführen, ohne die Workflow-Struktur zu ändern.

Variablen verwenden die Syntax `{{@variable_name}}` und können in die meisten Werkzeugparameter eingefügt werden.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <img src={require('/img/workflows/variables_de.webp').default} alt="Workflow-Variablen" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div>

## Variablentypen

| Typ | Verwendung |
|---|---|
| **Text** | Textwerte: Namen, Beschriftungen, Filterkriterien |
| **Zahl** | Numerische Werte: Entfernungen, Schwellenwerte, Zählungen |

## Variablen erstellen

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie auf das <code>{"{}"}</code>-Symbol <strong>Variablen</strong> in der Werkzeugleiste am unteren Rand der Leinwand, um den Variablen-Dialog zu öffnen.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie auf <strong>Variable hinzufügen</strong>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Geben Sie einen <strong>Namen</strong> ein. Namen müssen mit einem Buchstaben oder Unterstrich beginnen und dürfen nur Buchstaben, Ziffern und Unterstriche enthalten, keine Leerzeichen (z. B. <code>puffer_abstand</code>, nicht <code>puffer abstand</code>).</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Wählen Sie einen <strong>Typ</strong>: <code>Text</code> oder <code>Zahl</code>.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Geben Sie optional einen <strong>Standardwert</strong> ein.</div>
</div>

<div class="step">
  <div class="step-number">6</div>
  <div class="content">Geben Sie optional eine <strong>Bezeichnung</strong> ein. Die Bezeichnung sehen Nutzende anstelle des technischen Namens, überall dort, wo sie die Variable auswählen oder ihren Wert setzen (z. B. <code>Maximaler Abstand der Gruppierung</code> für <code>max_abstand_gruppierung</code>). Ausdrücke und SQL verwenden weiterhin den Namen. Für einen Hilfetext klicken Sie auf die Sprechblase <img src={require('/img/icons/chat-bubble.png').default} alt="Beschreibung" style={{ maxHeight: '20px', maxWidth: '20px', verticalAlign: 'middle'}}/> neben der Variable, geben eine <strong>Beschreibung</strong> ein (bis zu 500 Zeichen) und klicken neben das Feld, um sie zu übernehmen; mit <code>Esc</code> verwerfen Sie die Änderung. Ein ausgefülltes Symbol <img src={require('/img/icons/chat-bubble-filled.png').default} alt="Beschreibung vorhanden" style={{ maxHeight: '20px', maxWidth: '20px', verticalAlign: 'middle'}}/> zeigt, dass eine Variable eine Beschreibung hat; beim Darüberfahren erscheint der Text.</div>
</div>

<div class="step">
  <div class="step-number">7</div>
  <div class="content">Klicken Sie auf <strong>Fertig</strong>, um zu speichern. Um eine Variable zu löschen, klicken Sie auf das Löschen-Symbol daneben.</div>
</div>

## Variablen in Werkzeugparametern verwenden

Klicken Sie auf das <code>{"{}"}</code>-Symbol in einem kompatiblen Parameterfeld und wählen Sie die gewünschte Variable aus dem Menü. Nach dem Einfügen zeigt das Feld den Variablenverweis (z. B. <code>{"{{@variable_name}}"}</code>) grün hervorgehoben an. Das signalisiert, dass das Feld durch eine Variable gesteuert wird.

Eine Variable mit Bezeichnung wird mit ihrer Bezeichnung aufgeführt, der Verweis steht daneben, und ihre Beschreibung erscheint, wenn Sie mit der Maus darüberfahren. Ein Feld, das eine Variable mit Bezeichnung enthält, zeigt die Bezeichnung darunter an. Wenn Sie <code>{"{{@"}</code> in ein Feld tippen, berücksichtigen die Vorschläge Namen und Bezeichnungen; im SQL-Editor suchen sie nach Namen und zeigen die Bezeichnung neben dem Namen.

:::tip
Verwenden Sie beschreibende Namen, die den Zweck des Parameters klar angeben: `puffer_abstand` statt `abstand`, `poi_typ` statt `typ`.
:::

## Workflows mit Variablen aus der Kartenansicht ausführen

Workflows mit Variablen können direkt aus der Kartenansicht ausgeführt werden, ohne den Workflow-Editor zu öffnen.

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Öffnen Sie die <code>Toolbox</code> und klicken Sie auf den Tab <strong>Workflows</strong>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie auf einen Workflow aus der Liste, um ihn zu öffnen.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Ein Abschnitt <strong>Variablen</strong> zeigt alle im Workflow definierten Variablen. Geben Sie die gewünschten Werte für diesen Durchlauf ein. Jedes Feld trägt die Bezeichnung der Variable (oder ihren Namen, wenn sie keine hat), ihre Beschreibung steht unter dem Feld.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Klicken Sie auf <strong>Ausführen</strong>. Der Workflow wird mit den eingegebenen Werten ausgeführt. Klicken Sie auf <strong>Zurücksetzen</strong>, um die Standardwerte wiederherzustellen.</div>
</div>

:::info
Die hier eingegebenen Werte gelten nur für diesen Durchlauf. Beim nächsten Öffnen des Workflows werden die Standardwerte wiederhergestellt.
:::
