CREATE OR REPLACE FUNCTION return_func_description(func_name text)
RETURNS TEXT 
LANGUAGE SQL AS 
$$
	SELECT d.description
	FROM pg_proc p
	LEFT JOIN pg_description d
	ON d.objoid = p.oid
	WHERE p.proname = func_name
$$
/*
SELECT return_func_description('unnest_2d_1d')
SELECT REPLACE(substring(return_func_description('heatmap_geoserver'),'\[(.*?)\]'),', geom','')
*/