DROP FUNCTION IF EXISTS pgrouting_edges_multi;
CREATE OR REPLACE FUNCTION public.pgrouting_edges_multi(userid_input integer, minutes integer,array_starting_points NUMERIC[][],speed NUMERIC, number_isochrones integer, ids_calc int[], objectid_input integer, modus_input integer,routing_profile text)
 RETURNS void --SETOF type_catchment_vertices_multi
 LANGUAGE plpgsql
AS $function$
DECLARE
	distance integer;
	array_starting_ids bigint[] := array[]::bigint[];
  array_starting_geom geometry[] :=array[]::geometry[]; 
  array_original_wid bigint[] := array[]::bigint[];
  array_new_wid bigint[] := array[]::bigint[];
	excluded_class_id text;
	categories_no_foot text;
	buffer text;
  userid_vertex integer;
  counter integer := 1;
  new_vid bigint := 999999999;
  wid bigint;
  new_wid1 bigint := 999999999;
  new_wid2 bigint := 999999998;
  closest_point geometry;
  fraction float;
  single_id integer;
  x numeric;
  y numeric;
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

  distance = (60*minutes)*speed;
  
  SELECT ST_AsText(ST_Buffer(ST_Union(ST_POINT(c.lat_lon[1],c.lat_lon[2]))::geography,distance)::geometry)  
  INTO buffer
  FROM (SELECT unnest_2d_1d(array_starting_points) lat_lon) c;

  DROP TABLE IF EXISTS temp_fetched_ways;
  CREATE TEMP TABLE temp_fetched_ways AS 
  SELECT * FROM fetch_ways_routing(buffer,modus_input,userid_input,routing_profile);

  ALTER TABLE temp_fetched_ways ADD PRIMARY KEY(id);
  CREATE INDEX ON temp_fetched_ways (target);
  CREATE INDEX ON temp_fetched_ways (source);
  CREATE INDEX ON temp_fetched_ways (death_end);

  FOREACH single_id IN ARRAY ids_calc
	LOOP
    new_wid1 = new_wid1 - 1;
    new_wid2 = new_wid1 - 1;
    

    new_vid = new_vid - 1;
    raise notice '%',new_vid;
    x = array_starting_points[counter][1];
    y = array_starting_points[counter][2];

    SELECT c.closest_point, c.fraction, c.wid
    INTO closest_point, fraction, wid
    FROM closest_point_network(x,y) c;

    INSERT INTO temp_fetched_ways(id,cost,reverse_cost,source,target,geom)
    SELECT new_wid1, cost*fraction,reverse_cost*fraction,SOURCE,new_vid,ST_LINESUBSTRING(geom,0,fraction)
    FROM temp_fetched_ways 
    WHERE id = wid
    UNION ALL 
    SELECT new_wid2, cost*(1-fraction),reverse_cost*(1-fraction),new_vid,target,ST_LINESUBSTRING(geom,fraction,1)
    FROM temp_fetched_ways 
    WHERE id = wid;   

    array_starting_ids = array_starting_ids || new_vid;
    array_starting_geom = array_starting_geom || closest_point;
    array_original_wid = array_original_wid || wid;
    array_new_wid = array_new_wid || new_wid1 || new_wid2;

    counter = counter + 1;
    new_wid1 = new_wid1 - 1;

  END LOOP;

  DROP TABLE IF EXISTS starting_vertices;
  CREATE temp TABLE starting_vertices AS 
  SELECT UNNEST(array_starting_ids) vid,UNNEST(ids_calc) id_calc;

  DROP TABLE IF EXISTS temp_reached_vertices;

  CREATE TEMP TABLE temp_reached_vertices AS
  SELECT array_agg(agg_cost/speed) costs,array_agg(s.id_calc) ids_calc,
  --jsonb_object_agg(s.id_calc,agg_cost/speed) AS node_cost,sort(array_agg(s.id_calc)) ids_calc,
  x.node::int, min((x.agg_cost/speed)::numeric) AS min_cost, v.geom, v.death_end
  FROM 
  (SELECT from_v, node, edge, agg_cost FROM pgr_drivingDistance(
  'SELECT * FROM temp_fetched_ways WHERE NOT id = ANY('''||array_original_wid::text||''')'
  ,array_starting_ids, distance,FALSE,FALSE)
  ) x, ways_userinput_vertices_pgr v, starting_vertices s  
  WHERE v.id = x.node AND s.vid = x.from_v
  GROUP BY x.node, v.geom, v.death_end;

  ALTER TABLE temp_reached_vertices ADD PRIMARY KEY(node);
  CREATE INDEX ON temp_reached_vertices (death_end);
  PERFORM get_reached_network_multi_array(ids_calc,minutes*60, number_isochrones, array_new_wid, objectid_input);

END ;
$function$;


/*
SELECT * 
FROM public.pgrouting_edges_multi(100,20, ARRAY[[11.2570,48.1841],[11.2314,48.1736],[11.2503,48.1928],[11.2487,48.1718]], 
1.33, 1, ARRAY[1,2,3,4], 12,20, 'walking_wheelchair');
*/