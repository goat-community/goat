CREATE OR REPLACE FUNCTION basic.get_reference_study_area(point geometry)
RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE 
    setting_study_area_id integer;
BEGIN 
	
	setting_study_area_id = (
		SELECT s.id 
		FROM basic.study_area s
		ORDER BY ST_CLOSESTPOINT(s.geom, point) <-> point
		LIMIT 1	
	); 
    RETURN setting_study_area_id;
END;
$function$ IMMUTABLE;
/*
SELECT *
FROM basic.get_reference_study_area(ST_SETSRID(ST_MAKEPOINT(8.5, 47.5), 4326));
*/