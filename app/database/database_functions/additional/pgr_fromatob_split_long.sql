DROP FUNCTION IF EXISTS pgr_FROMatob_split_long;
CREATE OR REPLACE FUNCTION public.pgr_FROMatob_split_long(edges_subset character varying, x1 double precision, y1 double precision, x2 double precision, y2 double precision, OUT seq integer, OUT cost double precision, OUT geom geometry, OUT heading double precision)
 RETURNS SETOF record
 LANGUAGE sql
AS $function$

WITH
dijkstra AS (
    SELECT * FROM pgr_dijkstra(
        'SELECT id, source, target, length_m AS cost FROM ' || $1 || ' WHERE class_id not in(101,102,103,104,105,106,107,501,502,503,504)',
        -- source
        (SELECT id FROM ways_split_long_vertices_pgr
            ORDER BY geom <-> ST_SetSRID(ST_Point(x1,y1),4326) LIMIT 1),
        -- target
        (SELECT id FROM ways_split_long_vertices_pgr
            ORDER BY geom <-> ST_SetSRID(ST_Point(x2,y2),4326) LIMIT 1),
        false) -- undirected
    ),
    with_geom AS (
        SELECT dijkstra.seq, dijkstra.cost,
        CASE
            WHEN dijkstra.node = ways_split_long.source THEN geom
            ELSE ST_Reverse(geom)
        END AS route_geom
        FROM dijkstra JOIN ways_split_long
        ON (edge = id) ORDER BY seq
    )
    SELECT *,
    ST_azimuth(ST_StartPoint(route_geom), ST_EndPoint(route_geom))
    FROM with_geom;
$function$

