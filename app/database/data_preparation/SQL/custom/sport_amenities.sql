---------------------------------------------------------
-----------GOAT Sport facilities processing--------------
---------------------------------------------------------
---------------------- DRAFT!!! -------------------------
-- Select sport complex by name or leisure type

DROP TABLE IF EXISTS sport_facilities;
SELECT * INTO sport_facilities FROM planet_osm_polygon pop WHERE (leisure = 'sports_centre' OR name LIKE '%Bezirkssportanlage%') AND amenity IS null;
---(242)

-- Count the no. of gates per polygon and extract doors

DROP TABLE IF EXISTS doors_field;
SELECT pol.osm_id, count(poi.osm_id) INTO doors_field
FROM (SELECT * FROM planet_osm_point pop WHERE barrier = 'gate') poi
JOIN sport_facilities AS pol 
ON st_intersects (poi.way, pol.way)
GROUP BY pol.osm_id, pol.way;

SELECT * FROM doors_field;

-- Left join to sport_facilities

DROP TABLE IF EXISTS doors_per_field;
SELECT sf.*, count AS no_of_doors INTO doors_per_field
FROM sport_facilities sf
LEFT JOIN doors_field df ON df.osm_id = sf.osm_id;

SELECT * FROM doors_per_field;

SELECT * FROM doors_per_field WHERE no_of_doors IS NULL;

-- Calculate intersection points here

SELECT ST_Intersection(l.way, ST_boundary(pol.way))
FROM 
(SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','cycleway','path'])) AS l, 
(SELECT * FROM doors_per_field WHERE no_of_doors IS NULL) AS pol
WHERE
st_intersects(l.way, pol.way) ;

-- Append point to gates



-- Select specific sports fields into sport complex and group sport types in array 
-- Only variety of sports are considered, please ask Elias if we also need the number of amenities inside.

DROP TABLE IF EXISTS grouping_sports;
SELECT pop.osm_id AS group_id, pop.name AS complex_name, pops.sport, count(pops.sport) AS number_fields INTO grouping_sports
FROM (SELECT * FROM planet_osm_polygon pop WHERE leisure = 'sports_centre' OR name LIKE '%Bezirkssportanlage%') AS pop 
JOIN (SELECT * FROM planet_osm_polygon pop WHERE sport IS NOT NULL) AS pops
ON st_intersects(pop.way, pops.way) GROUP BY pop.osm_id, pop.name, pops.sport;

SELECT * FROM grouping_sports;

SELECT group_id, complex_name, sport, count(sport) AS no_fields FROM grouping_sports GROUP BY group_id,complex_name,sport;

-- Grouped amenities

SELECT group_id, complex_name, array_agg(sport::Text) FROM grouping_sports GROUP BY group_id, complex_name ORDER BY group_id;


------

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