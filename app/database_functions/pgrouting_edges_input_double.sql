CREATE OR REPLACE FUNCTION public.pgrouting_edges_input_double(minutes integer, x numeric, y numeric, speed numeric, userid_input integer, objectid_input integer)
 RETURNS SETOF type_edges
 LANGUAGE plpgsql
AS $function$
	DECLARE
	r type_edges;
	distance numeric;
	id_vertex integer;
	excluded_class_id text;
	begin
	--The speed and minutes input are considered as distance
	  distance=speed*minutes;
	  
      SELECT variable_array::text
  	  into excluded_class_id 
      FROM variable_container v
      where v.identifier = 'excluded_class_id_walking';

	  SELECT id into id_vertex
      FROM ways_userinput_vertices_pgr  v
--It is snapped to the closest vertex within 50 m. If no vertex is within 50m not calculation is started.
      WHERE ST_DWithin(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326), 250)
      ORDER BY ST_Distance(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326))
      limit 1;
	  FOR r IN select *  from 
	--The function Pgr_DrivingDistance delivers the reached network 
	--In this case the routing is done on a modified table
			  (SELECT t1.seq, t1.id1 AS Node, t1.id2 AS Edge, t1.cost, t2.geom FROM PGR_DrivingDistance(
	--This routing is for pedestrians, thus some way_classes are excluded.  			
				'SELECT id::int4, source, target, length_m as cost FROM ways_userinput 
				where not class_id = any(''' || excluded_class_id || ''') and userid is null or userid='||userid_input,
	  		   id_vertex, 
		       distance, false, false) t1, ways_userinput t2
	           WHERE t1.id2 = t2.id) as route
	           LOOP
	  RETURN NEXT r;
	  
	  END LOOP;
	  RETURN;
	END ;
	$function$
