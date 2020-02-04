DROP FUNCTION IF EXISTS ids_modified_features;
CREATE OR REPLACE FUNCTION public.ids_modified_features(userid_input integer,table_input text)
 RETURNS SETOF INTEGER[]
 LANGUAGE plpgsql
AS $function$
BEGIN 
	RETURN query EXECUTE'
		SELECT array_append(array_agg(x.id),0) 
		FROM (
			SELECT Unnest(deleted_feature_ids)::integer id 
			FROM user_data
			WHERE userid = $1 
			AND layer_name = $2
			UNION ALL
			SELECT original_id::integer modified
			FROM '|| quote_ident(table_input)||'_modified 
			WHERE userid = $3 AND original_id IS NOT NULL
		) x'
		USING userid_input, table_input, userid_input;
END;
$function$