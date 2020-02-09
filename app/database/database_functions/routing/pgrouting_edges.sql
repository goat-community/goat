DROP FUNCTION IF EXISTS pgrouting_edges;
CREATE OR REPLACE FUNCTION public.pgrouting_edges(minutes integer, x numeric, y numeric, speed numeric, userid_input integer, objectid_input integer, modus_input integer, routing_profile text)
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
  speed_elderly numeric;
  speed_wheelchair numeric;
  userid_vertex integer;
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

  SELECT closest_vertex[1] AS id, closest_vertex[2] geom 
  INTO id_vertex, geom_vertex
  FROM closest_vertex(userid_vertex,x,y,0.0018 /*100m => approx. 0.0009 */,modus_input, routing_profile);
    
  raise notice '%', id_vertex;

  IF modus_input <> 3 THEN 
		SELECT count(objectid) + 1 INTO number_calculation_input
		FROM starting_point_isochrones
		WHERE userid = userid_input; 
		INSERT INTO starting_point_isochrones(userid,geom,objectid,number_calculation)
		SELECT userid_input, v.geom, objectid_input, number_calculation_input
		FROM ways_userinput_vertices_pgr v
		WHERE v.id = id_vertex;
	END IF; 
  
  --Adjust for Routing Profile
  SELECT select_from_variable_container_s('walking_speed_elderly')::numeric, select_from_variable_container_s('walking_speed_wheelchair')::numeric
  INTO speed_elderly, speed_wheelchair;

  IF  routing_profile = 'walking_elderly' THEN
    speed = speed_elderly; 
  ELSEIF routing_profile = 'walking_wheelchair' THEN
    speed = speed_wheelchair; 
  END IF; 
  
  distance=speed*(minutes*60);


  SELECT ST_AsText(ST_Buffer(ST_Union(geom_vertex)::geography,distance)::geometry)  
  INTO buffer;

  SELECT select_from_variable_container_s('max_length_links')::integer 
  INTO max_length_links;
	
  DROP TABLE IF EXISTS temp_fetched_ways;
  CREATE TEMP TABLE temp_fetched_ways AS 
  SELECT id,SOURCE,target,cost,reverse_cost,geom 
  FROM fetch_ways_routing(buffer,speed,modus_input,userid_input,routing_profile);
  ALTER TABLE temp_fetched_ways ADD PRIMARY KEY(id);
  CREATE INDEX ON temp_fetched_ways (target);
  CREATE INDEX ON temp_fetched_ways (source);

  DROP TABLE IF EXISTS temp_reached_vertices;

  IF modus_input = 1 THEN 
    CREATE TEMP TABLE temp_reached_vertices as 
    SELECT id_vertex AS start_vertex, id1::integer AS node, id2::integer AS edge, 1 AS cnt, (cost/speed)::NUMERIC AS cost, v.geom, objectid_input AS objectid 
    FROM PGR_DrivingDistance( 
        'SELECT * FROM temp_fetched_ways'
        ,id_vertex, distance,FALSE,FALSE
        )p, ways_vertices_pgr v
    WHERE p.id1 = v.id;
  ELSE
    CREATE TEMP TABLE temp_reached_vertices as 
    SELECT id_vertex AS start_vertex, id1::integer AS node, id2::integer AS edge, 1 AS cnt, (cost/speed)::NUMERIC AS cost, v.geom, objectid_input AS objectid
    FROM PGR_DrivingDistance(
      'SELECT * FROM temp_fetched_ways',
      id_vertex, 
      distance, false, false
    ) p, ways_userinput_vertices_pgr v
    WHERE p.id1 = v.id;
  END IF;

  DROP TABLE IF EXISTS temp_extrapolated_vertices;
  CREATE TEMP TABLE temp_extrapolated_vertices as 
  SELECT * FROM extrapolate_reached_vertices(minutes*60,max_length_links,buffer,speed,modus_input,userid_input,routing_profile);
  ALTER TABLE temp_extrapolated_vertices ADD COLUMN id serial;
  ALTER TABLE temp_extrapolated_vertices ADD PRIMARY key(id);
  CREATE INDEX ON temp_extrapolated_vertices(edge);
  --Save reached network 
  INSERT INTO edges(edge,cost,geom,objectid)
  WITH not_in_reached_vertices AS 
  (
    SELECT w.*
    FROM temp_fetched_ways w 
    LEFT JOIN (SELECT * FROM temp_extrapolated_vertices WHERE w_geom IS NOT NULL) v
    ON w.id = v.edge 
    WHERE v.edge IS NULL
  )
  SELECT DISTINCT * 
  FROM (
	  SELECT n.id AS edge, v.cost,n.geom, objectid_input 
	  FROM not_in_reached_vertices n, temp_extrapolated_vertices v 
	  WHERE v.node = n.SOURCE
	  AND v.w_geom IS NULL
	  UNION ALL 
	  SELECT n.id AS edge, v.cost,n.geom,objectid_input  
	  FROM not_in_reached_vertices n, temp_extrapolated_vertices v 
	  WHERE v.node = n.SOURCE
	  AND v.w_geom IS NULL
	  UNION ALL 
	  SELECT v.edge, v.cost,w.geom,objectid_input 
	  FROM temp_fetched_ways w, temp_extrapolated_vertices v 
	  WHERE v.edge = w.id
	  AND v.w_geom IS NULL
	  UNION 
	  SELECT edge, cost, w_geom AS geom,objectid_input 
	  FROM temp_extrapolated_vertices 
	  WHERE w_geom IS NOT NULL
  ) x;


  RETURN query 
  SELECT start_vertex,node,edge,cost,geom,w_geom,objectid_input 
  FROM temp_extrapolated_vertices;
  RETURN;
END ;
$function$;

--SELECT * FROM public.pgrouting_edges(7, 11.546394, 48.195533, 1.33, 1, 15, 1, 'walking_safe_night');
