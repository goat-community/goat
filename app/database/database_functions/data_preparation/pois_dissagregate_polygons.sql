CREATE OR REPLACE FUNCTION pois_dissagregate_polygons(subset text)
	RETURNS void
	LANGUAGE plpgsql
AS $function$
DECLARE
	gate varchar :='gate';
	NO varchar :='no';
	private varchar := 'private';
	entrance varchar := 'entrance';
	main varchar := 'main';
	yes varchar := 'yes';
	entrance_array varchar[] := ARRAY['main','yes'];
	
BEGIN 
	-- 01. Get doors and entrance gates
	DROP TABLE IF EXISTS access_points;
	EXECUTE 'CREATE TABLE access_points (LIKE '||quote_ident(subset)||' INCLUDING ALL)';
	
	ALTER TABLE access_points
	ADD COLUMN gates geometry;
	
	EXECUTE ' INSERT INTO access_points
	SELECT pol.*, poi.way as point FROM 
	(SELECT * FROM planet_osm_point WHERE (barrier = '||quote_literal(gate)||' AND (NOT ("access" = '||quote_literal(no)||' OR "access" ='||quote_literal(private)||' ) OR "access" IS NULL))
	OR (tags->'||quote_literal(entrance)||' = ANY(ARRAY['||quote_literal(main)||','||quote_literal(yes)||'])) ) poi
	JOIN '|| quote_ident(subset) ||' AS pol
	ON ST_intersects(poi.way, pol.way)';
	ALTER TABLE access_points 
	DROP COLUMN way;
	
	-- 02. Identify polygons without previous matches
	
	DROP TABLE IF EXISTS no_of_doors;
	CREATE TABLE no_of_doors(osm_id int, way geometry, no_doors int);
	
	INSERT INTO no_of_doors
	SELECT test.osm_id, test.way, count(access_points.osm_id) AS no_doors FROM 
	test
	LEFT JOIN access_points
	ON test.osm_id = access_points.osm_id GROUP BY test.osm_id, test.way;

	-- 03. Calculate intersection points between polygons without access and road network (footway, path, service)
	
	DROP TABLE IF EXISTS access_intersections;
	CREATE TABLE access_intersections (LIKE planet_osm_polygon INCLUDING ALL);
	
	ALTER TABLE access_intersections
	ADD COLUMN access_point geometry;
	
	INSERT INTO access_intersections
	SELECT pol.*, (ST_Dump(ST_Intersection(l.way, ST_boundary(pol.way)))).geom AS geom 
	FROM 
	(SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','path','service','services'])) AS l, 
	(SELECT t.* FROM test t
		LEFT JOIN no_of_doors n
		ON t.osm_id = n.osm_id
		WHERE no_doors = 0) AS pol
	WHERE
	st_intersects(l.way, pol.way) ;

	


END;
$function$

SELECT pois_dissagregate_polygons('test')
SELECT * FROM access_intersections WHERE name IS null;

DROP TABLE IF EXISTS access_intersections;

SELECT pol.*, (ST_Dump(ST_Intersection(l.way, ST_boundary(pol.way)))).geom AS geom 
FROM 
(SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','path','service','services'])) AS l, 
(	SELECT t.* FROM test t
	LEFT JOIN no_of_doors n
	ON t.osm_id = n.osm_id
	WHERE no_doors = 0) AS pol
WHERE
st_intersects(l.way, pol.way) ;

SELECT * FROM access_points;










	SELECT t.* FROM test t
	LEFT JOIN no_of_doors n
	ON t.osm_id = n.osm_id
	WHERE no_doors = 0;




SELECT osm_id, count(osm_id) FROM access_points GROUP BY test.osm_id, test.way;
SELECT pois_dissagregate_polygons('test')
SELECT * FROM access_points;

SELECT * FROM test;
SELECT * FROM no_of_doors;

DROP TABLE IF EXISTS test;
CREATE TABLE test (LIKE planet_osm_polygon INCLUDING all);
INSERT INTO test
SELECT * FROM planet_osm_polygon WHERE (leisure = ANY(ARRAY['sports_centre','water_park']) OR name LIKE '%Bezirkssportanlage%') AND building IS NULL;



-- Select doors and entrances
SELECT pop.* FROM 

SELECT * FROM 
(SELECT * FROM planet_osm_point WHERE (barrier = 'gate' AND (NOT ("access" = 'no' OR "access" ='private' ) OR "access" IS NULL)) OR (tags->'entrance' = ANY (ARRAY['main','yes']))) poi
JOIN test AS pol 
ON st_intersects(poi.way,st_boundary(pol.way))

SELECT ST_Buffer(way::geography, 1) INTO geotest FROM planet_osm_point WHERE tags->'entrance' = 'main'
DROP TABLE geotest;

SELECT * FROM test;
SELECT * FROM planet_osm_point WHERE tags->'entrance' ='main'

DROP TABLE IF EXISTS doors_field;
SELECT pol.osm_id, count(poi.osm_id), 'Sport complex with gates' AS "case" INTO doors_field
FROM (SELECT * FROM planet_osm_point pop WHERE barrier = 'gate' AND NOT ("access" = 'no' OR "access" ='private' ) OR "access" IS null) poi
JOIN sport_centers AS pol 
ON st_intersects (poi.way, ST_Boundary(pol.way))
GROUP BY pol.osm_id, pol.way;