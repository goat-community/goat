---
sidebar_position: 9
---

# 15-Min-Score

The 15-Min-Score gives a city-wide overview of how good the accessibility is to important destinations of the 15-minute city: housing, leisure, shopping, public transport, education and health. The easier the various facilities can be reached on foot, the higher the score (on a scale of 0-100).

![15-min-city score](/img/docs/indicators/scores/15-min-score/15-min-score-muenchen.png "15-min-city score")

## 1. Explanation

The 15-minute-city is <i>“an urban set-up where locals are able to access all of their basic essentials at distances that would not take them more than 15 min by foot or by bicycle”</i> (Moreno et al., 2021, S. 100). The 15-min-score shows on a hexagonal grid, how good accessibility to these basic needs is given. The score takes the following destinations into account: 

![Essential destinations of the 15-min-city](/img/docs/indicators/scores/15-min-score/15-min-score-categories.png "Essential destinations of the 15-min-city")

TODO: translate the image


TODO: add info from https://plan4better-my.sharepoint.com/:w:/g/personal/elias_pajares_plan4better_de/EQsnShs-E0RDk6Eo__jDfSQBgb0xBILtYJPUqPf2NsIq5Q?e=YeT0JI
  & acatech & Lime report


## 2. Which planning questions can be answered? 

For what can this indicator be used? (planning question list from tutorials)

- How 15-min-city-ready are different neighborhoods? 
- Which neighborhoods are more 15-min-city-ready than others?
- How polycentric is a city? 

## 3. How to use the indicator?

TODO: How to use the indicator? (from tutorials) / Sample calculation(s)
Show as many samples as necessary to explain a feature

## 4. Technical details 

TODO: mit Infos + graphiken aus Acatech report synchen



### 1. Erreichbarkeit je Einrichtungstyp

Die Berechnung des Index basiert auf dem Potentialindikator für den Fußverkehr (Heatmap Lokale Erreichbarkeit). Daher wird für die Berechnung der Erreichbarkeiten zu den einzelnen Zielen, die in Kapitel Indikator 2: Potentialindikator (Heatmap) beschriebene Kalibrierung verwendet.

Zunächst wird pro Hexagon i die Erreichbarkeit Ai zu allen POIs j eines Einrichtungstyps (z.B. Supermärkte) auf Basis der Reisezeit berechnet. Dabei wird je Einrichtungstyps eine kalibrierte Widerstandsfunktion f(tij) verwendet, die statistisch widerspiegelt, wie weit Menschen bereit sind zu einer Einrichtung zu gehen. Diese Widerstandsfunktionen wurden mit Hilfe einer deutschlandweiten Studie für verschiedene Einrichtungen kalibriert und lassen sich auf den gesamten DACH-Raum übertragen. 




A_i=∑_j^ ▒〖D_j f(t_ij ) 〗	(see Lime report)

Ai: 	Erreichbarkeit des Hexagons i
Dj: 	Zielpotential des POIs j
tij: 	Reisezeit zwischen i und j
f(tij): 	Widerstandsfunktion, die auf die Reisezeit zwischen i und j angewendet wird

Die Erreichbarkeitswerte werden stadtweit je Einrichtungstyp statistisch miteinander verglichen und mittels Quintilen klassifiziert. Dadurch entsteht ein speziell auf den Untersuchungsraum angepasst Klassifizierung, die aufzeigt welche Räume eine besonders gute bzw. schlechte Erreichbarkeit zu der jeweiligen Einrichtung aufweisen. Als maximal für Personen zumutbare Reisezeit werden 20 Minuten angenommen, dadurch werden alle Einrichtung die weiter als 20 Minuten vom Mittelpunkt des Hexagons entfernt sind, nicht berücksichtigt. Falls von einem Hexagon keine einzige Einrichtung eines Einrichtungstyps erreicht werden kann, erhält das Hexagon die niedrigste Erreichbarkeitsklasse. 

### 2. Berechnung Subscores

Im nächsten Schritt werden die Erreichbarkeitsklassen je POI zu den sechs Subscores (Bildung, Freizeit, Mobilität, Gesundheit, Service und Einkaufen) zusammengefasst. Hierbei werden erneut Quintile genutzt, um die verschiedenen Einrichtungen in Relation zueinander zu setzen. Somit wird sichergestellt, dass z.B. die in großer Vielzahl vorhandenen Bushaltestellen nicht höher gewichtet werden, als die in geringerer Zahl vorhandenen U-Bahnstationen. 

### 3. Berechnung Gesamtscore

Im nächsten Schritt werden die Subscores zueinander in Relation gesetzt. Durch erneute Bildung von Quintilen entsteht somit der 15-Minuten-Score mit einer Punkte-Skala von 0-100 Punkten. 100 Punkte bedeuten, dass alle Ziele des täglichen Bedarfs innerhalb von 15-Minuten erreicht werden können. 0 Punkte bedeuten, dass die Ziele des täglichen Bedarfs nicht erreicht werden können. Die Punkteabstufungen dazwischen geben eine relative Auskunft über die Erreichbarkeit. Somit dient der 15-Min-Score als allumfassende Analyse, die einen Gesamtüberblick über die Erreichbarkeit zu wichtigen Zielen in einer Stadt gibt. 


## 5. Further readings

(Links to tutorials)
Links to videos
Related docs


- https://www.mdpi.com/2624-6511/4/1/6
- https://www.deloitte.com/global/en/Industries/government-public/perspectives/urban-future-with-a-purpose/15-minute-city.html
- https://www.itv.com/news/2023-02-20/what-is-a-15-minute-city-and-why-is-the-idea-so-controversial
- https://www.eiturbanmobility.eu/wp-content/uploads/2022/11/EIT-UrbanMobilityNext9_15-min-City_144dpi.pdf 

## 6. Resources

bibliography of cited literature


drafts: https://plan4better-my.sharepoint.com/:w:/g/personal/elias_pajares_plan4better_de/EQsnShs-E0RDk6Eo__jDfSQBgb0xBILtYJPUqPf2NsIq5Q?e=5dyphs&isSPOFile=1&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIyNy8yMzA3MDMwNzM0NiIsIkhhc0ZlZGVyYXRlZFVzZXIiOmZhbHNlfQ%3D%3D