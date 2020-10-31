
/*This function works for POIs and Ways*/
DROP FUNCTION IF EXISTS get_ids_modified_export;
CREATE OR REPLACE FUNCTION public.get_ids_modified_export(scenario_id_input integer, table_input text)
 RETURNS TABLE (gid integer, edit_type text)
 LANGUAGE plpgsql
AS $function$
DECLARE 
	t_name text;
BEGIN 
	RETURN query EXECUTE 'SELECT Unnest(deleted_'|| quote_ident(table_input) ||')::integer gid, ''deleted'' AS edit_type
		FROM scenarios
		WHERE scenario_id = $1
		UNION ALL
		SELECT original_id::integer modified, ''old_modified'' AS edit_type
		FROM '|| quote_ident(table_input)||'_modified 
		WHERE scenario_id = $2 
		AND original_id IS NOT NULL
		' USING scenario_id_input, scenario_id_input;
END;
$function$

/*SELECT * FROM get_ids_modified(15,'pois')*/