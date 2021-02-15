CREATE OR REPLACE FUNCTION ways_category_aggregated()
RETURNS TABLE (highway text, geom geometry) AS
$$
    SELECT w.highway, w.geom
    FROM ways w, study_area s
    WHERE highway IS NOT NULL
    AND ST_Intersects(s.geom,w.geom)
;
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION ways_category_aggregated() 
IS '**FOR-API-FUNCTION** RETURNS col_names[highway,geom] **FOR-API-FUNCTION**';
