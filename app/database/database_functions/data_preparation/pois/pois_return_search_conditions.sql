DROP FUNCTION IF EXISTS pois_return_search_conditions;
CREATE OR REPLACE FUNCTION public.pois_return_search_conditions(amenity TEXT, search_restriction TEXT)
RETURNS text[]
LANGUAGE plpgsql
AS $function$
DECLARE 
	cnt_keys integer;
	json_condition jsonb := (select_from_variable_container_o('pois_search_conditions') -> amenity);
	arr_search_conditions TEXT[];
BEGIN
	
	DROP TABLE IF EXISTS array_elements;	
	IF jsonb_typeof(json_condition) = 'object' THEN 
		CREATE TEMP TABLE array_elements AS 
		WITH json_keys AS 
		(
			SELECT jsonb_object_keys(json_condition) AS k
		)
		SELECT jsonb_array_elements_text(json_condition -> k) elem
		FROM json_keys
		UNION ALL 
		SELECT * FROM json_keys;
	ELSEIF jsonb_typeof(json_condition) = 'array' THEN  
		CREATE TEMP TABLE array_elements AS 
		SELECT jsonb_array_elements_text(json_condition) elem;
	ELSE
		RAISE NOTICE 'There was found no object nor array!';
	END IF; 

	SELECT array_agg(elem)
	INTO arr_search_conditions
	FROM 
	(
		SELECT CASE WHEN search_restriction = 'left' THEN '%'||elem  
		WHEN search_restriction = 'right' THEN elem || '%'
		WHEN search_restriction = 'any' THEN '%'||elem||'%'
		END AS elem 
		FROM array_elements
	) x; 

	RETURN arr_search_conditions;

END
$function$
/*SELECT pois_return_search_conditions('discount_supermarket','any')*/