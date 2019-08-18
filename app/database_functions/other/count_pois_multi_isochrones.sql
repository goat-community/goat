CREATE OR REPLACE FUNCTION public.count_pois_multi_isochrones (minutes integer, speed_input numeric, region_type text, region NUMERIC[], amenities text[])
    RETURNS TABLE (
        count_pois integer, geom geometry, buffer_geom geometry
)
    AS $function$
DECLARE
    buffer_geom geometry;
    region_geom geometry;
BEGIN
    IF region_type = 'study_area' THEN
        SELECT
            s.geom INTO region_geom
        FROM
            study_area s
        WHERE
            ST_Intersects (s.geom, ST_SetSrid (ST_POINT (region[1], region[2]), 4326));
    ELSE
        SELECT
            ST_Envelope (region[1],
                region[2],
                region[3],
                region[4]) INTO region_geom;
    END IF;
    buffer_geom = ST_Buffer (region_geom::geography, (speed_input / 3.6) * 60 * minutes)::geometry;
    RETURN query WITH count_pois AS (
        SELECT
            count(*) AS count_pois
        FROM
            pois p
        WHERE
            ST_Intersects (p.geom,
                buffer_geom)
            AND amenity IN (
                SELECT
                    UNNEST(amenities))
            UNION ALL
            SELECT
                count(*)
            FROM
                public_transport_stops p
            WHERE
                ST_Intersects (p.geom,
                    buffer_geom)
                AND public_transport_stop IN (
                    SELECT
                        UNNEST(amenities)))
        SELECT
            sum(c.count_pois)::integer,
        region_geom,
        buffer_geom
    FROM
        count_pois c;
END;
$function$
LANGUAGE plpgsql;

