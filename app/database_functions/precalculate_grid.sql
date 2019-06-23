CREATE OR REPLACE FUNCTION public.precalculate_grid(grid text, minutes integer,array_starting_points NUMERIC[][],speed NUMERIC, objectids int[])
RETURNS SETOF type_catchment_edges
 LANGUAGE plpgsql
AS $function$
DECLARE 
	i integer;
	count_vertices integer;
BEGIN 
	DROP TABLE IF EXISTS temp_multi_reached_vertices;
	DROP TABLE IF EXISTS temp_all_extrapolated_vertices;
	CREATE temp TABLE temp_multi_reached_vertices AS 
	SELECT *
	FROM pgrouting_edges_multi(minutes,array_starting_points,speed,objectids);
	ALTER TABLE temp_multi_reached_vertices ADD COLUMN id serial;
	ALTER TABLE temp_multi_reached_vertices ADD PRIMARY key(id);
	

	FOR i IN SELECT DISTINCT objectid FROM temp_multi_reached_vertices
	LOOP 
		RAISE NOTICE 'loop';
		DROP TABLE IF EXISTS temp_reached_vertices;	
		DROP TABLE IF EXISTS temp_extrapolated_reached_vertices;
		
	    CREATE temp TABLE temp_reached_vertices AS 
		SELECT start_vertex, node, edge, cost, geom, objectid 
		FROM temp_multi_reached_vertices
		WHERE objectid = i;
				
		IF (SELECT count(*)	FROM temp_reached_vertices LIMIT 4) > 3 THEN 
	
			CREATE temp TABLE temp_extrapolated_reached_vertices AS 
			SELECT * 
			FROM extrapolate_reached_vertices(minutes*speed,ARRAY[0,101,102,103,104,105,106,107,501,502,503,504,701,801],ARRAY['no','use_sidepath']);
			
			ALTER TABLE temp_extrapolated_reached_vertices ADD COLUMN id serial;
			ALTER TABLE temp_extrapolated_reached_vertices ADD PRIMARY key(id);
			CREATE INDEX ON temp_extrapolated_reached_vertices USING gist(geom);
		
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
			
		END IF; 
	
		END LOOP;
END 
$function$;