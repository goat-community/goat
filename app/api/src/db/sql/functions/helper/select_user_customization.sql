CREATE OR REPLACE FUNCTION basic.select_user_customization(user_id_input integer, setting_type text)
RETURNS jsonb
 LANGUAGE sql
AS $function$

	SELECT u.setting -> c.type
	FROM customer.customization c, customer.user_customization u, customer.user u2
	WHERE u2.id = user_id_input
	AND u2.active_study_area_id = u.study_area_id
	AND c.type = setting_type 
	AND u.customization_id = c.id
	AND u.user_id = user_id_input;

$function$ IMMUTABLE;
/*
SELECT select_user_customization(1, 'poi_groups');
*/
