CREATE OR REPLACE FUNCTION street_crossings()
RETURNS TABLE (osm_id bigint, geom geometry, crossing text, crossing_ref text, traffic_signals text, kerb text, segregated text, supervised text, tactile_paving text, wheelchair text) AS
$$
	SELECT c.osm_id, c.geom, c.crossing, c.crossing_ref, c.traffic_signals, c.kerb, c.segregated, c.supervised, c.tactile_paving, c.wheelchair
    FROM street_crossings c, study_area s
    WHERE ST_Intersects(s.geom,c.geom) 
    AND crossing IN ('zebra','traffic_signals');
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION street_crossings() 
IS '**FOR-API-FUNCTION** RETURNS col_names[osm_id,geom,crossing,crossing_ref,traffic_signals,kerb,segregated,supervised,tactile_paving,wheelchair] **FOR-API-FUNCTION**';
