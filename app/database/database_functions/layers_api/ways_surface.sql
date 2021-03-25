CREATE OR REPLACE FUNCTION ways_surface()
RETURNS TABLE (highway text, surface text, geom geometry) AS
$$
    SELECT w.highway, w.surface, w.geom
    FROM ways w, study_area s
    WHERE highway IS NOT NULL
    AND ST_Intersects(s.geom,w.geom);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION ways_surface() 
IS '**FOR-API-FUNCTION** RETURNS col_names[highway,surface,geom] **FOR-API-FUNCTION**';