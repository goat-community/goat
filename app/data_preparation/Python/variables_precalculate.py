prepare_tables = '''select * from hexagrid(grid_size); 

	with w as(
	select way as geom from planet_osm_polygon 
	where "natural" = 'water'
	),
	g as(
	select g.geom from grid_grid_size g, w
	where st_within(g.geom,w.geom)
	)
	delete from grid_grid_size where geom in (select * from g);


	ALTER TABLE grid_grid_size add column grid_id serial; 
	DROP TABLE IF EXISTS precalculate_walking_grid_size;
    create table precalculate_walking_grid_size(grid_id int4,step int4,geom geometry,thematic_data jsonb);

    ALTER TABLE grid_grid_size add column area_isochrone float8;

    ALTER TABLE grid_grid_size add column area_buffer float8;
	'''



thematic_data_sql ='''	--Pois and public transport stops are combined and all which are intersecting with the precalculate_walking_grid_size
	--are selected.
        with var_poi as (
		select i.grid_id,i.step, p.gid as poi_gid,p.amenity,p.name, p.geom  
		from pois p,precalculate_walking_grid_size i,variable_container v 
		where v.identifier = 'poi_categories'
		and amenity = any(variable_array)
		and i.grid_id= grid_id_replace
		and st_intersects(p.geom,i.geom)
		union all
		select i.grid_id,i.step,p.gid as poi_gid,public_transport_stop,p.name,p.geom
		from public_transport_stops p, precalculate_walking_grid_size i
		where i.grid_id= grid_id_replace
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
		in(select node from edges_temp)
		and St_dwithin(v.geom::geography,x.geom::geography,50,true)
	)
	
	,min_dist1 as (
		select * from min_dist where min_dist <> 0
		and min_dist in(
		select min(min_dist) from min_dist group by poi_gid)
	)	
		
	--The pois are saved as jsonb and saved at the precalculate_walking_grid_size table	
	,test_pois as (
		select amenity,name,cost from min_dist1 m,
		(select node,min(cost) as cost from edges_temp 
		group by node) x
		where m.id = x.node
	
	)
	UPDATE precalculate_walking_grid_size set thematic_data = z.array_to_json
	from (
	select grid_id_replace,array_to_json(array_agg(row_to_json(x))) from(
	select amenity,name,min(cost) as cost from test_pois --Every entrance or bus_stop is only counted once (shortest distance is taken)
	where amenity in('subway_entrance','bus_stop','tram_stop','sbahn_regional') 
	group by amenity,name
	union all
	select amenity,name,cost from test_pois
	where amenity not in('subway_entrance','bus_stop','tram_stop','sbahn_regional'))x) z 
	where precalculate_walking_grid_size.grid_id = grid_id_replace; '''


final_sql = '''UPDATE grid_grid_size set area_isochrone = st_area(x.geom::geography)
               from precalculate_walking_grid_size x
               where grid_grid_size.grid_id = x.grid_id;'''


sensitivities = [0.001]

sql_calculate_accessibility = '''with y as (
	select grid_id, jsonb_build_object(amenity, sum(exp(cost::numeric*-0.001))) index_part from(

		SELECT u.grid_id, obj.value->>'amenity' as amenity,obj.value->>'name',obj.value->>'cost' As cost
		FROM  (
		   select grid_id,thematic_data
		   FROM   precalculate_walking_grid_size
		   WHERE  thematic_data @> '[{"amenity":"amenity_type"}]'
		   ) u
		JOIN LATERAL jsonb_array_elements(thematic_data) obj(value) 
		ON obj.value->>'amenity' = 'amenity_type'
		order by grid_id) x
	group by grid_id, amenity
)

UPDATE precalculate_walking_grid_size 
SET index_0_001 = index_0_001||y.index_part
from y
where precalculate_walking_grid_size.grid_id = y.grid_id;'''

sql_new_grid= '''DROP TABLE IF EXISTS grid;
select distinct grid_id, geom into grid from grid_grid_size;
ALTER TABLE grid add primary key (grid_id);
--drop table grid_grid_size  '''



sql_clean = 'DROP TABLE IF EXISTS grid; ALTER TABLE grid_grid_size add column id serial; CREATE INDEX test_index_sensitivity ON test(sensitivity);'

public_transport_stops = ['bus_stop','tram_stop','subway_entrance','sbahn_regional']
