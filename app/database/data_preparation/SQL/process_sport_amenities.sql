-----------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------GOAT Sport facilities processing----------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------

-----------------------------------------------------------DRAFT!!! ---------------------------------------------------------

-- Spatial join of the sports fields into each sport complex

DROP TABLE IF EXISTS grouping_sports;
SELECT pop.osm_id AS group_id, pop.name AS complex_name, pops.sport, count(pops.sport) AS number_fields INTO grouping_sports
FROM (SELECT * FROM planet_osm_polygon pop WHERE leisure = 'sports_centre' OR name LIKE '%Bezirkssportanlage%') AS pop 
JOIN (SELECT * FROM planet_osm_polygon pop WHERE sport IS NOT NULL) AS pops
ON st_intersects(pop.way, pops.way) GROUP BY pop.osm_id, pop.name, pops.sport;

SELECT * FROM grouping_sports;

-- Grouped amenities

SELECT group_id, complex_name, array_agg(sport::Text) FROM grouping_sports GROUP BY group_id, complex_name ORDER BY group_id;

-- Left join from grouped amenities into sport complex

DROP TABLE IF EXISTS sport_complex;
SELECT sc.*, s.array_agg AS sports INTO sport_complex
FROM (SELECT * FROM planet_osm_polygon pop WHERE leisure = 'sports_centre' OR name LIKE '%Bezirkssportanlage%') AS sc
LEFT JOIN (SELECT group_id, complex_name, array_agg(sport::Text) FROM grouping_sports GROUP BY group_id, complex_name ORDER BY group_id) AS s
ON sc.osm_id = s.group_id;

SELECT * FROM sport_complex;

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

-- Case "Sport complex with gates", transfer data to gates

-- Check this procedure as well as the limitations

DROP TABLE IF EXISTS sport_gate_pois;
SELECT poi.osm_id AS point_osm_id , sc.*, poi.way AS waypoint INTO sport_gate_pois
FROM (SELECT * FROM planet_osm_point pop WHERE barrier = 'gate') poi
JOIN sport_complex AS sc
ON st_intersects (poi.way, ST_boundary(sc.way));
--ON st_intersects(poi.way, sc.way);

SELECT * FROM sport_gate_pois;
-- Process sport amenities into pois

SELECT point_osm_id AS osm_id, 'polygon' AS origin_geometry, ACCESS, "addr:housenumber" AS housenumber, sports AS amenity, shop, 
tags ->'origin' AS origin, tags ->'organic' AS organic, denomination, brand, name,
OPERATOR, public_transport, railway, religion, tags ->'opening_hours' AS opening_hours, REF, tags, waypoint AS geom, tags -> 'wheelchair' AS wheelchair
FROM sport_gate_pois;

-- Case 2, calculate intersections with main roads

SELECT * FROM sport_complex_c1 WHERE "case" IS NULL ;

DROP TABLE IF EXISTS sport_complex_inter;
SELECT pol.osm_id, ST_Intersection(l.way, ST_boundary(pol.way)), (ST_Dump(ST_Intersection(l.way, ST_boundary(pol.way)))).geom AS geom, pol.way INTO sport_complex_inter
FROM 
(SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','service'])) AS l, 
(SELECT * FROM sport_complex_c1 WHERE "case" IS NULL) AS pol
WHERE
st_intersects(l.way, pol.way) ;

SELECT * FROM sport_complex_inter;


SELECT DISTINCT highway FROM planet_osm_roads ORDER BY highway;

SELECT DISTINCT highway FROM planet_osm_line ORDER by highway;

SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY['service','services', ])
WHERE highway = 'service_road';


-- END --

-- Backup

DROP TABLE IF EXISTS pois;
SELECT * INTO pois FROM pois_backup;

SELECT * INTO pois_backup FROM pois;
----

-- Left join to sport_facilities

DROP TABLE IF EXISTS doors_per_field;
SELECT sf.*, count AS no_of_doors INTO doors_per_field
FROM sport_facilities sf
LEFT JOIN doors_field df ON df.osm_id = sf.osm_id;

SELECT * FROM doors_per_field;
UPDATE doors_per_field SET no_of_doors = 0 WHERE no_of_doors IS NULL;

-- Calculate intersection points here



DROP TABLE IF EXISTS intersections;
SELECT osm_id, count(osm_id) INTO intersections FROM pois_intersections GROUP BY osm_id;
SELECT * FROM intersections;

SELECT dpf.*, i.count AS intersection FROM
doors_per_field dpf
LEFT JOIN intersections i ON dpf.osm_id = dpf.osm_id;



geom FROM pois_intersections GROUP BY osm_id, geom;

-- Append point to gates






--- Join Array results to point lists

------


--- Calculate intersection pois between areas and roads

SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','cycleway','path']);

SELECT ST_Intersection(l.way, ST_boundary(pol.way))
FROM 
(SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','cycleway','path'])) AS l, 
(SELECT * FROM planet_osm_polygon pop WHERE leisure = 'sports_centre' OR name LIKE '%Bezirkssportanlage%') AS pol
WHERE
st_intersects(l.way, pol.way);

FROM planet_osm_line l, planet_osm_polygon pol;


SELECT ST_boundary(way) FROM planet_osm_polygon pop WHERE leisure = 'sports_centre' OR name LIKE '%Bezirkssportanlage%';


SELECT ST_Intersection(l.way, ST_boundary(pol.way)) FROM planet_osm_line l, planet_osm_polygon pol;


SELECT ST_Intersection(l.way, ST_boundary(pol.way)

SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','cycleway','path'])