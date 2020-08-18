---------------------------------------
-----AOIS visualization function ------
---------------------------------------

DROP FUNCTION IF EXISTS aois_visualization;
CREATE OR REPLACE FUNCTION public.aois_visualization(userid_input integer, amenities_input TEXT[])
RETURNS SETOF pois_visualization
LANGUAGE plpgsql
AS $function$
DECLARE 
excluded_pois_id integer [] := ids_modified_features(userid_input,'pois');
BEGIN 
	RETURN query
	SELECT a.gid, a.amenity, a.name, a.osm_id, a.opening_hours, a.origin_geometry, a.geom, 'accessible', a.wheelchair FROM aois a
	WHERE a.amenity IN(SELECT UNNEST (amenities_input));

END;
$function$

/*
WITH am AS (
	SELECT string_to_array(amenity::text,',') AS amenity
	FROM convert_from(decode('cGFyaw==','base64'),'UTF-8') AS amenity
)
SELECT *,concat(amenity,'_',status) AS amenity_icon
FROM aois_visualization(1,(SELECT amenity FROM am))
*/