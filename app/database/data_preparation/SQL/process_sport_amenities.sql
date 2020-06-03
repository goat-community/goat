-----------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------GOAT Sport facilities processing----------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------DRAFT!!! ---------------------------------------------------------

-- Spatial join of the sports fields into each sport complex
-- Save polygons with sport centers

DROP TABLE IF EXISTS sport_centers;
CREATE TABLE sport_centers (LIKE planet_osm_polygon INCLUDING ALL);

INSERT INTO sport_centers
	SELECT * FROM planet_osm_polygon WHERE leisure = any(ARRAY['sports_centre', 'water_park'])  OR name LIKE '%Bezirkssportanlage%' OR landuse ='recreation_ground';

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
FROM sport_centers sc
LEFT JOIN (SELECT group_id, complex_name, array_agg(sport::Text) FROM grouping_sports GROUP BY group_id, complex_name ORDER BY group_id) AS s
ON sc.osm_id = s.group_id;

SELECT * FROM sport_complex;

-- Delete sport complex without sports assigned
DELETE FROM sport_complex WHERE sports IS NULL ;

-- Count the no. of gates per polygon

DROP TABLE IF EXISTS doors_field;
SELECT pol.osm_id, count(poi.osm_id), 'Sport complex with gates' AS "case" INTO doors_field
FROM (SELECT * FROM planet_osm_point pop WHERE barrier = 'gate' AND NOT ("access" = 'no' OR "access" ='private' ) OR "access" IS null) poi
JOIN sport_centers AS pol 
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
FROM (SELECT * FROM planet_osm_point WHERE barrier = 'gate' AND NOT ("access" = 'no' OR "access" ='private')OR "access" IS null) AS poi
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

-- Sport fields that does not below to any complex

DROP TABLE IF EXISTS sports_no_complex;
SELECT * INTO sports_no_complex FROM planet_osm_polygon WHERE sport IS NOT NULL 
EXCEPT
SELECT pol.* FROM planet_osm_polygon pol, sport_centers sc
WHERE st_intersects(pol.way, sc.way);

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

UNION ALL 

SELECT osm_id AS osm_id, 'polygon' AS origin_geometry, ACCESS, "addr:housenumber" AS housenumber, (concat('{',sport,'}'))::text[] AS amenity_array, 
tags ->'origin' AS origin, tags ->'organic' AS organic, denomination, brand, name,
OPERATOR, public_transport, railway, religion, tags ->'opening_hours' AS opening_hours, REF, tags, ST_Centroid(way) AS geom, tags -> 'wheelchair' AS wheelchair
FROM sports_no_complex

);

SELECT * FROM dummy_pois;

SELECT * FROM variable_container vc;

--End

-- Count sports

SELECT DISTINCT amenity FROM dummy_pois;
SELECT count(DISTINCT bi)
FROM (select(UNNEST(amenity) AS bi) FROM dummy_pois) s;

select(UNNEST(amenity)) FROM dummy_pois;

SELECT unnest(amenity) FROM dummy_pois;

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

SELECT * FROM planet_osm_point WHERE sport IS NOT NULL;



DROP TABLE IF EXISTS access_tests;
SELECT * INTO access_tests FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','path','service','services'] ) AND ("access" != ANY (ARRAY ['private','no']) )



SELECT * FROM planet_osm_polygon WHERE name = 'Michaeli-Freibad'

SELECT * FROM planet_osm_polygon WHERE leisure ='water_park'


SELECT * FROM planet_osm_polygon WHERE sport IS NOT NULL 
EXCEPT
SELECT pol.* FROM planet_osm_polygon pol, sport_centers sc
WHERE st_intersects(pol.way, sc.way)

;