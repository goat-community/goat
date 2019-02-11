

ALTER TABLE study_area ALTER COLUMN sum_pop TYPE integer using sum_pop::integer;

ALTER TABLE study_area DROP COLUMN IF EXISTS area;

DROP TABLE IF EXISTS buildings_residential;
DROP TABLE IF EXISTS buildings_residential_table;
DROP TABLE IF EXISTS buildings_pop;
DROP TABLE IF EXISTS leisure_table;
DROP TABLE IF EXISTS school_table;
DROP TABLE IF EXISTS landuse_table;
DROP TABLE IF EXISTS non_residential_ids;
DROP TABLE IF EXISTS population;

ALTER TABLE study_area add column area float;

UPDATE study_area set area = st_area(geom::geography);

CREATE TABLE buildings_residential_table as 
SELECT osm_id,building, "addr:housenumber",tags,way as geom
FROM planet_osm_polygon 
WHERE building IS NOT NULL
AND leisure IS NULL
AND name IS NULL
AND amenity IS NULL
AND tourism IS NULL
AND shop IS NULL
AND sport IS NULL
AND building in('residential','yes','house','detached','terrace','apartments','home');

SELECT way INTO leisure_table FROM planet_osm_polygon WHERE leisure IS NOT NULL;

SELECT way INTO school_table FROM planet_osm_polygon WHERE amenity ='school';

SELECT way INTO landuse_table 
FROM planet_osm_polygon 
WHERE landuse in('quarry','industrial','retail','commercial','military','cemetery','landfill','allotments','recreation ground','railway')
OR tourism ='zoo'
OR amenity='hospital'
OR amenity='university'
OR amenity='community_centre';


CREATE INDEX index_buildings_residential_table ON buildings_residential_table  USING GIST (geom);
CREATE INDEX index_leisure ON leisure_table  USING GIST (way);
CREATE INDEX index_landuse ON landuse_table USING GIST (way);
CREATE INDEX index_schools ON school_table   USING GIST (way);


CREATE TABLE non_residential_ids as
SELECT osm_id FROM
(SELECT osm_id 
FROM planet_osm_polygon b,school_table s
WHERE st_intersects(b.way,s.way)
AND building IS NOT NULL
UNION ALL 
SELECT osm_id  
FROM planet_osm_polygon b,leisure_table l
WHERE st_intersects(b.way,l.way)
AND building IS NOT NULL
UNION ALL
SELECT osm_id
FROM planet_osm_polygon b,landuse_table lu
WHERE st_intersects(b.way,lu.way)
AND building IS NOT NULL) as x;


--Intersect with custom landuse table
insert INTO non_residential_ids 
SELECT p.osm_id FROM 
landuse l, variable_container v, planet_osm_polygon p
WHERE l.landuse = any(variable_array)
AND v.identifier = 'landuse_with_no_residents'
AND p.building IS NOT NULL 
AND st_intersects(p.way,l.geom);
--Delete duplicates 
WITH x AS
    (SELECT DISTINCT osm_id FROM non_residential_ids)
DELETE FROM non_residential_ids 
WHERE osm_id NOT IN (SELECT osm_id FROM x);



ALTER TABLE buildings_residential_table add column gid serial;

ALTER TABLE buildings_residential_table add primary key(gid);

ALTER TABLE non_residential_ids add column gid serial;

ALTER TABLE non_residential_ids add primary key(gid);

--All buildings smaller 54 square meters are excluded

CREATE TABLE buildings_residential as
SELECT b.* ,st_area(b.geom::geography) as area, 
CASE WHEN (tags -> 'building:levels')~E'^\\d+$' THEN (tags -> 'building:levels')::integer ELSE null end as building_levels,
CASE WHEN (tags -> 'roof:levels')~E'^\\d+$' THEN (tags -> 'roof:levels')::integer ELSE null end as roof_levels
FROM buildings_residential_table b, landuse l
WHERE b.osm_id not in(SELECT osm_id FROM non_residential_ids)
AND ST_Intersects(b.geom,l.geom) 
AND ST_Area(b.geom::geography) > 54;


--All Building with no levels get building_levels = 2 AND roof_levels = 1
UPDATE buildings_residential 
set building_levels = 2, roof_levels = 1 
WHERE building_levels IS NULL;

--Substract one level when POI on building (more classification has to be done in the future)

ALTER TABLE buildings_residential 
add column building_levels_residential integer; 

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


--Population of each adminstrative boundary is assigned to the residential buildings

with x as (
SELECT m.gid,sum(b.area*building_levels_residential) as sum_buildings_area 
FROM buildings_residential b, study_area m
WHERE st_intersects(b.geom,m.geom) 
GROUP BY m.gid
)
SELECT b.*,m.sum_pop as sum_population,m.area as area_administrative_boundary,
x.sum_buildings_area,
round(m.sum_pop*(b.area*building_levels_residential/sum_buildings_area)) as population_building
INTO buildings_pop
FROM buildings_residential b, x,
study_area m
WHERE st_intersects(b.geom,m.geom) AND x.sum_buildings_area <> 0
AND m.gid=x.gid;




DROP TABLE buildings_residential;
alter table buildings_pop drop column gid;
select * into buildings_residential from buildings_pop ;
drop table buildings_pop;
CREATE INDEX index_buildings_residential ON buildings_residential  USING GIST (geom);
alter table buildings_residential add column gid serial;
ALTER TABLE buildings_residential add primary key(gid);


CREATE TABLE population AS 
SELECT ST_Centroid(geom) geom,population_building population 
FROM buildings_residential;
CREATE INDEX index_population ON population USING GIST (geom);
ALTER TABLE population ADD COLUMN gid serial;
ALTER TABLE population ADD PRIMARY KEY(gid);

DROP TABLE buildings_residential_table;
DROP TABLE leisure_table;
DROP TABLE landuse_table;
DROP TABLE school_table;
DROP TABLE non_residential_ids;

