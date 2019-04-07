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
    ALTER TABLE grid_grid_size add column area_isochrone float8;
    ALTER TABLE grid_grid_size ADD COLUMN isochrone_gid integer;
    ALTER TABLE grid_grid_size ADD COLUMN pois jsonb;
    ALTER TABLE grid_grid_size add column area_buffer float8;
	'''

sensitivities = ['001']

sql_calculate_accessibility = '''with y as (
	select grid_id, jsonb_build_object(amenity, sum(exp(cost::numeric*-%f))) index_part from(

		SELECT u.grid_id, obj.value->>'amenity' as amenity,obj.value->>'name',obj.value->>'cost' As cost
		FROM  (
		   select grid_id,pois
		   FROM   grid_%i
		   WHERE  pois @> '[{"amenity":"%s"}]'
		   ) u
		JOIN LATERAL jsonb_array_elements(pois) obj(value) 
		ON obj.value->>'amenity' = '%s'
		order by grid_id) x
	group by grid_id, amenity
)
UPDATE grid_%i 
SET index_0_%s = index_0_%s||y.index_part
from y
where grid_%i.grid_id = y.grid_id;'''

sql_new_grid= '''DROP TABLE IF EXISTS grid;
select distinct grid_id, geom into grid from grid_grid_size;
ALTER TABLE grid add primary key (grid_id);
--drop table grid_grid_size  '''



sql_clean = 'DROP TABLE IF EXISTS grid; ALTER TABLE grid_grid_size add column id serial; CREATE INDEX test_index_sensitivity ON test(sensitivity);'

#public_transport_stops = ['bus_stop','tram_stop','subway_entrance','sbahn_regional']

sql_grid_population = '''
ALTER TABLE grid_grid_size ADD COLUMN population integer;
ALTER TABLE grid_grid_size ADD COLUMN percentile_population smallint;
WITH sum_pop AS (
	SELECT g.grid_id, sum(p.population)::integer AS population  
	FROM grid_grid_size g, population p
	WHERE ST_Intersects(g.geom,p.geom)
	GROUP BY grid_id
)
UPDATE grid_grid_size SET population=s.population
FROM sum_pop s 
WHERE grid_grid_size.grid_id = s.grid_id;


WITH p AS (
	SELECT grid_id,ntile(5) over 
	(order by population) AS percentile
	FROM grid_grid_size where population <> 0
	ORDER BY grid_id
)
UPDATE grid_grid_size SET percentile_population = p.percentile
FROM p
WHERE grid_grid_size.grid_id = p.grid_id;

UPDATE grid_grid_size SET percentile_population = 0
WHERE percentile_population IS NULL;

ALTER TABLE grid_grid_size ADD COLUMN percentile_area_isochrone smallint;
WITH p AS (
	SELECT grid_id,ntile(5) over 
	(order by area_isochrone) AS percentile
	FROM grid_grid_size where area_isochrone IS NOT NULL 
	ORDER BY grid_id
)
UPDATE grid_grid_size SET percentile_area_isochrone = p.percentile
FROM p
WHERE grid_grid_size.grid_id = p.grid_id;

UPDATE grid_grid_size SET percentile_population = 0
WHERE percentile_population IS NULL;

'''