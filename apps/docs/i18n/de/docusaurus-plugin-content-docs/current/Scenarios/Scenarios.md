---
sidebar_position: 4
slug: /Scenarios
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Szenarien
Neben der Analyse bestehender realer Daten und Situationen ermöglicht GOAT die Erstellung benutzerdefinierter Szenarien wie Netzwerkänderungen oder neue Infrastrukturprojekte. Wege, Punkte und Polygone können hinzugefügt, bearbeitet oder entfernt werden, und deren Auswirkungen auf die Zugänglichkeit können analysiert werden.

## 1. Erklärung

Mit der Szenarienfunktion können Sie Ihre Layer bearbeiten und Indikatoren basierend auf den vorgenommenen Änderungen berechnen. Der größte Vorteil dieses Tools ist, dass Ihre ursprüngliche Ebene intakt bleibt: Keine Ihrer ursprünglichen Daten werden gelöscht, sodass Sie keine geänderte Ebene neu hochladen müssen, um die verschiedenen Analysen durchzuführen.
Zusätzlich zu Ihren Layern können Sie das [**Straßennetz - Kanten**](#4-straßennetz---kanten) ändern. Diese Ebene ist eine Basisebene, die in allen Projekten verfügbar ist und das Straßennetz darstellt. Sie kann in den Szenarien als Linienebene modifiziert werden.

:::info INFO
Sie können nur **geografische Layer** ändern: Tabellen und Raster können in Szenarien nicht geändert werden. Erfahren Sie hier mehr über die Datentypen [hier](data/data_types)
:::

## 2. Wie bearbeitet man ein Szenario? 

<div class="step">
  <div class="step-number">1</div>
  <div class="content">Klicken Sie auf <code>Szenarien</code>   <img src={require('/img/scenarios/compass-drafting.png').default} alt="Layer" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>. </div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie auf <code>Szenario erstellen</code> und benennen Sie Ihr Szenario. Das Szenario wird der Szenarienliste hinzugefügt. </div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">  Klicken Sie auf die drei Punkte <img src={require('/img/scenarios/3dots.png').default} alt="Layer" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/>  neben dem Szenarionamen, wählen Sie <code>Bearbeiten</code>, um die Layer in einem Szenario zu bearbeiten.
  </div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">  Wählen Sie in <code>Layer auswählen</code> einen Layer zum Bearbeiten aus. In <code>Bearbeitungswerkzeug</code> können Sie <img src={require('/img/scenarios/add.png').default} alt="Layer" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> zeichnen, <img src={require('/img/scenarios/edit.png').default} alt="Layer" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> modifizieren oder <img src={require('/img/scenarios/trash-solid.png').default} alt="Layer" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> Features löschen. </div>
</div>
  <Tabs>

  <TabItem value="Zeichnen" label="Zeichnen" default className="tabItemBox">

  <div class="step">
  <div class="step-number">5</div>
  <div class="content">
    Abhängig vom Layer-Typ können Sie verschiedene geografische Formen zeichnen: </div>
</div>
 <Tabs>
  <TabItem value="Punkt" label="Punkt" default className="tabItemBox">
   Klicken Sie auf die gewünschte Position auf der Karte.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

   <img src={require('/img/scenarios/point_drawing-final.gif').default} alt="Benutzerdefiniertes Ordinal für Zeichenfolgen" style={{ maxHeight: "500px", maxWidth: "500px", objectFit: "cover"}}/>

   </div> 

   Füllen Sie die Attribute Ihrer neuen Features aus, wenn erforderlich. Klicken Sie auf Speichern, um Ihre Daten zu aktualisieren. Die neuen Features sind blau. 
 </TabItem>
  <TabItem value="Linie" label="Linie" default className="tabItemBox">
  Klicken Sie auf die Karte, um eine neue Linie zu zeichnen. Klicken Sie weiter, um die Linie zu formen, und doppelklicken Sie, um das Zeichnen abzuschließen.
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

   <img src={require('/img/scenarios/line_drawing-final.gif').default} alt="Benutzerdefiniertes Ordinal für Zeichenfolgen" style={{ maxHeight: "500px", maxWidth: "500px", objectFit: "cover"}}/>

   </div> 

   Füllen Sie die Attribute Ihrer neuen Features aus, wenn erforderlich. Klicken Sie auf Speichern, um Ihre Daten zu aktualisieren. Die neuen Features sind blau. 
 </TabItem>
   <TabItem value="Polygon" label="Polygon" default className="tabItemBox">
   Klicken Sie auf die Karte, um ein neues Polygon zu zeichnen. Klicken Sie weiter, um jede Ecke zu definieren, und klicken Sie auf den Ausgangspunkt, um die Form zu vervollständigen.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

   <img src={require('/img/scenarios/Polygon_drawing-final.gif').default} alt="Benutzerdefiniertes Ordinal für Zeichenfolgen" style={{ maxHeight: "500px", maxWidth: "500px", objectFit: "cover"}}/>

   </div> 
  Füllen Sie die Attribute Ihrer neuen Features aus, wenn erforderlich. Klicken Sie auf Speichern, um Ihre Daten zu aktualisieren. Die neuen Features sind blau. 
 </TabItem>
   </Tabs>

  </TabItem>

  <TabItem value="Modifizieren" label="Modifizieren" default className="tabItemBox">

<div class="step">
  <div class="step-number">5</div>
  <div class="content"> Wählen Sie ein ursprüngliches Feature oder ein von Ihnen erstelltes aus. Sie können alle verfügbaren Attribute bearbeiten. Klicken Sie auf Speichern, um die Aktualisierungen anzuwenden. Bearbeitete Features aus dem ursprünglichen Datensatz werden gelb hervorgehoben.  </div>
</div>

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

   <img src={require('/img/scenarios/modify_features.png').default} alt="Benutzerdefiniertes Ordinal für Zeichenfolgen" style={{ maxHeight: "500px", maxWidth: "500px", objectFit: "cover"}}/>

   </div> 
  </TabItem>


   <TabItem value="Löschen" label="Löschen" default className="tabItemBox">

   <div class="step">
  <div class="step-number">5</div>
  <div class="content"> Klicken Sie auf das Feature, das Sie löschen möchten, und dann auf die Schaltfläche Löschen im erscheinenden Feld. Gelöschte Features werden rot hervorgehoben.</div>
</div>
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>

   <img src={require('/img/scenarios/delete_feature.png').default} alt="Benutzerdefiniertes Ordinal für Zeichenfolgen" style={{ maxHeight: "500px", maxWidth: "500px", objectFit: "cover"}}/>

   </div> 
  </TabItem>
  </Tabs>


<div class="step">
  <div class="step-number">6</div>
  <div class="content">  Nun können Sie eine Analyse auf Ihrer aktualisierten Ebene durchführen.
  Klicken Sie auf <code>Toolbox</code> und wählen Sie einen Indikator aus. 
</div>  
</div>
  
<div class="step">
  <div class="step-number">7</div>
  <div class="content"> Wählen Sie eine Ebene, die mit einem Szenario verknüpft ist, um Ihre Analyse durchzuführen. Am unteren Rand des Indikatormenüs unter Szenario wählen Sie das zugehörige Szenario aus.
</div>  
</div>

   ![Ebenenanalyse im Szenario](/img/scenarios/layer_analysis.png "Ebenenanalyse im Szenario")


## 3. Szenarienverwaltung
Sie können mehrere Szenarien erstellen, um verschiedene Konfigurationen zu testen. Um Ihre Szenarien zu verwalten, können Sie:

- **Ein Szenario auswählen**: Klicken Sie auf ein Szenario in der Szenarienliste, um dessen spezifische Änderungen oder hinzugefügte Funktionen anzuzeigen.
- **Ein Szenario ändern**: Klicken Sie auf die drei Punkte <img src={require('/img/scenarios/3dots.png').default} alt="Layers" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> neben dem Szenarionamen, um das Szenario umzubenennen oder zu löschen oder um die Ebenen zu bearbeiten.
- **Eine Ebene bearbeiten**: Eine Ebene, die mit einem Szenario verknüpft ist, wird durch <img src={require('/img/scenarios/compass-drafting.png').default} alt="Layers" style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover"}}/> und eine Zahl markiert, die die vorgenommenen Änderungen anzeigt.
- **Ein Szenario abwählen**: Klicken Sie erneut auf das ausgewählte Szenario, um zur Standardkartenansicht zurückzukehren oder ein anderes Szenario auszuwählen.

## 4. Straßennetz - Kanten

Das „Straßennetz – Kanten" ist eine Basisebene, die in allen Projekten verfügbar ist und das [realistische Straßennetz](data/data_basis#street-network-and-topography) darstellt. Sie können die Ebene nur anzeigen, wenn Sie sie im Szenario-Editor auswählen und in die Karte hineinzoomen.  
Mit **Szenarien** können Sie die Linien dieser Basisebene, die Straßen darstellen, ändern.

   ![Straßennetz](/img/scenarios/street_network.png "Straßennetz")

Szenarien, die auf die Straßennetzebene angewendet werden, betreffen nur den Indikator **Einzugsgebiet**. Änderungen am Straßennetz haben keinen Einfluss auf die Berechnung anderer Indikatoren.
