CREATE OR REPLACE FUNCTION pois_reclassification(old_col TEXT, old_name TEXT, new_col TEXT, new_name TEXT)
	RETURNS VOID
	LANGUAGE plpgsql
AS $function$
BEGIN
	EXECUTE 
	'UPDATE pois 
	 SET '|| quote_ident(new_col) ||' = '|| quote_literal(new_name) ||'
     WHERE '|| quote_ident(old_col) ||' = '|| quote_literal(old_name)||'' ;
END;
$function$;