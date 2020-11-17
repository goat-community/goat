---- POIS displacements
-------------------------------------
/*
 * Inputs: amenity_set (array text), set of amenities to compare
 * radius: (float8) degrees to be used to move points, if you have meters, you can put the next expression to convert to degrees = (distance(m)/(27*3600))
 * building_radius (int) (meters)
 * building_tag_radius (int) (meters)
 * Result: Modified pois with the pois displaced the amount of distance defined, if the point comes from a polygon, and it is outside the polygon, the point is translated to the polygon boundary)
 * 
 */
CREATE OR REPLACE FUNCTION public.pois_displacement(amenity_set text[], radius double PRECISION, building_radius double PRECISION, building_tag_radius double PRECISION)
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN
	--- Identify duplicated geometries and extract them in pois_duplicated
	DROP TABLE IF EXISTS pois_duplicated;
	CREATE TEMP TABLE pois_duplicated (LIKE pois);
	ALTER TABLE pois_duplicated ADD COLUMN row_no int8;
	
	INSERT INTO pois_duplicated
	WITH pois_filtered AS (SELECT * FROM pois WHERE amenity = ANY( amenity_set))
	SELECT p.*, row_number() over(PARTITION BY p.geom ORDER BY p.amenity desc) AS row_no FROM pois_filtered p 
	LEFT JOIN pois_filtered p2
	ON p.osm_id = p2.osm_id
	WHERE ST_Equals(p.geom, p2.geom) AND p.amenity != p2.amenity ORDER BY p.geom;
	
	--ADD column for max no of repeated entities
	ALTER TABLE pois_duplicated ADD COLUMN repeated_entities int8;
	
	UPDATE pois_duplicated
	SET repeated_entities = subquery.max_repeated
	FROM (SELECT osm_id, max(row_no) AS max_repeated FROM pois_duplicated GROUP BY osm_id) AS subquery
	WHERE subquery.osm_id = pois_duplicated.osm_id;
		
	--- Define angle according to position and repeated	
	ALTER TABLE pois_duplicated ADD COLUMN angle float8;
	UPDATE pois_duplicated
	SET angle = ((pi()/4) + (2*pi()/repeated_entities*(row_no-1)));

	--- Create columns to store delta values
	
	ALTER TABLE pois_duplicated ADD COLUMN x_delta float8;
	ALTER TABLE pois_duplicated ADD COLUMN y_delta float8;
	
	UPDATE pois_duplicated SET x_delta = (radius/(27*3600)::float8)*cos(angle);
	UPDATE pois_duplicated SET y_delta = (radius/(27*3600)::float8)*sin(angle);

	-- Select buildings nearby duplicated pois (cancelled for now)
	/*

	DROP TABLE IF EXISTS closer_buildings;
	CREATE TEMP TABLE closer_buildings(LIKE buildings );
	
	
	INSERT INTO closer_buildings
	SELECT DISTINCT b.*
	FROM buildings b, pois_duplicated pd 
	WHERE ST_within(b.geom,ST_Buffer(pd.geom::geography,building_radius)::geometry);
		
	--- Move pois based on the x_delta and y_delta*/
	UPDATE pois_duplicated SET geom = st_translate(geom, x_delta, y_delta);
	/*
	-- Calculate distance from each point to buildings
	
	DROP TABLE IF EXISTS distance_to_buildings;
	CREATE TEMP TABLE distance_to_buildings (LIKE pois_duplicated);
	ALTER TABLE distance_to_buildings ADD COLUMN building_gid int8, ADD COLUMN distance float8, ADD COLUMN row_order int8;
	
	--- All points will be tagged
	--- POints with distances greater than certain value will be discarded from next stage (snapping)

	INSERT INTO distance_to_buildings

	SELECT pd.*, cb.gid AS building_gid, ST_Distance(cb.geom, pd.geom), row_number() 
	OVER(PARTITION BY pd.geom ORDER BY ST_Distance(cb.geom, pd.geom) ASC) AS distance_order
	FROM pois_duplicated pd, closer_buildings cb;
	
	DELETE FROM distance_to_buildings
	WHERE row_order != 1;
	DELETE FROM distance_to_buildings
	WHERE distance = 0 OR distance >= (building_tag_radius::float8/(27::float8*3600::float8));
	
	--distance_to_buldings now contains points outside polygon and the respective ID, now snap to the polygon.
	--translate distance_to_buildings to the polygons in a new table
	
	DROP TABLE IF EXISTS pois_out_boundary;
	CREATE TEMP TABLE pois_out_boundary (gid int4, geom geometry);
	
	INSERT INTO pois_out_boundary
	WITH building AS (SELECT * FROM closer_buildings WHERE gid = ANY (SELECT building_gid FROM distance_to_buildings))
	SELECT dtb.gid, ST_ClosestPoint(b.geom, dtb.geom) AS geom FROM distance_to_buildings dtb, building b WHERE dtb.building_gid = b.gid;

	UPDATE pois_duplicated
	SET geom = (
		CASE WHEN pois_duplicated.gid = ANY (
				SELECT gid FROM pois_out_boundary) THEN subquery.geom
				ELSE pois_duplicated.geom END)
	FROM (
		SELECT * FROM pois_out_boundary)AS subquery
	WHERE pois_duplicated.gid = subquery.gid ;
	*/

	--- Load adjusted pois out of boundary to duplicated
		
	UPDATE pois
	SET geom = (CASE WHEN pois.osm_id = ANY (SELECT DISTINCT osm_id FROM pois_duplicated) THEN subquery.geom
	ELSE pois.geom END)
	FROM (SELECT * FROM pois_duplicated) AS subquery
	WHERE pois.osm_id = subquery.osm_id AND pois.amenity = subquery.amenity;

END
$function$
/* 
SELECT pois_displacement(ARRAY['primary_school','secondary_school'], 20::float8, 50:float8, 30::float8)
 */