CREATE OR REPLACE FUNCTION basic.select_user_customization(user_id_input integer, setting_type text)
RETURNS jsonb
 LANGUAGE sql
AS $function$

	SELECT u.setting -> c.type
	FROM customer.customization c, customer.user_customization u 
	WHERE c.type = setting_type 
	AND u.customization_id = c.id
	AND u.user_id = user_id_input;

$function$ IMMUTABLE;
/*
SELECT select_user_customization(1, 'poi_group');
*/