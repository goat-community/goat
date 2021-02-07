---------------------------------------
-----AOIS visualization function ------
---------------------------------------

DROP FUNCTION IF EXISTS aois_visualization;
CREATE OR REPLACE FUNCTION public.aois_visualization(userid_input INTEGER, amenities_input TEXT[])
RETURNS TABLE (gid int, geom geometry, amenity text, name text, osm_id bigint, opening_hours text, wheelchair text)
LANGUAGE plpgsql
AS $function$

BEGIN 

RETURN query
	SELECT a.gid, a.geom, a.amenity, a.name, a.osm_id, a.opening_hours, a.wheelchair 
	FROM aois a
	WHERE a.amenity IN(SELECT UNNEST (amenities_input));
	
END
$function$;

COMMENT ON FUNCTION aois_visualization(userid_input INTEGER, amenities_input TEXT[]) 
IS '**FOR-API-FUNCTION** RETURNS col_names[gid,geom,amenity,name,osm_id,opening_hours,wheelchair] **FOR-API-FUNCTION**';


/*
WITH am AS (
	SELECT string_to_array(amenity::text,',') AS amenity
	FROM convert_from(decode('cGFyaw==','base64'),'UTF-8') AS amenity
)
SELECT *
FROM aois_visualization(1,(SELECT amenity FROM am))
*/