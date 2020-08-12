CREATE OR REPLACE FUNCTION public.reached_pois_heatmap(sensitivities integer[], userid integer default 1, scenario_id integer default 1)
RETURNS VOID
AS $function$
DECLARE 

BEGIN 
    IF userid = 1 THEN 
        DROP TABLE IF EXISTS reached_pois_heatmap;
        CREATE TABLE reached_pois_heatmap AS 
        WITH p AS 
        (
            SELECT p.gid, p.amenity, p.name, p.geom, e.edge, e.gridids, e.fraction, e.start_cost, e.end_cost
            FROM pois_userinput p
            CROSS JOIN LATERAL
            (
                SELECT f.edge, f.gridids, ST_LineLocatePoint(f.geom,p.geom) AS fraction, f.start_cost, f.end_cost 
                FROM reached_edges_heatmap f
                WHERE f.geom && ST_Buffer(p.geom,0.0014)
                ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
                LIMIT 1
            ) AS e
            WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances')))
        )
        SELECT p.gid, p.amenity, p.name, p.gridids, p.fraction, p.start_cost, p.end_cost, c.arr_true_cost, c.accessibility_indices::integer[]
        FROM p, compute_accessibility_index(fraction,start_cost,end_cost,ARRAY[200000, 250000, 300000, 350000, 400000, 450000]) c;

        ALTER TABLE reached_pois_heatmap ADD COLUMN id serial;
        ALTER TABLE reached_pois_heatmap ADD PRIMARY key(id);
        CREATE INDEX ON reached_pois_heatmap (amenity);
    END IF; 

END;
$function$ LANGUAGE plpgsql ;