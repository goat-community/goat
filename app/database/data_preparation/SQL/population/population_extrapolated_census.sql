/*Split up census tracts that are intersecting several study areas.*/
DROP TABLE IF EXISTS splitted_census; 
CREATE TEMP TABLE splitted_census AS 
SELECT c.gid, c.pop, ST_Intersection(c.geom, s.geom) AS geom 
FROM census c, study_area s
WHERE ST_Intersects(c.geom, ST_BOUNDARY(s.geom));

CREATE INDEX ON splitted_census USING GIST(geom);
CREATE INDEX ON splitted_census (gid);

DROP TABLE IF EXISTS census_splitted_sum_built_up;
CREATE TEMP TABLE census_splitted_sum_built_up AS 
SELECT DISTINCT c.gid, COALESCE(c.pop,0) pop, COALESCE(c.sum_gross_floor_area_residential,0) AS sum_gross_floor_area_residential, c.number_buildings_now, c.geom 
FROM study_area s
INNER JOIN LATERAL 
(
	SELECT c.gid, c.pop, sum(a.gross_floor_area_residential) sum_gross_floor_area_residential, count(a.gid) AS number_buildings_now, c.geom 
	FROM splitted_census c, residential_addresses a 
	WHERE ST_Intersects(c.geom, s.geom) 
	AND ST_Intersects(c.geom, a.geom) 
	GROUP BY c.gid, c.pop, c.geom   
) c ON TRUE;

DROP TABLE IF EXISTS census_prepared; 
CREATE TEMP TABLE census_prepared 
(
	gid serial, 
	pop integer, 
	sum_gross_floor_area_residential integer,
	number_buildings_now integer, 
	geom geometry,
	new_pop float
);

ALTER TABLE census_prepared ADD PRIMARY KEY (gid);
CREATE INDEX ON census_prepared USING GIST(geom);

INSERT INTO census_prepared(pop, sum_gross_floor_area_residential, number_buildings_now, geom)
SELECT CASE WHEN c.sum_gross_floor_area_residential <> 0 THEN c.pop * (s.sum_gross_floor_area_residential::float/c.sum_gross_floor_area_residential::float) 
ELSE 0 END AS pop, s.sum_gross_floor_area_residential,
s.number_buildings_now, s.geom 
FROM census_splitted_sum_built_up s, census_sum_built_up c
WHERE s.gid = c.gid;

INSERT INTO census_prepared(pop, sum_gross_floor_area_residential, number_buildings_now, geom)
SELECT a.pop, a.sum_gross_floor_area_residential, a.number_buildings_now, a.geom 
FROM census_sum_built_up a
LEFT JOIN census_splitted_sum_built_up s
ON a.gid = s.gid 
WHERE s.gid IS NULL; 

/*Delete buildings that have fixed population*/
DROP TABLE IF EXISTS fixed_residential_addresses;
CREATE TABLE fixed_residential_addresses AS 
SELECT * FROM residential_addresses 
WHERE fixed_population IS NOT NULL;

DELETE FROM residential_addresses
WHERE fixed_population IS NOT NULL;

/*Compute population for new development area using average gross living area*/
UPDATE census_prepared SET new_pop = pop;

WITH census_to_update AS (
	SELECT c.gid,sum(fixed_population) AS sum_fixed_pop
	FROM fixed_residential_addresses b, census_prepared c
	WHERE ST_Intersects(b.geom,c.geom)
	AND c.new_pop > 0
	GROUP BY c.gid
)
UPDATE census_prepared c 
SET new_pop = new_pop - cu.sum_fixed_pop
FROM census_to_update cu
WHERE c.gid = cu.gid;

UPDATE census_prepared 
SET new_pop = sum_gross_floor_area_residential/select_from_variable_container_s('average_gross_living_area')::float
WHERE number_buildings_now > select_from_variable_container_s('census_minimum_number_new_buildings')::integer
AND pop < 1; 

DROP TABLE IF EXISTS census_split_new_development;
CREATE TABLE census_split_new_development as
SELECT * 
FROM census_prepared 
WHERE pop < 1 
AND number_buildings_now >= select_from_variable_container_s('census_minimum_number_new_buildings')::integer;

ALTER TABLE census_split_new_development ADD PRIMARY key(gid);
CREATE INDEX ON census_split_new_development USING GIST(geom);
 
