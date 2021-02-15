CREATE OR REPLACE FUNCTION mapping_buildings_type()
RETURNS TABLE (osm_id bigint, building text, geom geometry) AS
$$
    SELECT b.osm_id, b.building, b.geom
    FROM buildings_mapping b , landuse l
    WHERE b.residential_status = 'with_residents'
    AND b.building = 'yes'
    AND ST_Intersects(b.geom,l.geom)
    AND l.landuse = 'AX_FlaecheGemischterNutzung';
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION mapping_buildings_type() 
IS '**FOR-API-FUNCTION** RETURNS col_names[osm_id,building,geom] **FOR-API-FUNCTION**';