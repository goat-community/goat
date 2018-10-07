

select p.* from (
select i.gid,count(*),amenity from isochrones i, 
pois p
where st_intersects(i.geom,p.geom)  and objectid=2217719 and shop is null
group by i.gid,amenity
union all
select i.gid,count(*),shop from isochrones i, 
pois p
where st_intersects(i.geom,p.geom)  and objectid=2217719 and amenity is null
group by i.gid,shop
union all
select gid,count(*),public_transport_stop
from
(select i.gid, p.name,public_transport_stop,1 as count
from public_transport_stops p, isochrones i
where st_intersects(i.geom,p.geom)
and i.objectid = 2217719
group by i.gid,public_transport_stop,p.name) p
group by gid,public_transport_stop) p,variable_container
where amenity = any(variable_array)
and identifier = 'poi_categories';
