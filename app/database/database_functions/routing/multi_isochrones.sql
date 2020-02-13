DROP FUNCTION IF EXISTS multi_isochrones;
CREATE OR REPLACE FUNCTION public.multi_isochrones (userid_input integer, minutes integer, n integer, routing_profile_input text, speed_input numeric, 
    alphashape_parameter_input NUMERIC, modus_input integer, parent_id_input integer, points_array NUMERIC[][])
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
    buffer text;
    buffer_point geometry;
    distance integer;
    counter integer;
    x numeric;
    y numeric;

    arow record;
BEGIN

    IF modus_input IN(1,3)  THEN
		userid_input = 1;
	END IF;


    SELECT variable_simple::NUMERIC 
    INTO max_length_links
    FROM variable_container
    WHERE identifier = 'max_length_links';
    
    SELECT select_from_variable_container ('excluded_class_id_walking')::text[],
    select_from_variable_container ('categories_no_foot')::text 
    INTO excluded_class_id, categories_no_foot;

    SELECT array_agg(series) 
    INTO objectids_array
    FROM 
    (
        SELECT generate_series(1, array_length(points_array, 1)) AS series
    ) x;

    CREATE TEMP TABLE IF NOT EXISTS temp_catchment_vertices OF type_temp_catchment_vertices_multi (PRIMARY KEY (id));
    TRUNCATE temp_catchment_vertices;

    INSERT INTO temp_catchment_vertices
    SELECT row_number() over() as id, start_vertex,node,edge,cost,geom,objectid,routing_profile_input
    FROM pgrouting_edges_multi (userid_input,minutes,points_array,speed_input::NUMERIC,objectids_array,modus_input,routing_profile_input);
    
    -- routing is expensive
    CREATE INDEX IF NOT EXISTS index_temp_catchment_vertices ON temp_catchment_vertices (objectid);
    ----------------------------------------------------------------------------------------
    -----------------extrapolate the catchment vertices-------------------------------------
    ----------------------------------------------------------------------------------------
   
    CREATE TEMP TABLE IF NOT EXISTS temp_extrapolated_reached_vertices OF type_catchment_vertices_single;
    TRUNCATE temp_extrapolated_reached_vertices;

    CREATE TEMP TABLE IF NOT EXISTS isos (geom geometry,step integer);
    TRUNCATE isos;

    FOR i IN SELECT DISTINCT objectid FROM temp_catchment_vertices LOOP
        CREATE TEMP TABLE IF NOT EXISTS temp_reached_vertices OF type_catchment_vertices_single;
        CREATE TEMP TABLE IF NOT EXISTS temp_step_vertices OF type_catchment_vertices_single;
        TRUNCATE temp_extrapolated_reached_vertices;
        TRUNCATE temp_reached_vertices;
        
        INSERT INTO temp_reached_vertices 
        SELECT start_vertex, node, edge, COST, geom, NULL, objectid
        FROM temp_catchment_vertices
        WHERE objectid = i::integer;

        counter = 0;

        SELECT points_array[i][1] FROM temp_catchment_vertices
        INTO x;
        SELECT points_array[i][2] FROM temp_catchment_vertices
        INTO y;
        buffer_point = ST_SetSRID(ST_MakePoint(x,y), 4326);
        distance = minutes*speed_input*60;
        buffer = ST_AsText(ST_Buffer(buffer_point::geography,distance)::geometry);
        --extrapolate each cluster of catchment vertices
        INSERT INTO temp_extrapolated_reached_vertices
        SELECT *
        FROM extrapolate_reached_vertices(minutes * 60, max_length_links, buffer, (speed_input/3.6) ,userid_input, modus_input, routing_profile_input);
        LOOP
            DELETE FROM temp_step_vertices;
            exit WHEN counter = n;
            counter := counter + 1;
            upper_limit := (minutes * 60 / n) * counter;
            INSERT INTO temp_step_vertices
            SELECT *
            FROM temp_extrapolated_reached_vertices
            WHERE COST BETWEEN 0 AND upper_limit;
            IF (SELECT count(*) FROM temp_step_vertices LIMIT 4) > 3 THEN
                INSERT INTO isos
                SELECT ST_SETSRID (pgr_pointsaspolygon ('SELECT (row_number() over())::integer as id, ST_X(geom)::float x, ST_Y(geom)::float y 
                FROM temp_step_vertices',alphashape_parameter_input), 4326),(upper_limit / 60)::integer;
            END IF;
        END LOOP;
    END LOOP;
    objectid_multi_isochrone = random_between (1, 900000000);

    INSERT INTO multi_isochrones (objectid, coordinates, userid, step, speed, alphashape_parameter, modus, parent_id, routing_profile, geom)
    SELECT objectid_multi_isochrone,points_array AS coordinates,userid_input,step,speed_input,
    alphashape_parameter_input,modus_input,parent_id_input, routing_profile_input as routing_profile,ST_Union(geom) AS geom
    FROM isos
    GROUP BY step;

    RETURN query
    SELECT gid,objectid,coordinates,userid,step,routing_profile,speed,
    alphashape_parameter,modus,parent_id,population,geom geometry
    FROM multi_isochrones
    WHERE objectid = objectid_multi_isochrone;
END;
$function$
LANGUAGE plpgsql;


/*SELECT * FROM multi_isochrones(100,15,5,'walking_wheelchair',1.33,0.00003,1,1,ARRAY[[11.5669,48.1546],[11.5788,48.1545]]);
*/
