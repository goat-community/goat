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

--sidewalk quality
UPDATE footpaths_union f SET sidewalk = 'yes' where sidewalk is null and highway in ('footway', 'path', 'cycleway', 'living_street', 'steps', 'pedestrian');
UPDATE footpaths_union f SET sidewalk = 'no' where sidewalk is null;
UPDATE footpaths_union f SET smoothness = 'average' where smoothness is null;

UPDATE footpaths_union f SET sidewalk_quality = 
(
    select_weight_walkability('sidewalk',sidewalk) 
	+ select_weight_walkability('smoothness',smoothness) 
	+ select_weight_walkability('surface',surface)
	+ select_weight_walkability('wheelchair',wheelchair)
	+ select_weight_walkability_range('width', width)
)
*(100/0.29);

