CREATE OR REPLACE FUNCTION public.pgrouting_edges_multi(userid_input integer, minutes integer,array_starting_points NUMERIC[][],speed NUMERIC, objectids int[], modus_input integer)
 RETURNS SETOF type_catchment_vertices
 LANGUAGE plpgsql
AS $function$
DECLARE
	distance integer;
	array_starting_vertices bigint[];
	excluded_class_id text;
	categories_no_foot text;
	buffer text;
begin
  DROP TABLE IF EXISTS closest_vertices;
  speed = speed/3.6;
  distance = minutes*speed*60;
 
  SELECT select_from_variable_container('excluded_class_id_walking'),
  select_from_variable_container('categories_no_foot')
  INTO excluded_class_id, categories_no_foot;
 
  CREATE temp TABLE closest_vertices AS  
  SELECT closest_vertex[1]::bigint closest_vertices, closest_vertex[2]::geometry AS geom, objectid 
  FROM (
	  SELECT closest_vertex(userid_input,lat_lon_array[1],lat_lon_array[2],0.0018 /*100m => approx. 0.0009 */,'excluded_class_id_walking', modus_input), objectid
	  FROM (
	  	SELECT UNNEST_2d_1d(array_starting_points) AS lat_lon_array, UNNEST(objectids) AS objectid
	  )x
  ) y;
  
 SELECT DISTINCT array_agg(closest_vertices)
 INTO array_starting_vertices
 FROM closest_vertices;
 
 SELECT ST_AsText(ST_Buffer(ST_Union(c.geom)::geography,distance)::geometry)  
 INTO buffer
 FROM closest_vertices c;
	
 RETURN query 
  SELECT x.from_v::int start_vertex, x.node::int, x.edge::int, w.cnt, (x.agg_cost/speed)::numeric AS cost, w.geom, c.objectid
  FROM ways_userinput_vertices_pgr w, 
  (SELECT from_v, node, edge, agg_cost FROM pgr_drivingDistance(
	'SELECT * FROM fetch_ways_routing('''||buffer||''','||speed||','''||excluded_class_id||''','''||categories_no_foot||''','||modus_input||','||userid_input||')'
	,array_starting_vertices, distance,FALSE,FALSE)
  )x, closest_vertices c
  WHERE w.id = x.node AND c.closest_vertices = from_v;
END ;
$function$;