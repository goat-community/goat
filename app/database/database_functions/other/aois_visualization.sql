---------------------------------------
-----AOIS visualization function ------
---------------------------------------

DROP FUNCTION IF EXISTS aois_visualization;
CREATE OR REPLACE FUNCTION public.aois_visualization(userid_input INTEGER, amenities_input TEXT[], zone_size_type TEXT)
RETURNS SETOF pois_visualization
LANGUAGE plpgsql
AS $function$
DECLARE 

extra_parameter TEXT;
BEGIN 
	IF zone_size_type = 'small' THEN 
		RETURN query
			SELECT a.gid, a.amenity, a.name, a.osm_id, a.opening_hours, a.origin_geometry, a.geom, 'accessible', a.wheelchair FROM aois a
			WHERE a.amenity IN(SELECT UNNEST (amenities_input));
	ELSE 
		RETURN query
			SELECT a.gid, a.amenity, a.name, a.osm_id, a.opening_hours, a.origin_geometry, a.geom, 'accessible', a.wheelchair FROM aois a
			WHERE a.amenity IN(SELECT UNNEST (amenities_input)) AND zone_size = 'large_zone';
	
	END IF;
	
END;
$function$

/*
WITH am AS (
	SELECT string_to_array(amenity::text,',') AS amenity
	FROM convert_from(decode('cGFyaw==','base64'),'UTF-8') AS amenity
)
SELECT *,concat(amenity,'_',status) AS amenity_icon
FROM aois_visualization(1,(SELECT amenity FROM am), 'large')
*/