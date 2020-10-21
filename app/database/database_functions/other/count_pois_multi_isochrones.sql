DROP FUNCTION IF EXISTS count_pois_multi_isochrones;
CREATE OR REPLACE FUNCTION public.count_pois_multi_isochrones (userid_input integer, scenario_id_input integer, modus_input text, minutes integer, speed_input numeric, region_type text, region NUMERIC[], amenities text[])
    RETURNS TABLE (region_name text, count_pois integer, geom geometry, buffer_geom geometry)
    AS $function$
DECLARE
    buffer_geom geometry;
    region_geom geometry;
    region_name text;
    excluded_pois_id integer[];
BEGIN
    IF modus_input = 'default' THEN
        scenario_id_input = 0;
        excluded_pois_id = ARRAY[]::integer[];
    ELSE
        excluded_pois_id = ids_modified_features(scenario_id_input,'pois');
    END IF;

    IF region_type = 'study_area' THEN
        SELECT s.geom, name  
        INTO region_geom, region_name
        FROM study_area s
        WHERE ST_Intersects (s.geom, ST_SetSrid (ST_POINT (region[1], region[2]), 4326));
    ELSE
        SELECT st_MAKEEnvelope (region[1],region[2],region[3],region[4]) INTO region_geom;
        region_name = 'envelope';
    END IF;
    buffer_geom = ST_Buffer (region_geom::geography, (speed_input / 3.6) * 60 * minutes)::geometry;
    RETURN query 
    	WITH count_pois AS (
            SELECT count(*) AS count_pois
            FROM pois_userinput p
            WHERE ST_Intersects (p.geom,buffer_geom)
            AND (p.scenario_id = scenario_id_input OR p.scenario_id IS NULL)
            AND p.gid NOT IN (SELECT UNNEST(excluded_pois_id))
            AND amenity IN (SELECT UNNEST(amenities))
        )
        SELECT region_name,sum(c.count_pois)::integer,
        region_geom, buffer_geom
    	FROM count_pois c;
END;
$function$
LANGUAGE plpgsql;

--SELECT * FROM count_pois_multi_isochrones(100,'default,'10,5,'envelope',ARRAY[11.4988,48.1879,11.5284,481723],ARRAY['bar','restaurant'])
--SELECT * FROM count_pois_multi_isochrones(100,'default',10,5,'study_area',ARRAY[11.247437,48.177883],ARRAY['bar','restaurant'])
