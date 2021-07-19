DROP FUNCTION IF EXISTS group_index;  

CREATE OR REPLACE FUNCTION public.group_index(arr1 NUMERIC[], arr2 NUMERIC[])
RETURNS NUMERIC 
AS $function$

DECLARE 
	grouped_index NUMERIC;  
BEGIN 

	WITH unnested AS 
	(
		SELECT COALESCE(x.a, 0) a, CASE WHEN x.a IS NOT NULL THEN x.b ELSE 0 END AS b  
		FROM (
			SELECT UNNEST(arr1) a, UNNEST(arr2) b
		) x
	)
	SELECT CASE WHEN sum(b) > 0 THEN sum(a)/sum(b) ELSE NULL END AS index
	INTO grouped_index
	FROM unnested;	 
	
	RETURN grouped_index;
END;
$function$ LANGUAGE plpgsql immutable;