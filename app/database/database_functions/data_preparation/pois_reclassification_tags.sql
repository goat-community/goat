CREATE OR REPLACE FUNCTION pois_reclassification_tags(tag TEXT, old_name TEXT, new_col TEXT, new_name TEXT)
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN
	EXECUTE 
	'UPDATE pois 
	 SET '|| quote_ident(new_col) ||' = '|| quote_literal(new_name) ||'
     WHERE tags -> '||quote_literal(tag)||' '||quote_ident(criteria)||' '||quote_literal(old_name)||'';	
END;
$function$;