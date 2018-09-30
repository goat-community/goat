
--Drops the former created tables
drop table if exists building_derived_addresses;
drop table if exists directly_derived_addresses;
drop table if exists entrances_derived_addresses;
drop table if exists all_addresses;
drop table if exists house_address;


--Find all addresses tagged as points
select osm_id,tags -> 'addr:street' as street,"addr:housenumber" as housenumber,way as geom 
into directly_derived_addresses 
from planet_osm_point  
where (tags -> 'addr:street') is not null 
or "addr:housenumber" is not null 
order by street,"addr:housenumber";

CREATE INDEX index_directly_derived_addresses ON directly_derived_addresses USING GIST (geom);

--Find all buildings which have an address attached
SELECT h.* into house_address 
FROM  
(select osm_id,tags -> 'addr:street' as street,"addr:housenumber" as housenumber, tags -> 'addr:city' as city,way as geom 
from planet_osm_polygon  
where (tags -> 'addr:street') is not null 
or "addr:housenumber" is not null) h;






CREATE INDEX index_houses_address ON house_address USING GIST (geom);

--Find all entrances which are lying on a building

select x.osm_id,h.street,h.housenumber,x.geom 
into entrances_derived_addresses 
from (
	select osm_id,way as geom,tags -> 'door' as door,tags -> 'entrance' as entrance,tags, tags -> 'level' as level1, 
	exist(tags, 'subway') subway, 
	exist(tags, 'entrance_marker:subway') subway1, 
	exist(tags, 'indoor') indoor, 
	exist(tags, 'entrance_marker:s-train') sbahn, 
	exist(tags, 'entrance_marker:tram') tram 
	from planet_osm_point where "addr:housenumber" is null 
	) x, house_address h 

where subway = false and subway1 =false and indoor=false and sbahn=false and tram=false 
and entrance is not null 
and entrance <> 'emergency' 
and level1 is null 
and st_intersects(x.geom,h.geom);

CREATE INDEX index_entrances_derived_addresses  ON entrances_derived_addresses USING GIST (geom);


--entrances was changes to entrances derived (it has to be checked if results are good enough)
with x as (
	select h.osm_id
	from house_address h,entrances_derived_addresses e  
	where st_intersects(e.geom,h.geom)
),
xx as (
	select x.osm_id,street,housenumber,city,geom
	from house_address x where x.osm_id  
	not in (select * from x)
)
select osm_id,street,housenumber,st_centroid(geom) as geom 
into building_derived_addresses 
from xx;


CREATE INDEX index_building_derived_addresses ON building_derived_addresses USING GIST (geom);

--Add columns for the origin of the address

alter table building_derived_addresses add column origin varchar(20);
alter table directly_derived_addresses add column origin varchar(20);
alter table entrances_derived_addresses add column origin varchar(20);

update building_derived_addresses set origin='building';
update directly_derived_addresses set origin='point_data';
update entrances_derived_addresses set origin ='entrances';


alter table building_derived_addresses add column x varchar;
update building_derived_addresses set x=concat(street,housenumber);

alter table entrances_derived_addresses add column x varchar;
update entrances_derived_addresses set x=concat(street,housenumber);

alter table directly_derived_addresses add column x varchar;
update directly_derived_addresses set x=concat(street,housenumber);


-- Merge all the addresses together
drop table if exists all_addresses;
select *,(select max(gid) from public_transport_stops) + row_number() over() as gid
into all_addresses from  
(select * from entrances_derived_addresses 
union all 
select * from directly_derived_addresses 
union all 
select * from building_derived_addresses where x not in(select x from directly_derived_addresses)) as x;



CREATE INDEX index_all_addresses ON all_addresses USING GIST (geom);
ALTER TABLE all_addresses ADD PRIMARY KEY (id);
--Drop all not used tables and index
drop table if exists house_address; 
drop table if exists x;
drop table if exists xx;























