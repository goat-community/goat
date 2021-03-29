CREATE OR REPLACE FUNCTION ways_parking()
RETURNS TABLE (parking text, parking_lane text, highway text, geom geometry) AS
$$
    SELECT p.parking, p.parking_lane, p.highway, p.geom 
    FROM parking p, study_area s
    WHERE ST_Intersects(p.geom,s.geom);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION ways_parking() 
IS '**FOR-API-FUNCTION** RETURNS col_names[parking,parking_lane,highway,geom] **FOR-API-FUNCTION**';