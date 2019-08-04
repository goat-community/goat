CREATE OR REPLACE FUNCTION public.heatmap_new(amenities text)
  RETURNS TABLE(grid_id integer, geom geometry, accessibility_index numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
 
  i jsonb;
  sql_query text =  'SELECT grid_id,geom,';
BEGIN
  For i IN SELECT * FROM jsonb_array_elements(amenities::jsonb)
  LOOP

  sql_query = concat(sql_query, (i ->> jsonb_object_keys(i))::jsonb ->> 'weight');  
	sql_query = concat(sql_query,'*part_accessibility_index(');
	sql_query = concat(sql_query,jsonb_object_keys(i));
	sql_query = concat(sql_query,',');
	sql_query = concat(sql_query,(i ->> jsonb_object_keys(i))::jsonb ->> 'sensitivity');
	sql_query = concat(sql_query,')+');
	
  END LOOP;
  sql_query = sql_query || '0 from grid_500';
  Return query EXECUTE(sql_query);
  RETURN;
END;
$function$
