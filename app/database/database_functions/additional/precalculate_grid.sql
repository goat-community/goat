DROP FUNCTION IF EXISTS precalculate_grid;
CREATE OR REPLACE FUNCTION public.precalculate_grid(userid_input integer, objectid_input integer, grid text, minutes integer,array_starting_points NUMERIC[][],speed NUMERIC, ids_calc int[], modus_input integer,routing_profile text)
RETURNS SETOF type_catchment_vertices_single
LANGUAGE plpgsql
AS $function$
DECLARE 
	i integer;

	--new
	number_isochrones integer := 1;	
	calc_step integer := 900;	

BEGIN 

	DELETE FROM edges_multi;
	DELETE FROM edges_multi_extrapolated;
	PERFORM pgrouting_edges_multi(userid_input, minutes, array_starting_points, speed, number_isochrones, ids_calc, objectid_input, modus_input, routing_profile);

	FOREACH i IN ARRAY ids_calc
	LOOP 

		DROP TABLE IF EXISTS temp_extrapolated_reached_vertices;
		
		CREATE TEMP TABLE temp_extrapolated_reached_vertices AS
		SELECT v_geom AS geom, cost
   		FROM edges_multi_extrapolated
    	WHERE objectid = 100
    	AND cost = 900 
    	UNION ALL
    	SELECT v_geom AS geom, greatest(COALESCE((node_cost_1 -> '1')::float,0),
    	COALESCE((node_cost_2 -> '1')::float,0)) AS cost
    	FROM edges_multi
    	WHERE objectid = 100
    	AND	((node_cost_1 -> '1') IS NOT NULL OR (node_cost_2 -> '1') IS NOT NULL)
		AND greatest(COALESCE((node_cost_1 -> '1')::float,0),
    		COALESCE((node_cost_1 -> '1')::float,0)) < 900;
    	
    	CREATE INDEX ON temp_extrapolated_reached_vertices USING gist(geom);
    	ALTER TABLE temp_extrapolated_reached_vertices ADD COLUMN id serial;
		ALTER TABLE temp_extrapolated_reached_vertices ADD PRIMARY key(id);
						

		DROP TABLE IF EXISTS isochrone;
		CREATE temp TABLE isochrone AS 
		SELECT ST_area(ST_convexhull(ST_collect(geom))::geography) AS area,ST_convexhull(ST_collect(geom)) AS geom
		FROM temp_extrapolated_reached_vertices;
			/*Isochrone calculation should be changed to alpha-shape. Challenge when network is not dense.*/
			--ST_setSRID(pgr_pointsaspolygon,4326) AS geom 
			--FROM pgr_pointsaspolygon('select node id,st_x(geom) x,st_y(geom) y FROM temp_extrapolated_reached_vertices',0.000005); 
			
		EXECUTE format('
			UPDATE '||grid||' set pois = closest_pois, area_isochrone = x.area
			FROM (
				SELECT i.area, closest_pois(0.0009)
				FROM isochrone i
			) x
			WHERE grid_id = '||i
		);
				
		END LOOP;
END 
$function$;

--SELECT * FROM public.precalculate_grid(100, 100, 'grid_500'::TEXT, 15, ARRAY[[11.2570,48.1841]], 5, ARRAY[1], 1, 'walking_standard');


