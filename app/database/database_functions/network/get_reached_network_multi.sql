DROP FUNCTION IF EXISTS get_reached_network_multi;
CREATE OR REPLACE FUNCTION public.get_reached_network_multi(objectid_input integer[],max_cost NUMERIC, number_isochrones integer, edges_to_exclude bigint[])
RETURNS void AS
$$
DECLARE
	i NUMERIC;
	step_isochrone NUMERIC := max_cost/number_isochrones;
BEGIN
	INSERT INTO edges_multi(edge,node,cost,geom,v_geom,objectid) 
	SELECT w.id,s.node,CASE WHEN s.cost > f.cost THEN s.cost ELSE f.cost END AS cost,w.geom,s.geom AS v_geom,objectid_input
	FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
	WHERE f.node = w.source 
	AND s.node = w.target;
	
	
	FOR i IN SELECT generate_series(step_isochrone,max_cost,step_isochrone)
	LOOP
		INSERT INTO edges_multi 
		SELECT x.id AS edge, x.node, i AS cost, ST_LINE_SUBSTRING(x.geom,1-((i-x.agg_cost)/x.cost),1) AS geom,
		ST_STARTPOINT(ST_LINE_SUBSTRING(x.geom,1-((i-x.agg_cost)/x.cost),1)) AS v_geom, objectid_input 
		FROM 
		(
			SELECT w.id, v.node, v.cost agg_cost, w.cost, w.geom
			FROM temp_reached_vertices v, temp_fetched_ways w
			WHERE v.node = w.target
			AND w.death_end IS NULL 
			AND v.cost < i
		) x
		LEFT JOIN (SELECT edge FROM edges_multi e WHERE e.objectid = objectid_input AND cost < i) e
		ON x.id = e.edge 
		WHERE e.edge IS NULL
		AND x.id NOT IN(SELECT UNNEST(edges_multi_to_exclude))
		UNION ALL 
		SELECT x.id AS edge, x.node, i AS cost, ST_LINE_SUBSTRING(x.geom,0,((i-x.agg_cost)/x.cost)) AS geom,
		ST_ENDPOINT(ST_LINE_SUBSTRING(x.geom,0,(i-x.agg_cost)/x.cost)) AS v_geom, objectid_input 
		FROM 
		(
			SELECT w.id, v.node, v.cost agg_cost, w.cost, w.geom 
			FROM temp_reached_vertices v, temp_fetched_ways w
			WHERE v.node = w.source
			AND w.death_end IS NULL 
			AND v.cost < i
		) x
		LEFT JOIN (SELECT edge FROM edges_multi e WHERE e.objectid = objectid_input AND cost < i) e
		ON x.id = e.edge 
		WHERE e.edge IS NULL
		AND x.id NOT IN(SELECT UNNEST(edges_multi_to_exclude));
	
	END LOOP;
	
	INSERT INTO edges_multi	
	SELECT w.id AS edge,v.node,CASE WHEN w.SOURCE = v.node THEN v.cost + w.cost ELSE v.cost + w.reverse_cost END AS cost, 
	w.geom,CASE WHEN w.source = v.node THEN ST_ENDPOINT(w.geom) ELSE ST_STARTPOINT(w.geom) END AS v_geom,objectid_input
	FROM temp_reached_vertices v, temp_fetched_ways w 
	WHERE v.death_end = TRUE 
	AND v.node = w.death_end
	AND w.cost < (max_cost-v.cost);
	
END;
$$ LANGUAGE plpgsql;


WITH x AS (
	SELECT w.id,s.node,CASE WHEN s.min_cost > f.min_cost THEN s.min_cost ELSE f.min_cost END AS min_cost,
	w.geom,s.geom AS v_geom,1, 
	CASE WHEN f.objectids <> s.objectids 
	THEN array_intersect(f.objectids,s.objectids)::text[] END AS objectids_intersect, 
	f.node_cost f_node_cost,s.node_cost s_node_cost
	FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
	WHERE f.node = w.source 
	AND s.node = w.target
)
SELECT x.id,x.node,x.min_cost,
x.geom,x.v_geom,1,get_unique_max_jsonb(f_node_cost,s_node_cost,objectids_intersect::text[])
FROM x 
WHERE objectids_intersect IS NOT NULL 


SELECT w.id,s.node,CASE WHEN s.min_cost > f.min_cost THEN s.min_cost ELSE f.min_cost END AS min_cost,
w.geom,s.geom AS v_geom,1,f.node_cost f_node_cost,s.node_cost s_node_cost, 
CASE WHEN f.objectids <> s.objectids THEN (f.node_cost||s.node_cost)- 
(	
	CASE WHEN f.objectids < s.objectids THEN array_substraction(s.objectids,f.objectids)::text[] 
	ELSE array_substraction(f.objectids,s.objectids)::text[] END
)
ELSE s.node_cost END AS node_cost
FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
WHERE f.node = w.source 
AND s.node = w.target

EXPLAIN ANALYZE
SELECT w.id,s.node,CASE WHEN s.min_cost > f.min_cost THEN s.min_cost ELSE f.min_cost END AS min_cost,
w.geom,s.geom AS v_geom,1,f.node_cost f_node_cost,s.node_cost s_node_cost
FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
WHERE f.node = w.source 
AND s.node = w.target
AND (s.node_cost ->> '1') IS NOT NULL 
AND (f.node_cost ->> '1') IS NOT NULL 




EXPLAIN ANALYZE 
SELECT w.id,s.node,CASE WHEN s.min_cost > f.min_cost THEN s.min_cost ELSE f.min_cost END AS min_cost,
w.geom,s.geom AS v_geom,1,
CASE WHEN f.objectids <> s.objectids THEN f.node_cost - 
(	
	CASE WHEN array_length(f.objectids,1) < array_length(s.objectids,1) THEN (s.objectids - f.objectids)::text[] 
	ELSE array_substraction(f.objectids,s.objectids)::text[] END
) 
ELSE f.node_cost END AS node_cost1,
CASE WHEN f.objectids <> s.objectids THEN s.node_cost - 
(	
	CASE WHEN array_length(f.objectids,1) < array_length(s.objectids,1) THEN (s.objectids - f.objectids)::text[] 
	ELSE array_substraction(f.objectids,s.objectids)::text[] END
)
ELSE s.node_cost END AS node_cost_2
FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
WHERE f.node = w.source 
AND s.node = w.target