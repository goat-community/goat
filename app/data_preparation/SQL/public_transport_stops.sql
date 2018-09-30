
--------------------------------------------------------------------------
--Create first pois as it is continuing with gid----------------------------
--------------------------------------------------------------------------



--Alter table hilfstabelle_pois
--alter table hilfstabelle_pois add column bus_station integer;
--alter table hilfstabelle_pois add column subway_station integer;
--alter table hilfstabelle_pois add column tram_station integer;
--alter table hilfstabelle_pois add column railway_station integer;


--Create public_transport_stops
drop table if exists public_transport_stops;
select *, (select max(gid) from pois) + row_number() over() as gid
into public_transport_stops from (
select 'bus_stop' as public_transport_stop,name,way as geom from planet_osm_point 
where highway = 'bus_stop' and name is not null
union all
select 'bus_stop' as public_transport_stop,name,way as geom from planet_osm_point 
where public_transport = 'platform' and name is not null and tags -> 'bus'='yes'
union all
select 'tram_stop' as public_transport_stop,name,way as geom from planet_osm_point 
where public_transport = 'stop_position' 
and tags -> 'tram'='yes'
and name is not null
union all
select  'subway_entrance' as public_transport,name, way as geom from planet_osm_point
where railway = 'subway_entrance'
union all
select 'sbahn_regional' as public_transport,name,way as geom 
from planet_osm_point where railway = 'stop'
and tags -> 'train' ='yes') x;



update public_transport_stops set name = x.name 
from
(select p.geom,x.name,min(st_distance(p.geom::geography,x.geom::geography))
from public_transport_stops p,
	(select 'subway' as public_transport,name,way as geom  from planet_osm_point 
	where public_transport ='station' and
	tags -> 'subway' = 'yes' and railway <> 'proposed') x
where st_dwithin(p.geom::geography,x.geom::geography,500)
group by p.geom,x.name) x
where public_transport_stops.geom = x.geom
and public_transport_stop = 'subway_entrance';



alter table public_transport_stops add primary key (gid); 
CREATE INDEX index_public_transport_stops ON public_transport_stops USING GIST (geom);
