CREATE OR REPLACE FUNCTION public.bulk_closest_edges()
 RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
BEGIN	
	DROP TABLE IF EXISTS start_vertices;
	CREATE TEMP TABLE start_vertices AS 
	SELECT g.grid_id, g.section_id, CASE WHEN fraction = 0 THEN SOURCE 
	WHEN fraction = 1 THEN target 
	ELSE 999999999 - g.id END AS vid, 
	c.id wid, c.SOURCE, c.target, c.COST, c.reverse_cost, c.fraction, c.w_geom w_geom, c.closest_point
	FROM grid_ordered g
	CROSS JOIN LATERAL
	(
		SELECT w.id, w.SOURCE, w.target, w.COST, w.reverse_cost, w.geom w_geom,ST_CLOSESTPOINT(w.geom,g.centroid) AS closest_point,ST_LineLocatePoint(geom,g.centroid) AS fraction
	    FROM fetched_ways_bulk w
	    WHERE w.geom && ST_Buffer(g.centroid,0.0018)
	    ORDER BY ST_CLOSESTPOINT(w.geom,g.centroid) <-> g.centroid
	    LIMIT 1
	) AS c;
	
    ALTER TABLE start_vertices ADD PRIMARY KEY(grid_id);

	DROP TABLE IF EXISTS duplicated_artificial_edges;
	CREATE TEMP TABLE duplicated_artificial_edges AS  
	WITH duplicated_ids AS 
	(
		SELECT count(wid), wid
		FROM start_vertices 
		WHERE fraction NOT IN (0,1)
		GROUP BY wid 
		HAVING count(wid) > 1
	),
	duplicated_with_attr AS 
	(
		SELECT c.wid, c.vid, c.SOURCE, c.target, c.COST, c.reverse_cost, c.w_geom, c.fraction
		FROM start_vertices c, duplicated_ids d 
		WHERE c.wid = d.wid 
		AND c.fraction NOT IN (0,1)
		ORDER BY w_geom, fraction
	)
	SELECT wid, SOURCE, target, COST, reverse_cost, w_geom, array_agg(vid) vids, array_agg(fraction) fractions
	FROM duplicated_with_attr 
	GROUP BY wid, SOURCE, target, COST, reverse_cost, w_geom;
	
	DROP TABLE IF EXISTS artificial_edges;
	CREATE TEMP TABLE artificial_edges AS 
	SELECT v.wid, 999999998-(1+ROW_NUMBER() OVER())*2 AS id, v.cost*v.fraction AS cost,v.reverse_cost*v.fraction AS reverse_cost,v.SOURCE,v.vid target,ST_LINESUBSTRING(v.w_geom,0,v.fraction) geom
	FROM start_vertices v
	WHERE v.wid NOT IN (SELECT wid FROM duplicated_artificial_edges)
	AND fraction NOT IN (0,1)
	UNION ALL 
	SELECT v.wid, 999999999-(1+ROW_NUMBER() OVER())*2 AS id, v.cost*(1-v.fraction) AS cost,v.reverse_cost*(1-v.fraction) AS reverse_cost,v.vid source,v.target,ST_LINESUBSTRING(v.w_geom,v.fraction,1) geom
	FROM start_vertices v 
	WHERE v.wid NOT IN (SELECT wid FROM duplicated_artificial_edges)
	AND fraction NOT IN (0,1);
	ALTER TABLE artificial_edges ADD PRIMARY KEY(id);
	PERFORM multiple_artificial_edges(wid,SOURCE,target,COST,reverse_cost,w_geom, vids, fractions)
	FROM duplicated_artificial_edges;
END;
$function$;
