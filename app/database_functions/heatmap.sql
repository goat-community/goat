CREATE OR REPLACE FUNCTION public.heatmap(amenities text, sensitivity character varying)
 RETURNS TABLE(grid_id integer, geom geometry, accessibility_index double precision)
 LANGUAGE plpgsql
AS $function$
DECLARE
 
    i jsonb;
	sql_query text =  'SELECT grid_id,geom,';
BEGIN
  For i IN SELECT * FROM jsonb_array_elements(amenities::jsonb)
  LOOP
    
	sql_query = concat(sql_query,i ->> jsonb_object_keys(i));
	sql_query = sql_query||'*COALESCE(('||sensitivity;
    
	sql_query = concat(sql_query,'->>');
	sql_query = concat(sql_query,jsonb_object_keys(i));
	sql_query = concat(sql_query,')::float,0)+');
  	RAISE NOTICE 'output FROM space %', sql_query;
  END LOOP;
  
  sql_query = sql_query || '0' || ' FROM grid_500';
  RAISE NOTICE 'output FROM space %',sql_query;
  Return query
  	execute sql_query;
  return;
END ;
$function$

--Example
--select  * from heatmap('[{"''bus_stop''":2},{"''tram_stop''":3}]','index_0_001')