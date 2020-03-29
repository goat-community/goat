DROP FUNCTION IF EXISTS closest_pois_precalculated;
CREATE OR REPLACE FUNCTION closest_pois_precalculated(snap_distance NUMERIC, grid_id_input integer, 
userid_input integer DEFAULT NULL, amenities text[] default '{}')
RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE

BEGIN 
	DROP TABLE IF EXISTS pois_and_pt;
	IF amenities = '{}' THEN 
		amenities = select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances');	
		CREATE temp TABLE pois_and_pt AS 
		SELECT p.gid as poi_gid,p.amenity,p.name, p.geom  
		FROM pois_userinput p, isochrones b 
		WHERE amenity = any(amenities)
		AND ST_Intersects(p.geom, b.geom)
		AND b.objectid = grid_id_input;
	ELSE 
		DELETE FROM reached_pois_heatmap WHERE userid = userid_input;
		CREATE temp TABLE pois_and_pt AS 
		SELECT p.gid as poi_gid,p.amenity,p.name, p.geom  
		FROM pois_userinput p, isochrones b 
		WHERE amenity = any(amenities)
		AND ST_Intersects(p.geom, b.geom)
		AND b.objectid = grid_id_input
		AND p.userid = userid_input;
	END IF; 

	ALTER TABLE pois_and_pt ADD PRIMARY key(poi_gid);
	CREATE INDEX ON pois_and_pt USING gist(geom);

	DROP TABLE IF EXISTS reached_vertices;
	CREATE TEMP TABLE reached_vertices AS
	SELECT geom, cost 
	FROM reached_vertices_heatmap v
	WHERE grid_id = grid_id_input;
	CREATE INDEX ON reached_vertices USING GIST(geom);

	INSERT INTO reached_pois_heatmap(poi_gid, amenity, name,cost, geom, grid_id, userid)
	SELECT p.poi_gid, p.amenity, p.name, v.cost, p.geom, grid_id_input, userid_input
	FROM pois_and_pt p
	CROSS JOIN LATERAL
  	(SELECT geom, cost
   	FROM reached_vertices t
   	WHERE t.geom && ST_Buffer(p.geom,snap_distance)
   	ORDER BY
    p.geom <-> t.geom
   	LIMIT 1) AS v;
	
END 
$function$;

--SELECT closest_pois_precalculated(0.0009,27,602589,ARRAY['kindergarten'])