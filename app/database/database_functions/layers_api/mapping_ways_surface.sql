CREATE OR REPLACE FUNCTION mapping_ways_surface()
RETURNS TABLE (osm_id bigint, highway text, geom geometry) AS
$$
    SELECT w.osm_id, w.highway, w.geom
    FROM ways_mapping w, study_area s
    WHERE surface IS NULL
    AND highway IN ('cycleway','residential','path')
    AND ST_Intersects(s.geom,w.geom);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION mapping_ways_surface() 
IS '**FOR-API-FUNCTION** RETURNS col_names[osm_id,highway,geom] **FOR-API-FUNCTION**';