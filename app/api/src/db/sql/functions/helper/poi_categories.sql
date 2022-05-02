CREATE OR REPLACE FUNCTION basic.poi_categories(user_id_input integer)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE 
	active_study_area_id integer := (SELECT active_study_area_id FROM customer.USER WHERE id = user_id_input);
	classified_pois jsonb;
BEGIN 
		
	classified_pois = (
		WITH poi_categories AS 
		(
			SELECT o.multiple_entrance, array_agg(o.category) arr_categories
			FROM basic.active_opportunities(user_id_input, active_study_area_id) o, basic.opportunity_group g 
			WHERE g.TYPE = 'poi'
			AND o.category_group = g.GROUP
			GROUP BY o.multiple_entrance
		)
		SELECT jsonb_object_agg(COALESCE(multiple_entrance, FALSE), arr_categories)
		FROM poi_categories
	); 
	RETURN classified_pois; 
END ;
$function$

/* Function that returns the default and user poi categories grouped into multiple_entrance and single_entrance:
SELECT basic.poi_categories(1) 
*/