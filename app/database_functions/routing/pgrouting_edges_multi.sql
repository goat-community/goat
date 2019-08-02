CREATE OR REPLACE FUNCTION public.pgrouting_edges_multi(minutes integer,array_starting_points NUMERIC[][],speed NUMERIC, objectids int[])
 RETURNS SETOF type_catchment_vertices
 LANGUAGE plpgsql
AS $function$
DECLARE
distance integer;
array_starting_vertices bigint[];
excluded_class_id text;
categories_no_foot text;
buffer geometry;
begin
  DROP TABLE IF EXISTS closest_vertices;
  distance = minutes*speed*60;
 
  SELECT select_from_variable_container('excluded_class_id_walking'),
  select_from_variable_container('categories_no_foot')
  INTO excluded_class_id, categories_no_foot;
 
  CREATE temp TABLE closest_vertices AS  
  SELECT closest_vertex[1]::bigint closest_vertices, closest_vertex[2]::geometry AS geom, objectid 
  FROM (
	  SELECT closest_vertex(lat_lon_array[1],lat_lon_array[2],0.0018 /*100m => approx. 0.0009 */,'excluded_class_id_walking'), objectid
	  FROM (
	  	SELECT UNNEST_2d_1d(array_starting_points) AS lat_lon_array, UNNEST(objectids) AS objectid
	  )x
  ) y;

  
 SELECT array_agg(closest_vertices)
 INTO array_starting_vertices
 FROM closest_vertices;
 
 SELECT ST_Buffer(ST_Union(c.geom)::geography,distance)::geometry 
 INTO buffer
 FROM closest_vertices c;
  
 RETURN query 
  SELECT x.from_v::int start_vertex, x.node::int, x.edge::int, x.agg_cost::numeric AS cost, w.geom, c.objectid
  FROM ways_vertices_pgr w, 
  (	SELECT from_v, node, edge, agg_cost FROM pgr_drivingDistance(
	'SELECT id::int4, source, target, length_m*'||speed||' as cost 
	FROM ways
	WHERE NOT class_id = any(''' || excluded_class_id || ''')
    AND (NOT foot = any('''||categories_no_foot||''') OR foot IS NULL)
	AND geom && (SELECT ST_Buffer(ST_Union(c.geom)::geography,'||distance||')::geometry FROM closest_vertices c)'
	,array_starting_vertices, distance,FALSE,FALSE)
  )x, closest_vertices c
  WHERE w.id = x.node AND c.closest_vertices = from_v;
END ;
$function$;