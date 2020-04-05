DROP FUNCTION IF EXISTS pgr_FROMatob;
CREATE OR REPLACE FUNCTION public.pgr_FROMatob(edges_subset character varying, x1 double precision, y1 double precision, x2 double precision, y2 double precision, OUT ways_id bigint, OUT seq integer, OUT cost double precision, OUT name text, OUT geom geometry, OUT heading double precision)
 RETURNS SETOF record
 LANGUAGE sql
AS $function$

WITH
dijkstra AS (
    SELECT * FROM pgr_dijkstra(
        'SELECT id, source, target, length_m AS cost FROM ' || $1,
        -- source
        (SELECT id FROM ways_vertices_pgr
            ORDER BY geom <-> ST_SetSRID(ST_Point(x1,y1),4326) LIMIT 1),
        -- target
        (SELECT id FROM ways_vertices_pgr
            ORDER BY geom <-> ST_SetSRID(ST_Point(x2,y2),4326) LIMIT 1),
        false) -- undirected
    ),
    with_geom AS (
        SELECT ways.id as ways_id,dijkstra.seq, dijkstra.cost, ways.name,
        CASE
            WHEN dijkstra.node = ways.source THEN geom
            ELSE ST_Reverse(geom)
        END AS route_geom
        FROM dijkstra JOIN ways
        ON (edge = id) ORDER BY seq
    )
    SELECT *,
    ST_azimuth(ST_StartPoint(route_geom), ST_EndPoint(route_geom))
    FROM with_geom;
$function$

