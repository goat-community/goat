DROP FUNCTION IF EXISTS mapping_ways_surface;
CREATE OR REPLACE FUNCTION mapping_ways_surface()
RETURNS TABLE (osm_id bigint, highway text, osm_type text, geom geometry) AS
$$
    SELECT w.osm_id, w.highway, 'way' AS osm_type, w.geom
    FROM ways_mapping w, study_area s
    WHERE surface IS NULL
    AND highway IN ('cycleway','residential','path')
    AND ST_Intersects(s.geom,w.geom);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION mapping_ways_surface() 
IS '**FOR-API-FUNCTION** RETURNS col_names[osm_id,highway,osm_type,geom] **FOR-API-FUNCTION**';