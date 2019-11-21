DROP TABLE IF EXISTS temp_reached_vertices;
CREATE temp TABLE temp_reached_vertices
(
	start_vertex integer,
	node integer,
	edge integer,
	cnt integer,
	cost NUMERIC,
	geom geometry,
	objectid integer
);
DROP FUNCTION IF EXISTS extrapolate_reached_vertices;
CREATE OR REPLACE FUNCTION public.extrapolate_reached_vertices(max_cost NUMERIC, max_length_links NUMERIC, buffer_geom text, speed NUMERIC ,userid_input integer, modus_input integer,  routing_profile text )
RETURNS SETOF type_catchment_vertices
 LANGUAGE sql
AS $function$

WITH touching_network AS 
(
	SELECT t.start_vertex, w.id, w.geom, w.SOURCE, w.target, t.cost, t.node, t.edge, 1 as cnt, w.cost AS w_cost, t.objectid
	FROM temp_reached_vertices t, 
	fetch_ways_routing(buffer_geom,speed,modus_input,userid_input,routing_profile) as w 
	WHERE t.node = w.target 
	AND t.node <> w.SOURCE
	AND t.cost + (max_length_links/speed) > max_cost
	UNION ALL 
	SELECT t.start_vertex, w.id, w.geom, w.SOURCE, w.target, t.cost, t.node, t.edge, 1 as cnt, w.cost AS w_cost, t.objectid
	FROM temp_reached_vertices t, 
	fetch_ways_routing(buffer_geom,speed,modus_input,userid_input,routing_profile) as w 
	WHERE t.node <> w.target
	AND t.node = w.SOURCE
	AND t.cost + (max_length_links/speed) > max_cost
),
not_completely_reached_network AS (
	SELECT SOURCE 
	FROM (
		SELECT SOURCE 
		FROM touching_network t 
		UNION ALL 
		SELECT target 
		FROM touching_network t 
	) x
	GROUP BY x.source
	HAVING count(x.source) < 2
)
SELECT t.start_vertex::integer, 99999999 AS node, t.id::integer edges, t.cnt, max_cost AS cost, st_startpoint(st_linesubstring(geom,1-(max_cost-cost)/w_cost,1)) geom, st_linesubstring(geom,1-(max_cost-cost)/w_cost,1) as w_geom,objectid 
FROM touching_network t, not_completely_reached_network n 
WHERE t.SOURCE = n.source 
AND 1-(max_cost-cost)/w_cost BETWEEN 0 AND 1
UNION ALL 
SELECT t.start_vertex::integer, 99999999 AS node, t.id::integer edges, t.cnt, max_cost AS cost, st_endpoint(st_linesubstring(geom,0.0,(max_cost-cost)/w_cost)) geom,st_linesubstring(geom,0.0,(max_cost-cost)/w_cost) as w_geom, objectid
FROM touching_network t, not_completely_reached_network n
WHERE t.target = n.source 
AND (max_cost-cost)/w_cost BETWEEN 0 AND 1 
UNION ALL 
SELECT start_vertex, node, edge, 1 as cnt , cost, geom, null, objectid FROM temp_reached_vertices;

$function$;
