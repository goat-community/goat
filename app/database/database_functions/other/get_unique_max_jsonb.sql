CREATE OR REPLACE FUNCTION get_unique_max_jsonb(json1 jsonb, json2 jsonb, duplicates text[]) 
RETURNS SETOF jsonb 
AS $$
DECLARE 
	value1 NUMERIC;
	value2 NUMERIC;
	new_json_element jsonb;
	new_json jsonb := '{}'::jsonb;
	i text;
BEGIN 
	FOREACH i IN ARRAY duplicates 
	LOOP
		value1 = json1 ->> i;
		value2 = json2 ->> i;
		IF value1 > value2 THEN
			new_json_element = jsonb_build_object(i,value1);
		ELSE 
			new_json_element = jsonb_build_object(i,value2);
		END IF; 
		new_json = new_json || new_json_element;
	END LOOP; 

	RETURN query SELECT new_json;
	
END;
$$ LANGUAGE plpgsql;
--SELECT get_unique_max('{"1":"1","2":"2","3":"3"}','{"1":"4","2":"3","3":"3"}',ARRAY['1','2'])



CREATE OR REPLACE FUNCTION get_unique_max_jsonb(json1 jsonb, json2 jsonb, array1 text[],array2 text[]) 
RETURNS SETOF jsonb 
AS $$
DECLARE 
	value1 NUMERIC;
	value2 NUMERIC;
	new_json_element jsonb;
	new_json jsonb := '{}'::jsonb;
	i text;
	duplicates text[];
BEGIN 
	
	IF array1 <> array2 THEN 
	
		duplicates = array_intersect(array1,array2);
	
		FOREACH i IN ARRAY duplicates 
		LOOP
			value1 = json1 ->> i;
			value2 = json2 ->> i;
			IF value1 > value2 THEN
				new_json_element = jsonb_build_object(i,value1);
			ELSE 
				new_json_element = jsonb_build_object(i,value2);
			END IF; 
			new_json = new_json || new_json_element;
		END LOOP; 
		RETURN query SELECT new_json;
	ELSE 
		RETURN query SELECT json2; 
	END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION array_substraction(anyarray, anyarray) 
RETURNS anyarray AS $$
  SELECT ARRAY(SELECT unnest($1) 
               EXCEPT 
               SELECT unnest($2))
$$ LANGUAGE sql;