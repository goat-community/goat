DROP FUNCTION IF EXISTS get_reached_network;
CREATE OR REPLACE FUNCTION public.get_reached_network(objectid_input integer,max_cost numeric)
RETURNS void AS
$$
BEGIN
	INSERT INTO edges(edge,node,cost,geom,v_geom,objectid) 
	SELECT w.id,s.node,s.cost,w.geom,s.geom AS v_geom,objectid_input
	FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
	WHERE f.node = w.source 
	AND s.node = w.target;
		
	INSERT INTO edges 
	SELECT x.id AS edge, x.node, max_cost AS cost, ST_LINE_SUBSTRING(x.geom,1-((max_cost-x.agg_cost)/x.cost),1) AS geom,
	ST_STARTPOINT(ST_LINE_SUBSTRING(x.geom,1-((max_cost-x.agg_cost)/x.cost),1)) AS v_geom, objectid_input 
	FROM 
	(
		SELECT w.id, v.node, v.cost agg_cost, w.cost, w.geom
		FROM temp_reached_vertices v, temp_fetched_ways w
		WHERE v.node = w.target
		AND w.death_end IS NULL 
	) x
	LEFT JOIN (SELECT edge FROM edges e WHERE e.objectid = objectid_input) e
	ON x.id = e.edge 
	WHERE e.edge IS NULL
	UNION ALL 
	SELECT x.id AS edge, x.node, max_cost AS cost, ST_LINE_SUBSTRING(x.geom,0,((max_cost-x.agg_cost)/x.cost)) AS geom,
	ST_ENDPOINT(ST_LINE_SUBSTRING(x.geom,0,(max_cost-x.agg_cost)/x.cost)) AS v_geom, objectid_input 
	FROM 
	(
		SELECT w.id, v.node, v.cost agg_cost, w.cost, w.geom 
		FROM temp_reached_vertices v, temp_fetched_ways w
		WHERE v.node = w.source
		AND w.death_end IS NULL 
	) x
	LEFT JOIN (SELECT edge FROM edges e WHERE e.objectid = objectid_input) e
	ON x.id = e.edge 
	WHERE e.edge IS NULL
	UNION ALL
	SELECT w.id AS edge,v.node,CASE WHEN w.SOURCE = v.node THEN v.cost + w.cost ELSE v.cost + w.reverse_cost END AS cost, 
	w.geom,CASE WHEN w.source = v.node THEN ST_ENDPOINT(w.geom) ELSE ST_STARTPOINT(w.geom) END AS v_geom,objectid_input
	FROM temp_reached_vertices v, temp_fetched_ways w 
	WHERE v.death_end = TRUE 
	AND v.node = w.death_end
	AND w.cost < (max_cost-v.cost);
END;
$$ LANGUAGE plpgsql;