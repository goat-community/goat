/*Extrapolation census grid*/
/*There is used the census table, OSM data and (optional) a table with building footprints (they could be also used from OSM)*/

DROP TABLE IF EXISTS population;
DROP TABLE IF EXISTS intersection_buildings_grid;
DROP TABLE IF EXISTS buildings_points;
DROP TABLE IF EXISTS census_split_new_development;
DROP TABLE IF EXISTS point_addresses;
DROP TABLE IF EXISTS census_split;
DROP TABLE IF EXISTS buildings_to_map;
DROP TABLE IF EXISTS buildings_fixed_population;
DROP TABLE IF EXISTS updated_census;


CREATE TABLE point_addresses AS
SELECT row_number() over() AS gid, b.building_levels, 
b.roof_levels, b.building_levels_residential,p.way AS geom 
FROM planet_osm_point p, buildings_residential b 
WHERE p."addr:housenumber" IS NOT NULL
AND ST_Intersects(p.way,b.geom);

ALTER TABLE point_addresses ADD PRIMARY key(gid);
CREATE INDEX ON point_addresses USING GIST(geom);
ALTER TABLE point_addresses ADD COLUMN area NUMERIC; 

WITH count_addresses AS 
(
	SELECT b.geom, b.area, count(a.gid) number_addresses
	FROM buildings_residential b, point_addresses a
	WHERE ST_Intersects(b.geom,a.geom)
	GROUP BY b.geom, b.area
)
UPDATE point_addresses SET area = c.area/c.number_addresses
FROM count_addresses c 
WHERE ST_Intersects(point_addresses.geom,c.geom);

---Intersect buildings and grids 

CREATE TABLE intersection_buildings_grid AS
WITH buildings_no_address AS (
	SELECT b.* 
	FROM buildings_residential b
	LEFT JOIN point_addresses a ON ST_Intersects(b.geom,a.geom)
	WHERE a.gid IS NULL 
)
SELECT ST_intersection (c.geom, b.geom) AS geom, b.building_levels, b.building_levels_residential,  
b.gid, ST_Area(b.geom::geography) area_complete
FROM buildings_no_address b, census c
WHERE ST_intersects(c.geom, b.geom)
AND ST_area(b.geom::geography) > (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'minimum_building_size_residential');


---order by biggest area and allocate grid
CREATE TABLE buildings_points AS
WITH x AS (
	SELECT gid, max(st_area(geom)) AS area_part
	FROM intersection_buildings_grid
	GROUP BY gid
	)
SELECT row_number() over() as gid, u.*
FROM 
(
	SELECT i.building_levels, i.building_levels_residential, 
	i.area_complete AS area, ST_Centroid(i.geom) geom 
	FROM intersection_buildings_grid i, x
	WHERE x.area_part = st_area(geom) 
	and x.gid = i.gid
	UNION ALL 
	SELECT p.building_levels, p.building_levels_residential, p.area, p.geom 
	FROM point_addresses p
) u;

CREATE INDEX ON buildings_points USING GIST(geom);
ALTER TABLE buildings_points ADD PRIMARY key(gid);

ALTER TABLE buildings_points ADD COLUMN fixed_population numeric;
DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'fixed_population'
            )
        THEN
            WITH fixed_population AS (
				SELECT b.geom, f.population AS fixed_population
				FROM buildings_residential b, fixed_population f
				WHERE ST_Intersects(f.geom,b.geom)
			)
			UPDATE buildings_points b
			SET fixed_population = f.fixed_population
			FROM fixed_population f
			WHERE ST_Intersects(b.geom,f.geom);
        END IF ;
    END
$$ ;

