-----------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------GOAT Sport facilities processing----------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------DRAFT!!! ---------------------------------------------------------

-- Spatial join of the sports fields into each sport complex

-- Save polygons with sport centers

DROP TABLE IF EXISTS sport_centers;
CREATE TABLE sport_centers (LIKE planet_osm_polygon INCLUDING ALL);

INSERT INTO sport_centers
	SELECT * FROM planet_osm_polygon WHERE leisure = 'sports_centre' OR name LIKE '%Bezirkssportanlage%';

-- Join sport fields (sport is not null) 

DROP TABLE IF EXISTS grouping_sports;
SELECT pop.osm_id AS group_id, pop.name AS complex_name, pops.sport, count(pops.sport) AS number_fields INTO grouping_sports
FROM sport_centers AS pop 
JOIN (SELECT * FROM planet_osm_polygon pop WHERE sport IS NOT NULL) AS pops
ON st_intersects(pop.way, pops.way) GROUP BY pop.osm_id, pop.name, pops.sport;

SELECT * FROM grouping_sports;

-- Grouped amenities

SELECT group_id, complex_name, array_agg(sport::Text) FROM grouping_sports GROUP BY group_id, complex_name ORDER BY group_id;

-- Left join from grouped amenities into sport complex

DROP TABLE IF EXISTS sport_complex;
SELECT sc.*, s.array_agg AS sports INTO sport_complex
FROM (SELECT * FROM planet_osm_polygon pop WHERE leisure = 'sports_centre' OR name LIKE '%Bezirkssportanlage%' ) AS sc
LEFT JOIN (SELECT group_id, complex_name, array_agg(sport::Text) FROM grouping_sports GROUP BY group_id, complex_name ORDER BY group_id) AS s
ON sc.osm_id = s.group_id;

SELECT * FROM sport_complex;

-- Delete sport complex without sports assigned
DELETE FROM sport_complex WHERE sports IS NULL ;

-- Count the no. of gates per polygon

DROP TABLE IF EXISTS doors_field;
SELECT pol.osm_id, count(poi.osm_id), 'Sport complex with gates' AS "case" INTO doors_field
FROM (SELECT * FROM planet_osm_point pop WHERE barrier = 'gate') poi
JOIN (SELECT * FROM planet_osm_polygon pop WHERE leisure = 'sports_centre' OR name LIKE '%Bezirkssportanlage%') AS pol 
ON st_intersects (poi.way, ST_Boundary(pol.way))
GROUP BY pol.osm_id, pol.way;

SELECT * FROM doors_field;

-- Join back to sport_complex

DROP TABLE IF EXISTS sport_complex_c1;
SELECT sc.*, df."case" INTO sport_complex_c1
FROM sport_complex sc
LEFT JOIN doors_field df ON df.osm_id = sc.osm_id;

SELECT * FROM sport_complex_c1;

-- Case "Sport complex with gates", transfer data to gates (Case 1 completed)

DROP TABLE IF EXISTS sport_gate_pois;
SELECT poi.osm_id AS point_osm_id , sc.*, poi.way AS waypoint INTO sport_gate_pois
FROM (SELECT * FROM planet_osm_point pop WHERE barrier = 'gate') poi
JOIN sport_complex AS sc
ON st_intersects (poi.way, ST_boundary(sc.way));
--ON st_intersects(poi.way, sc.way);

SELECT * FROM sport_gate_pois;

-- Case 2, calculate intersections with main roads
-- Calculate intersection points between  ways (footway, path, service, services) with sport complex polygons

