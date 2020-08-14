CREATE OR REPLACE FUNCTION public.reached_pois_heatmap(userid integer DEFAULT 1, scenario_id integer DEFAULT 1, buffer_study_area integer DEFAULT 1600)
RETURNS VOID
AS $function$
DECLARE 
	sensitivities integer[] := select_from_variable_container('heatmap_sensitivities')::integer[];
	compute_section geometry;
	cnt_sections integer := 0;
	max_sections integer;
BEGIN 
	DROP TABLE IF EXISTS compute_sections; 
	CREATE TEMP TABLE compute_sections AS
	WITH b AS 
	(
		SELECT ST_BUFFER(geom::geography, buffer_study_area)::geometry AS geom 
		FROM study_area_union 
	),
	g AS 
	(
		SELECT (ST_DUMP(makegrid_2d(ST_BUFFER(geom::geography, buffer_study_area)::geometry, 2000, 2000))).geom
		FROM b
	)
	SELECT g.geom 
	FROM b, g
	WHERE ST_Intersects(b.geom,g.geom);
	
    IF userid = 1 THEN 
    	max_sections = (SELECT count(*) FROM compute_sections);
    	FOR compute_section IN SELECT geom FROM compute_sections 
    	LOOP 
    		cnt_sections = cnt_sections + 1;
    		RAISE NOTICE 'Section count %:%', cnt_sections,max_sections;
    		INSERT INTO reached_pois_heatmap
    		WITH p AS 
	        (
	            SELECT p.gid, p.amenity, p.name, p.geom, e.edge, e.gridids, e.fraction, e.start_cost, e.end_cost
	            FROM pois_userinput p
	            CROSS JOIN LATERAL
	            (
	                SELECT f.edge, f.gridids, ST_LineLocatePoint(f.geom,p.geom) AS fraction, f.start_cost, f.end_cost 
	                FROM reached_edges_heatmap f
	                WHERE f.geom && ST_Buffer(p.geom,0.0014)
	                AND ST_Intersects(f.geom,ST_BUFFER(compute_section,0.0014))
	                ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
	                LIMIT 1
	            ) AS e
	            WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances')))
	            AND ST_Intersects(p.geom,compute_section)
	        )
	        SELECT p.gid, p.amenity, p.name, p.gridids, p.fraction, p.start_cost, p.end_cost, c.arr_true_cost, c.accessibility_indices::integer[]
	        FROM p, compute_accessibility_index(fraction,start_cost,end_cost,sensitivities) c;
    	
    	END LOOP;
  
    END IF; 

END;
$function$ LANGUAGE plpgsql 