CREATE TABLE census_split AS 
WITH built_up_per_grid AS (
	SELECT c.gid, sum(b.area) AS sum_built_up
	FROM census c, buildings_points b
	WHERE ST_Intersects(c.geom,b.geom)
	GROUP BY c.gid
),
split_grids AS (
	SELECT row_number() over() as gid, c.gid AS parent_id, c.pop, ST_Intersection(c.geom,s.geom) geom 
	FROM census c, study_area s 
	WHERE ST_Intersects(c.geom,s.geom)
),
built_up_part_grid AS (
	SELECT s.gid, sum(b.area) AS sum_built_up_part
	FROM split_grids s, buildings_points b
	WHERE ST_intersects(s.geom,b.geom)
	GROUP BY s.gid
)
SELECT s.gid,s.geom, (p.sum_built_up_part/b.sum_built_up) * s.pop AS pop, b.sum_built_up
FROM built_up_per_grid b, split_grids s, built_up_part_grid p
WHERE b.gid = s.parent_id 
AND s.gid = p.gid;

--Delete buildings that have fixed population
CREATE TABLE buildings_fixed_population (LIKE buildings_points INCLUDING ALL); 
INSERT INTO buildings_fixed_population
SELECT * FROM buildings_points
WHERE fixed_population IS NOT NULL;

DELETE FROM buildings_points 
WHERE fixed_population IS NOT NULL;


--Add number of residential buildings to census_split

ALTER TABLE census_split DROP COLUMN IF EXISTS number_buildings_now;
ALTER TABLE census_split ADD COLUMN number_buildings_now integer;

WITH count_addresses_per_grid AS
(
	SELECT c.gid, count(a.geom) AS num
	FROM buildings_points a, census_split c
	WHERE st_intersects(a.geom,c.geom)
	GROUP BY c.gid
)
UPDATE census_split set number_buildings_now = count_addresses_per_grid.num
FROM count_addresses_per_grid
WHERE census_split.gid=count_addresses_per_grid.gid; 

ALTER TABLE census_split DROP COLUMN IF EXISTS new_pop;
ALTER TABLE census_split ADD COLUMN new_pop numeric;
UPDATE census_split SET new_pop = pop;

WITH census_to_update AS (
	SELECT c.gid,sum(fixed_population) AS sum_fixed_pop
	FROM buildings_fixed_population b, census_split c
	WHERE ST_Intersects(b.geom,c.geom)
	AND c.new_pop > 0
	GROUP BY c.gid
)
UPDATE census_split c 
SET new_pop = new_pop - cu.sum_fixed_pop
FROM census_to_update cu
WHERE c.gid = cu.gid;

WITH grids_new_development AS
(
	SELECT c.gid, 
	b.area*building_levels_residential AS new_floor_area, 
	(b.area*building_levels_residential)/(SELECT variable_simple::numeric FROM variable_container WHERE identifier = 'average_gross_living_area') AS new_residents
	FROM census_split c, buildings_points b
	WHERE pop < 1 
	AND number_buildings_now >= (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'census_minimum_number_new_buildings')
	AND ST_Intersects(c.geom,b.geom)
)
UPDATE census_split SET new_pop = x.new_pop
FROM 
(
	SELECT gid, sum(new_residents) new_pop
	FROM grids_new_development
	GROUP BY gid 
) x
WHERE census_split.gid = x.gid;

CREATE TABLE census_split_new_development as
SELECT * 
FROM census_split
WHERE pop < 1 
AND number_buildings_now >= (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'census_minimum_number_new_buildings');

ALTER TABLE census_split_new_development ADD PRIMARY key(gid);
CREATE INDEX ON census_split_new_development USING GIST(geom);

CREATE TABLE buildings_to_map AS 
SELECT b.*  
FROM buildings_residential b, 
(	
	SELECT b.* 
	FROM buildings_points b, census_split_new_development c 
	WHERE ST_Intersects(c.geom,b.geom)
) c
WHERE ST_Intersects(b.geom,c.geom)
AND (b.building_levels) IS NULL; 
 
--Substract fixed population from study_area
WITH study_area_to_update AS (
	SELECT s.gid,sum(fixed_population) AS sum_fixed_pop
	FROM buildings_fixed_population b, study_area s
	WHERE ST_Intersects(b.geom,s.geom)
	GROUP BY s.gid
)
UPDATE study_area s 
SET sum_pop = sum_pop - c.sum_fixed_pop
FROM study_area_to_update c
WHERE s.gid = c.gid; 

