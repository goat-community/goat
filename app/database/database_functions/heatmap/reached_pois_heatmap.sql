CREATE OR REPLACE FUNCTION public.reached_pois_heatmap(userid integer DEFAULT 0, scenario_id integer DEFAULT 0, buffer_study_area integer DEFAULT 1600)
RETURNS VOID
AS $function$
DECLARE 
	sensitivities integer[] := select_from_variable_container('heatmap_sensitivities')::integer[];
	compute_section geometry;
	cnt_sections integer := 0;
	max_sections integer;
BEGIN 
    IF userid = 0 THEN 
    	
    	max_sections = (SELECT count(*) FROM compute_sections);
    	FOR compute_section IN SELECT geom FROM compute_sections 
    	LOOP 
    		cnt_sections = cnt_sections + 1;
    		RAISE NOTICE 'Section count %:%', cnt_sections,max_sections;
    		PERFORM reached_pois_derive_costs(compute_section, sensitivities, 0.0014);

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