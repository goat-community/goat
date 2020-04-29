ALTER TABLE study_area ALTER COLUMN sum_pop TYPE integer using sum_pop::integer;
ALTER TABLE study_area DROP COLUMN IF EXISTS area;
ALTER TABLE study_area add column area float;
UPDATE study_area set area = st_area(geom::geography);


DROP TABLE IF EXISTS buildings_residential;
DROP TABLE IF EXISTS buildings_residential_table;
DROP TABLE IF EXISTS buildings_pop;
DROP TABLE IF EXISTS landuse_no_residents;
DROP TABLE IF EXISTS non_residential_ids;
DROP TABLE IF EXISTS population;
DROP TABLE IF EXISTS landuse_osm;


CREATE TABLE buildings_residential_table as 
SELECT osm_id,building, "addr:housenumber",tags,way as geom
FROM planet_osm_polygon 
WHERE building IS NOT NULL
AND leisure IS NULL
AND amenity IS NULL
AND tourism IS NULL
AND office IS NULL
AND shop IS NULL
AND sport IS NULL
AND building IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'building_types_potentially_residential');


CREATE TABLE landuse_no_residents AS 
SELECT way 
FROM planet_osm_polygon 
WHERE landuse IN(SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'osm_landuse_no_residents')
OR tourism IN(SELECT UNNEST(variable_array)  FROM variable_container WHERE identifier = 'tourism_no_residents')
OR amenity IN(SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'amenity_no_residents');


CREATE INDEX index_buildings_residential_table ON buildings_residential_table  USING GIST (geom);
CREATE INDEX index_landuse ON landuse_no_residents USING GIST (way);

CREATE TABLE non_residential_ids AS
SELECT osm_id
FROM planet_osm_polygon b,landuse_no_residents lu
WHERE st_intersects(b.way,lu.way) AND ST_Area(ST_Intersection(b.way, lu.way)) / ST_Area(b.way) > 0.5
AND building NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'building_types_residential');

DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse'
            )
        THEN
			--Intersect with custom landuse table
			INSERT INTO non_residential_ids 
			SELECT p.osm_id FROM 
			landuse l, variable_container v, planet_osm_polygon p
			WHERE l.landuse IN(SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'custom_landuse_no_residents')
			AND p.building NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'building_types_residential')
			AND st_intersects(p.way,l.geom) AND ST_Area(ST_Intersection(p.way, l.geom)) / ST_Area(p.way) > 0.5;
        END IF ;
    END
$$ ;

--Delete duplicates 
CREATE TABLE distinct_non_residential_ids AS 
SELECT DISTINCT osm_id FROM non_residential_ids;
DROP TABLE non_residential_ids;
ALTER TABLE distinct_non_residential_ids RENAME TO non_residential_ids;

ALTER TABLE buildings_residential_table add column gid serial;
ALTER TABLE buildings_residential_table add primary key(gid);
ALTER TABLE non_residential_ids add column gid serial;
ALTER TABLE non_residential_ids add primary key(gid);

--All buildings smaller 54 square meters are excluded
DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse'
            )
        THEN			
			CREATE TABLE buildings_residential AS
			WITH x AS (
			SELECT b.* ,st_area(b.geom::geography) as area, 
			CASE WHEN (tags -> 'building:levels')~E'^\\d+$' THEN (tags -> 'building:levels')::integer ELSE null end as building_levels,
			CASE WHEN (tags -> 'roof:levels')~E'^\\d+$' THEN (tags -> 'roof:levels')::integer ELSE null end as roof_levels
			FROM buildings_residential_table b, landuse l
			WHERE  st_intersects(b.geom,l.geom) and ST_Area(b.geom::geography) > (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'minimum_building_size_residential')
			)
			SELECT DISTINCT x.* 
			FROM x 
			LEFT JOIN non_residential_ids n
			ON  x.osm_id = n.osm_id
			WHERE n.gid IS NULL; 
		ELSE
			CREATE TABLE buildings_residential AS
			WITH x AS (
				SELECT b.* ,st_area(b.geom::geography) as area, 
				CASE WHEN (tags -> 'building:levels')~E'^\\d+$' THEN (tags -> 'building:levels')::integer ELSE null end as building_levels,
				CASE WHEN (tags -> 'roof:levels')~E'^\\d+$' THEN (tags -> 'roof:levels')::integer ELSE null end as roof_levels
				FROM buildings_residential_table b
				WHERE  ST_Area(b.geom::geography) > (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'minimum_building_size_residential')
			)
			SELECT DISTINCT x.* 
			FROM x 
			LEFT JOIN non_residential_ids n
			ON  x.osm_id = n.osm_id
			WHERE n.gid IS NULL; 
        END IF ;
    END
$$ ;

UPDATE buildings_residential 
set building_levels = (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'default_building_levels'), 
roof_levels = 1 
WHERE building_levels IS NULL;

--Substract one level when POI on building (more classification has to be done in the future)

ALTER TABLE buildings_residential 
ADD COLUMN building_levels_residential integer; 

with x as (
    SELECT distinct b.gid
    FROM buildings_residential b, pois p 
    WHERE st_intersects(b.geom,p.geom)
)
UPDATE buildings_residential 
set building_levels_residential = building_levels - 1
FROM x
WHERE buildings_residential.gid = x.gid;
UPDATE buildings_residential 
set building_levels_residential = building_levels
WHERE building_levels_residential IS NULL;

CREATE TABLE landuse_osm AS 
SELECT landuse, name, tags, way AS geom 
FROM planet_osm_polygon 
WHERE landuse IS NOT NULL;

DROP TABLE buildings_residential_table;
DROP TABLE non_residential_ids;
DROP TABLE IF EXISTS landuse_no_residents;