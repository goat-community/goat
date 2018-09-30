CREATE OR REPLACE FUNCTION public.heatmap(amenities text, sensitivity character varying)
 RETURNS TABLE(grid_id integer, geom geometry, accessibility_index double precision)
 LANGUAGE plpgsql
AS $function$
DECLARE
 
    i jsonb;
	sql_query text =  'select grid_id,geom,';
BEGIN
  FOR i IN SELECT * FROM jsonb_array_elements(amenities::jsonb)
  LOOP
    
	sql_query = concat(sql_query,i ->> jsonb_object_keys(i));
	sql_query = sql_query||'*COALESCE(('||sensitivity;
    
	sql_query = concat(sql_query,'->>');
	sql_query = concat(sql_query,jsonb_object_keys(i));
	sql_query = concat(sql_query,')::float,0)+');
  	RAISE NOTICE 'output from space %', sql_query;
  END LOOP;
  
  sql_query = sql_query || '0' || ' from grid_500';
  RAISE NOTICE 'output from space %',sql_query;
  Return query
  	execute sql_query;
  return;
END ;
$function$
