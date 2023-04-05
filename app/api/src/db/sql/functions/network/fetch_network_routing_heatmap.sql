		
CREATE OR REPLACE FUNCTION basic.fetch_network_routing_heatmap(
	x float[], y float[], max_cutoff float, speed float, modus text, 
	scenario_id integer, routing_profile TEXT, artificial_tables_prefix TEXT = 'worker1')
 RETURNS SETOF type_fetch_edges_routing
 LANGUAGE plpgsql
AS $function$
DECLARE 
	union_buffer_network geometry;
	cnt_starting_points integer := 0;
	length_starting_points integer := array_length(x, 1);
	point geometry;
	artificial_table_name TEXT := artificial_tables_prefix || '_' || 'heatmap_edges_artificial';
	vertices_table_name TEXT := artificial_tables_prefix || '_' || 'heatmap_starting_vertices';
BEGIN 
	
	PERFORM basic.create_multiple_artificial_edges(x, y, max_cutoff, speed, modus, scenario_id, routing_profile);
	
	DROP TABLE IF EXISTS buffer_network; 
	CREATE TEMP TABLE buffer_network (id serial, geom geometry);
	
	DROP TABLE IF EXISTS buffer_starting_points;
	CREATE TEMP TABLE buffer_starting_points(geom geometry);

	/*Loop through starting points*/
	WHILE cnt_starting_points < length_starting_points 
	LOOP
		cnt_starting_points = cnt_starting_points + 1;
		point = ST_SETSRID(ST_POINT(x[cnt_starting_points],y[cnt_starting_points]), 4326);
		
		INSERT INTO buffer_network(geom) 
		SELECT ST_Buffer(point::geography,max_cutoff * speed)::geometry;
		
		INSERT INTO buffer_starting_points(geom)
		SELECT ST_BUFFER(point, 0.000000001); 
	END LOOP; 
	
	CREATE INDEX ON buffer_starting_points USING GIST(geom); 

	union_buffer_network  = (SELECT ST_UNION(b.geom) FROM buffer_network b);

	DROP TABLE IF EXISTS batch_artificial_edges; 
	EXECUTE 'CREATE TEMP TABLE batch_artificial_edges AS
	SELECT *
	FROM temporal.'||artificial_table_name||' a
	WHERE ST_Intersects(a.geom, $1);' USING union_buffer_network; 
	
	DROP TABLE IF EXISTS batch_starting_vertices; 
	EXECUTE 'CREATE TEMP TABLE batch_starting_vertices AS
	SELECT v.*
	FROM temporal.'||vertices_table_name||' v, buffer_starting_points s  
	WHERE ST_Intersects(v.geom, s.geom);'; 
	
	EXECUTE 'DROP TABLE IF EXISTS temporal.'||artificial_table_name;
	EXECUTE 'DROP TABLE IF EXISTS temporal.'||vertices_table_name;

	/*Fetch Network*/
	RETURN query EXECUTE 
	'SELECT 1, 1, 1, 1, 1, 1, NULL, ''[[1.1,1.1],[1.1,1.1]]''::json, $1, $2
	 UNION ALL ' || 
	basic.query_edges_routing(ST_ASTEXT(union_buffer_network),modus,scenario_id,speed,routing_profile,True) || 
    ' AND id NOT IN (SELECT wid FROM batch_artificial_edges)
	UNION ALL 
	SELECT id, source, target, ST_LENGTH(ST_TRANSFORM(geom, 3857)) AS length_3857, cost, reverse_cost, 
	NULL AS death_end, ST_AsGeoJSON(ST_Transform(geom,3857))::json->''coordinates'', NULL AS starting_ids, NULL AS starting_geoms
	FROM batch_artificial_edges' USING (SELECT array_agg(s.id) FROM batch_starting_vertices s), (SELECT array_agg(ST_ASTEXT(s.geom)) FROM batch_starting_vertices s); 

END;
$function$;

/*
WITH p AS 
(
	SELECT ST_CENTROID(geom) geom 
	FROM temporal.heatmap_grid_helper h 
	WHERE cid = 0
),
agg AS 
(
	SELECT array_agg(ST_X(geom)) AS x, array_agg(ST_Y(geom)) AS y
	FROM p  
)
SELECT n.* 
FROM agg, 
LATERAL basic.fetch_network_routing_heatmap(x,y, 1200., 1.33, 'default', 1, 'walking_standard') n
*/