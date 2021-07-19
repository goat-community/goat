------------------------------------------------
----- Pois reclassification function------
-- Look for elements in "old_column" = "old_value" and tag them with "new_name" in "new_col"
-- Input values
-- 	old_col	: Column to look up
--	old name: Values to look, in this case correspond to a name in the variable container -> pois_search_conditions.
-- 	new_col	: Column to be modified with the new name
-- 	new name: Value to put in the new column
-- 	elementtype: type of search to be performed, when elementype= 'singlevalue', the search will be performed in column, other values brings search in tags

CREATE OR REPLACE FUNCTION pois_reclassification(old_col TEXT, old_name TEXT, new_col TEXT, new_name TEXT, elementtype  TEXT)
	RETURNS VOID
	LANGUAGE plpgsql
AS $function$
DECLARE 
	looktype TEXT;
BEGIN
	
	IF elementtype = 'singlevalue' THEN
	looktype = ' WHERE ';
	ELSE 
	looktype = ' WHERE tags -> ';
	END IF; 
	EXECUTE 
	'UPDATE pois 
	 SET '|| quote_ident(new_col) ||' = '|| quote_literal(new_name) ||
	 looktype|| quote_ident(old_col) ||' = '|| quote_literal(old_name)||'' ;
    
END;
$function$;