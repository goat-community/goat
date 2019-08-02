
EXPLAIN ANALYZE


SELECT grid_id, part_accessibility_index((pois -> 'atm'),0.01)+
part_accessibility_index((pois -> 'bar'),0.01) 
FROM grid_500




select  * from heatmap_new('[{"''bus_stop''":{{"''sensitivity''":0.001},{"''weight''":2}}}]')



DROP FUNCTION heatmap_new

CREATE OR REPLACE FUNCTION public.heatmap_new(amenities text)
 RETURNS SETOF text
 LANGUAGE plpgsql
AS $function$
DECLARE
 
  i jsonb;
  sql_query text =  'SELECT grid_id,geom,';
BEGIN
  For i IN SELECT * FROM jsonb_array_elements(amenities::jsonb)
  LOOP
    
	sql_query = concat(sql_query,'(');
    sql_query = concat(sql_query,i ->> jsonb_object_keys(i)) ->> 'weight';    
	sql_query = concat(sql_query,'->>');
	sql_query = concat(sql_query,jsonb_object_keys(i));
	sql_query = concat(sql_query,')::numeric,0)+');

  END LOOP;
  
  sql_query = sql_query || '0' || ' FROM grid_500';
  RAISE NOTICE 'output FROM space %',sql_query;
  Return query SELECT sql_query;
END;
$function$