--Substract fixed population from study_area
WITH study_area_to_update AS (
	SELECT s.name, sum(fixed_population) AS sum_fixed_pop
	FROM fixed_residential_addresses b, study_area s
	WHERE ST_Intersects(b.geom,s.geom)
	GROUP BY s.name
)
UPDATE study_area s 
SET sum_pop = sum_pop - c.sum_fixed_pop
FROM study_area_to_update c
WHERE s.name = c.name; 

--Check if assigned population exceed population growth
--If so reduce population in the affected grids
--Distribute the rest of the population
WITH comparison_pop AS (
	SELECT s.name, s.sum_pop,sum(c.new_pop) sum_new_pop, s.geom
	FROM census_prepared c, study_area s
	WHERE ST_Intersects(ST_Centroid(c.geom),s.geom)
	AND c.new_pop > 0
	GROUP BY s.name, s.sum_pop, s.geom
),
sum_distributed_pop AS (
	SELECT s.name, sum(c.new_pop) distributed_pop
	FROM census_prepared c, study_area s
	WHERE c.pop < 1 
	AND c.number_buildings_now >= select_from_variable_container_s('census_minimum_number_new_buildings')::integer
	AND ST_Intersects(ST_Centroid(c.geom), s.geom)
	GROUP BY s.name
),
to_reduce_pop AS (
	SELECT s.name, c.sum_pop, c.sum_new_pop, -(sum_pop-sum_new_pop) AS difference, s.distributed_pop, c.geom
	FROM comparison_pop c, sum_distributed_pop s 
	WHERE s.name = c.name
	AND sum_new_pop > sum_pop
)
UPDATE census_prepared
SET new_pop=new_pop-(new_pop::float/cc.distributed_pop::float)::float*cc.difference::float 
FROM to_reduce_pop cc
WHERE ST_Intersects(ST_Centroid(census_prepared.geom), cc.geom)
AND number_buildings_now > select_from_variable_container_s('census_minimum_number_new_buildings')::integer
AND pop < 1; 

WITH new_comparison_pop AS 
(
	SELECT s.name, sum(c.sum_gross_floor_area_residential) sum_gross_floor_area_residential, s.sum_pop, sum(c.new_pop) sum_new_pop, s.geom
	FROM census_prepared c, study_area s
	WHERE ST_Intersects(ST_Centroid(c.geom),s.geom)
	AND c.pop > 0
	GROUP BY s.name, s.sum_pop, s.geom
)
UPDATE census_prepared c
SET new_pop = new_pop + (n.sum_pop::float - n.sum_new_pop::float) * (c.sum_gross_floor_area_residential::float/n.sum_gross_floor_area_residential::float)
FROM new_comparison_pop n, study_area s 
WHERE n.name = s.name 
AND ST_Intersects(ST_CENTROID(c.geom), s.geom)
AND c.pop > 0;

DROP TABLE IF EXISTS population CASCADE; 
CREATE TABLE population AS 
SELECT a.gid, a.geom, a.fixed_population, 
CASE WHEN c.sum_gross_floor_area_residential <> 0 THEN 
(a.gross_floor_area_residential::float/c.sum_gross_floor_area_residential::float)*new_pop 
ELSE 0 END AS population, a.building_gid 
FROM residential_addresses a, census_prepared c 
WHERE ST_Intersects(a.geom,c.geom)
AND c.sum_gross_floor_area_residential <> 0;

INSERT INTO population(building_gid, geom, fixed_population, population)
SELECT building_gid, geom, fixed_population, fixed_population 
FROM fixed_residential_addresses;

--Add fixed population again to study_area
WITH study_area_to_update AS (
	SELECT s.name, sum(fixed_population) AS sum_fixed_pop
	FROM fixed_residential_addresses b, study_area s
	WHERE ST_Intersects(b.geom,s.geom)
	GROUP BY s.name
)
UPDATE study_area s 
SET sum_pop = sum_pop + c.sum_fixed_pop
FROM study_area_to_update c
WHERE s.name = c.name; 

/*Cleaning and adding indices*/
ALTER TABLE population DROP COLUMN gid;
ALTER TABLE population ADD COLUMN gid serial;
ALTER TABLE population add primary key(gid);
CREATE INDEX ON population USING GIST (geom);

DELETE FROM population 
WHERE population < 0;

DROP TABLE IF EXISTS census_sum_built_up;
