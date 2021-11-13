/*Fetches the routing network*/
DROP FUNCTION IF EXISTS fetch_network_routing;
CREATE OR REPLACE FUNCTION public.fetch_network_routing(x float[], y float[], max_cutoff float, speed float, modus integer, scenario_id integer, routing_profile text)
 RETURNS SETOF type_fetch_ways_routing
 LANGUAGE plpgsql
AS $function$
DECLARE 
	buffer_starting_point geometry; 
	buffer_network geometry;
	point geometry := ST_SETSRID(ST_POINT(x[1],y[1]), 4326);
	snap_distance_network float := 200;
	buffer_distance float;

BEGIN 

	SELECT ST_Buffer(point::geography,snap_distance_network)::geometry
	INTO buffer_starting_point;

	SELECT ST_Buffer(point::geography,max_cutoff * speed)::geometry
	INTO buffer_network;

	DROP TABLE IF EXISTS artificial_edges;
	CREATE TEMP TABLE artificial_edges AS   
	SELECT * 
	FROM create_artificial_edges(query_ways_routing(ST_ASTEXT(buffer_starting_point),modus,scenario_id,speed,routing_profile),
		point, snap_distance_network
	); 
		
	RETURN query EXECUTE 
	query_ways_routing(ST_ASTEXT(buffer_network),modus,scenario_id,speed,routing_profile) || 
    ' AND id NOT IN (SELECT wid FROM artificial_edges)
	UNION ALL 
	SELECT id, source, target, length_m, cost, reverse_cost, NULL AS death_end, geom 
	FROM artificial_edges' USING buffer_network;

END;
$function$;

/*
SELECT * 
FROM fetch_network_routing(11.543274,48.195524, 1200., 1.33, 1, 1, 'walking_standard')
*/