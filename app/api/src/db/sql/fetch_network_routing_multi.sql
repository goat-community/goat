CREATE OR REPLACE FUNCTION basic.fetch_network_routing_multi(x float[], y float[], max_cutoff float, speed float, modus text, scenario_id integer, routing_profile text)
 RETURNS SETOF type_fetch_edges_routing
 LANGUAGE plpgsql
AS $function$
DECLARE 
	union_buffer_network geometry;
BEGIN 
	
	PERFORM basic.create_multiple_artificial_edges(x, y, max_cutoff, speed, modus, scenario_id, routing_profile);
	union_buffer_network  = (SELECT ST_UNION(geom) FROM buffer_network);
	
	/*Fetch Network*/
	RETURN query EXECUTE 
	'SELECT 1, 1, 1, 1, 1, 1, NULL, ''[[1.1,1.1],[1.1,1.1]]''::json, $1, $2
	 UNION ALL ' || 
	basic.query_edges_routing(ST_ASTEXT(union_buffer_network),modus,scenario_id,speed,routing_profile,True) || 
    ' AND id NOT IN (SELECT wid FROM artificial_edges)
	UNION ALL 
	SELECT id, source, target, ST_LENGTH(ST_TRANSFORM(geom, 3857)) AS length_3857, cost, reverse_cost, NULL AS death_end, ST_AsGeoJSON(ST_Transform(geom,3857))::json->''coordinates'', NULL AS starting_ids, NULL AS starting_geoms
	FROM artificial_edges' USING (SELECT array_agg(s.id) FROM starting_vertices s), (SELECT array_agg(ST_ASTEXT(s.geom)) FROM starting_vertices s); 

END;
$function$;

/*
WITH p AS 
(
	SELECT geom
	FROM basic.poi 
	LIMIT 100
),
agg AS 
(
	SELECT array_agg(ST_X(geom)) AS x, array_agg(ST_Y(geom)) AS y
	FROM p  
)
SELECT n.* 
FROM agg, 
LATERAL basic.fetch_network_routing_multi(x,y, 1200., 1.33, 'default', 1, 'walking_standard') n 
*/