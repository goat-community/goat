

ALTER TABLE study_area ALTER COLUMN sum_pop TYPE integer using sum_pop::integer;

alter table study_area drop column area;

drop table if exists buildings_residential;
drop table if exists buildings_residential_table;
drop table if exists buildings_pop;
drop table if exists leisure_table;
drop table if exists school_table;
drop table if exists landuse_table;
drop table if exists non_residential_ids;

alter table study_area add column area float;

update study_area set area = st_area(geom::geography);

select osm_id,building, "addr:housenumber",tags,way as geom
into buildings_residential_table
from planet_osm_polygon 
where building is not null
and leisure is null
and name is null
and amenity is null
and tourism is null
and shop is null
and sport is null
and building in('residential','yes','house','detached','terrace','apartments','home');



select way into leisure_table from planet_osm_polygon where leisure is not null;

select way into school_table from planet_osm_polygon where amenity ='school';


select way into landuse_table 
from planet_osm_polygon 
where landuse in('quarry','industrial','retail','commercial','military','cemetery','landfill','allotments','recreation ground','railway')
or tourism ='zoo'
or amenity='hospital'
or amenity='university'
or amenity='community_centre';


CREATE INDEX index_buildings_residential_table ON buildings_residential_table  USING GIST (geom);
CREATE INDEX index_leisure ON leisure_table  USING GIST (way);
CREATE INDEX index_landuse ON landuse_table USING GIST (way);
CREATE INDEX index_schools ON school_table   USING GIST (way);

select osm_id as osm into non_residential_ids from
(select osm_id 
from planet_osm_polygon b,school_table s
where st_intersects(b.way,s.way)
and building is not null
union all 
select osm_id  
from planet_osm_polygon b,leisure_table l
where st_intersects(b.way,l.way)
and building is not null
union all
select osm_id
from planet_osm_polygon b,landuse_table lu
where st_intersects(b.way,lu.way)
and building is not null) as x;

alter table buildings_residential_table add column gid serial;

alter table buildings_residential_table add primary key(gid);

alter table non_residential_ids add column gid serial;

alter table non_residential_ids add primary key(gid);

--All buildings smaller 54 square meters are excluded

select * ,st_area(geom::geography) as area, 
(tags -> 'building:levels')::integer as building_levels, 
(tags -> 'roof:levels')::integer as roof_levels 
into buildings_residential
from buildings_residential_table b
where b.osm_id not in(select osm from non_residential_ids)
and st_area(geom::geography) > 54
;

--All Building with no levels get building_levels = 2 and roof_levels = 1
update buildings_residential 
set building_levels = 2, roof_levels = 1 
where building_levels is null;

--Substract one level when POI on building (more classification has to be done in the future)

alter table buildings_residential 
add column building_levels_residential integer; 

with x as (
    select distinct b.gid
    from buildings_residential b, pois p 
    where st_intersects(b.geom,p.geom)
)
update buildings_residential 
set building_levels_residential = building_levels - 1
from x
where buildings_residential.gid = x.gid;
update buildings_residential 
set building_levels_residential = building_levels
where building_levels_residential is null;

--Population of each adminstrative boundary is assigned to the residential buildings
with x as (
select m.gid,sum(b.area*building_levels_residential) as sum_buildings_area 
from buildings_residential b, study_area m
where st_intersects(b.geom,m.geom) 
group by m.gid
)
select b.*,m.sum_pop as sum_population,m.area as area_administrative_boundary,
x.sum_buildings_area,
round(m.sum_pop*(b.area*building_levels_residential/sum_buildings_area)) as population_building
into buildings_pop
from buildings_residential b, x,
study_area m
where st_intersects(b.geom,m.geom)
and m.gid=x.gid;

--drop table buildings_residential;

--alter table population_building rename to buildings_residential;


CREATE INDEX index_buildings_residential ON buildings_residential  USING GIST (geom);

alter table buildings_residential add primary key(gid);

drop table buildings_residential_table;
drop table leisure_table;
drop table landuse_table;
drop table school_table;
drop table non_residential_ids;


