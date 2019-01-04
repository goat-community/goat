CREATE OR REPLACE FUNCTION public.pgrouting_edges_input(minutes integer, x numeric, y numeric, speed numeric, userid_input integer, objectid_input integer, modus integer)
 RETURNS SETOF type_edges
 LANGUAGE plpgsql
AS $function$
	DECLARE
	r type_edges;
	distance numeric;
	id_vertex integer;
	excluded_class_id text;
	excluded_ways_id text;
	userid_vertex integer;
	number_calculation_input integer;
	begin
	--The speed AND minutes input are considered as distance
	  distance=speed*minutes;
	  userid_vertex = userid_input;
	 
	  IF modus = 3  THEN
		userid_vertex = 1;
		userid_input = 1;
  
	  ELSEIF modus = 4 THEN  	 
	  	userid_vertex = 1;
	  END IF;
	 
	  IF modus = 2 OR modus = 4 THEN 
	  	SELECT count(objectid) + 1 INTO number_calculation_input
		FROM starting_point_isochrones
		WHERE userid = userid_input; 
		INSERT INTO starting_point_isochrones(userid,geom,objectid,number_calculation)
		SELECT userid_input, v.geom, objectid_input, number_calculation_input
		FROM ways_vertices_pgr v
		WHERE v.id = id_vertex;
	  END IF; 
     
	  SELECT variable_array::text
  	  INTO excluded_class_id 
      FROM variable_container v
      WHERE v.identifier = 'excluded_class_id_walking';
     
	  SELECT array_append(array_agg(id),0::bigint)::text INTO excluded_ways_id FROM (
		SELECT Unnest(deleted_feature_ids) id FROM user_data
		WHERE id = userid_input
		UNION ALL
		SELECT original_id modified
		FROM ways_modified 
		WHERE userid = userid_input AND original_id IS NOT null
	  ) x;
	 
	  SELECT id INTO id_vertex
      FROM ways_userinput_vertices_pgr  v
--It is snapped to the closest vertex within 50 m. If no vertex is within 50m not calculation is started.
      WHERE ST_DWithin(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326), 250)
	  AND userid is null or userid = userid_vertex
      ORDER BY ST_Distance(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326))
      limit 1;
      
     
     For r IN SELECT *  FROM 
	--The function Pgr_DrivingDistance delivers the reached network 
	--In this case the routing is done on a modified table
			  (SELECT t1.seq, t1.id1 AS Node, t1.id2 AS Edge, t1.cost, t2.geom FROM PGR_DrivingDistance(
	--This routing is for pedestrians, thus some way_classes are excluded.  			
				'SELECT id::int4, source, target, length_m as cost FROM ways_userinput 
				WHERE not class_id = any(''' || excluded_class_id || ''') 
				AND not id::int4 = any('''|| excluded_ways_id ||''') 
				AND userid IS NULL OR userid='||userid_input,
	  		   id_vertex, 
		       distance, false, false) t1, ways_userinput t2
	           WHERE t1.id2 = t2.id) as route
	           LOOP
	  RETURN NEXT r;
	  
	  END LOOP;
	  RETURN;
	END ;
$function$