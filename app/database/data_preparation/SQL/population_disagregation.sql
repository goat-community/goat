DROP TABLE IF EXISTS buildings_residential;
CREATE TABLE buildings_residential AS 
SELECT * 
FROM buildings
WHERE residential_status = 'with_residents';

DROP TABLE IF EXISTS population;
--Population of each adminstrative boundary is assigned to the residential buildings
CREATE TABLE buildings_pop AS
with x as (
    SELECT m.gid,sum(b.area*building_levels_residential) as sum_buildings_area 
    FROM buildings_residential b, study_area m
    WHERE st_intersects(ST_Centroid(b.geom),m.geom) 
    GROUP BY m.gid
)
SELECT b.*,m.sum_pop as sum_population,m.area as area_administrative_boundary,
x.sum_buildings_area,
m.sum_pop*(b.area*building_levels_residential/sum_buildings_area) as population_building
FROM buildings_residential b, x,
study_area m
WHERE st_intersects(St_Centroid(b.geom),m.geom) AND x.sum_buildings_area <> 0
AND m.gid=x.gid;

DROP TABLE buildings_residential;
ALTER TABLE buildings_pop drop column gid;
CREATE TABLE buildings_residential as 
SELECT * from buildings_pop ;
DROP TABLE buildings_pop;

CREATE INDEX index_buildings_residential ON buildings_residential  USING GIST (geom);
alter table buildings_residential add column gid serial;
ALTER TABLE buildings_residential add primary key(gid);


CREATE TABLE population AS 
SELECT ST_Centroid(geom) geom,population_building population, gid as building_gid 
FROM buildings_residential;
CREATE INDEX index_population ON population USING GIST (geom);
ALTER TABLE population ADD COLUMN gid serial;
ALTER TABLE population ADD PRIMARY KEY(gid);

DROP TABLE IF EXISTS buildings_residential;