CREATE OR REPLACE FUNCTION footpath_width()
RETURNS TABLE (sidewalk text, width numeric, highway text, geom geometry) AS
$$
	SELECT f.sidewalk, f.width, f.highway, f.geom FROM footpath_visualization f, study_area s
    WHERE ST_Intersects(s.geom,f.geom);
$$
LANGUAGE sql;

COMMENT ON FUNCTION footpath_width() 
IS '**FOR-API-FUNCTION** RETURNS col_names[sidewalk,width,highway,geom] **FOR-API-FUNCTION**';


