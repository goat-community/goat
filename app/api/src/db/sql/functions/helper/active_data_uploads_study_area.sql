CREATE OR REPLACE FUNCTION basic.active_data_uploads_study_area(user_id_input integer)
 RETURNS integer[]
 LANGUAGE plpgsql
AS $function$
DECLARE 
	upload_ids integer[];
	area_id integer;
	upload_id integer; 
	poi_user_category TEXT;
	valid_ids integer[]; 
BEGIN 
	SELECT u.active_data_upload_ids, u.active_study_area_id  
	INTO upload_ids, area_id 
	FROM customer.USER u 
	WHERE u.id = user_id_input;

	SELECT ARRAY_AGG(d.id)
	INTO valid_ids 
	FROM customer.data_upload d, (SELECT UNNEST(upload_ids) id) u  
	WHERE d.study_area_id = area_id 
	AND d.id = u.id; 
	
	RETURN valid_ids;  

END ;
$function$

/*
SELECT * FROM basic.active_data_uploads_study_area(4)
*/