CREATE OR REPLACE FUNCTION basic.create_multiple_artificial_edges(x float[], y float[], max_cutoff float, speed float, modus text, scenario_id integer, 
routing_profile text, grid_ids text[] DEFAULT NULL)
 RETURNS VOID 
 LANGUAGE plpgsql
AS $function$
DECLARE 
	buffer_starting_point geometry; 
	union_buffer_network geometry;
	point geometry; 
	snap_distance_network integer;
	cnt_starting_points integer := 0;
	length_starting_points integer := array_length(x, 1);
	max_new_node_id integer := 2147483647;
	max_new_edge_id integer := 2147483647;
	current_grid_id text;
	setting_study_area_id integer;
BEGIN 
	/*Prepare temporary tables*/
	DROP TABLE IF EXISTS artificial_edges; 
	CREATE TEMP TABLE artificial_edges (
		wid integer, 
		id integer, 
		COST float, 
		reverse_cost float, 
		length_m float, 
		SOURCE integer, 
		target integer, 
		fraction float, 
		geom geometry, 
		vid integer, 
		point_geom geometry,
		grid_id text
	); 
	
	setting_study_area_id = basic.get_reference_study_area(ST_SETSRID(ST_MAKEPOINT(x[1], y[1]), 4326));
	snap_distance_network = basic.select_customization('snap_distance_network', setting_study_area_id)::integer;

	DROP TABLE IF EXISTS duplicated_artificial_edges; 
	CREATE TEMP TABLE duplicated_artificial_edges (LIKE artificial_edges); 

	DROP TABLE IF EXISTS buffer_network; 
	CREATE TEMP TABLE buffer_network (id serial, geom geometry);
	
	/*Loop through starting points*/
	WHILE cnt_starting_points < length_starting_points 
	LOOP
		cnt_starting_points = cnt_starting_points + 1;
		IF grid_ids IS NOT NULL THEN
			current_grid_id = grid_ids[cnt_starting_points];
		ELSE
			current_grid_id = NULL;
		END IF;
		
		point = ST_SETSRID(ST_POINT(x[cnt_starting_points],y[cnt_starting_points]), 4326);
		
		SELECT ST_SETSRID(ST_Buffer(point::geography,snap_distance_network)::geometry, 4326)
		INTO buffer_starting_point;	
		
		INSERT INTO artificial_edges
		SELECT c.*, max_new_node_id, point AS point_geom, current_grid_id  
		FROM basic.create_artificial_edges(basic.query_edges_routing(ST_ASTEXT(buffer_starting_point),modus,scenario_id,speed,routing_profile,FALSE),
			point, snap_distance_network, max_new_node_id, max_new_edge_id  
		) c; 

		INSERT INTO buffer_network(geom) 
		SELECT ST_Buffer(point::geography,max_cutoff * speed)::geometry;
		
		max_new_node_id = max_new_node_id - 1;
		max_new_edge_id = max_new_edge_id - 2; 
	END LOOP; 
	
	union_buffer_network  = (SELECT ST_UNION(b.geom) FROM buffer_network b);
	
	DROP TABLE IF EXISTS starting_vertices; 
	CREATE TEMP TABLE starting_vertices (id integer, geom geometry, grid_id text);

	/*Identify duplicates and unique artificial edges */
	DROP TABLE IF EXISTS final_artificial_edges; 
	CREATE TEMP TABLE final_artificial_edges AS 
	WITH cnt_artificial_edges AS 
	(
		SELECT a.wid, count(*)::integer AS cnt 
		FROM artificial_edges a  
		GROUP BY a.wid
	),	
	not_duplicates AS 
	(
		SELECT a.wid, a.vid, a.id, a.COST, a.reverse_cost, a.length_m, a.SOURCE, a.target, a.geom, a.point_geom, a.grid_id  
		FROM artificial_edges a, cnt_artificial_edges c
		WHERE a.wid = c.wid 
		AND c.cnt <= 2
	),
	insert_not_duplicates AS 
	(
		INSERT INTO starting_vertices 
		SELECT DISTINCT n.vid, n.point_geom, n.grid_id 
		FROM not_duplicates n 	
	),
	insert_duplicates AS 
	(
		INSERT INTO duplicated_artificial_edges
		SELECT a.* 
		FROM artificial_edges a, cnt_artificial_edges c
		WHERE a.wid = c.wid 
		AND c.cnt > 2 
	)
	SELECT n.wid, n.id, n.COST, n.reverse_cost, n.length_m, n.SOURCE, n.target, n.geom, n.point_geom, n.grid_id  
	FROM not_duplicates n; 
	
	/*Handle duplicated artificial edges*/
	DROP TABLE IF EXISTS cleaned_duplicates; 
	CREATE TEMP TABLE cleaned_duplicates AS 
	WITH sum_costs AS 
	(
		SELECT d.vid, round(SUM(d.COST::numeric), 4) AS cost, round(SUM(d.reverse_cost::numeric), 4) AS reverse_cost
		FROM duplicated_artificial_edges d 
		GROUP BY d.vid
	),
	ordered AS 
	(
		SELECT DISTINCT d.wid, d.vid, d.fraction, s.COST, s.reverse_cost, d.point_geom, d.grid_id  
		FROM duplicated_artificial_edges d, sum_costs s  
		WHERE d.vid = s.vid 
		AND d.fraction NOT IN (0,1)
		ORDER BY d.wid, d.fraction 
	),
	insert_distinct_starting_points AS 
	(
		INSERT INTO starting_vertices 
		SELECT o.vid, o.point_geom, o.grid_id  
		FROM ordered o
	),
	grouped AS 
	(	
		SELECT g.wid, array_agg(g.vid) vids, array_agg(g.fraction) fractions
		FROM ordered g  
		GROUP BY g.wid
	),
	distinct_costs AS 
	(
		SELECT DISTINCT o.wid, o.COST, o.reverse_cost
		FROM ordered o
	),
	distinct_duplicated_edges AS 
	(
		SELECT g.wid, o.COST, o.reverse_cost, g.vids, g.fractions, e.SOURCE, e.target, e.geom
		FROM grouped g
		LEFT JOIN distinct_costs o
		ON g.wid = o.wid 
		LEFT JOIN basic.edge e 
		ON g.wid = e.id 
	)
	SELECT edge_id AS wid, (max_new_edge_id - ROW_NUMBER() OVER()) AS id, f.COST, f.reverse_cost,
	ST_LENGTH(f.geom::geography) AS length_m, f.SOURCE, f.target, f.geom, NULL AS point_geom  
	FROM distinct_duplicated_edges d, 
	LATERAL basic.fix_multiple_artificial_edges(d.wid, d.SOURCE, d.target, d.COST, d.reverse_cost, d.geom, d.vids, d.fractions) f; 
	
	UPDATE cleaned_duplicates d
	SET point_geom = s.geom 
	FROM starting_vertices s  
	WHERE d.SOURCE = s.id;

	UPDATE cleaned_duplicates d
	SET point_geom = s.geom 
	FROM starting_vertices s  
	WHERE d.target = s.id;

	INSERT INTO final_artificial_edges 
	SELECT * FROM cleaned_duplicates; 

END;
$function$;

/*
WITH p AS 
(
	SELECT ST_CENTROID(geom) AS geom 
	FROM basic.grid_calculation
	LIMIT 10
),
agg AS 
(
	SELECT array_agg(ST_X(geom)) AS x, array_agg(ST_Y(geom)) AS y
	FROM p  
)
SELECT basic.create_multiple_artificial_edges(x, y, 1200., 1.33, 'default', 1, 'walking_standard') a
FROM agg 
*/