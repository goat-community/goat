CREATE OR REPLACE FUNCTION basic.intersection_poi_categories(available_categories jsonb, requested_categories TEXT[])
 RETURNS text[]
 LANGUAGE plpgsql
AS $function$
DECLARE 
	allowed_categories text[]; 	
BEGIN 
	SELECT ARRAY_AGG(s.value)
	INTO allowed_categories 
	FROM jsonb_array_elements_text(available_categories) s,
	UNNEST(requested_categories) r
	WHERE r.r = s.value; 
	
	RETURN allowed_categories; 
END ;
$function$
/*SELECT basic.intersection_poi_categories(basic.poi_categories(4) -> 'false', ARRAY['supermarket'])*/

/*
CREATE OR REPLACE FUNCTION basic.intersection_poi_categories(available_categories jsonb, requested_categories TEXT[])
 RETURNS text[]
 LANGUAGE plpgsql
AS $function$
DECLARE 
	allowed_categories text[]; 	
BEGIN 
	SELECT ARRAY_AGG(s.value)
	INTO allowed_categories 
	FROM jsonb_array_elements_text(available_categories) s;
	--,
	--UNNEST(requested_categories) r
	--WHERE r.r = s.value;
	 
	
	RETURN allowed_categories; 
END ;
$function$
*/
/*SELECT basic.intersection_poi_categories(basic.poi_categories(4) -> 'false', ARRAY['supermarket'])*/



