CREATE OR REPLACE FUNCTION public.pgrouting_edges_multi(minutes integer,array_starting_points NUMERIC[][],speed numeric)
 RETURNS TABLE (start_vertex bigint, geom geometry, cost numeric) 
 LANGUAGE plpgsql
AS $function$
DECLARE
distance integer;
array_starting_vertices bigint[];
excluded_class_id text;
categories_no_foot text;
buffer geometry;
begin
  DROP TABLE closest_vertices;
  distance = minutes*speed;
 
  SELECT variable_array::text
  INTO excluded_class_id 
  FROM variable_container v
  WHERE v.identifier = 'excluded_class_id_walking';
  
  SELECT variable_array::text 
  INTO categories_no_foot
  FROM variable_container
  WHERE identifier = 'categories_no_foot';
 
  CREATE temp TABLE closest_vertices AS  
  SELECT closest_vertex[1]::bigint closest_vertices, closest_vertex[2]::geometry AS geom FROM (
	  SELECT closest_vertex(lat_lon_array[1],lat_lon_array[2],0.0018,'excluded_class_id_walking')
	  --INTO array_starting_vertices
	  FROM (
	  	SELECT UNNEST_2d_1d(array_starting_points) AS lat_lon_array
	  )x
  ) y;
  
 SELECT array_agg(closest_vertices)
 INTO array_starting_vertices
 FROM closest_vertices;
 
 SELECT ST_Buffer(ST_Union(c.geom)::geography,distance)::geometry 
 INTO buffer
 FROM closest_vertices c;
  
 RETURN query 
  SELECT from_v start_vertex, v.geom, x.agg_cost::numeric AS cost
  FROM ways_vertices_pgr v, 
  (	SELECT seq, from_v, node, edge, agg_cost FROM pgr_drivingDistance(
	'SELECT id::int4, source, target, length_m as cost 
	FROM ways
	WHERE NOT class_id = any(''' || excluded_class_id || ''')
    AND (NOT foot = any('''||categories_no_foot||''') OR foot IS NULL)
	AND geom && (SELECT ST_Buffer(ST_Union(c.geom)::geography,'||distance||')::geometry FROM closest_vertices c)'
	,array_starting_vertices, distance,FALSE,FALSE)
  )x
  WHERE v.id = x.node;
END ;
$function$;

--SELECT * FROM pgrouting_edges_multi(10,array[[11.50972,48.18523],[11.51356,48.18517],[11.51160,48.18301]],83.33)
