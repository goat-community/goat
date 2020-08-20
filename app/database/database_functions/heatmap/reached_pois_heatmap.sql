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
    		
    		INSERT INTO reached_pois_heatmap(gid,amenity,name,gridids,arr_cost,accessibility_indices)
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
	                AND partial_edge IS FALSE 
	                ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
	                LIMIT 1
	            ) AS e
	            WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances')))
	            AND ST_Intersects(p.geom,compute_section)
	        )
	        SELECT p.gid, p.amenity, p.name, p.gridids, c.arr_true_cost arr_cost, c.accessibility_indices::integer[]
	        FROM p, compute_accessibility_index(fraction,start_cost,end_cost,sensitivities) c;
	      
		   	DROP TABLE IF EXISTS reached_pois_partial;
	       	CREATE TABLE reached_pois_partial AS 
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
		            AND partial_edge IS TRUE
		            ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
		            LIMIT 1
		        ) AS e
		        WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances')))
		        AND ST_Intersects(p.geom,compute_section)
		    )
		    SELECT p.gid, p.amenity, p.name, p.gridids, c.arr_true_cost arr_cost, c.accessibility_indices::integer[]
		    FROM p, compute_accessibility_index(fraction,start_cost,end_cost,sensitivities) c;
		   	
		   	CREATE INDEX ON reached_pois_partial(gid);
		   
		   	WITH pois_to_update AS 
			(
				SELECT p.gid, r.gridids, r.gridids # p.gridids[1] arr_position, 
				r.gridids - p.gridids[1] + p.gridids[1] new_gridids, p.gridids[1], r.arr_cost, p.arr_cost[1] new_cost, r.accessibility_indices a1, p.accessibility_indices a2
				FROM reached_pois_heatmap r, reached_pois_partial p 
				WHERE r.gid = p.gid 
				AND r.gridids && p.gridids
				AND r.arr_cost[r.gridids # p.gridids[1]] > p.arr_cost[1]
			),
			updated_arrays AS 
			(
				SELECT x.gid, new_gridids AS gridids, arr_cost[1:(-1+arr_position)] + new_cost || arr_cost[arr_position+1:] AS arr_cost, 
				update_accessibility_array(x.a1, x.a2, arr_position) AS accessibility_indices
				FROM pois_to_update x
			)
			UPDATE reached_pois_heatmap r
			SET gridids = u.gridids, arr_cost = u.arr_cost, accessibility_indices = u.accessibility_indices
			FROM updated_arrays u 
			WHERE r.gid = u.gid;
	       	
			WITH grids_to_add AS 
			(
				SELECT p.gid, r.gridids + p.gridids[1] gridids, r.arr_cost + p.arr_cost[1] arr_cost,
				append_accessibility_array(r.accessibility_indices, p.accessibility_indices) AS accessibility_indices 
				FROM reached_pois_heatmap r, reached_pois_partial p  
				WHERE r.gid = p.gid 
				AND (r.gridids && p.gridids) IS FALSE
			)
			UPDATE reached_pois_heatmap r
			SET gridids = u.gridids, arr_cost = u.arr_cost, accessibility_indices = u.accessibility_indices
			FROM grids_to_add u 
			WHERE r.gid = u.gid;
					
			INSERT INTO reached_pois_heatmap(gid,amenity,name,gridids,arr_cost,accessibility_indices)
			SELECT p.* 
			FROM reached_pois_partial p
			LEFT JOIN reached_pois_heatmap r 
			ON p.gid = r.gid
			WHERE r.gid IS NULL;	
	
    	END LOOP;
  
    END IF; 

END;
$function$ LANGUAGE plpgsql 





DROP TABLE IF EXISTS reached_pois_heatmap;
CREATE TABLE reached_pois_heatmap (
	gid integer,
	amenity text,
	name text,
	gridids integer[],
	arr_cost integer[],
	accessibility_indices integer[]
);

ALTER TABLE reached_pois_heatmap ADD COLUMN id serial;
ALTER TABLE reached_pois_heatmap ADD PRIMARY key(id);
CREATE INDEX ON reached_pois_heatmap (amenity);

CREATE INDEX ON reached_pois_heatmap USING gin (gridids gin__int_ops);
CREATE INDEX ON reached_pois_heatmap USING gin (arr_cost gin__int_ops);


WITH grids_to_add AS 
(
	SELECT p.gid, r.gridids + p.gridids[1] gridids, r.arr_cost + p.arr_cost[1] arr_cost,
	append_accessibility_array(r.accessibility_indices, p.accessibility_indices) AS accessibility_indices 
	FROM reached_pois_heatmap r, reached_pois_partial p  
	WHERE r.gid = p.gid 
	AND (r.gridids && p.gridids) IS FALSE
)
UPDATE reached_pois_heatmap r
SET gridids = u.gridids, arr_cost = u.arr_cost, accessibility_indices = u.accessibility_indices
FROM grids_to_add u 
WHERE r.gid = u.gid;