DROP FUNCTION IF EXISTS mapping_parking_lane;
CREATE OR REPLACE FUNCTION mapping_parking_lane()
RETURNS TABLE (osm_id bigint, highway text, "parking:lane:both" text, "parking:lane:left" text,
    "parking:lane:right" text, osm_type text, geom geometry) AS
$$
    SELECT w.osm_id, w.highway, "parking:lane:both", "parking:lane:left", "parking:lane:right", 'way' AS osm_type, w.geom
    FROM ways_mapping w, study_area s 
    WHERE w.highway IN ('primary','secondary','tertiary','residential','primary_link','secondary_link','tertiary_link',
    'living_street', 'unclassified')
    AND ST_Intersects(s.geom,w.geom)
    AND "parking:lane:both" IS NULL 
    AND "parking:lane:left" IS NULL 
    AND "parking:lane:right"IS NULL;
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION mapping_parking_lane() 
IS '**FOR-API-FUNCTION** RETURNS col_names[osm_id,highway,"parking:lane:both","parking:lane:left","parking:lane:right",osm_type,geom] **FOR-API-FUNCTION**';