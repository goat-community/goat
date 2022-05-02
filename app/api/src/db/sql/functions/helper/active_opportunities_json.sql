CREATE OR REPLACE FUNCTION basic.active_opportunities_json(opportunity_type text, user_id_input integer, active_study_area_id integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
DECLARE 
	settings json; 
BEGIN 

	WITH prepared_json AS 
	(
		SELECT category_group AS "group", category, json_build_object('icon', icon, 'color', color) AS icon_color, 
		CASE WHEN multiple_entrance IS NULL THEN '{}'::json ELSE json_build_object('multiple_entrance', multiple_entrance) END AS multiple_entrance,
		CASE WHEN sensitivity IS NULL THEN '{}'::json ELSE json_build_object('sensitivity', sensitivity) END AS sensitivity
		FROM basic.active_opportunities(user_id_input, active_study_area_id) 
	),
	grouped_categories AS 
	(
		SELECT "group", json_agg(json_build_object(category, (icon_color::jsonb || multiple_entrance::jsonb || sensitivity::jsonb)::json)) AS children
		FROM prepared_json 
		GROUP BY "group"
	),
	sorted_as_group AS 
	(
		SELECT json_build_object(o."group", json_build_object('icon', o.icon, 'color', o.color, 'children', g.children)) AS opportunity_groups
		FROM basic.opportunity_group o, grouped_categories g 
		WHERE o."group" = g."group"
	    AND o.type = opportunity_type
	   	ORDER BY o.id
   	)
   	SELECT json_agg(opportunity_groups)
   	INTO settings
	FROM sorted_as_group; 

	RETURN settings; 

END ;
$function$

/*
SELECT basic.active_opportunities_json('poi', 40, 91620000)
*/