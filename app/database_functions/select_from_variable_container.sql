CREATE OR REPLACE FUNCTION public.select_from_variable_container(identifier_input text)
RETURNS SETOF text 
 LANGUAGE sql
AS $function$

    SELECT variable_array::text
    FROM variable_container v
    WHERE v.identifier = identifier_input;
  
$function$