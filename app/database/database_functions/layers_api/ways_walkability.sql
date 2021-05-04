CREATE OR REPLACE FUNCTION ways_walkability()
RETURNS TABLE (sidewalk_quality numeric, traffic_protection numeric, security numeric, vegetation numeric, comfort numeric, walkability numeric, geom geometry) AS
$$
	SELECT f.sidewalk_quality , f.traffic_protection, f.security, f.vegetation, f.comfort, f.walkability, f.geom 
    FROM footpath_visualization f, study_area s
    WHERE ST_Intersects(s.geom,f.geom);
$$
LANGUAGE sql;

COMMENT ON FUNCTION ways_walkability() 
IS '**FOR-API-FUNCTION** RETURNS col_names[sidewalk_quality,traffic_protection,security,vegetation,comfort,walkability,geom] **FOR-API-FUNCTION**';