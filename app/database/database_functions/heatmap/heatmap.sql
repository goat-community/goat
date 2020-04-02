DROP FUNCTION IF EXISTS heatmap;
CREATE OR REPLACE FUNCTION public.heatmap(amenities jsonb)
  RETURNS TABLE(grid_id integer, accessibility_index numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
	sql_query text =  'SELECT grid_id,';
	sql_single_query text;
	array_amenities text[];
	amenity text;
	column_index text;
	weight_amenity text;
BEGIN
  For amenity IN SELECT * FROM jsonb_object_keys(amenities)
  LOOP

	  column_index = format('index_%s',(amenities -> amenity ->> 'sensitivity')::integer);
	  weight_amenity = (amenities -> amenity ->> 'weight')::integer;
	 
      sql_single_query = format('%s*COALESCE((%s ->> ''%s'')::numeric,0) +',weight_amenity,column_index,amenity);
	  sql_query = concat(sql_query,sql_single_query);
	  array_amenities = array_amenities || (''''||amenity||'''');
  END LOOP;
  sql_query = sql_query || format('0 from grid_500 WHERE %s ?| array[%s]',column_index,REPLACE(REPLACE(array_amenities::text,'{',''),'}',''));
  Return query EXECUTE sql_query;
  RETURN;
END;
$function$

--SELECT heatmap('{"kindergarten":{"sensitivity":250000,"weight":1},"bus_stop":{"sensitivity":250000,"weight":1}}'::jsonb)
