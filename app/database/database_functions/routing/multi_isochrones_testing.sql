DROP FUNCTION IF EXISTS multi_isochrones;
CREATE OR REPLACE FUNCTION public.multi_isochrones_new(userid_input integer, objectid_input integer, minutes integer, number_isochrones integer, routing_profile_input text, speed_input numeric, 
    alphashape_parameter_input NUMERIC, modus_input integer, parent_id_input integer, points_array NUMERIC[][])
    RETURNS SETOF text--type_pois_multi_isochrones
    AS $function$
DECLARE
    i NUMERIC;
    max_cost NUMERIC:= minutes * 60;
	step_isochrone NUMERIC := max_cost/number_isochrones;
    ids_calc integer[];
    id_calc integer; 
BEGIN

    IF modus_input IN(1,3)  THEN
		userid_input = 1;
	END IF;

    SELECT array_agg(s.series) 
    INTO ids_calc 
    FROM (SELECT generate_series(1,array_length(points_array,1),1) series) s;

    speed_input = speed_input/3.6;

 --(userid_input integer, minutes integer,array_starting_points NUMERIC[][],speed NUMERIC, number_isochrones integer, ids_calc int[], objectid_input integer, modus_input integer,routing_profile text)
    
    PERFORM pgrouting_edges_multi(userid_input,minutes,points_array,speed_input,number_isochrones,ids_calc,objectid_input,modus_input,routing_profile_input);
    
    DROP TABLE IF EXISTS isos;
    CREATE TABLE isos (geom geometry,step integer);
    DROP TABLE IF EXISTS x;
    CREATE TABLE x (id integer,x float,y float,geom geometry,id_calc integer);

    FOREACH id_calc IN ARRAY ids_calc	
	LOOP

        FOR i IN SELECT generate_series(step_isochrone,max_cost,step_isochrone) 
        LOOP
            raise notice '%',i;
            raise notice '%',id_calc;
/*
            INSERT INTO x
            SELECT (row_number() over())::integer AS id, ST_X(select_reached_edges)::float x, 
            ST_Y(select_reached_edges)::float y,select_reached_edges, id_calc
            FROM select_reached_edges(id_calc,objectid_input,i);
*/

            INSERT INTO isos
            SELECT ST_SETSRID(pgr_pointsaspolygon('SELECT (row_number() over())::integer AS id, ST_X(select_reached_edges)::float x, 
            ST_Y(select_reached_edges)::float y
            FROM select_reached_edges('||id_calc||','||objectid_input||','||i||')',alphashape_parameter_input),4326),(i/60)::integer;


        END LOOP;
        
    END LOOP;
/*

    IF (SELECT count(*) FROM temp_step_vertices LIMIT 4) > 3 THEN
        INSERT INTO isos
        SELECT ST_SETSRID (pgr_pointsaspolygon ('SELECT (row_number() over())::integer as id, ST_X(geom)::float x, ST_Y(geom)::float y 
        FROM temp_step_vertices',alphashape_parameter_input), 4326),(upper_limit / 60)::integer;
    END IF;


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

*/
END;
$function$
LANGUAGE plpgsql;

/*
SELECT * 
FROM multi_isochrones_new(1,999,10,3,'walking_standard',5,0.00003,1,1,
ARRAY[[11.2570,48.1841],[11.2314,48.1736],[11.2503,48.1928],[11.2487,48.1718]])
*/

