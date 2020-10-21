---- POIS displacements
-------------------------------------
/*
 * Inputs: amenity_set (array text), set of amenities to compare
 * delta: (float8) degrees to be used to move points, if you have meters, you can put the next expression to convert to degrees = (distance(m)/(27*3600))
 * Result: Modified pois with the pois displaced the amount of distance defined, if the point comes from a polygon, and it is outside the polygon, the point is translated to the polygon boundary)
 * 
 */
CREATE OR REPLACE FUNCTION pois_displacement (amenity_set TEXT[], delta float8)
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN
	--- Identify duplicated geometries and extract them in pois_duplicated
	DROP TABLE IF EXISTS pois_duplicated;
	CREATE TEMP TABLE pois_duplicated (LIKE pois INCLUDING ALL);
	ALTER TABLE pois_duplicated ADD COLUMN row_no int8;
	
	INSERT INTO pois_duplicated
		WITH pois_filtered AS (SELECT * FROM pois WHERE amenity = ANY( amenity_set))
	SELECT p.*, row_number() over(PARTITION BY p.geom ORDER BY p.amenity desc) AS row_no FROM pois_filtered p 
	LEFT JOIN pois_filtered p2
	ON p.osm_id = p2.osm_id
	WHERE ST_Equals(p.geom, p2.geom) AND p.amenity != p2.amenity ORDER BY p.geom;
	
	--- Create columns to store delta values
	ALTER TABLE pois_duplicated ADD COLUMN x_delta float8;
	ALTER TABLE pois_duplicated ADD COLUMN y_delta float8;
	
	--- Assign delta values to each row in pois_duplicates
	UPDATE pois_duplicated 
		SET x_delta = (CASE WHEN row_no = 1 OR row_no = 4 THEN delta
			                WHEN row_no = 2 OR row_no = 3 THEN -delta ELSE x_delta END);
				   
	UPDATE pois_duplicated
		SET y_delta = (CASE WHEN row_no = 1 OR row_no = 3 THEN delta
				            WHEN row_no = 2 OR row_no = 4 THEN -delta ELSE y_delta END);
	
	--- Move pois based on the x_delta and y_delta
	UPDATE pois_duplicated
		SET geom = st_translate(geom, x_delta, y_delta);
	
	--- Verify that pois are into buildings and if not, translate into the boundaries
	DROP TABLE IF EXISTS pois_out_boundary;
	CREATE TEMP TABLE pois_out_boundary (osm_id int8, origin_geometry TEXT, amenity TEXT, name TEXT, geom geometry, way geometry, adjusted_pois geometry);

	INSERT INTO pois_out_boundary
		WITH duplicated_pois AS (SELECT * FROM pois_duplicated WHERE origin_geometry = 'polygon'),
		dup_polygon AS (SELECT * FROM planet_osm_polygon WHERE osm_id = ANY (SELECT osm_id FROM pois_duplicated WHERE origin_geometry = 'polygon')),
		polygon_pois AS (SELECT dp.*, way FROM duplicated_pois dp, dup_polygon dpol WHERE dp.osm_id = dpol.osm_id)
	SELECT pp.osm_id, pp.origin_geometry, pp.amenity, pp.name, pp.geom, pp.way, ST_ClosestPoint(pp.way, pp.geom) AS adjusted_pois FROM polygon_pois pp WHERE ST_contains(way,geom) = FALSE;
	
	--- Load adjusted pois out of boundary to duplicated
	UPDATE pois_duplicated
		SET geom = (CASE WHEN pois_duplicated.osm_id = ANY (SELECT DISTINCT osm_id FROM pois_out_boundary) THEN subquery.adjusted_pois
			ELSE pois_duplicated.geom END)
			FROM (SELECT * FROM pois_out_boundary)AS subquery
			WHERE pois_duplicated.osm_id = subquery.osm_id AND pois_duplicated.amenity = subquery.amenity;
		
UPDATE pois
	SET geom = (CASE WHEN pois.osm_id = ANY (SELECT DISTINCT osm_id FROM pois_duplicated) THEN subquery.geom
	ELSE pois.geom END)
	FROM (SELECT * FROM pois_duplicated) AS subquery
	WHERE pois.osm_id = subquery.osm_id AND pois.amenity = subquery.amenity;

END
$function$
/* 
SELECT pois_displacement(ARRAY['primary_school','secondary_school'], (20/(27*3600)::float8))
 */