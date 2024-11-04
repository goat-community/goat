---
sidebar_position: 4
---

# Katalog

Der **Datenkatalog** ist eine umfassende Liste aller verfügbaren [räumlichen Datensätzen](../further_reading/glossary#geospatial-data) zur Erkundung und Analyse. Eine breite Palette von Datensätzen wird von Plan4Better, unseren Partnern und Open-Source-Bibliotheken bereitgestellt, wodurch eine **zuverlässige und genaue** Datenbank für Ihre GIS-Projekte sichergestellt wird.

<div class="content"><img src={require('/img/workspace/catalog/home-catalog.png').default} alt="Data Catalog" style={{ maxHeight: "700px", maxWidth: "800px"}}/></div>

## Den Katalog erkunden

Der Zugang erfolgt über den [Workspace](../category/workspace) oder über die Schaltfläche [`+ Layer hinzufügen`](../map/layers#add-layers) in Ihrem GOAT-Projekt. Sie können unsere Sammlung von Datensätzen nach *Schlüsselwörtern durchsuchen und räumliche und nicht-räumliche Filter* anwenden, um eine effiziente Entdeckung zu ermöglichen. Sie können auch Datensätze interaktiv in unserer Benutzeroberfläche vorab ansehen, um den Inhalt und die Qualität zu bewerten und so eine visuelle Erkundung ermöglichen. Seien Sie versichert, dass unsere Sammlung aus autoritativen Quellen stammt und eine hohe Datenqualität aufweist.

Unser Katalog bietet eine umfangreiche Sammlung von Datensätzen, die verschiedene thematische Bereiche abdecken und in verschiedenen Kategorien unterteilt sind, darunter:

- **Grundkarte:** Grundlegende Kartenebene, die wesentliche geografische Merkmale wie Küstenlinien, Flüsse und Gelände enthält und als Hintergrund für zusätzliche Daenebenen dient.

- **Bildmaterial:** Hochauflösende visuelle Daten, die von Satelliten oder Luftaufnahmen erfasst wurden und detaillierte Ansichten von Landschaften, städtischen Gebieten und Infrastrukturen bieten.

- **Grenzen:** Räumliche Abgrenzungen, die administrative, politische oder geografische Grenzen darstellen, einschließlich Landesgrenzen, Staats-/Provinzgrenzen und Gemeindebezirke.

- **Landnutzung:** Kategorisierung von Landflächen basierend auf ihrer primären Nutzung, einschließlich Klassifikationen wie Wohngebiete, Gewerbegebiete, Industriegebiete, Landwirtschafts- und Erholungszonen.

- **Umwelt:** Daten, die natürliche Merkmale und Phänomene darstellen, wie Ökosysteme, Klimamuster und ökologische Lebensräume.

- **Menschen:** Demografische Daten zu menschlichen Popultionen, wie Bevölkerungsdichte, Bevölkerungsverteilung, Altersgruppen und sozioökonomische Merkmale.

- **Verkehr** Informationen zu Verkehrsnetzen und Infrastrukturen, einschließlich Straßen, Autobahnen, Eisenbahnen, Flughäfen, Häfen und öffentlichen Verkehrssystemen.

- **Orte:** Sehenswürdigkeiten und geographische Wahrzeichen wie Schulen, Carsharing-Standorte, Touristenattraktionen und Krankenhäuser.

![Datenkatalog in GOAT](/img/workspace/catalog/catalog_general.png "Datenkatalog in GOAT")

Ein Klick auf einen Datensatz innerhalb der Katalogseite führt Sie zum **Metadaten**-Bereich. Hier können Sie detaillierte Informationen zum Datensatz ansehen, einschließlich seiner **Beschreibung**, den **[Datensatztyp](../data/dataset_types)**, der **geografischen Ausdehnung** und des **Sprachcodes** (basierend auf dem [ISO 3166-1 alpha-2](https://www.iso.org/iso-3166-country-codes.html)), den **Verteilernamen** sowie die **Lizenzdetails**. Sie können auch die **Kartenvorschau des Datensatzes** und die zugehörigen Daten direkt von der Datenseite aus ansehen.

## Katalogdaten in Ihrem GOAT-Projekt verwenden

<div class="step">
  <div class="step-number">1</div>
  <div class="content"> Unter <b>Layer</b> klicke Sie auf <code> + Layer hinzufügen</code>.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content"> Wählen Sie <code>Katalog Explorer</code> aus.</div>
</div>

<div class="content"><img src={require('/img/workspace/catalog/map-catalog.png').default} alt="Catalog Explorer" style={{ maxHeight: "700px", maxWidth: "800px"}}/></div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content"> Wählen Sie einen <i>Datensatz</i> und klicken anschließend auf <code>Layer hinzufügen</code>.</div>
</div>

<div class="content"><img src={require('/img/workspace/catalog/add-layer.png').default} alt="Catalog Explorer" style={{ maxHeight: "700px", maxWidth: "800px"}}/></div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Nach dem Hinzufügen wenden Sie einen <code><img src={require('/img/map/filter/filter_icon.png').default} alt="Filter Icon" style={{ maxHeight: "16px", maxWidth: "16px"}}/> Filter</code> auf den neuen Layer an. Dies wird die Daten durch einen logischen oder räumlichen Ausdruck filtern, sodass nur die für Ihre Analyse erforderlichen Daten beibehalten werden und die Arbeit erleichtert wird.</div>
</div>


:::tip Tipp

Um mehr über die erweiterten Filterfunktionen von GOAT zu erfahren, besuchen Sie die Seite [Filter](../map/filter.md "Filter dataset").

:::
