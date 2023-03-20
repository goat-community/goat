CREATE OR REPLACE FUNCTION basic.select_customization(setting_type text, study_area_id integer)
RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE 
	setting_study_area jsonb; 
	setting_standard jsonb; 
BEGIN 
	
	setting_study_area = (
		SELECT (setting -> setting_type) AS customization 
		FROM basic.study_area sa 
		WHERE id = study_area_id
	); 
	
	IF setting_study_area IS NOT NULL THEN 
		RETURN setting_study_area;
	ELSE
		setting_standard = (
			SELECT setting -> c.type
			FROM customer.customization c 
			WHERE c.type = setting_type
		);
		RETURN setting_standard; 
	END IF; 
END;
$function$ IMMUTABLE;
/*
SELECT *
FROM basic.select_customization('excluded_class_id_walking', 11000009);
*/