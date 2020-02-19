DROP FUNCTION IF EXISTS pgrouting_edges;
CREATE OR REPLACE FUNCTION public.pgrouting_edges(minutes integer, x numeric, y numeric, speed numeric, number_isochrones integer, userid_input integer, objectid_input integer, modus_input integer, routing_profile text)
 RETURNS VOID--SETOF type_catchment_vertices_single
 LANGUAGE plpgsql
AS $function$
DECLARE
  r type_edges;
  buffer text;
  distance numeric := speed*(minutes*60);
  id_vertex integer;
  start_point geometry;
  geom_vertex geometry;
  number_calculation_input integer;
  max_length_links integer := select_from_variable_container_s('max_length_links')::integer;
  speed_elderly numeric := select_from_variable_container_s('walking_speed_elderly')::numeric;
  speed_wheelchair numeric := select_from_variable_container_s('walking_speed_wheelchair')::numeric;
  userid_vertex integer;
  closest_point geometry; 
  fraction float;
  vid integer; 
  wid integer;
begin
  --Adjust for Routing Modus(Default, Scenario, Comparison)
  
  IF modus_input IN(1,3)  THEN
		userid_vertex = 1;
		userid_input = 1;
  ELSEIF modus_input = 2 THEN
    userid_vertex = userid_input;
	ELSEIF modus_input = 4 THEN  	 
		userid_vertex = 1;
	END IF;

/*
  SELECT closest_vertex[1] AS id, closest_vertex[2] geom 
  INTO id_vertex, geom_vertex
  FROM closest_vertex(userid_vertex,x,y,0.0018 100m => approx. 0.0009 ,modus_input, routing_profile);

*/


/*start_point still has to be tested as it is the point were the user clicked. Worst case could be that we don't fetch the whole network*/  

  start_point = ST_SETSRID(ST_POINT(x,y),4326);
  IF modus_input <> 3 THEN 
		SELECT count(objectid) + 1 
    INTO number_calculation_input
		FROM starting_point_isochrones
		WHERE userid = userid_input; 
		INSERT INTO starting_point_isochrones(userid,geom,objectid,number_calculation)
		SELECT userid_input, start_point, objectid_input, number_calculation_input;
	END IF; 
  
  IF routing_profile = 'walking_elderly' THEN
    speed = speed_elderly; 
  ELSEIF routing_profile = 'walking_wheelchair' THEN
    speed = speed_wheelchair; 
  END IF; 


  SELECT ST_AsText(ST_Buffer(start_point::geography,distance)::geometry)  
  INTO buffer;

  DROP TABLE IF EXISTS temp_fetched_ways;
  DROP TABLE IF EXISTS temp_reached_vertices;

  CREATE TEMP TABLE temp_fetched_ways AS 
  SELECT *
  FROM fetch_ways_routing(buffer,modus_input,userid_input,routing_profile);

  ALTER TABLE temp_fetched_ways ADD PRIMARY KEY(id);
  CREATE INDEX ON temp_fetched_ways (target);
  CREATE INDEX ON temp_fetched_ways (source);
  CREATE INDEX ON temp_fetched_ways (death_end);

  SELECT c.closest_point, c.fraction, c.wid, c.vid 
  INTO closest_point, fraction, wid, vid
  FROM closest_point_network(x,y) c;

  INSERT INTO temp_fetched_ways(id,cost,reverse_cost,source,target,geom)
  SELECT 99999998, cost*fraction,reverse_cost*fraction,SOURCE,vid,ST_LINESUBSTRING(geom,0,fraction)
	FROM temp_fetched_ways 
  WHERE id = wid
  UNION ALL 
  SELECT 99999999, cost*(1-fraction),reverse_cost*(1-fraction),vid,target,ST_LINESUBSTRING(geom,fraction,1)
	FROM temp_fetched_ways 
  WHERE id = wid;
  
  DELETE FROM temp_fetched_ways WHERE id = wid;

  IF modus_input = 1 THEN 
    CREATE TEMP TABLE temp_reached_vertices as 
    SELECT id_vertex AS start_vertex, id1::integer AS node, (cost/speed)::NUMERIC AS cost, v.geom, objectid_input AS objectid, v.death_end 
    FROM PGR_DrivingDistance( 
        'SELECT * FROM temp_fetched_ways WHERE id <> '||wid,
        vid, distance,FALSE,FALSE
        )p, ways_vertices_pgr v
    WHERE p.id1 = v.id
    UNION ALL 
    SELECT vid, vid, 0, closest_point, objectid_input, NULL;

  ELSE
    CREATE TEMP TABLE temp_reached_vertices as 
    SELECT id_vertex AS start_vertex, id1::integer AS node, (cost/speed)::NUMERIC AS cost, v.geom, objectid_input AS objectid, v.death_end
    FROM PGR_DrivingDistance(
      'SELECT * FROM temp_fetched_ways  WHERE id <> '||wid,
      vid, distance, FALSE, FALSE
    ) p, ways_userinput_vertices_pgr v
    WHERE p.id1 = v.id
    UNION ALL 
    SELECT vid, vid, 0, closest_point, objectid_input, NULL;
  END IF;

  ALTER TABLE temp_reached_vertices ADD PRIMARY KEY(node);

  PERFORM get_reached_network(objectid_input,minutes*60,number_isochrones,ARRAY[99999998,99999999]);

  RETURN;
END ;
$function$;

--SELECT * FROM public.pgrouting_edges(7, 11.546394, 48.195533, 1.33, 2, 1, 15, 1, 'walking_safe_night');
--Speed in m/s