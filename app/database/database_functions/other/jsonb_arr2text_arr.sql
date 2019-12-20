DROP FUNCTION IF EXISTS jsonb_arr2text_arr;
CREATE OR REPLACE FUNCTION jsonb_arr2text_arr(_js jsonb)
  RETURNS text[] LANGUAGE sql IMMUTABLE AS
'SELECT ARRAY(SELECT jsonb_array_elements_text(_js))';