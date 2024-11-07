---
sidebar_position: 10
slug: /troubleshooting
---

# Fehlerbehebung

Bei der Verwendung von GOAT können Probleme bei bestimmten Aufgaben auftreten, die Sie ausführen möchten. Diese Probleme resultieren in der Regel aus den Rechenbeschränkungen von GOAT. Solche Beschränkungen sind wichtig, um die Stabilität und Effizienz des Servers zu gewährleisten und eine zuverlässige Leistung sicherzustellen. Das Verständnis und die Behebung dieser Probleme hilft Ihnen, mit Ihrer Analyse weiterzukommen. Diese Seite soll Sie durch gängige Fehler führen und Ihnen helfen, diese zu lösen, damit Sie Ihre Arbeit mit GOAT fortsetzen können.

## Job-Fehler

Wenn Sie eine Analyse in einem Projekt ausführen, wird die Aufgabe in der Software als **Job** bezeichnet. Eine Fehlermeldung mit **Job-Fehler** bedeutet, dass die Aufgabe nicht ausgeführt werden konnte. Um mehr über die Ursache des Fehlers zu erfahren, überprüfen Sie bitte die [Statusleiste](workspace/home#statusleiste). Nachfolgend finden Sie häufige Ursachen für Job-Fehler und Vorschläge zu deren Behebung.

* Analysen dürfen eine Dauer von zwei Minuten nicht überschreiten, und es gibt eine Begrenzung der Anzahl der Merkmale, die analysiert werden können.

<div style={{ display: "flex", alignItems: "center" }}>
  <img 
    src={require('/img/troubleshooting/arrow-right.png').default} 
    alt="Layers" 
    style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover", marginRight: "8px" }} 
  />
  <span>
    <strong>Sie können den  <a href="map/filter">Filter</a> verwenden, um Ihre Analyse in kleinere Ebenen zu unterteilen.</strong>
  </span>
</div>

  ![Filtern zur Berechnung größerer Flächen](/img/troubleshooting/filtering.jpg "Filtern zur Berechnung größerer Flächen")
  

  
* Bei der Schwerkraftanalyse akzeptiert GOAT keine Empfindlichkeiten über 1.000.000.
<div style={{ display: "flex", alignItems: "center" }}>
  <img 
    src={require('/img/troubleshooting/arrow-right.png').default} 
    alt="Layers" 
    style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover", marginRight: "8px" }} 
  />
  <span>
    <strong>Sie können die vorgeschlagenen Empfindlichkeiten in GOAT als Referenz verwenden.</strong>
  </span>
</div>
  
* Startpunkte eines Routing-Indikators wie Einzugsgebiet oder Nähe zu öffentlichen Verkehrsmitteln sollten weniger als 100m vom Straßennetz entfernt sein.
<div style={{ display: "flex", alignItems: "center" }}>
  <img 
    src={require('/img/troubleshooting/arrow-right.png').default} 
    alt="Layers" 
    style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover", marginRight: "8px" }} 
  />
  <span>
    <strong>Sie können das Netz entweder direkt mit der Grundkarte oder durch Visualisierung der Straßennetzebene in Szenarien anzeigen.</strong>
  </span>
</div>
  

![Startpunkt der Streckenführung](/img/troubleshooting/routing_start.jpeg "Startpunkt der Streckenführung")

* Wenn Sie einen Indikator berechnen, aber das Ergebnis leer ist, wird kein Output bereitgestellt und ein Job-Fehler tritt auf. Beispielsweise schlägt die Berechnung der Anzahl von ÖPNV-Fahrten in einem Gebiet und einem Zeitraum ohne Fahrten mit dem Fehler **The Layer is None** fehl.
<div style={{ display: "flex", alignItems: "center" }}>
  <img 
    src={require('/img/troubleshooting/arrow-right.png').default} 
    alt="Layers" 
    style={{ maxHeight: "20px", maxWidth: "20px", objectFit: "cover", marginRight: "8px" }} 
  />
  <span>
    <strong>Versuchen Sie, den räumlichen oder zeitlichen Bereich Ihrer Analyse zu erweitern.</strong>
  </span>
</div>

## Fehler beim Hochladen von Datensätzen

* Wenn Sie versuchen, einen Datensatz hochzuladen, der von GOAT nicht unterstützt wird, tritt ein Fehler auf. Siehe die autorisierten [Datensatztypen](data/dataset_types).
