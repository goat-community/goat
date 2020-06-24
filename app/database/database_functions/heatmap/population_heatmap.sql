
/*
WITH modified_population AS 
(
	SELECT geom, -population AS population
	FROM population_userinput 
	WHERE building_gid IN (SELECT UNNEST(deleted_feature_ids) FROM user_data WHERE layer_name = 'buildings' AND userid = 5680566)
	UNION ALL 
	SELECT geom, population 
	FROM population_userinput 
	WHERE userid = 5680566
)
SELECT g.grid_id, sum(p.population) 
FROM grid_500 g, modified_population p
WHERE ST_Intersects(g.geom,p.geom)
GROUP BY grid_id;


(CASE WHEN population BETWEEN 1 AND 20 THEN 1 
WHEN population BETWEEN 20 AND 80 THEN 2
WHEN population BETWEEN 80 AND 200 THEN 3 
WHEN population BETWEEN 200 AND 400 THEN 4 
WHEN population > 400 THEN 5 END)
WHERE population IS NOT NULL; */