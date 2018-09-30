CREATE OR REPLACE FUNCTION public.thematic_data_json(input_gid integer)
 RETURNS TABLE(gid_isochrone integer, pois_isochrones text)
 LANGUAGE plpgsql
AS $function$
begin
	

	
	--Pois and public transport stops are combined and all which are intersecting with the isochrones
	--are selected.
with var_poi as (
		select i.gid,i.step, p.gid as poi_gid,p.amenity,p.name, p.geom  
		from pois p,isochrones i,variable_container v 
		where v.identifier = 'poi_categories'
		and amenity = any(variable_array)
		and i.gid= input_gid
		and st_intersects(p.geom,i.geom)
		union all 
		select i.gid,i.step, p.gid as poi_gid,p.shop,p.name, p.geom  
		from pois p,isochrones i,variable_container v 
		where v.identifier = 'poi_categories'
		and shop = any(variable_array)
		and i.gid= input_gid
		and st_intersects(p.geom,i.geom)
		union all
		select i.gid,i.step,p.gid as poi_gid,public_transport_stop,p.name,p.geom
		from public_transport_stops p, isochrones i
		where i.gid= input_gid
		and st_intersects(p.geom,i.geom)
		
	)	
	
	--The distance from each POI/transport stop to a calculated vertex from the edges table
	--is calculated and the cost is passed is saved.
	--!!!!The selection of the nearest vertex has to be improved!!!!
	,min_dist as (
		select  poi_gid,name,amenity,v.id,st_distance(x.geom,v.geom) as min_dist,x.geom 
		from  ways_vertices_pgr v,var_poi x
		where 
		v.id 
		in(select node from edges where objectid= (select distinct objectid from isochrones where gid = input_gid))
		and St_dwithin(v.geom::geography,x.geom::geography,50,true)
	)
	
	,min_dist1 as (
		select * from min_dist where min_dist <> 0
		and min_dist in(
		select min(min_dist) from min_dist group by poi_gid)
	)	
		
	--The pois are saved as jsonb and saved at the isochrones table	
	,test_pois as (
		select amenity,name,cost from min_dist1 m,
		(select node,min(cost) as cost from edges 
		where objectid = (select objectid from isochrones where gid = input_gid) 
		group by node) x
		where m.id = x.node
	
	)
	update isochrones set pois = z.array_to_json::text
	from (
	select input_gid,array_to_json(array_agg(row_to_json(x))) from(
	select amenity,name,min(cost) as cost from test_pois --Every entrance or bus_stop is only counted once (shortest distance is taken)
	where amenity in('subway_entrance','bus_stop','tram_stop','sbahn_regional') 
	group by amenity,name
	union all
	select amenity,name,cost from test_pois
	where amenity not in('subway_entrance','bus_stop','tram_stop','sbahn_regional'))x) z 
	where isochrones.gid = z.input_gid;
		
		--update isochrones set pois = zz.array_to_json 
	--from 
		--where isochrones.gid = zz.gid;
	
	--The same is done for the population
	--Be aware the population data is saved without geometry and address (data privacy!)
	--with var_population as (
	--		select i.gid,i.step, p.gid address_gid,p.population,p.geom 
		--	from addresses_residential p,isochrones i
			--where gid= input_gid
			--and st_intersects(p.geom,i.geom)
			
			
	--	)	
	--!!!!The selection of the nearest vertex has to be improved!!!!	
	--,min_dist as (
		--select  min(st_distance(x.geom,v.geom)) as min_dist,
		--x.address_gid,v.id 
		--from  ways_vertices_pgr v,var_population x
		--where v.id in
		--(select node from edges where gid= input_gid)
		--and St_dwithin(v.geom::geography,x.geom::geography,50,true)
		--group by x.address_gid,v.id
		--)
	--update isochrones set population = zz.array_to_json 
	--from 	
	--(select gid,array_to_json(array_agg(row_to_json(z))) from	
	--(select v.gid,v.step,v.address_gid,v.population,cost 
	--from var_population v,	
	--(select min(cost) as cost,address_gid 
	--from min_dist m,edges where m.id=node
	--group by address_gid) z
	--where v.address_gid = z.address_gid) z
	--group by gid) zz
	--where isochrones.gid = zz.gid;
	return query select i.gid, i.pois from isochrones i where gid= input_gid;
END ;
$function$
