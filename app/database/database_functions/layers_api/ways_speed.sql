CREATE OR REPLACE FUNCTION ways_speed()
RETURNS TABLE (highway text, maxspeed_forward integer, maxspeed_backward integer, death_end bigint, geom geometry) AS
$$
    SELECT w.highway, w.maxspeed_forward, w.maxspeed_backward, w.death_end, w.geom
    FROM ways w, study_area s 
    WHERE w.highway IN ('motorway','trunk','primary','secondary','tertiary','residential',
	'motorway_link','trunk_link','primary_link','secondary_link','tertiary_link',
	'living_street','service', 'unclassified')
    AND ST_Intersects(s.geom,w.geom)
    AND NOT (highway = 'service' AND death_end IS NOT NULL);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION ways_speed() 
IS '**FOR-API-FUNCTION** RETURNS col_names[highway,maxspeed_forward,maxspeed_backward,death_end,geom] **FOR-API-FUNCTION**';