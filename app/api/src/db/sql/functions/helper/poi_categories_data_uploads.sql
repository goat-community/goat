CREATE OR REPLACE FUNCTION basic.poi_categories_data_uploads(user_id_input integer)
 RETURNS text[]
 LANGUAGE plpgsql
AS $function$
DECLARE 
	upload_ids integer[];
	area_id integer;
	upload_id integer; 
	poi_user_category TEXT;
	categories text[] := '{}'::TEXT[];
BEGIN 
	SELECT u.active_data_upload_ids, u.active_study_area_id  
	INTO upload_ids, area_id 
	FROM customer.USER u 
	WHERE u.id = user_id_input;

	FOREACH upload_id IN ARRAY upload_ids 
	LOOP
		SELECT category 
		INTO poi_user_category 
		FROM customer.poi_user p, customer.data_upload d
		WHERE p.data_upload_id = upload_id 
		AND p.data_upload_id = d.id 
		AND d.study_area_id = area_id  
		LIMIT 1; 
		
		IF poi_user_category IS NOT NULL THEN  
			categories = array_append(categories, poi_user_category );
		END IF; 
	
	END LOOP;
	
	RETURN COALESCE(categories, '{}'::TEXT[]);

END ;
$function$

/*
SELECT * FROM basic.poi_categories_data_uploads(4)
*/