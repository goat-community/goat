DROP FUNCTION IF EXISTS ids_modified_features;
CREATE OR REPLACE FUNCTION public.ids_modified_features(userid_input integer, scenario_id_input integer, table_input text)
 RETURNS SETOF INTEGER[]
 LANGUAGE plpgsql
AS $function$
DECLARE 
	t_name text;
BEGIN 

	IF table_input = 'pois' THEN 
		t_name = 'pois_modified';
	ELSEIF table_input = 'ways' THEN
		t_name = 'ways_userinput';
	END IF;

	RETURN query EXECUTE'
		SELECT array_append(array_agg(DISTINCT x.id),0) 
		FROM (
			SELECT Unnest(deleted_feature_ids)::integer id 
			FROM user_data
			WHERE userid = $1 
			AND scenario_id = $2
			AND layer_name = $3
			UNION ALL
			SELECT original_id::integer modified
			FROM '|| quote_ident(t_name)||' 
			WHERE userid = $4 AND original_id IS NOT NULL
		) x'
		USING userid_input, scenario_id_input, table_input, userid_input;
END;
$function$

--SELECT ids_modified_features(1,0,'ways')