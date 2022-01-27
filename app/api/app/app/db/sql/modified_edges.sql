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
			SELECT edge_id 
			FROM basic.edge 
			WHERE scenario_id = scenario_id_input 
			AND edge_id IS NOT NULL
			UNION ALL 
			SELECT UNNEST(deleted_ways)
			FROM customer.scenario 
			WHERE id = scenario_id_input 
		),
		distinct_ids AS 
		(
			SELECT DISTINCT edge_id FROM ids 
		)
		SELECT COALESCE(ARRAY_AGG(edge_id), array[]::integer[]) 
		FROM distinct_ids
	);
	
	RETURN modified_features;
	
END;
$function$
/*
SELECT * FROM basic.modified_edges(1)
*/