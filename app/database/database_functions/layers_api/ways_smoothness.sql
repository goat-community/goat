CREATE OR REPLACE FUNCTION ways_smoothness()
RETURNS TABLE (highway text, smoothness text, geom geometry) AS
$$
    SELECT w.highway, w.smoothness, w.geom
    FROM ways w, study_area s
    WHERE highway IS NOT NULL
    AND ST_Intersects(s.geom,w.geom);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION ways_smoothness() 
IS '**FOR-API-FUNCTION** RETURNS col_names[highway,smoothness,geom] **FOR-API-FUNCTION**';