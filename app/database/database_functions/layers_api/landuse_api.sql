CREATE OR REPLACE FUNCTION landuse_api()
RETURNS TABLE (gid integer, landuse TEXT, geom geometry) AS
$$
	SELECT l.gid, l.landuse, l.geom 
    FROM landuse l, study_area s 
    WHERE ST_Intersects(l.geom,s.geom)
$$
LANGUAGE sql;

COMMENT ON FUNCTION landuse_api() 
IS '**FOR-API-FUNCTION** RETURNS col_names[gid,landuse] **FOR-API-FUNCTION**';
