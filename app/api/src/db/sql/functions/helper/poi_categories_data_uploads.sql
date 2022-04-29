CREATE OR REPLACE FUNCTION basic.poi_categories_data_uploads(user_id_input integer)
 RETURNS text[]
 LANGUAGE plpgsql
AS $function$
DECLARE 
	categories text[];
BEGIN 

	SELECT ARRAY_AGG(data_upload_id)
	INTO categories 
	FROM customer.opportunity_user_config o, customer.USER u
	WHERE o.user_id = u.id
	AND u.id = user_id_input
	AND o.study_area_id = u.active_study_area_id;

	RETURN COALESCE(categories, '{}'::TEXT[]);

END ;
$function$

/*
SELECT * FROM basic.poi_categories_data_uploads(4)
*/