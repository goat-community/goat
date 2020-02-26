--Function has to be rewritten!!!!
DROP FUNCTION IF EXISTS thematic_data_sum_time;
CREATE OR REPLACE FUNCTION public.thematic_data_sum_time(input_objectid integer, d integer, h integer, m integer)
 RETURNS TABLE(objectid_out integer, gid_out integer, sum_pois_time_out text)
 LANGUAGE plpgsql
AS $function$
begin
	
	with yy as (
		SELECT p.*--, select_from_variable_container('amenity_opening_hours') AS amenity_opening_hours
		FROM 
		(
			SELECT i.gid,count(*),amenity,p.opening_hours 
			FROM isochrones i, pois p
			WHERE st_intersects(i.geom,p.geom)  
			AND objectid=input_objectid
			AND amenity IN (SELECT (UNNEST(select_from_variable_container('amenity_opening_hours'))))
			AND check_open(p.opening_hours,array[d,h,m]) = 'True'
			GROUP BY i.gid,amenity,p.opening_hours
		) p ,variable_container
		WHERE amenity = any(variable_array)
		AND identifier = 'poi_categories'
	)
	UPDATE isochrones SET sum_pois_time = jsonb_object::text 
	FROM (
	SELECT gid,jsonb_object(array_agg(count::text)) FROM yy
	GROUP BY gid) x 
	WHERE isochrones.gid = x.gid;

END ;
$function$