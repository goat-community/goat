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
			WHERE scenario_id = scenario_id_input 
			AND edit_type IN ('d', 'm')
		)
		SELECT COALESCE(ARRAY_AGG(uid), array[]::text[]) 
		FROM ids
	);
	
	RETURN modified_features;
	
END;
$function$
/*
SELECT * FROM basic.modified_pois(75)
*/
