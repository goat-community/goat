DROP FUNCTION IF EXISTS select_from_variable_container;
CREATE OR REPLACE FUNCTION select_from_variable_container(identifier_input text)
RETURNS SETOF text[]
 LANGUAGE sql
AS $function$

	SELECT variable_array 
	FROM variable_container
	WHERE identifier = identifier_input;

$function$;

DROP FUNCTION IF EXISTS select_from_variable_container_s;
CREATE OR REPLACE FUNCTION select_from_variable_container_s(identifier_input text)
RETURNS text
 LANGUAGE sql
AS $function$

	SELECT variable_simple 
	FROM variable_container
	WHERE identifier = identifier_input;

$function$;

DROP FUNCTION IF EXISTS select_from_variable_container_o;
CREATE OR REPLACE FUNCTION select_from_variable_container_o(identifier_input text)
RETURNS jsonb
 LANGUAGE sql
AS $function$

	SELECT variable_object 
	FROM variable_container
	WHERE identifier = identifier_input;

$function$;