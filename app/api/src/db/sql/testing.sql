CREATE OR REPLACE FUNCTION basic.fetch_network_routing_v2(x float[], y float[], max_cutoff float, speed float, modus text, scenario_id integer, routing_profile text)
 RETURNS SETOF void 
 LANGUAGE plpgsql
AS $function$
DECLARE 
	buffer_starting_point geometry; 
	buffer_network geometry;
	point geometry; 
	snap_distance_network integer := basic.select_customization('snap_distance_network')::integer;
	cnt_starting_points integer := 0;
	length_starting_points integer := array_length(x, 1);
	artifcial_1 record; 
	artificial_2 record; 
	max_new_node_id integer := 999999999;
	max_new_edge_id integer := 999999999;
BEGIN 

	DROP TABLE IF EXISTS artificial_edges; 
	CREATE TABLE artificial_edges (wid integer, id integer, COST float, reverse_cost float, length_m float, SOURCE integer, target integer, fraction float, geom geometry, starting_point geometry); 

	DROP TABLE IF EXISTS duplicated_artificial_edges; 
	CREATE TABLE duplicated_artificial_edges (wid integer, id integer, COST float, reverse_cost float, length_m float, SOURCE integer, target integer, fraction float, geom geometry, starting_point geometry); 

	DROP TABLE IF EXISTS buffer_network; 
	CREATE TABLE buffer_network (id serial, geom geometry);
	

	WHILE cnt_starting_points < length_starting_points 
	LOOP
		cnt_starting_points = cnt_starting_points + 1;
		point = ST_SETSRID(ST_POINT(x[cnt_starting_points],y[cnt_starting_points]), 4326);
		
		SELECT ST_Buffer(point::geography,snap_distance_network)::geometry
		INTO buffer_starting_point;	
		
		INSERT INTO artificial_edges
		SELECT c.*, point AS point_geom  
		FROM basic.create_artificial_edges(basic.query_edges_routing(ST_ASTEXT(buffer_starting_point),modus,scenario_id,speed,routing_profile,FALSE),
			point, snap_distance_network, max_new_node_id, max_new_edge_id  
		) c; 

		INSERT INTO buffer_network(geom) 
		SELECT ST_Buffer(point::geography,max_cutoff * speed)::geometry;
		
		max_new_node_id = max_new_node_id - 1;
		max_new_edge_id = max_new_edge_id - 2; 
	END LOOP; 
	
	DROP TABLE IF EXISTS final_artificial_edges; 
	CREATE TABLE final_artificial_edges AS 
	WITH cnt_artificial_edges AS 
	(
		SELECT a.wid, count(*)::integer AS cnt 
		FROM artificial_edges a  
		GROUP BY wid
	),
	insert_duplicates AS 
	(
		INSERT INTO duplicated_artificial_edges
		SELECT a.* 
		FROM artificial_edges a, cnt_artificial_edges c
		WHERE a.wid = c.wid 
		AND c.cnt > 2 
	)
	SELECT a.* 
	FROM artificial_edges a, cnt_artificial_edges c
	WHERE a.wid = c.wid 
	AND c.cnt <= 2;  


END;
$function$;




CREATE OR REPLACE FUNCTION public.multiple_artificial_edges(wid integer, s integer, t integer, c float, rc float, vids bigint[],fractions float[])
 RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE 
	start_fraction float := 0;
	source_id integer := s;
	end_fraction float;
	start_id integer := s;
	cnt integer := 1;
	edge_id integer := (SELECT min(id)-1 FROM artificial_edges);
BEGIN 
	fractions = array_append(fractions,1::float);
	vids = array_append(vids,t::bigint);
	

	FOREACH end_fraction IN ARRAY fractions
	LOOP 
		INSERT INTO artificial_edges 
		SELECT wid, edge_id, c*(end_fraction-start_fraction),rc*(end_fraction-start_fraction), 
		source_id, vids[cnt], ST_LINESUBSTRING(w_geom,start_fraction,end_fraction);
		
		start_fraction = end_fraction;
		source_id = vids[cnt];
		edge_id = edge_id - 1;
		cnt = cnt + 1;
	END LOOP;
END 
$function$;



WITH sum_cost_duplicated AS 
(
	SELECT d.wid, sum(cost) AS cost, sum(reverse_cost) AS reverse_cost 
	FROM duplicated_artificial_edges d
	GROUP BY d.wid
)

SELECT * 
FROM duplicated_artificial_edges 
ORDER BY wid, fraction  

WITH p AS 
(
	SELECT geom
	FROM basic.poi 
	LIMIT 1000
),
agg AS 
(
	SELECT array_agg(ST_X(geom)) AS x, array_agg(ST_Y(geom)) AS y
	FROM p  
)
SELECT n.* 
FROM agg, 
LATERAL basic.fetch_network_routing_v2(x,y, 1200., 1.33, 'default', 1, 'walking_standard') n