--Check if assigned population exceed population growth
--If so reduce population in the affected grids
--Distribute the rest of the population
WITH comparison_pop AS (
	SELECT s.name, s.sum_pop,sum(c.new_pop) sum_new_pop, s.geom
	FROM census_split c, study_area s
	WHERE ST_Intersects(ST_Centroid(c.geom),s.geom)
	AND c.new_pop > 0
	GROUP BY s.name, s.sum_pop, s.geom
),
sum_distributed_pop AS (
	SELECT s.name, sum(c.new_pop) distributed_pop
	FROM census_split c, study_area s
	WHERE c.pop < 1 
	AND c.number_buildings_now >= (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'census_minimum_number_new_buildings')
	AND ST_Intersects(ST_Centroid(c.geom), s.geom)
	GROUP BY s.name
),
to_reduce_pop AS (
	SELECT s.name, c.sum_pop, c.sum_new_pop, -(sum_pop-sum_new_pop) AS difference,s.distributed_pop, c.geom
	FROM comparison_pop c, sum_distributed_pop s 
	WHERE s.name = c.name
	AND sum_new_pop > sum_pop
),
substract_exceed_pop AS (
	UPDATE census_split
	SET new_pop=new_pop-(new_pop::float/cc.distributed_pop::float)::float*cc.difference::float 
	FROM to_reduce_pop cc
	WHERE ST_Intersects(ST_Centroid(census_split.geom), cc.geom)
	AND census_split.pop < 0 
	AND census_split.number_buildings_now >= (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'census_minimum_number_new_buildings')
),
remaining_pop AS (
	SELECT c.name, (sum_pop::numeric-sum_new_pop::numeric)/x.count_grids::numeric to_add
	FROM comparison_pop c,
	(	SELECT s.name,count(*) AS count_grids
		FROM census_split c, study_area s
		WHERE c.pop > 0
		AND ST_Intersects(ST_Centroid(c.geom),s.geom)
		GROUP BY s.name
	) x
	WHERE sum_new_pop < sum_pop
	AND c.name = x.name 
)
UPDATE census_split SET new_pop = new_pop + r.to_add
FROM study_area s, remaining_pop r 
WHERE s.name = r.name 
AND ST_Intersects(s.geom,ST_Centroid(census_split.geom))
AND census_split.pop > 0;


CREATE TABLE population AS 
SELECT b.*, (b.area/c.sum_built_up)*new_pop population 
FROM buildings_points b, census_split c 
WHERE ST_Intersects(b.geom,c.geom);

ALTER TABLE population DROP COLUMN fixed_population;

INSERT INTO population
SELECT * 
FROM buildings_fixed_population;

--Add fixed population again to study_area
WITH study_area_to_update AS (
	SELECT s.gid,sum(fixed_population) AS sum_fixed_pop
	FROM buildings_fixed_population b, study_area s
	WHERE ST_Intersects(b.geom,s.geom)
	GROUP BY s.gid
)
UPDATE study_area s 
SET sum_pop = sum_pop + c.sum_fixed_pop
FROM study_area_to_update c
WHERE s.gid = c.gid; 

ALTER TABLE population DROP COLUMN gid;
ALTER TABLE population ADD COLUMN gid serial;

ALTER TABLE population add primary key(gid);
CREATE INDEX ON population USING GIST (geom);

DELETE FROM population 
WHERE population < 0;

--Create new census_table
CREATE TABLE updated_census AS 
SELECT c.id,sum(population) pop, c.geom  
FROM population p, census c 
WHERE ST_Intersects(c.geom, p.geom)
GROUP BY c.id, c.geom;

ALTER TABLE updated_census ADD COLUMN gid serial;
ALTER TABLE updated_census ADD PRIMARY key(gid);
CREATE INDEX ON updated_census USING gist(geom);

DROP TABLE IF EXISTS intersection_buildings_grid;
DROP TABLE IF EXISTS buildings_points;
DROP TABLE IF EXISTS point_addresses;
DROP TABLE IF EXISTS census_split;
DROP TABLE IF EXISTS buildings_fixed_population;