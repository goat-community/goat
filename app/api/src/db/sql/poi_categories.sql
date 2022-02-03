CREATE OR REPLACE FUNCTION basic.poi_categories(user_id_input integer)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE 
	default_setting jsonb := basic.select_customization('poi_group');
	user_setting jsonb := basic.select_user_customization(user_id_input, 'poi_group');
	classified_pois jsonb; 
BEGIN 
	classified_pois = (
		WITH poi_categories AS 
		(
			SELECT poi_group, jsonb_object_keys(default_setting  -> poi_group -> 'children') AS poi_category,
			(default_setting  -> poi_group -> 'children' -> jsonb_object_keys(default_setting  -> poi_group -> 'children') -> 'multiple_entrance') AS multiple_entrance
			FROM jsonb_object_keys(default_setting) AS poi_group
			UNION ALL 
			SELECT poi_group, jsonb_object_keys(user_setting  -> poi_group -> 'children') AS poi_category,
			(user_setting  -> poi_group -> 'children' -> jsonb_object_keys(user_setting  -> poi_group -> 'children') -> 'multiple_entrance')
			FROM jsonb_object_keys(user_setting) AS poi_group
		),
		poi_classified AS 
		(
			SELECT COALESCE(multiple_entrance::BOOLEAN, FALSE) multiple_entrance, array_agg(poi_category) arr_pois 
			FROM poi_categories
			GROUP BY multiple_entrance
		) 
		SELECT jsonb_object_agg(multiple_entrance, arr_pois)
		FROM poi_classified
	);

	RETURN classified_pois; 
END ;
$function$
/* Function that returns the default and user poi categories grouped into multiple_entrance and single_entrance:
SELECT basic.poi_categories(1) 
*/

/*TODO: Remove duplicates*/