CREATE OR REPLACE FUNCTION basic.poi_categories(user_id_input integer)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE 
	default_setting jsonb := basic.select_customization('poi_groups');
	user_setting jsonb := basic.select_user_customization(user_id_input, 'poi_groups');
	classified_pois jsonb; 
BEGIN 
	
	DROP TABLE IF EXISTS poi_groups_default; 
	CREATE TEMP TABLE poi_groups_default AS 
	WITH poi_groups AS 
	(
		SELECT jsonb_array_elements(default_setting) poi_group
	)
	SELECT jsonb_array_elements(p.poi_group -> jsonb_object_keys(p.poi_group) -> 'children') AS poi_category 
	FROM poi_groups p;

	DROP TABLE IF EXISTS poi_groups_user; 
	CREATE TEMP TABLE poi_groups_user AS 
	WITH poi_groups AS 
	(
		SELECT jsonb_array_elements(user_setting) poi_group
	)
	SELECT jsonb_array_elements(p.poi_group -> jsonb_object_keys(p.poi_group) -> 'children') AS poi_category 
	FROM poi_groups p; 
	
	classified_pois = (
		WITH poi_categories AS 
		(	
			SELECT jsonb_object_keys(p.poi_category) AS poi_category, (p.poi_category -> jsonb_object_keys(p.poi_category) -> 'multiple_entrance') AS multiple_entrance 
			FROM poi_groups_default p
			UNION ALL 
			SELECT jsonb_object_keys(p.poi_category) AS poi_category, (p.poi_category -> jsonb_object_keys(p.poi_category) -> 'multiple_entrance') AS multiple_entrance 
			FROM poi_groups_user p
		),
		
		poi_classified AS 
		(
			SELECT COALESCE(multiple_entrance::BOOLEAN, FALSE) multiple_entrance, array_agg(poi_category) arr_pois 
			FROM (SELECT DISTINCT * FROM poi_categories) p 
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