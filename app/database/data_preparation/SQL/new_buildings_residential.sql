
SELECT * FROM landuse WHERE name LIKE '%Seniorenheim%'

SELECT * FROM landuse

ALTER TABLE landuse RENAME COLUMN nam TO name 

SELECT * 
FROM landuse
WHERE nam IS NOT NULL 

ALTER TABLE study_area ALTER COLUMN sum_pop TYPE integer using sum_pop::integer;
ALTER TABLE study_area DROP COLUMN IF EXISTS area;
ALTER TABLE study_area ADD COLUMN area numeric;
UPDATE study_area SET area = st_area(geom::geography);




DROP TABLE IF EXISTS buildings;

DROP TABLE IF EXISTS buildings_pop;

DROP TABLE IF EXISTS area_no_residents;

DROP TABLE IF EXISTS landuse_osm;



CREATE TABLE buildings as 
SELECT ROW_NUMBER() OVER() AS gid, osm_id,building, 
CASE 
WHEN building = 'yes' THEN 'potential_residents' 
WHEN building IN (SELECT UNNEST(select_from_variable_container('building_types_residential'))) THEN 'with_residents'
ELSE 'no_residents' END AS residential_status,
"addr:housenumber",tags,way as geom
FROM planet_osm_polygon 
WHERE building IS NOT NULL;

CREATE INDEX ON buildings USING GIST(geom);
ALTER TABLE buildings ADD PRIMARY key(gid);

CREATE TABLE landuse_osm AS 
SELECT ROW_NUMBER() OVER() AS gid, landuse, tourism, amenity, name, tags, way AS geom 
FROM planet_osm_polygon 
WHERE landuse IS NOT NULL;

CREATE INDEX ON landuse_osm USING GIST(geom);
ALTER TABLE landuse_osm ADD PRIMARY key(gid);

CREATE TABLE area_no_residents AS 
SELECT way AS geom 
FROM planet_osm_polygon 
WHERE landuse IN(SELECT UNNEST(select_from_variable_container('osm_landuse_no_residents')))
OR tourism IN(SELECT UNNEST(select_from_variable_container('tourism_no_residents')))
OR amenity IN(SELECT UNNEST(select_from_variable_container('amenity_no_residents')));

CREATE INDEX ON area_no_residents USING GIST(geom);

UPDATE buildings b
SET residential_status = 'no_residents'
FROM area_no_residents l
WHERE ST_Contains(l.geom,b.geom)
AND b.residential_status = 'potential_residents';

UPDATE buildings b
SET residential_status = 'no_residents'
FROM area_no_residents l 
WHERE ST_Contains(l.geom,b.geom) = FALSE 
AND ST_Intersects(l.geom,b.geom)
AND ST_Area(ST_Intersection(b.geom, l.geom)) / ST_Area(b.geom) > 0.5
AND b.residential_status = 'potential_residents';


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
			
        	ALTER TABLE landuse ADD COLUMN IF NOT EXISTS name text;
        
        	UPDATE buildings b
			SET residential_status = 'no_residents'
			FROM landuse l
			WHERE ST_Contains(l.geom,b.geom)
			AND b.residential_status = 'potential_residents'
			AND l.landuse IN(SELECT UNNEST(select_from_variable_container('custom_landuse_no_residents')))
			AND NOT lower(name) ~~ ANY (SELECT UNNEST(select_from_variable_container('custom_landuse_with_residents_name')));
		
			UPDATE buildings b
			SET residential_status = 'no_residents'
			FROM landuse l 
			WHERE ST_Contains(l.geom,b.geom) = FALSE 
			AND ST_Intersects(l.geom,b.geom)
			AND ST_Area(ST_Intersection(b.geom, l.geom)) / ST_Area(b.geom) > 0.5
			AND b.residential_status = 'potential_residents'
			AND l.landuse IN(SELECT UNNEST(select_from_variable_container('custom_landuse_no_residents')))
			AND NOT lower(name) ~~ ANY (SELECT UNNEST(select_from_variable_container('custom_landuse_with_residents_name')));
		
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



DROP TABLE buildings_residential_table;
DROP TABLE non_residential_ids;
DROP TABLE IF EXISTS landuse_no_residents;