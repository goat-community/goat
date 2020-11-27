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


