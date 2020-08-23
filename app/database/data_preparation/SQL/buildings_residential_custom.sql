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
SET building_levels = CASE WHEN trunc(height/3)::integer = 0 THEN 1 ELSE trunc(height/3)::integer END, 
area = ST_AREA(geom::geography)::integer,
roof_levels = NULL; 

UPDATE buildings 
SET residential_status = 'potential_residential';

UPDATE buildings b
SET residential_status = 'no_residents'
FROM landuse l
WHERE ST_Intersects(b.geom,l.geom)
AND l.landuse IN(SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'custom_landuse_no_residents');

UPDATE buildings SET residential_status = 'no_residents'
WHERE ST_Area(geom::geography) < (SELECT select_from_variable_container_s('minimum_building_size_residential')::integer);

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

WITH b AS (
    SELECT DISTINCT b.gid
    FROM buildings b, pois p 
    WHERE ST_intersects(b.geom,p.geom)
)
UPDATE buildings 
SET building_levels_residential = building_levels - 1
FROM b
WHERE buildings.gid = b.gid;
UPDATE buildings 
SET building_levels_residential = building_levels
WHERE building_levels_residential IS NULL;

CREATE TABLE landuse_osm AS 
SELECT ROW_NUMBER() OVER() AS gid, landuse, tourism, amenity, name, tags, way AS geom 
FROM planet_osm_polygon 
WHERE landuse IS NOT NULL;

CREATE INDEX ON landuse_osm USING GIST(geom);
ALTER TABLE landuse_osm ADD PRIMARY key(gid);

UPDATE buildings b SET residential_status = 'no_residents'
FROM landuse_osm l
WHERE l.landuse IN (SELECT UNNEST(select_from_variable_container('osm_landuse_no_residents')))
AND ST_INTERSECTS(l.geom,b.geom)
AND b.residential_status = 'potential_residential';

/*Temporary fix*/
UPDATE buildings 
SET residential_status = 'with_residents'
WHERE residential_status = 'potential_residential';


