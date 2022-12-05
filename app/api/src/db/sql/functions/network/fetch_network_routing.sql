CREATE OR REPLACE FUNCTION basic.heatmap_prepare_artificial(x float[], y float[], max_cutoff float, speed float, modus text, scenario_id integer, routing_profile text)
 RETURNS void
 LANGUAGE plpgsql
AS $function$

BEGIN 

	PERFORM basic.create_multiple_artificial_edges(x, y, max_cutoff, speed, modus, scenario_id, routing_profile);
	
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
 * SELECT basic.heatmap_prepare_artificial(ARRAY[11.5828], ARRAY[48.2726], 1200., 1.33, 'default', 1, 'walking_standard'); 
 */