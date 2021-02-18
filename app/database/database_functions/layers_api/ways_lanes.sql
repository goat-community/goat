CREATE OR REPLACE FUNCTION ways_lanes()
RETURNS TABLE (highway text, lanes numeric, geom geometry) AS
$$
    SELECT w.highway, w.lanes, w.geom 
    FROM ways w, study_area s 
    WHERE w.highway IN ('motorway','trunk','primary','secondary','tertiary','residential',
	'motorway_link','trunk_link','primary_link','secondary_link','tertiary_link',
	'living_street','service', 'unclassified')
    AND ST_Intersects(s.geom,w.geom);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION ways_lanes() 
IS '**FOR-API-FUNCTION** RETURNS col_names[highway,lanes,geom] **FOR-API-FUNCTION**';