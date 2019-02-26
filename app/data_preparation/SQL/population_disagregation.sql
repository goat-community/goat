--All Building with no levels get building_levels = 2 AND roof_levels = 1
UPDATE buildings_residential 
set building_levels = (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'default_building_levels'), 
roof_levels = 1 
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
CREATE TABLE buildings_pop AS
with x as (
    SELECT m.gid,sum(b.area*building_levels_residential) as sum_buildings_area 
    FROM buildings_residential b, study_area m
    WHERE st_intersects(b.geom,m.geom) 
    GROUP BY m.gid
)
SELECT b.*,m.sum_pop as sum_population,m.area as area_administrative_boundary,
x.sum_buildings_area,
round(m.sum_pop*(b.area*building_levels_residential/sum_buildings_area)) as population_building
FROM buildings_residential b, x,
study_area m
WHERE st_intersects(b.geom,m.geom) AND x.sum_buildings_area <> 0
AND m.gid=x.gid;

DROP TABLE buildings_residential;
alter table buildings_pop drop column gid;
CREATE TABLE buildings_residential as 
SELECT * from buildings_pop ;
DROP TABLE buildings_pop;

CREATE INDEX index_buildings_residential ON buildings_residential  USING GIST (geom);
alter table buildings_residential add column gid serial;
ALTER TABLE buildings_residential add primary key(gid);


CREATE TABLE population AS 
SELECT ST_Centroid(geom) geom,population_building population 
FROM buildings_residential;
CREATE INDEX index_population ON population USING GIST (geom);
ALTER TABLE population ADD COLUMN gid serial;
ALTER TABLE population ADD PRIMARY KEY(gid);



