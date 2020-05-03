ALTER TABLE study_area ALTER COLUMN sum_pop TYPE integer using sum_pop::integer;
ALTER TABLE study_area DROP COLUMN IF EXISTS area;
ALTER TABLE study_area add column area float;
UPDATE study_area set area = st_area(geom::geography);

ALTER TABLE buildings ADD COLUMN IF NOT EXISTS building_levels integer;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS roof_levels integer;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS building_levels_residential integer;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS area numeric;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS residential_status text;

UPDATE buildings 
SET buildings_levels = CASE WHEN trunc(height/3)::integer = 0 THEN 1 ELSE trunc(height/3)::integer END AS building_levels, 
area = ST_AREA(geom::geography)::integer,
roof_levels = NULL; 

UPDATE buildings 
SET status_residential = 'potential_residential';

UPDATE buildings 
SET status_residential = 'no_residents'
FROM landuse l
WHERE ST_Intersects(b.geom,l.geom)
AND l.landuse IN(SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'custom_landuse_no_residents')
OR ST_Area(b.geom::geography) < (SELECT select_from_variable_container_s('minimum_building_size_residential')::integer);


UPDATE buildings
SET residential_status = 'no_residents'
FROM (
	SELECT b.gid
	FROM buildings b
	LEFT JOIN landuse l 
	ON ST_intersects(b.geom,l.geom)
	WHERE l.gid IS NULL 
	AND b.residential_status = 'potential_residents'
) x
WHERE buildings.gid = x.gid;


ALTER TABLE buildings_residential ADD COLUMN gid serial;
CREATE INDEX ON buildings_residential USING GIST(geom);
CREATE INDEX ON buildings_residential (gid);

ALTER TABLE buildings_residential ADD COLUMN building_levels_residential integer;

WITH b AS (
    SELECT DISTINCT b.gid
    FROM buildings_residential b, pois p 
    WHERE ST_intersects(b.geom,p.geom)
)
UPDATE buildings_residential 
SET building_levels_residential = building_levels - 1
FROM b
WHERE buildings_residential.gid = b.gid;
UPDATE buildings_residential 
SET building_levels_residential = building_levels
WHERE building_levels_residential IS NULL;