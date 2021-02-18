CREATE OR REPLACE FUNCTION mapping_ways_speed()
RETURNS TABLE (osm_id bigint, highway text, geom geometry) AS
$$
    SELECT w.osm_id,w.highway,w.geom
    FROM ways_mapping w, study_area s 
    WHERE w.highway IN ('motorway','trunk','primary','secondary','tertiary','residential','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link',
    'living_street', 'unclassified')
    AND ST_Intersects(s.geom,w.geom)
    AND maxspeed IS NULL;
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION mapping_ways_speed() 
IS '**FOR-API-FUNCTION** RETURNS col_names[osm_id,highway,geom] **FOR-API-FUNCTION**';