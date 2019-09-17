CREATE OR REPLACE FUNCTION public.heatmap(amenities text)
  RETURNS TABLE(grid_id integer, geom geometry, accessibility_index numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
	i jsonb;
	sql_query text =  'SELECT grid_id,geom,';
	sql_single_query text;
	array_amenities text[];
	amenity text;
	column_index text;
	weight_amenity text;
BEGIN
  For i IN SELECT * FROM jsonb_array_elements(amenities::jsonb)
  LOOP
	  amenity = ''''||jsonb_object_keys(i)::text||'''';	
	  column_index = format('index_%s',split_part(((i ->> jsonb_object_keys(i))::jsonb ->> 'sensitivity')::text,'.',2));
	  weight_amenity = ((i ->> jsonb_object_keys(i))::jsonb ->> 'weight');
	 
      sql_single_query = format('%s*COALESCE((%s -> %s)::text::numeric,0) +',weight_amenity,column_index,amenity);
	  sql_query = concat(sql_query,sql_single_query);
	  array_amenities = array_amenities || amenity;
  END LOOP;
  sql_query = sql_query || format('0 from grid_500 WHERE %s ?| array[%s]',column_index,REPLACE(REPLACE(array_amenities::text,'{',''),'}',''));
  Return query EXECUTE sql_query;
  RETURN;
END;
$function$

--Example
/*select * 
from heatmap('[
	{"bus_stop":{"sensitivity":-0.003,"weight":2}},
	{"tram_stop":{"sensitivity":-0.002,"weight":4}},
	{"subway_entrance":{"sensitivity":-0.001,"weight":4}},
	{"rail_station":{"sensitivity":-0.001,"weight":4}}
]')
*/