DROP FUNCTION IF EXISTS select_from_variable_container;
CREATE OR REPLACE FUNCTION select_from_variable_container(identifier_input text)
RETURNS SETOF text[]
 LANGUAGE sql
AS $function$

	SELECT variable_array 
	FROM variable_container
	WHERE identifier = identifier_input;

$function$