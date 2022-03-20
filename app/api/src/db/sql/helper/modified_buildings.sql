CREATE OR REPLACE FUNCTION basic.modified_buildings(scenario_id_input integer)
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
			SELECT DISTINCT building_id 
			FROM customer.building_modified   
			WHERE scenario_id = scenario_id_input 
			AND building_id IS NOT NULL 
			AND edit_type IN ('d')
		)
		SELECT COALESCE(ARRAY_AGG(building_id), array[]::integer[]) 
		FROM ids
	);
	
	RETURN modified_features;
	
END;
$function$
/*
SELECT * FROM basic.modified_buildings(1)
*/