CREATE OR REPLACE FUNCTION public.pgrouting_edges_snaptolerance(minutes integer, x numeric, y numeric, speed numeric, userid_input integer, objectid_input integer, snap_tolerance integer)
 RETURNS SETOF type_edges
 LANGUAGE plpgsql
AS $function$
DECLARE
r type_edges;
distance numeric;
id_vertex integer;
excluded_class_id text;
number_calculation_input integer;
begin
--The speed AND minutes input are considered as distance
  distance=speed*minutes;
  
  SELECT variable_array::text
  INTO excluded_class_id 
  FROM variable_container v
  WHERE v.identifier = 'excluded_class_id_walking';

  SELECT id INTO id_vertex
   FROM ways_vertices_pgr v
--It is snapped to the closest vertex within 50 m. If no vertex is within 50m not calculation is started.
           WHERE ST_DWithin(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326), snap_tolerance)
           ORDER BY ST_Distance(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326))
           limit 1;
  
  SELECT count(objectid) + 1 INTO number_calculation_input
  FROM starting_point_isochrones
  WHERE userid = userid_input;
 
  INSERT INTO starting_point_isochrones(userid,geom,objectid,number_calculation)
  SELECT userid_input, v.geom, objectid_input, number_calculation_input
  FROM ways_vertices_pgr v
  WHERE v.id = id_vertex;


  For r IN SELECT * FROM 
--The function Pgr_DrivingDistance delivers the reached network 
--In this case the routing is done on a not modified table
		  (SELECT t1.seq, t1.id1 AS Node, t1.id2 AS Edge, t1.cost, t2.geom FROM PGR_DrivingDistance(
--This routing is for pedestrians, thus some way_classes are excluded.  
  			'SELECT id::int4, source, target, length_m as cost FROM ways  WHERE not class_id = any(''' || excluded_class_id || ''')',
  		  id_vertex, 
	       distance, false, false) t1, ways t2
           WHERE t1.id2 = t2.id) as route
           LOOP
  RETURN NEXT r;
  
  END LOOP;
  RETURN;
END ;
$function$
