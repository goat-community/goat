CREATE OR REPLACE FUNCTION street_furniture()
RETURNS TABLE (amenity text, tags hstore, geom geometry) AS
$$
	SELECT p.amenity, p.tags, p.geom FROM pois p, study_area s
    WHERE st_intersects(s.geom,p.geom) 
    AND amenity IN ('bench','waste_basket','toilets','fountain');
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION street_furniture() 
IS '**FOR-API-FUNCTION** RETURNS col_names[amenity,tags,geom] **FOR-API-FUNCTION**';
