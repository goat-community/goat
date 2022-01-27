CREATE OR REPLACE FUNCTION basic.select_customization(setting_type text)
RETURNS jsonb
 LANGUAGE sql
AS $function$

	SELECT default_setting -> c.type
	FROM customer.customization c 
	WHERE c.type = setting_type;

$function$ IMMUTABLE;
/*
SELECT select_customization('categories_no_foot');
*/