DROP FUNCTION IF EXISTS PropagateInsert;
CREATE FUNCTION PropagateInsert(poi_id int, user_id int) RETURNS void AS
$BODY$
DECLARE
	insert_buffer geometry;
	network_chunk_query TEXT;
BEGIN
	
	-- area that's influenced by the insert
	insert_buffer =
		st_buffer(geom, 0.01)
		FROM pois_userinput
		WHERE gid = poi_id;
	
	-- mark cells that need updating
	UPDATE grid_500 SET dirty = TRUE
   	WHERE st_contains(insert_buffer, grid_500.geom);
   
    -- will be used for routing to get the cost from cells to new point
    network_chunk_query = fetch_ways_routing_text(st_astext(insert_buffer), 1, 1, 'walking_standard');
	
   	--DEBUG: save the chunk.
	--DROP TABLE IF EXISTS chunk;
	--EXECUTE concat('CREATE TABLE chunk AS ', network_chunk_query);
   
    -- TODO: Max snapping distance for cells
    -- sources: influenced cells  / corresponding nodes in the network
    -- target: the inserted point / corresponding node in the network
	WITH  source_target_nodes AS (
		SELECT source_nodes.id AS source_nodes, grid_id AS source_ids, target_node.id AS target_node, poi_id AS target_id
   		FROM (
			SELECT id, pois_userinput.gid FROM ways_vertices_pgr, pois_userinput  WHERE (NOT foot && ARRAY['use_sidepath','no'] OR foot IS NULL) ORDER BY ways_vertices_pgr.geom
			<->
    		(select geom from pois_userinput where gid = poi_id)
			LIMIT 1 
		) AS target_node	
		CROSS JOIN (
			SELECT grid_id, vertices.id
			FROM grid_500 g
			CROSS JOIN LATERAL
	  		(
	  			SELECT geom, id
	   			FROM ways_vertices_pgr w
				WHERE w.geom && ST_Buffer(g.centroid,0.002) AND g.dirty = TRUE AND (NOT foot && ARRAY['use_sidepath','no'] OR foot IS NULL)
	   			ORDER BY
	    		g.centroid <-> w.geom
	   			LIMIT 1
	   		) AS vertices
		) AS source_nodes
	),

	-- costs from sources to target
	routes AS (
		SELECT (pgr_astar(network_chunk_query, source_nodes::int4, target_node::int4, FALSE, FALSE)).cost, source_nodes, target_node, source_ids, target_id
		FROM source_target_nodes
		UNION ALL
		-- append manually very low cost in case cell and poi share the same node in the network (routing is null then)
		SELECT 0.0001, source_nodes, target_node, source_ids, target_id
		FROM source_target_nodes
		WHERE source_nodes = target_node
	)
	
	-- insert rows into reached points. Group by source nodes, because one route from a source node consists of multiple segments (a route is a sequence of traversed nodes with individual costs)
	-- there is an index on cell_id and object id. 
	--TODO: update cost on conflict -- actually there shouldn't be conflicts when inserting a poi in the frontend
	INSERT INTO reached_points (cost, cell_id, object_id, user_id, scenario)
	SELECT sum(cost) AS cost, source_ids AS cell_id, target_id AS object_id, PropagateInsert.user_id AS user_id, 1 AS scenario
	FROM routes
	GROUP BY source_nodes, source_ids, target_id;

/*
	-- impedanced cost, insert weight			-- impedance function. parameters to use are stored in designated table.										
   	UPDATE reached_points SET cost_sensitivity = SensitivityFunction(cost, amenity_alpha_weights.alpha), weight = amenity_alpha_weights.weight
   	FROM grid_500, amenity_alpha_weights, pois_userinput
    WHERE grid_id = reached_points.cell_id AND dirty = TRUE AND amenity_alpha_weights.amenity = pois_userinput.amenity AND object_id = gid;
	
    -- insert impedance cost * weight
   	UPDATE reached_points SET weighted_by_amenity = cost_sensitivity * weight
    WHERE object_id = poi_id;
	
    -- update accessibility in grid_500 in influenced cells
    UPDATE grid_500 SET poi_walkability_index = sum
	FROM (	
		SELECT sum(weighted_by_amenity), cell_id
		FROM (SELECT weighted_by_amenity, cell_id FROM reached_points t1 LEFT JOIN pois_modified t2 ON t1.object_id=t2.original_id WHERE t2.original_id IS NULL) AS without_modified
		GROUP BY cell_id
	) AS sum_per_cells
	WHERE cell_id = grid_id;
   */
   
	-- cells are done updating, unmark them
	UPDATE grid_500 SET dirty = FALSE
	WHERE dirty = TRUE;

    return;
