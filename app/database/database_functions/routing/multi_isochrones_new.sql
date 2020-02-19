DROP FUNCTION IF EXISTS multi_isochrones;
CREATE OR REPLACE FUNCTION public.multi_isochrones (userid_input integer, minutes integer, number_isochrones integer, routing_profile_input text, speed_input numeric, 
    alphashape_parameter_input NUMERIC, modus_input integer, parent_id_input integer, points_array NUMERIC[][])
    RETURNS SETOF type_pois_multi_isochrones
    AS $function$
DECLARE
    i NUMERIC;
    max_cost = minutes * 60;
	step_isochrone NUMERIC := max_cost/number_isochrones;
BEGIN

    IF modus_input IN(1,3)  THEN
		userid_input = 1;
	END IF;

    

    SELECT FROM pgrouting_edges_multi (userid_input,minutes,points_array,speed_input::NUMERIC,objectids_array,modus_input,routing_profile_input);



    FOR i IN SELECT generate_series(step_isochrone,max_cost,step_isochrone) 
    LOOP
        RAISE NOTICE '%',i;

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

$function$
LANGUAGE plpgsql;


/*SELECT * FROM multi_isochrones(100,15,5,'walking_wheelchair',1.33,0.00003,1,1,ARRAY[[11.5669,48.1546],[11.5788,48.1545]]);
*/
