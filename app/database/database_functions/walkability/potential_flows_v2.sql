CREATE OR REPLACE FUNCTION public.get_edge_nearest_persons_v2(p_objectid integer, convex geometry)
 RETURNS TABLE(edge integer, geom geometry, source integer, target integer, start_cost double precision, end_cost double precision, cost double precision, persons double precision, person_geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE
    rec record;
    rec2 record;
    cur refcursor;
BEGIN
    OPEN cur FOR 
    SELECT p.persons, p.geom, p.gid
    FROM persons p
    WHERE ST_Intersects(convex,p.geom);
    
    LOOP 
        FETCH cur INTO rec;
        EXIT WHEN NOT FOUND;
    
        SELECT rec.persons, rec.geom person_geom, e.edge, e.geom, e.source, e.target, e.start_cost, e.end_cost, e.cost
        INTO rec2
        FROM edges_potential_flows e
        WHERE e.objectid = p_objectid
        AND e.geom && st_buffer(rec.geom,0.0009)
        ORDER BY rec.geom <-> e.geom
        LIMIT 1;
    
        IF rec2 IS NOT NULL
        THEN
            persons = rec2.persons;
            person_geom = rec2.person_geom;
            edge = rec2.edge;
            geom = rec2.geom; 
            source = rec2.source;
            target= rec2.target;
            start_cost= rec2.start_cost;
            end_cost= rec2.end_cost;
            cost = rec2.cost ;
            RETURN NEXT;
        END IF;
    
    END LOOP;
END;
$function$;

CREATE OR REPLACE FUNCTION public.potential_pedestrian_flows_v2(x double precision, y double precision, userid_input integer, scenario_id_input integer)
 RETURNS TABLE(edge_out integer, persons_out integer, geom_out geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE 
    objectid_input integer := random_between(1,900000000);
    ts timestamptz;
    v_depth integer;
BEGIN 
    --ts = clock_timestamp();
    --RAISE NOTICE '% enter', ts;
    PERFORM public.pgrouting_edges_potential_flows(array[600.], array[[x,y]],1.33, userid_input, scenario_id_input, objectid_input, 1, 'walking_standard');
    --RAISE NOTICE '% Performed pgrouting_edges_potential_flows, % sec', date_trunc('millisecond', clock_timestamp()), clock_timestamp()-ts;

    --ts = clock_timestamp();
    DROP TABLE IF EXISTS raw_flows; 
    CREATE TEMP TABLE raw_flows AS 
    WITH convex AS 
    (
        SELECT ST_CONVEXHULL(ST_COLLECT(e.geom)) AS geom
        FROM edges_potential_flows e
        WHERE e.objectid = objectid_input
    ), 
    flows AS 
    (
        SELECT ed.edge, ed.geom, ed.source, ed.target, ed.start_cost, ed.end_cost, ed.cost,sum(ed.persons) AS persons
        FROM convex c, get_edge_nearest_persons_v2(objectid_input, c.geom) ed
        --where ST_Intersects(ed.person_geom,c.geom)
        GROUP BY ed.edge, ed.geom, ed.source, ed.target, ed.start_cost, ed.end_cost, ed.cost
    )
    SELECT e.edge, e.geom, e.source,e.target,e.start_cost, e.end_cost, e.cost, 0 as persons
    FROM edges_potential_flows e
    LEFT JOIN flows f ON e.edge = f.edge 
    WHERE f.edge IS NULL 
    AND e.objectid = objectid_input
    UNION ALL 
    SELECT * 
    FROM flows;
    
    CREATE INDEX ON raw_flows(edge);
    CREATE INDEX ON raw_flows using btree (cost);
    ANALYZE raw_flows;
    
    --RAISE NOTICE '% Created raw_flows, % sec', date_trunc('millisecond', clock_timestamp()), clock_timestamp()-ts;
    --ts = clock_timestamp();
    
    -- Compose flow tree.
    -- Delete excess edge at the center
    WITH origin AS ( 
        SELECT rf.source AS center_point 
        FROM raw_flows rf
        WHERE start_cost=0
    ),
    excess_edge AS (
        SELECT center_point, rf1.target, rf2.source, rf.edge, rf."source",rf.target
        from origin o
        JOIN raw_flows rf1 ON center_point=rf1."source"
        JOIN raw_flows rf2 ON center_point=rf2.target
        JOIN raw_flows rf ON 
            ( rf.source = rf1.target OR rf.source = rf2.source )
            AND ( rf.target = rf1.target OR rf.target = rf2.source )
    )
    DELETE FROM raw_flows rf
    USING excess_edge e
    WHERE e.edge = rf.edge;
    

    -- Tree vertices. One vertex has only one output edge.
    DROP TABLE IF EXISTS flow_vertices;
    CREATE TEMP TABLE flow_vertices (
         id serial primary key,
         vertex integer, 
         edge         integer, 
         next_vertex  integer, 
         persons      double precision, 
         depth        integer,
         cost         double precision,
         low_cost     double precision
    );
    
    
    INSERT INTO flow_vertices(vertex,next_vertex,edge,persons,depth,cost,low_cost)
    WITH RECURSIVE origin AS ( 
        SELECT rf.source AS center_point 
        from raw_flows rf
        where start_cost=0
    ),
    vertices AS ( 
        SELECT 
            CASE WHEN o.center_point=rf.source
                THEN rf.target 
                ELSE rf.source 
            END AS vertex,
            o.center_point as next_vertex,
            edge, persons, 0 as depth,rf.cost,least(start_cost,end_cost) low_cost
        FROM raw_flows rf, origin o
        WHERE o.center_point=rf.source or o.center_point=rf.target
        UNION 
        SELECT
            CASE WHEN start_cost>end_cost
                THEN rf.source 
                ELSE rf.target
            END AS vertex, 
            v.vertex as next_vertex,
            rf.edge,rf.persons,v.depth+1 as depth,rf.cost, least(rf.start_cost,rf.end_cost) low_cost
        FROM vertices v
        JOIN raw_flows rf ON 
            (v.vertex=rf.source AND start_cost<end_cost)
            OR (v.vertex=rf.target AND start_cost>end_cost) 
        WHERE v.cost=least(rf.start_cost,rf.end_cost)
    )
    SELECT *
    FROM vertices;
    
    CREATE INDEX ON flow_vertices USING btree(depth);
    
    -- Edge table for accumulating persons along flow tree.
    DROP TABLE IF EXISTS flow_edges;
    CREATE TEMP TABLE flow_edges (
         vertex_id integer  primary key, 
         edge         integer, 
         persons      double precision,
         depth     integer
    );
    
    INSERT INTO flow_edges(vertex_id, edge, persons, depth)
    SELECT id, edge, persons, depth
    FROM flow_vertices;
    
    CREATE INDEX ON flow_edges USING btree(edge);

    -- Get max tree depth. 
    SELECT max(depth)
    INTO v_depth
    FROM flow_vertices fv;

    loop 
        -- Summarize persons from uplink edges.
        -- Start from the most distant leaves and move to center.
        with sub as 
        (   
            SELECT v2.id vertex_id,  sum(e.persons) persons
            FROM flow_vertices v1 
            JOIN flow_vertices v2 ON v1.next_vertex=v2.vertex
            JOIN flow_edges e ON e.vertex_id = v1.id
            WHERE v1.depth=v_depth AND v1.low_cost=v2.cost
            GROUP BY v2.id
        )
        UPDATE flow_edges e 
        SET persons = e.persons+sub.persons
        FROM sub
        WHERE sub.vertex_id=e.vertex_id;
    
        -- Step one depth level closer to the center
        v_depth = v_depth - 1;
    
        EXIT WHEN v_depth=0;
    END LOOP;

    --RAISE NOTICE '% Summarize persons on flow edges, % sec', date_trunc('millisecond', clock_timestamp()), clock_timestamp()-ts;

    RETURN query 
    SELECT f.edge, (COALESCE(e.persons, f.persons,0))::integer AS persons, f.geom 
    FROM raw_flows f  
    JOIN flow_edges e ON e.edge=f.edge ;

END;
$function$;



--- Testing
/*
drop table potential_pedestrian_flows_v2;
create table potential_pedestrian_flows_v2 as 
SELECT * 
FROM potential_pedestrian_flows_v2(11.2374, 48.1778, 1, 1); --  Execution Time: 550.723 ms
*/