END;
$BODY$ LANGUAGE plpgsql;



		EXPLAIN ANALYZE
		SELECT sum(weighted_by_amenity), cell_id
		FROM reached_points r, grid_500
		LEFT JOIN pois_modified ON r.object_id=pois_modified.original_id
		WHERE grid_id = cell_id AND pois_modified.original_id IS NULL --AND dirty = TRUE
		GROUP BY cell_id
		
		
		EXPLAIN ANALYZE
		SELECT sum(weighted_by_amenity), cell_id
		FROM reached_points, grid_500
		WHERE grid_id = cell_id --AND dirty = TRUE
		GROUP BY cell_id

		CREATE TABLE reached_points_excluding_modified AS
		SELECT weighted_by_amenity, cell_id FROM reached_points t1 LEFT JOIN pois_modified t2 ON t1.object_id=t2.original_id WHERE t2.original_id IS NULL
		
----------------------------------------------------------------------------
/*
SELECT PropagateInsert(4132)


DELETE FROM reached_points
WHERE object_id = 4132;
UPDATE grid_500 SET dirty = FALSE;
UPDATE grid_500 SET poi_walkability_index = NULL;

UPDATE amenity_alpha_weights SET weight = 0
WHERE amenity != 'primary_school';

  
SELECT grid_id, poi_walkability_index
FROM grid_500
WHERE poi_walkability_index IS NOT NULL
ORDER BY poi_walkability_index DESC


SELECT gid, pois_userinput.amenity
FROM pois_userinput, amenity_alpha_weights
WHERE pois_userinput.amenity = amenity_alpha_weights.amenity


WITH txt AS (
	SELECT fetch_ways_routing(st_astext(st_buffer(geom, 1)), 1, 1, 'walking_standard')
	FROM pois
	WHERE gid = 225
),
routes AS (
	SELECT (pgr_astar(txt.fetch_ways_routing_text, source_nodes::int4, target_node::int4, FALSE, FALSE)).cost, source_nodes, target_node, source_ids, target_id
	FROM txt, source_target_nodes
)

SELECT sum(cost) AS cost, source_ids AS cell_id, target_id AS object_id
FROM routes
GROUP BY source_nodes, source_ids, target_id

SELECT  pgr_costresult.cost FROM  pgr_costresult;



select fetch_ways_routing_text(ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.01)),1,1,'walking_standard');
DROP TABLE IF EXISTS chunk;



CREATE TABLE chunk AS
SELECT id::integer, source, target,length_m as cost, length_m as reverse_cost,slope_profile,death_end, st_x(st_startpoint(geom)) AS x1, st_y(st_startpoint(geom)) AS y1, st_x(st_endpoint(geom)) AS x2, st_y(st_endpoint(geom)) AS y2, geom  
		FROM ways WHERE NOT class_id = ANY('{0,101,102,103,104,105,106,107,501,502,503,504,701,801}')
    	AND (NOT foot = ANY('{use_sidepath,no}') 
		OR foot IS NULL)
		 AND geom && ST_GeomFromText('POLYGON((11.2465718 48.1724684,11.246379652804 48.1705174967798,11.2458105953251 48.1686415656763,11.244886496123 48.1669126976698,11.2436428678119 48.1653973321881,11.2421275023302 48.164153703877,11.2403986343237 48.1632296046749,11.2385227032202 48.162660547196,11.2365718 48.1624684,11.2346208967798 48.162660547196,11.2327449656763 48.1632296046749,11.2310160976698 48.164153703877,11.2295007321881 48.1653973321881,11.228257103877 48.1669126976698,11.2273330046749 48.1686415656763,11.226763947196 48.1705174967798,11.2265718 48.1724684,11.226763947196 48.1744193032202,11.2273330046749 48.1762952343237,11.228257103877 48.1780241023302,11.2295007321881 48.1795394678119,11.2310160976698 48.180783096123,11.2327449656763 48.1817071953251,11.2346208967798 48.182276252804,11.2365718 48.1824684,11.2385227032202 48.182276252804,11.2403986343237 48.1817071953251,11.2421275023302 48.180783096123,11.2436428678119 48.1795394678119,11.244886496123 48.1780241023302,11.2458105953251 48.1762952343237,11.246379652804 48.1744193032202,11.2465718 48.1724684))')



CREATE TABLE _txt AS
	SELECT fetch_ways_routing_text(st_astext(st_buffer(geom, 0.01)), 1, 1, 'walking_standard')
	FROM pois
	WHERE gid = 225

EXECUTE txt.fetch_ways_routing_text


	SELECT fetch_ways_routing_text(st_astext(st_buffer(geom, 0.01)), 1, 1, 'walking_standard')
	FROM pois
	WHERE gid = 225

	
	
	UPDATE reached_points SET cost_sensitivity = SensitivityFunction(cost, amenity_alpha_weights.alpha), weight = amenity_alpha_weights.weight
   	FROM amenity_alpha_weights, pois_userinput
	WHERE amenity_alpha_weights.amenity = pois_userinput.amenity AND object_id = gid;




SELECT pgr_astar(

(
	SELECT fetch_ways_routing_text(st_astext(st_buffer(geom, 0.01)), 1, 1, 'walking_standard')
	FROM pois_userinput
	WHERE gid = 4132
)

, 5672, 13043, FALSE, FALSE)

*/