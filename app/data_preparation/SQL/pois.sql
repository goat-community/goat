drop table if exists pois;
create table pois as (

select osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
from planet_osm_point
where amenity is not null and shop is null and amenity <> 'school'

union all 

select osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
from planet_osm_point
where shop is not null and amenity is null

union all 

select osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
from planet_osm_polygon
where amenity is not null and amenity <> 'school' 

union all 

select osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
from planet_osm_polygon
where shop is not null 


union all

select osm_id, access,"addr:housenumber" as housenumber, tourism, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
from planet_osm_point
where tourism is not null


union all 

select * from (
select osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom
from planet_osm_polygon
where amenity = 'school') x
where name LIKE '%Grundschule%'
or name like 'gymnasium' 
or name like '%Mittelschule%' 
or name like '%Realschule%'
or name like '%Haupt%'

union all 

select * from (
select osm_id, access,"addr:housenumber" as housenumber, amenity, shop, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom
from planet_osm_point
where amenity = 'school') x
where name LIKE '%Grundschule%'
or name like '%gymnasium%' 
or name like '%Mittelschule%' 
or name like '%Haupt%'
or name like '%Realschule%'
);



update pois set amenity = 'primary_school'
where amenity = 'school' 
and name LIKE '%Grundschule%';

update pois set amenity = 'secondary_school'
where amenity = 'school' 
and name like '%gymnasium%' 
or name like '%Mittelschule%' 
or name like '%Haupt%'
or name like '%Realschule%';


--For Munich grocery == convencience
update pois set shop = 'convenience'
where shop ='grocery';

update pois set shop = 'clothes'
where shop ='fashion';


alter table pois add column gid serial;

alter table pois add primary key(gid); 


CREATE INDEX index_pois ON pois USING GIST (geom);

