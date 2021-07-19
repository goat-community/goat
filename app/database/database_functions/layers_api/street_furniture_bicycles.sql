CREATE OR REPLACE FUNCTION street_furniture_bicycles()
RETURNS TABLE (amenity text, geom geometry) AS
$$
    SELECT f.amenity, f.geom 
    FROM street_furniture f, study_area s
    WHERE st_intersects(s.geom,f.geom) 
    AND amenity IN ('bicycle_parking')
;
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION street_furniture_bicycles() 
IS '**FOR-API-FUNCTION** RETURNS col_names[amenity,geom] **FOR-API-FUNCTION**';
