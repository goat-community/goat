CREATE OR REPLACE FUNCTION ways_segregated()
RETURNS TABLE (segregated text, highway text, geom geometry) AS
$$
	SELECT f.segregated, f.highway, f.geom 
    FROM footpath_visualization f, study_area s
    WHERE ST_Intersects(s.geom,f.geom);
$$
LANGUAGE sql;

COMMENT ON FUNCTION ways_segregated() 
IS '**FOR-API-FUNCTION** RETURNS col_names[segregated,highway,geom] **FOR-API-FUNCTION**';