DROP TABLE IF EXISTS sport_complex_inter;
SELECT pol.osm_id, (ST_Dump(ST_Intersection(l.way, ST_boundary(pol.way)))).geom AS geom, pol.way INTO sport_complex_inter
FROM 
(SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','path','service','services'])) AS l, 
(SELECT * FROM sport_complex_c1 WHERE "case" IS NULL) AS pol
WHERE
st_intersects(l.way, pol.way) ;

SELECT * FROM sport_complex_inter;

--SELECT osm_id, count(geom) AS no_of_intersections FROM sport_complex_inter GROUP BY osm_id;
-- join to sport_complex c1, and case = c2

DROP TABLE IF EXISTS sport_complex_c2;

SELECT scc1.*, sc2.no_of_intersections INTO sport_complex_c2
FROM sport_complex_c1 scc1
LEFT JOIN (SELECT osm_id, count(geom) AS no_of_intersections FROM sport_complex_inter GROUP BY osm_id) AS sc2
ON scc1.osm_id = sc2.osm_id;

SELECT * FROM sport_complex_c2;
UPDATE sport_complex_c2
SET "case" = 'Sport_complex_intersections' WHERE no_of_intersections IS NOT NULL;

DROP TABLE IF EXISTS entry_points_intersections;
SELECT sci.geom, scc2.* INTO entry_points_intersections
FROM sport_complex_inter sci
LEFT JOIN sport_complex_c2 scc2
ON sci.osm_id = scc2.osm_id;

-- Join to pois (in this case dummy pois)

DROP TABLE IF EXISTS dummy_pois;
CREATE TABLE dummy_pois (LIKE pois INCLUDING all);
SELECT * FROM dummy_pois;


ALTER TABLE dummy_pois 
ALTER COLUMN amenity TYPE varchar USING ARRAY[3]; 

INSERT INTO dummy_pois (
SELECT osm_id AS osm_id, 'polygon' AS origin_geometry, ACCESS, "addr:housenumber" AS housenumber, sports AS amenity_array, 
tags ->'origin' AS origin, tags ->'organic' AS organic, denomination, brand, name,
OPERATOR, public_transport, railway, religion, tags ->'opening_hours' AS opening_hours, REF, tags, geom AS geom, tags -> 'wheelchair' AS wheelchair
FROM entry_points_intersections

UNION ALL

SELECT osm_id AS osm_id, 'polygon' AS origin_geometry, ACCESS, "addr:housenumber" AS housenumber, sports AS amenity_array, 
tags ->'origin' AS origin, tags ->'organic' AS organic, denomination, brand, name,
OPERATOR, public_transport, railway, religion, tags ->'opening_hours' AS opening_hours, REF, tags, waypoint AS geom, tags -> 'wheelchair' AS wheelchair
FROM sport_gate_pois

UNION ALL 

SELECT osm_id AS osm_id, 'polygon' AS origin_geometry, ACCESS, "addr:housenumber" AS housenumber, sports AS amenity_array, 
tags ->'origin' AS origin, tags ->'organic' AS organic, denomination, brand, name,
OPERATOR, public_transport, railway, religion, tags ->'opening_hours' AS opening_hours, REF, tags, ST_Centroid(way) AS geom, tags -> 'wheelchair' AS wheelchair
FROM sport_complex_c2 WHERE "case" IS null

);

SELECT * FROM dummy_pois;



SELECT * FROM entry_points_intersections;
SELECT * FROM sport_complex_c2 scc ;


SELECT * FROM sport_complex_c2 WHERE "case" IS NULL;
-- In pois format

SELECT osm_id AS osm_id, 'polygon' AS origin_geometry, ACCESS, "addr:housenumber" AS housenumber, sports AS amenity_array, shop, 
tags ->'origin' AS origin, tags ->'organic' AS organic, denomination, brand, name,
OPERATOR, public_transport, railway, religion, tags ->'opening_hours' AS opening_hours, REF, tags, geom AS geom, tags -> 'wheelchair' AS wheelchair
FROM entry_points_intersections;

-- Left join based on 

DROP TABLE IF EXISTS intersection_ways;
SELECT epi.osm_id AS osm_id_2, sc2.*, epi.geom AS waypoint INTO intersection_ways
FROM (SELECT * FROM entry_points_intersections) epi
JOIN (SELECT * FROM sport_complex_c2 WHERE "case" = 'Sport_complex_intersections') AS sc2
ON st_intersects(sc2.way, epi.geom);

SELECT * FROM intersection_ways;
SELECT * FROM entry_points_intersections;



SELECT * FROM sport_complex_c2 WHERE "case" = 'Sport_complex_intersections';

DROP TABLE IF EXISTS sport_gate_pois;
SELECT poi.osm_id AS point_osm_id , sc.*, poi.way AS waypoint INTO sport_gate_pois
FROM (SELECT * FROM planet_osm_point pop WHERE barrier = 'gate') poi
JOIN sport_complex AS sc
ON st_intersects (poi.way, ST_boundary(sc.way));




----------------------------------------------------------------------
------ Selection in pois_structure from case 1//Talk with Elías ------
----------------------------------------------------------------------

SELECT point_osm_id AS osm_id, 'polygon' AS origin_geometry, ACCESS, "addr:housenumber" AS housenumber, sports AS amenity_array, shop, 
tags ->'origin' AS origin, tags ->'organic' AS organic, denomination, brand, name,
OPERATOR, public_transport, railway, religion, tags ->'opening_hours' AS opening_hours, REF, tags, waypoint AS geom, tags -> 'wheelchair' AS wheelchair
FROM sport_gate_pois;

-- END --


--Extras temporal
-- Backup

DROP TABLE IF EXISTS pois;
SELECT * INTO pois FROM pois_backup;

SELECT * INTO pois_backup FROM pois;
----



--Exceptions to be handled ....
-- 01. Barrier lines around sport complex... no extra info
SELECT * FROM planet_osm_polygon WHERE barrier = 'fence';


-- ALSO ADD individual fields (as normal pois)
SELECT * FROM planet_osm_polygon pop WHERE landuse = 'recreation_ground';