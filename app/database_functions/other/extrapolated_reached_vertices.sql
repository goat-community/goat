DROP TABLE IF EXISTS temp_reached_vertices;
CREATE temp TABLE temp_reached_vertices
(
	start_vertex integer,
	node integer,
	edge integer,
	cost NUMERIC,
	geom geometry,
	objectid integer
);

CREATE OR REPLACE FUNCTION public.extrapolate_reached_vertices(max_cost NUMERIC, excluded_class_id integer[], categories_no_foot text[])
RETURNS SETOF type_catchment_vertices
 LANGUAGE sql
AS $function$

WITH touching_network AS 
(
	SELECT * FROM (
		SELECT t.start_vertex, w.id, w.geom, w.SOURCE, w.target, t.cost, t.node, t.edge, w.length_m, t.objectid, w.class_id, w.foot  
		FROM temp_reached_vertices t, ways w
		WHERE t.node = w.target 
		AND t.node <> w.SOURCE
		UNION ALL 
		SELECT t.start_vertex, w.id, w.geom, w.SOURCE, w.target, t.cost, t.node, t.edge, w.length_m, t.objectid, w.class_id, w.foot 
		FROM temp_reached_vertices t, ways w
		WHERE t.node <> w.target 
		AND t.node = w.SOURCE
	
	) x
	WHERE NOT x.class_id = ANY(excluded_class_id)
	AND (NOT x.foot = any(categories_no_foot) OR x.foot IS NULL)
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
SELECT t.start_vertex::integer, 99999999 AS node, t.id::integer edges, max_cost AS cost, st_startpoint(st_linesubstring(geom,1-(max_cost-cost)/length_m,1)) geom, objectid 
FROM touching_network t, not_completely_reached_network n 
WHERE t.SOURCE = n.source 
AND 1-(max_cost-cost)/t.length_m BETWEEN 0 AND 1
UNION ALL 
SELECT t.start_vertex::integer, 99999999 AS node, t.id::integer, max_cost AS cost, st_endpoint(st_linesubstring(geom,0.0,(max_cost-cost)/length_m)) geom, objectid
FROM touching_network t, not_completely_reached_network n
WHERE t.target = n.source 
AND (max_cost-cost)/t.length_m BETWEEN 0 AND 1 
UNION ALL 
SELECT * FROM temp_reached_vertices;

$function$;