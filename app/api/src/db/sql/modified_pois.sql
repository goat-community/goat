CREATE OR REPLACE FUNCTION basic.modified_pois(scenario_id_input integer)
 RETURNS TEXT[]
 LANGUAGE plpgsql
AS $function$
DECLARE 
	modified_features text[];
BEGIN 

	modified_features = 
	(
		WITH ids AS 
		(
			SELECT uid 
			FROM customer.poi_modified p 	
			WHERE scenario_id = 1 
			UNION ALL 
			SELECT UNNEST(deleted_pois)
			FROM customer.scenario 
			WHERE id = 1
		),
		distinct_ids AS 
		(
			SELECT DISTINCT uid FROM ids 
		)
		SELECT COALESCE(ARRAY_AGG(uid), array[]::text[]) 
		FROM distinct_ids
	);
	
	RETURN modified_features;
	
END;
$function$
/*
SELECT * FROM basic.modified_pois(1)
*/
