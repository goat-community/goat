---
sidebar_position: 3
---

# Datensätze

Auf der **Datensätze**-Seite können Daten **hochgeladen, verwaltet und geteilt** werden. Die Seite bietet den Nutzern eine organisierte Ansicht ihrer Datensätze, kategorisiert nach persönlichen Datensätzen, Team-Datensätzen und Datensätzen, die mit der gesamten Organisation geteilt werden. Darüber hinaus können Daten in **Ordnern** organisiert, **gefiltert** und **sortiert** werden, basierend auf ihrem Namen, Erstellungsdatum oder Datum der letzten Aktualisierung. Datensätze können auch **gelöscht**, **heruntergeladen** und deren **Metadaten** bearbeitet werden.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/datasets_general.png').default} alt="Datasets Page in Workspace of GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Daten hochladen

GOAT unterstützt das Hochladen von **GeoPackage-, GeoJSON-, Shapefile-, KML-, CSV**- und **XLSX**-Dateien. Folgen Sie diesen Schritten, um einen Datensatz über den Workspace hinzuzufügen:


<div class="step">
  <div class="step-number">1</div>
  <div class="content">Navigieren Sie zur <b>"Datensatz"</b> Seite mithilfe der Nebenleiste</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Klicken Sie auf <code>+ Datensatz hinzufügen</code>. </div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Wählen Sie eine Datei von Ihrem Rechner.</div>
</div>

<div class="step">
  <div class="step-number">4</div>
  <div class="content">Wählen Sie einen <b>Zielordner</b> und definieren Sie den <b>Namen</b> Ihres neuen Datensatzes. Des weiteren können Sie bei Bedarf eine <b>Beschreibung</b> hinzufügen.</div>
</div>

<div class="step">
  <div class="step-number">5</div>
  <div class="content">Überprüfen Sie ihre Informationen und klicken anschließend auf <code>Hochladen</code>.</div>
</div>



:::tip Tipp

Sie können Datensätze auch direkt in der [Karte](../map/layers) hochladen.

:::

## Datensätze filtern

Datensätze können basierend auf dem [Datensatztyp](../data/dataset_types "Was sind die Datensatztypen?") sortiert werden, d.h. *Features, Tabellen*, *externe Bilder und externe Vektorkacheln*. Klicken Sie einfach auf das Filtersymbol <img src={require('/img/map/filter/filter_icon.png').default} alt="Filter Icon" style={{ maxHeight: "20px", maxWidth: "20px"}}/>, um den gewünschten Datensatztyp für die Filterung auszuwählen.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/dataset_filter.gif').default} alt="Datasets filtering in Workspace of GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Datensätze verwalten
Durch Klicken auf die drei Punkte <img src={require('/img/map/filter/3dots.png').default} alt="Optionen" style={{ maxHeight: "25px", maxWidth: "25px", objectFit: "cover"}}/> können Sie die Metadaten von Datensätzen anzeigen und bearbeiten, einen Datensatz in einen anderen Ordner verschieben, ihn herunterladen, den Datensatz mit anderen Personen teilen oder ihn löschen.
<img src={require('/img/workspace/datasets/managing_datasets.gif').default} alt="Options" style={{ maxHeight: "300px", maxWidth: "300px"}}/>


## Metadaten der Datensätze anzeigen

Die **Metadaten** von Datensätzen können angezeigt und bearbeitet werden, indem Sie auf <code>Info</code> unter den drei Punkten <img src={require('/img/map/filter/3dots.png').default} alt="Optionen" style={{ maxHeight: "25px", maxWidth: "25px", objectFit: "cover"}}/> oder direkt auf den Datensatz klicken. Dies gewährt Zugang zu einer detaillierten **Zusammenfassung** der Daten, der **Attributtabelle** und einer **Kartenansicht mit Legende**.
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/metadata.gif').default} alt="Metadaten der Datensätze im Workspace von GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Ordner erstellen

Um Ihre Daten zu organisieren, können Sie neue Ordner im Arbeitsbereich erstellen. Klicken Sie dazu auf ``Neuer Ordner`` <img src={require('/img/workspace/datasets/folder_icon.png').default} alt="Neuer Ordner" style={{ maxHeight: "25px", maxWidth: "25px"}}/> und legen Sie den Namen des neuen Ordners fest.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/new_folder.gif').default} alt="Neue Ordner im Workspace von GOAT erstellen" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 

## Datensätze in Ordner verschieben

Um einen Datensatz in einen Ordner zu verschieben, klicken Sie auf die drei Punkte <img src={require('/img/map/filter/3dots.png').default} alt="Optionen" style={{ maxHeight: "25px", maxWidth: "25px"}}/> und wählen Sie **"In den Ordner verschieben"**. Wählen Sie im Dropdown-Menü den Ordner aus, in den Sie Ihren Datensatz verschieben möchten.

<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
  <img src={require('/img/workspace/datasets/move_to_folder.gif').default} alt="Verschieben Sie Ihre Datensätze in die Ordner im Workspace von GOAT" style={{ maxHeight: "auto", maxWidth: "auto", objectFit: "cover"}}/>
</div> 
