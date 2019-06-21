CREATE OR REPLACE FUNCTION closest_pois(snap_distance NUMERIC)
RETURNS SETOF jsonb
 LANGUAGE plpgsql
AS $function$

BEGIN 
	
	DROP TABLE IF EXISTS pois_and_pt;
	CREATE temp TABLE pois_and_pt AS 

	SELECT p.gid as poi_gid,p.amenity,p.name, p.geom  
	FROM pois p,variable_container v, isochrone b 
	WHERE v.identifier = 'poi_categories'
	AND amenity = any(variable_array)
	AND st_intersects(p.geom, b.geom)
	UNION ALL 
	SELECT p.gid as poi_gid,public_transport_stop AS amenity,p.name,p.geom
	FROM public_transport_stops p, isochrone b
	WHERE st_intersects(p.geom,b.geom);

	ALTER TABLE pois_and_pt ADD PRIMARY key(poi_gid);
	CREATE INDEX ON pois_and_pt USING gist(geom);
	--!!!!The Selection of the nearest vertex has to be improved!!!!
	RETURN query 
	WITH distance_pois as (
		SELECT DISTINCT on(x.poi_gid) x.poi_gid,name,amenity,st_distance(x.geom,v.geom) as min_dist, v.cost, x.geom 
		FROM  temp_extrapolated_reached_vertices v, pois_and_pt x
		WHERE v.geom && ST_Buffer(x.geom,snap_distance)--snap_distance/*100m => approx. 0.0009 */)
		ORDER BY x.poi_gid, st_distance(x.geom,v.geom)
	)
	SELECT array_to_json(array_agg(row_to_json(x)))::jsonb 
	FROM
	(
		SELECT amenity,name,min(cost) as cost FROM distance_pois --Every entrance OR bus_stop is only counted once (shortest distance is taken)
		WHERE amenity = ANY (ARRAY['subway_entrance','bus_stop','tram_stop','sbahn_regional'])
		GROUP BY amenity,name
		UNION ALL
		SELECT amenity,name,cost FROM distance_pois
		WHERE amenity != ANY (ARRAY['subway_entrance','bus_stop','tram_stop','sbahn_regional'])
	)x;
	
END 
$function$;