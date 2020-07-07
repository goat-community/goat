------------------------------------------------
----- Pois dissagregate polygons function ------
-- Calls a subset from planet_osm_polygons and look for doors or intersections with pedestrian or service roads, in case of no gates or intersections, It will return the centroid of the polygon.
-- This new points will be assigned to a specific amenity (input) and injected into pois database.
-- Input values
-- 	subset	: Name of the subset to be used
--  myamenity: category of the amenity to be assigned to these new points

CREATE OR REPLACE FUNCTION derive_access_from_polygons(subset TEXT, myamenity TEXT)
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN 
	-- Create dummy subset to avoid dynamic sql 
	DROP TABLE IF EXISTS polygon_subset;
	CREATE TEMP TABLE polygon_subset (LIKE planet_osm_polygon INCLUDING INDEXES);
	
	EXECUTE 'INSERT INTO polygon_subset
	SELECT * FROM '||quote_ident(subset);
	
	EXECUTE 'UPDATE polygon_subset
	SET amenity = '||quote_literal(myamenity); 
	-- Get doors and entrance gates
		
	DROP TABLE IF EXISTS access_points;
	CREATE TEMP TABLE access_points (LIKE planet_osm_polygon INCLUDING ALL);	
	ALTER TABLE access_points ADD COLUMN gates geometry;
	
	INSERT INTO access_points
	SELECT pol.*, poi.way as point FROM
	(SELECT * FROM planet_osm_point WHERE (barrier = 'gate' AND (NOT ("access" = 'no' OR "access" ='private' ) OR "access" IS NULL))
	OR (tags->'entrance' = ANY(ARRAY['main','yes']))) poi
	JOIN polygon_subset AS pol
	ON ST_intersects(poi.way, pol.way);

	-- Count the no. of doors and gates per polygon 
	
	DROP TABLE IF EXISTS no_of_doors;
	CREATE TEMP TABLE no_of_doors(osm_id int, way geometry, no_doors int);
	
	INSERT INTO no_of_doors
	SELECT t.osm_id, t.way, count(ap.osm_id) AS no_doors FROM polygon_subset t
	LEFT JOIN access_points ap
	ON t.osm_id = ap.osm_id GROUP BY t.osm_id, t.way;

	-- Calculate intersection points between polygons with access_points = 0 and road network (footway, path, service)
	
	INSERT INTO access_points
	SELECT pol.*, (ST_Dump(ST_Intersection(l.way, ST_boundary(pol.way)))).geom AS geom 
	FROM 
	(SELECT * FROM planet_osm_line WHERE highway = ANY (ARRAY ['footway','path','service','services'])) AS l, 
	(SELECT t.* FROM polygon_subset t
		LEFT JOIN no_of_doors n
		ON t.osm_id = n.osm_id
		WHERE n.no_doors = 0) AS pol
	WHERE
	st_intersects(l.way, pol.way) ;

	-- Select polygons without gates and intersections

	DROP TABLE IF EXISTS no_of_intersections;
	CREATE TEMP TABLE no_of_intersections(LIKE no_of_doors INCLUDING ALL);
	ALTER TABLE no_of_intersections ADD COLUMN no_of_intersections int;

	INSERT INTO no_of_intersections		
	SELECT d.*, count(ai.osm_id) FROM no_of_doors d
	LEFT JOIN access_points ai 
	ON d.osm_id = ai.osm_id
	GROUP BY d.osm_id, d.way, d.no_doors;

	-- Injection into pois of access_points
	INSERT INTO pois
	SELECT osm_id, 'polygon dissagregated' AS origin_geometry, ACCESS, "addr:housenumber" AS housenumber, amenity AS amenity,
	tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
	operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref, tags||hstore('sport', sport)||hstore('leisure', leisure)  AS tags, gates as geom,
	tags -> 'wheelchair' as wheelchair
	FROM access_points;	

	-- Injection into pois of centroids
	
	INSERT INTO pois
	SELECT t.osm_id, 'polygon' AS origin_geometry, ACCESS, "addr:housenumber" AS housenumber, amenity AS amenity,
	tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
	operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref, tags||hstore('sport', sport)||hstore('leisure', leisure)  AS tags, ST_centroid(t.way) as geom,
	tags -> 'wheelchair' as wheelchair
	FROM polygon_subset t, no_of_intersections ni WHERE (ni.no_doors + ni.no_of_intersections ) = 0 AND t.osm_id = ni.osm_id;
--SELECT * FROM no_of_intersections ni WHERE (ni.no_doors + ni.no_of_intersections ) = 0;
END;
$function$

--SELECT * FROM access_points;
-- Example, test is the subset that has the same structure than planet_osm_polygon
--SELECT pois_dissagregate_polygons('test','mynewamenity')


--SELECT * INTO test FROM planet_osm_polygon LIMIT 1;
--DELETE FROM test;

--SELECT * FROM test;