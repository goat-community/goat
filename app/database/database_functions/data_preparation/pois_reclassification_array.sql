CREATE OR REPLACE FUNCTION pois_reclassification_array(old_col TEXT, old_name TEXT, new_col TEXT, new_name TEXT, restriction int)
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN
	IF restriction = 1 THEN 
	EXECUTE 'UPDATE pois 
	SET '|| quote_ident(new_col) ||' = '|| quote_literal(new_name) ||'
	WHERE lower('|| lower(quote_ident(old_col)) ||') ~~ 
    ANY (SELECT concat(jsonb_object_keys(select_from_variable_container_o('||quote_literal('pois_search_conditions')||')
	->'||quote_literal(new_name)||'), '||'''%'''||'))
 	AND
	amenity = '|| quote_literal(old_name)||'';
	ELSE
	EXECUTE 'UPDATE pois 
	SET '|| quote_ident(new_col) ||' = '|| quote_literal(new_name) ||'
	WHERE lower('|| lower(quote_ident(old_col)) ||') ~~ 
    ANY (SELECT concat('||'''%'''||', jsonb_object_keys(select_from_variable_container_o('||quote_literal('pois_search_conditions')||')
	->'||quote_literal(new_name)||'), '||'''%'''||'))
 	AND
	amenity = '|| quote_literal(old_name)||'';
	END IF;
END;
$function$;