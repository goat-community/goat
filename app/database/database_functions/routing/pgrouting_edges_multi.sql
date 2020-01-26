DROP FUNCTION IF EXISTS pgrouting_edges_multi;
CREATE OR REPLACE FUNCTION public.pgrouting_edges_multi(userid_input integer, minutes integer,array_starting_points NUMERIC[][],speed NUMERIC, objectids int[], modus_input integer,routing_profile text)
 RETURNS SETOF type_catchment_vertices_multi
 LANGUAGE plpgsql
AS $function$
DECLARE
	distance integer;
	array_starting_vertices bigint[];
	excluded_class_id text;
	categories_no_foot text;
	buffer text;
  userid_vertex integer;
BEGIN
  
  IF modus_input IN(1,3)  THEN
		userid_vertex = 1;
		userid_input = 1;
  ELSEIF modus_input = 2 THEN
    userid_vertex = userid_input;
	ELSEIF modus_input = 4 THEN  	 
		userid_vertex = 1;
	END IF;
  raise notice '%',modus_input;
  DROP TABLE IF EXISTS closest_vertices;
  speed = speed/3.6;
  distance = minutes*speed*60;
 
  SELECT select_from_variable_container('excluded_class_id_walking'),
  select_from_variable_container('categories_no_foot')
  INTO excluded_class_id, categories_no_foot;
 
  CREATE TEMP TABLE IF NOT EXISTS closest_vertices (closest_vertices bigint, geom geometry, objectid integer);
  TRUNCATE closest_vertices;

  INSERT INTO closest_vertices
  SELECT closest_vertex[1]::bigint closest_vertices, closest_vertex[2]::geometry AS geom, objectid 
  FROM (
	  SELECT closest_vertex(userid_vertex,lat_lon_array[1],lat_lon_array[2],0.0018 /*100m => approx. 0.0009 */, modus_input, routing_profile), objectid
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
	'SELECT * FROM fetch_ways_routing('''||buffer||''','||speed||','||modus_input||','||userid_input||','''||routing_profile||''')'
	,array_starting_vertices, distance,FALSE,FALSE)
  )x, closest_vertices c
  WHERE w.id = x.node AND c.closest_vertices = from_v;
END ;
$function$;



--SELECT * FROM public.pgrouting_edges_multi(100, 15, ARRAY[[11.5669,48.1546],[11.5788,48.1545]], 1.33, ARRAY[1,2], 1, 'walking_wheelchair');