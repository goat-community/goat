CREATE OR REPLACE FUNCTION public.pgrouting_edges(minutes integer, x numeric, y numeric, speed numeric, userid_input integer, objectid_input integer)
 RETURNS SETOF type_edges
 LANGUAGE plpgsql
AS $function$
DECLARE
point geometry;
r type_edges;
distance numeric;
id_vertex integer;
geom_vertex geometry;
excluded_class_id text;
number_calculation_input integer;
begin
--The speed AND minutes input are considered as distance
  distance=speed*minutes;

  -- input point
  point:= ST_SetSRID(ST_MakePoint(x,y), 4326);
  
  SELECT variable_array::text
  INTO excluded_class_id 
  FROM variable_container v
  WHERE v.identifier = 'excluded_class_id_walking';
  
  SELECT id, geom INTO id_vertex, geom_vertex
  FROM ways_vertices_pgr
  ORDER BY geom <-> point
  LIMIT 1;
  IF ST_Distance(geom_vertex::geography,point::geography)>250 THEN
    RETURN;
  END IF;
 
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
			'SELECT id::int4, source, target, length_m as cost FROM ways 
			 WHERE not class_id = any(''' || excluded_class_id || ''')
       AND' || ' geom && ST_Buffer('''||point::text||'''::geography,'||distance||')::geometry',
  		  id_vertex, 
	       distance, false, false) t1, ways t2
           WHERE t1.id2 = t2.id) as route
           LOOP
  RETURN NEXT r;
  
  END LOOP;
  RETURN;
END ;
$function$;