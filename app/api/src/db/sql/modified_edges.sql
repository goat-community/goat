CREATE OR REPLACE FUNCTION basic.modified_edges(scenario_id_input integer)
 RETURNS INTEGER[]
 LANGUAGE plpgsql
AS $function$
DECLARE 
	modified_features integer[];
BEGIN 

	modified_features = 
	(
		WITH ids AS 
		(
			SELECT DISTINCT way_id 
			FROM customer.way_modified  
			WHERE scenario_id = scenario_id_input 
			AND way_id IS NOT NULL 
			AND edit_type IN ('d', 'm')
		)
		SELECT COALESCE(ARRAY_AGG(way_id), array[]::integer[]) 
		FROM ids
	);
	
	RETURN modified_features;
	
END;
$function$
/*
SELECT * FROM basic.modified_edges(1)
*/