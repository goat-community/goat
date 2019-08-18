CREATE OR REPLACE FUNCTION public.multi_isochrones(userid_input integer, minutes integer, n integer, speed_input numeric, alphashape_parameter_input NUMERIC, modus_input integer, points_array NUMERIC[][])
RETURNS SETOF type_pois_multi_isochrones
AS $function$
DECLARE 
	excluded_class_id integer[];
	categories_no_foot text[];
	max_length_links numeric;
	objectids_array integer[];
	objectid_multi_isochrone integer;
	i integer;
	upper_limit NUMERIC;
	under_limit NUMERIC;
	counter integer;
BEGIN 
	SELECT variable_simple::NUMERIC 
	INTO max_length_links
	FROM variable_container
	WHERE identifier = 'max_length_links';
		
	SELECT select_from_variable_container('excluded_class_id_walking')::text[],
	select_from_variable_container('categories_no_foot')::text
	INTO excluded_class_id, categories_no_foot;

	SELECT array_agg(series)
 	INTO objectids_array
 	FROM (
 		SELECT generate_series(1,array_length(points_array,1)) AS series
 	) x; 
 	
 	DROP TABLE IF EXISTS temp_catchment_vertices;
    CREATE TEMP TABLE temp_catchment_vertices AS
	SELECT start_vertex,node,edge,cnt,cost,geom,objectid 
 	FROM pgrouting_edges_multi(userid_input, minutes, points_array, speed_input::NUMERIC, objectids_array, modus_input); -- routing is expensive

 	ALTER TABLE temp_catchment_vertices ADD COLUMN id serial;
 	ALTER TABLE temp_catchment_vertices ADD PRIMARY key(id);
 	CREATE INDEX ON temp_catchment_vertices (objectid);
 	
    ----------------------------------------------------------------------------------------
    -----------------extrapolate the catchment vertices-------------------------------------
    ----------------------------------------------------------------------------------------
 
 	DROP TABLE IF EXISTS temp_extrapolated_reached_vertices;
	CREATE TEMP TABLE temp_extrapolated_reached_vertices AS  --create empty table that will hold the extrapolated vertices
	SELECT * FROM temp_catchment_vertices
	LIMIT 0;
	DROP TABLE IF EXISTS temp_step_vertices; 
	CREATE temp TABLE temp_step_vertices AS 
	SELECT * FROM temp_extrapolated_reached_vertices;

	DROP TABLE IF EXISTS isos;
	CREATE TEMP TABLE IF NOT EXISTS isos (geom geometry,step integer);
	
	FOR i IN SELECT DISTINCT objectid FROM temp_catchment_vertices 
 	LOOP
		DROP TABLE IF EXISTS temp_reached_vertices;
		DELETE FROM temp_extrapolated_reached_vertices;

		CREATE TEMP TABLE temp_reached_vertices ON COMMIT DROP AS 
		SELECT start_vertex, node, edge, cnt, cost, geom, objectid 
		FROM temp_catchment_vertices
		WHERE objectid = i;	
		counter = 0;
		
		 --extrapolate each cluster of catchment vertices
		INSERT INTO temp_extrapolated_reached_vertices
		SELECT * 
		FROM extrapolate_reached_vertices(minutes*60,max_length_links,(speed_input/3.6),excluded_class_id,categories_no_foot); 
		LOOP
		exit WHEN counter = n;
			counter :=counter + 1;
			upper_limit :=(minutes*60/n)*counter; 
			INSERT INTO temp_step_vertices 
			SELECT * FROM temp_extrapolated_reached_vertices
			WHERE cost BETWEEN 0 AND upper_limit;
			IF (SELECT count(*)	FROM temp_step_vertices LIMIT 4) > 3  THEN 
				INSERT INTO isos
		     	SELECT ST_SETSRID(
			     	pgr_pointsaspolygon('SELECT (row_number() over())::integer as id, ST_X(geom)::float x, ST_Y(geom)::float y 
					FROM temp_step_vertices',alphashape_parameter_input)
			    ,4326),(upper_limit/60)::integer;
			END IF;
			DELETE FROM temp_step_vertices;
	   	END LOOP;	
	END LOOP;

	objectid_multi_isochrone = random_between(1,900000000);

	INSERT INTO multi_isochrones(objectid, coordinates, userid, step, speed, alphashape_parameter, modus, parent_id, geom)
	SELECT objectid_multi_isochrone,points_array AS coordinates, userid_input,step,speed_input,alphashape_parameter_input,modus_input, 1, ST_Union(geom) AS geom
	FROM isos
	GROUP BY step;
	
	RETURN query 
	SELECT gid,objectid, coordinates, userid,step,speed,alphashape_parameter,modus, parent_id, population, geom geometry 
	FROM multi_isochrones
	WHERE objectid = objectid_multi_isochrone;

END;	
	
$function$ LANGUAGE plpgsql;