DROP FUNCTION IF EXISTS get_attr_for_max_val;
CREATE OR REPLACE FUNCTION get_attr_for_max_val(arr_val integer[], arr_attr text[]) 
RETURNS text
AS $$
DECLARE 
    arr_index integer; 
BEGIN 
    arr_index = arr_val # (sort_desc(arr_val))[1];
   
   
    RETURN arr_attr[arr_index];
END;
$$ LANGUAGE plpgsql IMMUTABLE;
/*SELECT get_attr_for_max_val(ARRAY[300,10,30000],ARRAY['natur','sss','eee'])*/ 