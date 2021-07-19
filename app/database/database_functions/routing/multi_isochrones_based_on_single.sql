DROP FUNCTION IF EXISTS multi_isochrones_based_on_single;
CREATE OR REPLACE FUNCTION public.multi_isochrones_based_on_single(userid_input integer, objectid_input integer, minutes integer, number_isochrones integer, routing_profile_input text, speed_input numeric, 
    alphashape_parameter_input NUMERIC, modus_input integer, parent_id_input integer, points_array NUMERIC[][])
    RETURNS void--type_pois_multi_isochrones
    AS $function$
DECLARE
    ids_calc integer[];
    id_calc integer; 
    counter integer := 1;
BEGIN

    IF modus_input IN(1,3)  THEN
		userid_input = 1;
	END IF;

    SELECT array_agg(random_between(1,1000000000))
    INTO ids_calc 
    FROM generate_series(1,array_length(points_array,1));
    

    FOREACH id_calc IN ARRAY ids_calc	
	LOOP
        INSERT INTO isochrones(geom,step,objectid) 
        SELECT geom, step, id_calc 
        FROM isochrones_alphashape(userid_input,minutes,points_array[counter][1],points_array[counter][2], 
        number_isochrones, speed_input, alphashape_parameter_input, modus_input, id_calc, 1, routing_profile_input);

        counter = counter + 1;
    END LOOP;

    INSERT INTO multi_isochrones (objectid, coordinates, userid, step, speed, alphashape_parameter, modus, parent_id, routing_profile, geom)
    SELECT objectid_input,points_array AS coordinates,userid_input,step,speed_input,
    alphashape_parameter_input,modus_input,parent_id_input, routing_profile_input as routing_profile,ST_Union(geom) AS geom
    FROM isochrones
    WHERE objectid IN(SELECT UNNEST(ids_calc))
    GROUP BY step;


END;
$function$
LANGUAGE plpgsql;


