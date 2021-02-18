CREATE OR REPLACE FUNCTION mapping_pois_opening_hours()
RETURNS TABLE (osm_id bigint, amenity text, name text, geom geometry) AS
$$
    WITH am AS 
    (
        SELECT string_to_array(amenity::text,',') AS amenity
        FROM convert_from(decode(%amenities%,'base64'),'UTF-8') AS amenity
    )
    SELECT osm_id, amenity, amenity || '_accessible' as amenity_icon, name, geom
    FROM pois_mapping
    WHERE opening_hours IS NULL
    AND amenity IN (SELECT UNNEST(amenity) FROM am);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION mapping_pois_opening_hours() 
IS '**FOR-API-FUNCTION** RETURNS col_names[osm_id,amenity,name,geom] **FOR-API-FUNCTION**';