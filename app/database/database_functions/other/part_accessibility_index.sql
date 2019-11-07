DROP FUNCTION IF EXISTS part_accessibility_index;
CREATE OR REPLACE FUNCTION public.part_accessibility_index(traveltime_array NUMERIC[], beta numeric)
RETURNS NUMERIC 
AS $function$
DECLARE 
	sum_index NUMERIC;
BEGIN 
	SELECT COALESCE(sum(part),0) INTO sum_index
	FROM ( 
		SELECT EXP(UNNEST(traveltime_array)*(beta)) AS part
	)
	index_part; 
	RETURN sum_index; 
END;
$function$ LANGUAGE plpgsql immutable;