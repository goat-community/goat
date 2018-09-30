CREATE OR REPLACE FUNCTION public.thematic_data_sum(input_objectid integer)
 RETURNS TABLE(gid_isochrone integer, pois_isochrones jsonb)
 LANGUAGE plpgsql
AS $function$
begin
	
with yy as (
with xx as (
	select a.gid,count(*) as count_address,
	sum(a.population)::integer+(5-(sum(a.population)::integer%5)) as sum_pop 
	from
	(select distinct concat(street,housenumber),population,isochrone_gid as gid
	from (select a.*,i.gid isochrone_gid 
		  from addresses_residential a, isochrones i
     	  where objectid = input_objectid 
     	  and st_intersects(i.geom,a.geom))x) a
	group by a.gid
	)
select gid,count_address as count,'address' as pois_type from xx
union all 
select gid,sum_pop, 'population' from xx
union all
select p.* from (
	select i.gid,count(*),amenity from isochrones i, 
	pois p
	where st_intersects(i.geom,p.geom)  and objectid=input_objectid and shop is null
	group by i.gid,amenity
	union all
	select i.gid,count(*),shop from isochrones i, 
	pois p
	where st_intersects(i.geom,p.geom)  and objectid=input_objectid and amenity is null
	group by i.gid,shop) p
	,variable_container
where amenity = any(variable_array)
and identifier = 'poi_categories'
union all
select gid,count(*),public_transport_stop
from
	(select i.gid, p.name,public_transport_stop,1 as count
	from public_transport_stops p, isochrones i
	where st_intersects(i.geom,p.geom)
	and i.objectid = input_objectid
	group by i.gid,public_transport_stop,p.name) p
group by gid,public_transport_stop)
update isochrones set sum_pois = jsonb_object::text 
from (
select gid,jsonb_object(array_agg(pois_type),array_agg(count::text)) from yy
group by gid) x 
where isochrones.gid = x.gid;
END ;
$function$
