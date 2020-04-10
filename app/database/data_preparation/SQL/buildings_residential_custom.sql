ALTER TABLE study_area ALTER COLUMN sum_pop TYPE integer using sum_pop::integer;
ALTER TABLE study_area DROP COLUMN IF EXISTS area;
ALTER TABLE study_area add column area float;
UPDATE study_area set area = st_area(geom::geography);

DROP TABLE IF EXISTS buildings_residential;
CREATE TABLE buildings_residential AS 
SELECT CASE WHEN trunc(height/3)::integer = 0 THEN 1 ELSE trunc(height/3)::integer END AS building_levels, 
ST_AREA(b.geom::geography) AS area,NULL AS roof_levels, b.geom 
FROM buildings b, landuse l
WHERE ST_Intersects(b.geom,l.geom)
AND l.landuse NOT IN(SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'custom_landuse_no_residents')
AND  ST_Area(b.geom::geography) > (SELECT select_from_variable_container_s('minimum_building_size_residential')::integer);


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