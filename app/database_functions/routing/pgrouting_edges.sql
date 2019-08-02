CREATE OR REPLACE FUNCTION public.pgrouting_edges(minutes integer, x numeric, y numeric, speed numeric, userid_input integer, objectid_input integer)
 RETURNS SETOF type_catchment_vertices
 LANGUAGE plpgsql
AS $function$
DECLARE
r type_edges;
distance numeric;
id_vertex integer;
geom_vertex geometry;
excluded_class_id text;
categories_no_foot text;
number_calculation_input integer;
begin
--The speed AND minutes input are considered as distance
  
  distance=speed*(minutes*60);
  -- input point
  SELECT select_from_variable_container('excluded_class_id_walking'),
  select_from_variable_container('categories_no_foot')
  INTO excluded_class_id, categories_no_foot;

  SELECT closest_vertex[1] AS id, closest_vertex[2] geom 
  INTO id_vertex, geom_vertex
  FROM closest_vertex(x,y,0.0018 /*100m => approx. 0.0009 */,'excluded_class_id_walking');
    
  SELECT count(objectid) + 1 INTO number_calculation_input
  FROM starting_point_isochrones
  WHERE userid = userid_input;
 
  INSERT INTO starting_point_isochrones(userid,geom,objectid,number_calculation)
  SELECT userid_input, v.geom, objectid_input, number_calculation_input
  FROM ways_vertices_pgr v
  WHERE v.id = id_vertex;
  
  RETURN query
  SELECT id_vertex, id1::integer AS node, id2::integer AS edge, (cost/speed)::NUMERIC, v.geom, objectid_input  
  FROM PGR_DrivingDistance( 
	'SELECT id::int4, source, target, length_m as cost FROM ways 
	 WHERE NOT class_id = any(''' || excluded_class_id || ''')
	 AND (NOT foot = any('''||categories_no_foot||''') OR foot IS NULL)
	 AND' || ' geom && ST_Buffer('''||geom_vertex::text||'''::geography,'||distance||')::geometry',
  id_vertex, 
   distance, false, false) p, ways_vertices_pgr v
   WHERE p.id1 = v.id;
  
  RETURN;
END ;
$function$;