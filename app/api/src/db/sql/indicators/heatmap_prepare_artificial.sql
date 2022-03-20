CREATE OR REPLACE FUNCTION basic.heatmap_prepare_artificial(grid_helper_classes integer[])
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE 
	x float[];
	y float[]; 
BEGIN 
	WITH p AS 
	(
		SELECT ST_CENTROID(c.geom) AS geom 
		FROM temporal.heatmap_grid_helper h, basic.grid_calculation c 
		WHERE cid IN (SELECT UNNEST(grid_helper_classes))
		AND h.id = c.grid_visualization_id 
	)
	SELECT array_agg(ST_X(geom)) AS x, array_agg(ST_Y(geom)) AS y
	FROM p
	INTO x, y; 

	PERFORM basic.create_multiple_artificial_edges(x, y, 1200., 1.33, 'default', 1, 'walking_standard'); 
	
	
	DROP TABLE IF EXISTS temporal.heatmap_edges_artificial; 
	CREATE TABLE temporal.heatmap_edges_artificial AS
	SELECT * FROM final_artificial_edges;
	ALTER TABLE temporal.heatmap_edges_artificial ADD PRIMARY KEY(id);
	CREATE INDEX ON temporal.heatmap_edges_artificial USING GIST(geom);
	
	DROP TABLE IF EXISTS temporal.heatmap_starting_vertices; 
	CREATE TABLE temporal.heatmap_starting_vertices AS
	SELECT * FROM starting_vertices;
	CREATE INDEX ON temporal.heatmap_starting_vertices USING GIST(geom);

END;
$function$;
/*
 * SELECT basic.heatmap_prepare_artificial(ARRAY[1,2,3,4])
 */