CREATE OR REPLACE FUNCTION street_furniture()
RETURNS TABLE (amenity text, geom geometry) AS
$$
	SELECT f.amenity, f.geom 
    FROM street_furniture f, study_area s
    WHERE st_intersects(s.geom,f.geom) 
    AND amenity IN ('bench','waste_basket','toilets','fountain');
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION street_furniture() 
IS '**FOR-API-FUNCTION** RETURNS col_names[amenity,geom] **FOR-API-FUNCTION**';
