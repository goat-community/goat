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
number_calculation_input integer;
max_length_links integer;
begin
--The speed AND minutes input are considered as distance

  IF  routing_profile = 'elderly' THEN
    speed = 0.833333; --in varibale container packen
  END IF; 
  
  distance=speed*(minutes*60);

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

  SELECT variable_simple::integer
  INTO max_length_links
  FROM variable_container 
  WHERE identifier = 'max_length_links';
	
  DROP TABLE IF EXISTS temp_reached_vertices;
  CREATE TEMP TABLE temp_reached_vertices as 
  SELECT id_vertex AS start_vertex, id1::integer AS node, id2::integer AS edge, 1 AS cnt, (cost/speed)::NUMERIC AS cost, v.geom, objectid_input AS objectid 
  FROM PGR_DrivingDistance( 
    	'SELECT * FROM fetch_ways_routing_edited('''||buffer||''','||speed||','||modus_input||','||userid_input||','''||routing_profile||''')'
	    ,id_vertex, distance,FALSE,FALSE
      )p, ways_vertices_pgr v
  WHERE p.id1 = v.id;
    
  RETURN query 
  SELECT start_vertex,node,edge,cost,geom,objectid_input 
  FROM extrapolate_reached_vertices(minutes*60,max_length_links,buffer,speed,modus_input,userid_input,routing_profile); 


  RETURN;
END ;
$function$;

--SELECT * FROM public.pgrouting_edges_edited(7, 11.546394, 48.195533, 1.33, 1, 15, 1, 'safe_night');
