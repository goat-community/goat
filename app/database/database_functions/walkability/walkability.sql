--THIS FILE NEEDS TO BE EXECUTED TO COMPUTE THE WALKBILITY INDICES

--Add columns for the walkability criteria
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS sidewalk_quality numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS traffic_protection numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS security numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS vegetation numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS walking_environment numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS comfort numeric;
ALTER TABLE footpaths_union ADD COLUMN IF NOT EXISTS walkability numeric;

------------------------
--Calculate the values--
------------------------


--sidewalk quality--
--prepara data
UPDATE footpaths_union f SET sidewalk = 'yes' where sidewalk is null and highway in ('footway', 'path', 'cycleway', 'living_street', 'steps', 'pedestrian');
UPDATE footpaths_union f SET sidewalk = 'no' where sidewalk is null;
UPDATE footpaths_union f SET smoothness = 'average' where smoothness is null;
UPDATE footpaths_union f SET smoothness = 'excellent' where smoothness = 'very_good';
UPDATE footpaths_union f SET surface = 'average' where surface is null;
UPDATE footpaths_union f SET width = 2.0 where width is null;

--calculate score
UPDATE footpaths_union f SET sidewalk_quality = 
(
    select_weight_walkability('sidewalk',sidewalk) 
	+ select_weight_walkability('smoothness',smoothness) 
	+ select_weight_walkability('surface',surface)
	+ select_weight_walkability('wheelchair',wheelchair_classified)
	+ select_weight_walkability_range('width', width)
)
*(100/0.29);

--traffic protection--
--prepara data
DROP TABLE IF EXISTS highway_buffer;
CREATE TABLE highway_buffer as
SELECT ST_BUFFER(geom,0.00015,'quad_segs=8') AS geom, lanes, oneway, maxspeed_forward, parking 
FROM ways 
WHERE highway IN ('living_street','residential','secondary','tertiary','primary');

UPDATE footpaths_union f SET lanes = 1 where lanes is null;
UPDATE footpaths_union f SET lanes = h.lanes
FROM highway_buffer h
WHERE ST_Within(f.geom,h.geom) and h.lanes is not null;

UPDATE footpaths_union f SET maxspeed_forward = 30 where highway in ('service','cycleway');
UPDATE footpaths_union f SET maxspeed_forward = 5 where highway in ('footpath','path','footway','track','steps','pedestrian');
UPDATE footpaths_union f SET maxspeed_forward = h.maxspeed_forward
FROM highway_buffer h
WHERE ST_Within(f.geom,h.geom) and h.maxspeed_forward is not null;

UPDATE footpaths_union f SET parking = 'lane' where (parking_lane_both is not null or parking_lane_left is not null OR parking_lane_right is not null);
UPDATE footpaths_union f SET parking = 'no' where parking is null;
UPDATE footpaths_union f SET parking = h.parking
FROM highway_buffer h
WHERE ST_Within(f.geom,h.geom) and h.parking is not null;


--calculate score
UPDATE footpaths_union f SET traffic_protection = 
(
    select_weight_walkability_range('lanes',lanes) 
	+ select_weight_walkability_range('maxspeed',maxspeed_forward)
	+ select_weight_walkability('parking',parking)
)
*(100/0.14);