CREATE OR REPLACE FUNCTION basic.fetch_network_routing(x float[], y float[], max_cutoff float, speed float, modus text, scenario_id integer, routing_profile text)
 RETURNS SETOF type_fetch_edges_routing
 LANGUAGE plpgsql
AS $function$
DECLARE 
	buffer_starting_point geometry; 
	buffer_network geometry;
	point geometry := ST_SETSRID(ST_POINT(x[1],y[1]), 4326);
	snap_distance_network integer;
	max_new_node_id integer := 2147483647;
	max_new_edge_id integer := 2147483647;
	setting_study_area_id integer;
BEGIN 

	setting_study_area_id = basic.get_reference_study_area(ST_SETSRID(ST_POINT(x[1], y[1]), 4326));
	snap_distance_network = basic.select_customization('snap_distance_network', setting_study_area_id)::integer;

	SELECT ST_Buffer(point::geography,snap_distance_network)::geometry
	INTO buffer_starting_point;

	SELECT ST_Buffer(point::geography,max_cutoff * speed)::geometry
	INTO buffer_network;

	DROP TABLE IF EXISTS artificial_edges;
	CREATE TEMP TABLE artificial_edges AS   
	SELECT * 
	FROM basic.create_artificial_edges(basic.query_edges_routing(ST_ASTEXT(buffer_starting_point),modus,scenario_id,speed,routing_profile,FALSE),point, 
		snap_distance_network, max_new_node_id, max_new_edge_id 
	); 
		
	RETURN query EXECUTE 
	'SELECT 0, 0, 0, 0, 0, 0, NULL,''[[1.1,1.1],[1.1,1.1]]''::json, $1, $2
	 UNION ALL ' || 
	basic.query_edges_routing(ST_ASTEXT(buffer_network),modus,scenario_id,speed,routing_profile,True) || 
    ' AND id NOT IN (SELECT wid FROM artificial_edges)
	UNION ALL 
	SELECT id, source, target, ST_LENGTH(ST_TRANSFORM(geom, 3857)) AS length_3857, cost, reverse_cost, NULL AS death_end, ST_AsGeoJSON(ST_Transform(geom,3857))::json->''coordinates'', NULL AS starting_ids, NULL AS starting_geoms
	FROM artificial_edges' USING ARRAY[max_new_node_id]::integer[], ARRAY[ST_ASTEXT(point)]::TEXT[];

END;
$function$;

/*Fetches the routing network
SELECT * 
FROM basic.fetch_network_routing(ARRAY[11.543274],ARRAY[48.195524], 1200., 1.33, 'default', 1, 'walking_standard')
*/