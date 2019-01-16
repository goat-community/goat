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



thematic_data_sql ='''
	with var_poi as (
		SELECT i.grid_id,i.step, p.gid as poi_gid,p.amenity,p.name, p.geom  
		FROM pois p,precalculate_walking_grid_size i,variable_container v 
		WHERE v.identifier = 'poi_categories'
		AND amenity = any(variable_array)
		AND i.grid_id= grid_id_replace
		AND st_intersects(p.geom,i.geom)
		UNION ALL
		SELECT i.grid_id,i.step,p.gid as poi_gid,public_transport_stop,p.name,p.geom
		FROM public_transport_stops p, precalculate_walking_grid_size i
		WHERE i.grid_id= grid_id_replace
		AND st_intersects(p.geom,i.geom)
		
	)	
	
	--The distance FROM each POI/transport stop to a calculated vertex FROM the edges table
	--is calculated AND the cost is passed is saved.
	--!!!!The SELECTion of the nearest vertex has to be improved!!!!
	,vertices_edges AS (
		SELECT min(cost) AS cost, geom
		FROM (SELECT st_startpoint(geom) geom, cost
			  FROM edges_temp
			  UNION ALL
			  SELECT st_endpoint(geom) geom, cost
			  FROM edges_temp
			) x
		GROUP BY geom
	)
	,distance as (
		SELECT  poi_gid,name,amenity,st_distance(x.geom,v.geom) as min_dist, v.cost, x.geom 
		FROM  vertices_edges v, var_poi x
		WHERE St_dwithin(v.geom::geography,x.geom::geography,50,true)
		AND st_distance(x.geom,v.geom) <> 0
	)
	,cost_pois as (
		SELECT * FROM distance 
		WHERE min_dist <> 0
		AND min_dist in(
		SELECT min(min_dist) FROM distance GROUP BY poi_gid)
	)
	UPDATE precalculate_walking_grid_size set thematic_data = z.array_to_json
	FROM (
	SELECT grid_id_replace as grid_id,array_to_json(array_agg(row_to_json(x))) 
		FROM(
			SELECT amenity,name,min(cost) as cost FROM cost_pois --Every entrance OR bus_stop is only counted once (shortest distance is taken)
			WHERE amenity in('subway_entrance','bus_stop','tram_stop','sbahn_regional') 
			GROUP BY amenity,name
			UNION ALL
			SELECT amenity,name,cost FROM cost_pois
			WHERE amenity not in('subway_entrance','bus_stop','tram_stop','sbahn_regional')
			)x
		) z 
	WHERE precalculate_walking_grid_size.grid_id = z.grid_id;

'''


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
