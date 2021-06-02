DROP TABLE IF EXISTS buildings_residential;
CREATE TABLE buildings_residential AS 
SELECT * 
FROM buildings
WHERE residential_status = 'with_residents';

DROP TABLE IF EXISTS households;
--Population of each adminstrative boundary is assigned to the residential buildings
CREATE TABLE buildings_hh AS
with x as (
    SELECT m.gid,sum(b.area*building_levels_residential) as sum_buildings_area 
    FROM buildings_residential b, study_area m
    WHERE st_intersects(ST_Centroid(b.geom),m.geom) 
    GROUP BY m.gid
)
SELECT b.*,m.sum_hh as sum_hh,m.area as area_administrative_boundary,
x.sum_buildings_area,
m.sum_hh*(b.area*building_levels_residential/sum_buildings_area) as hh_building
FROM buildings_residential b, x,
study_area m
WHERE st_intersects(St_Centroid(b.geom),m.geom) AND x.sum_buildings_area <> 0
AND m.gid=x.gid;

DROP TABLE buildings_residential;
ALTER TABLE buildings_hh drop column gid;
CREATE TABLE buildings_residential as 
SELECT * from buildings_hh ;
DROP TABLE buildings_hh;

CREATE INDEX index_buildings_residential ON buildings_residential  USING GIST (geom);
alter table buildings_residential add column gid serial;
ALTER TABLE buildings_residential add primary key(gid);


CREATE TABLE households AS 
SELECT ST_Centroid(geom) geom,hh_building households, gid as building_gid 
FROM buildings_residential;
CREATE INDEX index_households ON households USING GIST (geom);
ALTER TABLE households ADD COLUMN gid serial;
ALTER TABLE households ADD PRIMARY KEY(gid);

DROP TABLE IF EXISTS buildings_residential;