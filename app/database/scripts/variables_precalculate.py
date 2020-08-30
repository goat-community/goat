prepare_tables = '''
	DROP TABLE IF EXISTS grid_heatmap;
	CREATE TABLE grid_heatmap AS 
	SELECT hexagrid AS geom FROM hexagrid(%s); 

	with w as(
		select way as geom from planet_osm_polygon 
		where "natural" = 'water'
	),
	g as(
		select g.geom from grid_heatmap g, w
		where st_within(g.geom,w.geom)
	)
	delete from grid_heatmap where geom in (select * from g);


	ALTER TABLE grid_heatmap add column grid_id serial;
	ALTER TABLE grid_heatmap ADD COLUMN area_isochrone float;
	ALTER TABLE grid_heatmap ADD COLUMN percentile_area_isochrone smallint; 
	'''


sql_new_grid= '''DROP TABLE IF EXISTS grid;
select distinct grid_id, geom into grid from grid_heatmap;
ALTER TABLE grid add primary key (grid_id);
'''



sql_clean = 'DROP TABLE IF EXISTS grid; ALTER TABLE grid_heatmap add column id serial; CREATE INDEX test_index_sensitivity ON test(sensitivity);'



sql_grid_population = '''
ALTER TABLE grid_heatmap ADD COLUMN population integer;
ALTER TABLE grid_heatmap ADD COLUMN percentile_population smallint;
WITH sum_pop AS (
	SELECT g.grid_id, sum(p.population)::integer AS population  
	FROM grid_heatmap g, population p
	WHERE ST_Intersects(g.geom,p.geom)
	GROUP BY grid_id
)
UPDATE grid_heatmap SET population=s.population
FROM sum_pop s 
WHERE grid_heatmap.grid_id = s.grid_id;

UPDATE grid_heatmap 
SET percentile_population = 
(CASE WHEN population BETWEEN 1 AND 20 THEN 1 
WHEN population BETWEEN 20 AND 80 THEN 2
WHEN population BETWEEN 80 AND 200 THEN 3 
WHEN population BETWEEN 200 AND 400 THEN 4 
WHEN population > 400 THEN 5 END)
WHERE population IS NOT NULL; 

UPDATE grid_heatmap SET percentile_population = 0
WHERE percentile_population IS NULL;

UPDATE grid_heatmap SET percentile_area_isochrone = x.percentile 
FROM (
	SELECT grid_id,ntile(5) over 
	(order by area_isochrone) AS percentile
	FROM grid_heatmap
	WHERE area_isochrone IS NOT NULL 
) x
WHERE grid_heatmap.grid_id = x.grid_id;

UPDATE grid_heatmap SET percentile_area_isochrone = 0 WHERE percentile_area_isochrone IS NULL; 
'''