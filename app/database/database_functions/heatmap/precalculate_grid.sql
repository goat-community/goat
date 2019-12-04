DROP FUNCTION IF EXISTS precalculate_grid;
CREATE OR REPLACE FUNCTION public.precalculate_grid(userid_input integer, grid text, minutes integer,array_starting_points NUMERIC[][],speed NUMERIC, objectids int[], modus_input integer,routing_profile text)
RETURNS SETOF type_catchment_vertices
 LANGUAGE plpgsql
AS $function$
DECLARE 
	i integer;
	count_vertices integer;
	excluded_class_id integer[];
	categories_no_foot text[];
	max_length_links integer;
	buffer text;
    buffer_point geometry;
	distance integer;
	x integer;
	y integer;
BEGIN 

	DROP TABLE IF EXISTS temp_multi_reached_vertices;
	DROP TABLE IF EXISTS temp_all_extrapolated_vertices;
	CREATE temp TABLE temp_multi_reached_vertices AS 
	SELECT *
	FROM pgrouting_edges_multi(1,minutes,array_starting_points,speed,objectids,1,routing_profile);
	ALTER TABLE temp_multi_reached_vertices ADD COLUMN id serial;
	ALTER TABLE temp_multi_reached_vertices ADD PRIMARY key(id);
	
	SELECT select_from_variable_container('excluded_class_id_walking')::text[],
	select_from_variable_container('categories_no_foot')::text
	INTO excluded_class_id, categories_no_foot;
	
	SELECT variable_simple::integer
	INTO max_length_links
	FROM variable_container 
	WHERE identifier = 'max_length_links';

	FOR i IN SELECT DISTINCT objectid FROM temp_multi_reached_vertices
	LOOP 
		DROP TABLE IF EXISTS temp_reached_vertices;	
		DROP TABLE IF EXISTS temp_extrapolated_reached_vertices;
		
	    CREATE temp TABLE temp_reached_vertices AS 
		SELECT start_vertex, node, edge, cost, geom, objectid 
		FROM temp_multi_reached_vertices
		WHERE objectid = i;

		SELECT array_starting_points[i][1] INTO x;
    	SELECT array_starting_points[i][2] INTO y;

   		buffer_point = ST_SetSRID(ST_MakePoint(x,y), 4326);
    	distance = minutes*speed*60;
    	buffer = ST_AsText(ST_Buffer(buffer_point::geography,distance)::geometry);

		IF (SELECT count(*)	FROM temp_reached_vertices LIMIT 4) > 3 THEN 
	
			CREATE temp TABLE temp_extrapolated_reached_vertices AS 
			SELECT * 
			FROM extrapolate_reached_vertices(minutes*60,max_length_links,buffer,(speed/3.6),userid_input,modus_input,routing_profile);

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

--SELECT * FROM precalculate_grid(1,'grid_500',15,array[[11.5669,48.1546],[11.5788,48.1545]],5,	array[1,2],1,'walking_standard');
