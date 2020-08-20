CREATE OR REPLACE FUNCTION public.pgrouting_edges_multi_new(cutoffs float[], startpoints float[][], speed numeric, number_isochrones integer, userid_input integer, objectid_input integer[], modus_input integer, routing_profile text)
 RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE 
	buffer text;
	distance numeric;
	number_calculation_input integer;
	vids bigint[];
BEGIN
	
	SELECT *
	INTO vids
	FROM pgrouting_edges_preparation(cutoffs, startpoints, speed, userid_input, modus_input, routing_profile);

	DROP TABLE IF EXISTS reached_edges; 

	CREATE TEMP TABLE reached_edges AS 
	SELECT objectid_input[999999999-p.from_v], p.edge, p.start_perc, p.end_perc, greatest(start_cost,end_cost) AS COST, start_cost, end_cost
	FROM pgr_isochrones(
		'SELECT * FROM temp_fetched_ways WHERE id NOT IN(SELECT wid FROM start_vertices)', 
		vids, cutoffs,TRUE
	) p;

	
END;
$function$;




SELECT public.pgrouting_edges_multi_new(ARRAY[300.,600.,900.], array_agg(starting_points) , 
1.33, 2, 1, 15, 1, 'walking_standard')
FROM grid_ordered 
LIMIT 531

CREATE TABLE grid_ordered AS 
SELECT starting_points, grid_id
FROM (
    SELECT ARRAY[ST_X(st_centroid(geom))::numeric,ST_Y(ST_Centroid(geom))::numeric] starting_points, grid_id 
    FROM grid_500 
    ORDER BY st_centroid(geom)
) x