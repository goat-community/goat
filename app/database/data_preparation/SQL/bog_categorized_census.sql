------------------------------------------------------------------------------------------
------------------------------Goat population classification------------------------------
------------------------------------------------------------------------------------------

-- 0. Load functions

CREATE EXTENSION tablefunc;

-- 1. Pivot TABLE FOR categorize NEW pop

SELECT * FROM pop_per_block;

-- Comment: in this case the grouping variable is age_grouped, in the function, age_grouped should be an input parameter

DROP TABLE IF EXISTS population_categorized;
SELECT * INTO population_categorized FROM crosstab(
	'SELECT cod_mzn, age_grouped, sum(population::int) as population
	from pop_per_block GROUP BY cod_mzn, age_grouped ORDER BY 1,2',
	'SELECT DISTINCT age_grouped FROM pop_per_block ORDER BY age_grouped;'
) AS ct(cod_mz TEXT, "0 to 9" NUMERIC, "10 to 19" NUMERIC, "20 to 29" NUMERIC, "30 to 64" NUMERIC, "65 and more" NUMERIC);

-- 2. Fill NA values with zeros

UPDATE population_categorized SET "0 to 9" = 0 WHERE "0 to 9" IS NULL;
UPDATE population_categorized SET "10 to 19" = 0 WHERE "10 to 19" IS NULL;
UPDATE population_categorized SET "20 to 29" = 0 WHERE "20 to 29" IS NULL;
UPDATE population_categorized SET "30 to 64" = 0 WHERE "30 to 64" IS NULL;
UPDATE population_categorized SET "65 and more" = 0 WHERE "65 and more" IS NULL;

-- 3. Compute columns in one array

SELECT * FROM pop_per_block;
DROP TABLE IF EXISTS pop_by_gender;
SELECT cod_mzn, ARRAY[sum(male::int), sum(female::int)]AS pop_gender_array INTO pop_by_gender FROM pop_per_block GROUP BY cod_mzn;

-- 4. Compute columns in one array

DROP TABLE IF EXISTS pop_age_array;
SELECT pc.cod_mz, ARRAY["0 to 9", "10 to 19", "20 to 29", "30 to 64", "65 and more"] AS pop_age_groups, pop_gender_array INTO pop_age_array FROM population_categorized pc, pop_by_gender pg 
WHERE pc.cod_mz = pg.cod_mzn;

SELECT * FROM pop_age_array;

-- 5. Join to blocks database in population

DROP TABLE IF EXISTS population_classificated_array;
SELECT p.cod_dane, max(p.main_strat), sum(p.population) AS total_pop, p.geom AS geom, pag.pop_age_groups, pag.pop_gender_array, p.count_bloc INTO population_classificated_array
FROM population p, pop_age_array pag WHERE p.cod_dane = pag.cod_mz 
GROUP BY p.cod_dane, pag.pop_age_groups, p.geom, pag.pop_gender_array, p.count_bloc;

SELECT * FROM population_classificated_array;


SELECT * FROM population;
-- END

SELECT * FROM population;


SELECT * FROM grid_500_age_gender;

-------------------------------------------------------
------------------- Group by strata--------------------
-------------------------------------------------------

SELECT * FROM grid_500;

--- Select the main-strata based on the mayoritary porpulation

DROP TABLE IF EXISTS temporal_strata;
WITH strata_def AS (SELECT g.grid_id, p.main_strat, sum(p.population) AS pop_strata, row_number() OVER (PARTITION BY grid_id ORDER BY grid_id, sum(p.population) DESC )FROM population p
JOIN grid_500 g
ON ST_Intersects(g.geom, p.geom)
GROUP BY p.gid, grid_id 
) SELECT * INTO temporal_strata FROM strata_def sd WHERE ROW_NUMBER = 1;

SELECT * FROM temporal_strata;

-- Group by 
-- Test with taz


SELECT * FROM population;





----
SELECT * FROM grid_500

SELECT p.population FROM population p;


SELECT * FROM population;

SELECT p.gid, sum(p.population) AS pop_strata, row_number() over(PARTITION BY grid_id ORDER BY g.grid_id, sum(p.population)) FROM population p
JOIN grid_500 g
ON ST_Intersects(g.geom, p.geom)
GROUP BY p.gid, grid_id
ORDER BY grid_id, pop_strata DESC

SELECT * 

SELECT * FROM population;


SELECT * FROM taz;






