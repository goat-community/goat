INSERT INTO edges(edge,cost,geom,v_geom,objectid) 
SELECT w.id, s.cost, w.geom,s.geom AS v_geom,999
FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
WHERE f.node = w.SOURCE 
AND s.node = w.target;


INSERT INTO edges 
SELECT x.id AS edge, 1800 AS cost, ST_LINE_SUBSTRING(x.geom,1-((1800-x.agg_cost)/x.cost),1) AS geom,
ST_STARTPOINT(ST_LINE_SUBSTRING(x.geom,1-((1800-x.agg_cost)/x.cost),1)) AS v_geom, 999 
FROM 
(
	SELECT w.id, v.cost agg_cost, w.cost, w.geom
	FROM temp_reached_vertices v, temp_fetched_ways w
	WHERE v.node = w.target
	AND w.death_end IS NULL 
) x
LEFT JOIN (SELECT edge FROM edges e WHERE e.objectid = 999) e
ON x.id = e.edge 
WHERE e.edge IS NULL
UNION ALL 
SELECT x.id AS edge, 1800 AS cost, ST_LINE_SUBSTRING(x.geom,0,((1800-x.agg_cost)/x.cost)) AS geom,
ST_STARTPOINT(ST_LINE_SUBSTRING(x.geom,0,(1800-x.agg_cost)/x.cost)) AS v_geom, 999 
FROM 
(
	SELECT w.id, v.cost agg_cost, w.cost, w.geom 
	FROM temp_reached_vertices v, temp_fetched_ways w
	WHERE v.node = w.source
	AND w.death_end IS NULL 
) x
LEFT JOIN (SELECT edge FROM edges e WHERE e.objectid = 999) e
ON x.id = e.edge 
WHERE e.edge IS NULL
UNION ALL
SELECT w.id AS edge, CASE WHEN w.SOURCE = v.node THEN v.cost + w.cost ELSE v.cost + w.reverse_cost END AS cost, 
w.geom,st_startpoint(w.geom),999
FROM temp_reached_vertices v, temp_fetched_ways w 
WHERE v.death_end = TRUE 
AND v.node = w.death_end
AND w.cost < (1800-v.cost);