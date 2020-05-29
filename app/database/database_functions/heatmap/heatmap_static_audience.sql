DROP FUNCTION IF EXISTS heatmap_static_audience;
CREATE OR REPLACE FUNCTION public.heatmap_static_audience(impedance int)
  RETURNS TABLE(grid_id integer, audience_index int, geom geometry)
 LANGUAGE plpgsql
AS $function$

BEGIN
  
  Return query
  SELECT g.grid_id, (g.static_audience_index->>impedance::TEXT)::int, g.geom
  FROM grid_500 g;

END;
$function$

--SELECT heatmap_static_audience(250000)
