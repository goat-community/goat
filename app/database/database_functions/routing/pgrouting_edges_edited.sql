DROP FUNCTION IF EXISTS pgrouting_edges_edited;
CREATE OR REPLACE FUNCTION public.pgrouting_edges_edited(minutes integer, x numeric, y numeric, speed numeric, userid_input integer, objectid_input integer, modus_input integer, routing_profile text)
 RETURNS SETOF type_catchment_vertices_single
 LANGUAGE plpgsql
AS $function$
DECLARE
r type_edges;
buffer text;
distance numeric;
id_vertex integer;
geom_vertex geometry;
excluded_class_id text;
categories_no_foot text;
number_calculation_input integer;
begin
--The speed AND minutes input are considered as distance

  IF  routing_profile = 'elderly' THEN
    speed = 0.833333; --in varibale container packen
  END IF; 
  
  distance=speed*(minutes*60);
  -- input point
  SELECT select_from_variable_container('excluded_class_id_walking'),
  select_from_variable_container('categories_no_foot')
  INTO excluded_class_id, categories_no_foot;

  SELECT closest_vertex[1] AS id, closest_vertex[2] geom 
  INTO id_vertex, geom_vertex
  FROM closest_vertex(userid_input,x,y,0.0018 /*100m => approx. 0.0009 */,'excluded_class_id_walking',1);
    
  SELECT count(objectid) + 1 INTO number_calculation_input
  FROM starting_point_isochrones
  WHERE userid = userid_input;
 
  INSERT INTO starting_point_isochrones(userid,geom,objectid,number_calculation)
  SELECT userid_input, v.geom, objectid_input, number_calculation_input
  FROM ways_vertices_pgr v
  WHERE v.id = id_vertex;
  
  SELECT ST_AsText(ST_Buffer(ST_Union(geom_vertex)::geography,distance)::geometry)  
  INTO buffer;

  RETURN query
  SELECT id_vertex, id1::integer AS node, id2::integer AS edge, (cost/speed)::NUMERIC, v.geom, objectid_input  
  FROM PGR_DrivingDistance( 
    	'SELECT * FROM fetch_ways_routing_edited('''||buffer||''','||speed||','''||excluded_class_id||''','''||categories_no_foot||''','||modus_input||','||userid_input||','''||routing_profile||''')'
	    ,id_vertex, distance,FALSE,FALSE
      )p, ways_vertices_pgr v
   WHERE p.id1 = v.id;
  
  RETURN;
END ;
$function$;

/* SELECT * FROM public.pgrouting_edges_edited(7, 11.546394, 48.195533, 1.33, 1, 15, 1, 'safe_night');
*/