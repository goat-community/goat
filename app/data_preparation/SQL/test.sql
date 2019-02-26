CREATE TABLE buildings AS 
SELECT building, amenity, tourism, way AS geom 
FROM planet_osm_polygon 
WHERE building IS NOT NULL;

ALTER TABLE buildings ADD COLUMN gid serial;
ALTER TABLE buildings ADD PRIMARY KEY(gid);
CREATE INDEX ON buildings USING GIST(geom);
/*Extrapolation census grid*/
/*There is used the census table, OSM data and (optional) a table with building footprints (they could be also used from OSM)*/
DROP TABLE IF EXISTS population_census;
DROP TABLE IF EXISTS non_residential_buildings;
DROP TABLE IF EXISTS intersection_buildings_grid;
DROP TABLE IF EXISTS max_area;
DROP TABLE IF EXISTS buildings_points;
DROP TABLE IF EXISTS buildings_residential_intersect;
DROP TABLE IF EXISTS buildings_residential_fusion;
DROP TABLE IF EXISTS intersect_custom_landuse;
DROP TABLE IF EXISTS census_new_development;

CREATE TABLE non_residential_buildings AS
WITH x AS (
	SELECT p.osm_id
	FROM planet_osm_polygon p
	LEFT JOIN buildings_residential b on p.osm_id= b.osm_id
	WHERE b.osm_id is null
)
SELECT distinct amenity,shop,building,name,way geom FROM planet_osm_polygon p,x
WHERE p.osm_id=x.osm_id
and p.building is not null
and st_area(way::geography) > (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'minimum_building_size_residential');

ALTER TABLE non_residential_buildings ADD id serial;
ALTER TABLE non_residential_buildings add primary key(id);

CREATE INDEX index_non_residential_buildings  ON non_residential_buildings USING GIST (geom);

---Intersect buildings and grids 

CREATE TABLE intersection_buildings_grid AS
SELECT st_intersection (c.geom, b.geom) AS geom, b.gid, ST_Area(b.geom::geography) area_complete
FROM buildings b, census c
WHERE st_intersects(c.geom, b.geom)
AND st_area(b.geom::geography) > (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'minimum_building_size_residential');

---order by biggest area and allocate grid
CREATE TABLE buildings_points AS
WITH x AS (
	SELECT gid, max(st_area(geom)) AS area_part
	FROM intersection_buildings_grid
	GROUP BY gid
	)
SELECT ST_Centroid(i.geom) geom, i.area_complete AS area 
FROM intersection_buildings_grid i, x
WHERE x.area_part = st_area(geom) 
and x.gid = i.gid;


--Select only residential buildings
CREATE TABLE buildings_residential_intersect AS
SELECT b.geom, b.area
FROM 
  buildings_points AS b LEFT JOIN
  non_residential_buildings AS n ON
  ST_Intersects(b.geom,n.geom)
WHERE n.id IS NULL;


CREATE TABLE intersect_custom_landuse  AS 
SELECT 
br.geom, br.area
FROM 
buildings_residential_intersect AS br LEFT JOIN
(	SELECT gid, geom 
	FROM landuse 
	WHERE objart IN (SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'custom_landuse_no_residents')

) AS l 
ON ST_Intersects (br.geom, l.geom)
WHERE l.gid IS NULL;


CREATE TABLE buildings_residential_fusion AS 
SELECT b.geom, b.area, row_number() over() AS gid 
FROM intersect_custom_landuse b 
LEFT JOIN 
(
	SELECT row_number() over() as gid, way AS geom 
	FROM planet_osm_polygon 
	WHERE landuse IN(SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'osm_landuse_no_residents')
	OR tourism IN(SELECT UNNEST(variable_array)  FROM variable_container WHERE identifier = 'tourism_no_residents')
	OR amenity IN(SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'amenity_no_residents')
) AS l 
ON ST_Intersects(b.geom,l.geom)
WHERE l.gid IS NULL;

ALTER TABLE buildings_residential_fusion ADD COLUMN building_levels_residential integer;

UPDATE buildings_residential_fusion 
SET building_levels_residential = b.building_levels_residential 
FROM buildings_residential b
WHERE ST_Intersects(buildings_residential_fusion.geom,b.geom);

UPDATE buildings_residential_fusion
SET building_levels_residential = (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'default_building_levels')
WHERE building_levels_residential IS NULL; 


CREATE INDEX index_buildings_residential_fusion  ON buildings_residential_fusion USING GIST (geom);

--Add number of residential buildings to census

ALTER TABLE census DROP COLUMN IF EXISTS number_buildings_now;
ALTER TABLE census add column number_buildings_now integer;

WITH count_addresses_per_grid AS
(

	SELECT c.id, count(a.geom) AS num
	FROM buildings_residential_fusion a, census c
	WHERE st_intersects(a.geom,c.geom)
	GROUP BY id
)
UPDATE census set number_buildings_now = count_addresses_per_grid.num
FROM count_addresses_per_grid
WHERE census.id=count_addresses_per_grid.id; 

--A table wearing all the census grids where new development was done 
--To improve the result it is recommended to make sure that the number of building floors for the buildings in these cells is existing in OSM or from another source
--As only a fraction of the buildings have to be checked the effort to map is relatively low. 
CREATE TABLE census_new_development as
SELECT * 
FROM census
WHERE pop < 1 
AND number_buildings_now >= (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'census_minimum_number_new_buildings');
	

	
ALTER TABLE census DROP COLUMN IF EXISTS new_pop;
ALTER TABLE census ADD COLUMN new_pop numeric;
UPDATE census SET new_pop = pop;

WITH grids_new_development AS
(
	SELECT c.gid, 
	b.area*building_levels_residential AS new_floor_area, 
	(b.area*building_levels_residential)/(SELECT variable_simple::numeric FROM variable_container WHERE identifier = 'average_gross_living_area') AS new_residents
	FROM census c, buildings_residential_fusion b
	WHERE pop < 1 
	AND number_buildings_now >= (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'census_minimum_number_new_buildings')
	AND ST_Intersects(c.geom,b.geom)
)
UPDATE census SET new_pop = x.new_pop
FROM 
(
	SELECT gid, sum(new_residents) new_pop
	FROM grids_new_development
	GROUP BY gid
) x
WHERE census.gid = x.gid;



--Check if assigned population exceed population growth
--If so reduce population in the affected grids
--Distribute the rest of the population
WITH comparison_pop AS (
	SELECT s.name, s.sum_pop,sum(c.new_pop) sum_new_pop, s.geom
	FROM census c, study_area s
	WHERE ST_Intersects(c.geom,s.geom)
	AND c.new_pop > 0
	GROUP BY s.name, s.sum_pop, s.geom
),
sum_distributed_pop AS (
	SELECT s.name, sum(c.new_pop) distributed_pop
	FROM census c, study_area s
	WHERE c.pop < 1 
	AND c.number_buildings_now >= (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'census_minimum_number_new_buildings')
	AND ST_Intersects(c.geom, s.geom)
	GROUP BY s.name
),
to_reduce_pop AS (
	SELECT s.name, c.sum_pop, c.sum_new_pop, -(sum_pop-sum_new_pop) AS difference,s.distributed_pop, c.geom
	FROM comparison_pop c, sum_distributed_pop s 
	WHERE s.name = c.name
	AND sum_new_pop > sum_pop
),
substract_exceed_pop AS (
	UPDATE census
	SET new_pop=new_pop-(new_pop::float/cc.distributed_pop::float)::float*cc.difference::float 
	FROM to_reduce_pop cc
	WHERE ST_Intersects(census.geom, cc.geom)
	AND census.pop < 1 
	AND census.number_buildings_now >= (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'census_minimum_number_new_buildings')
),
remaining_pop AS (
	SELECT c.name, (sum_pop::numeric-sum_new_pop::numeric)/x.count_grids::numeric to_add
	FROM comparison_pop c,
	(	SELECT s.name,count(*) AS count_grids
		FROM census c, study_area s
		WHERE c.pop > 0
		AND ST_Intersects(c.geom,s.geom)
		GROUP BY s.name
	) x
	WHERE sum_new_pop < sum_pop
	AND c.name = x.name 
)
UPDATE census SET new_pop = new_pop + r.to_add
FROM study_area s, remaining_pop r 
WHERE s.name = r.name 
AND ST_Intersects(s.geom,census.geom)
AND census.pop > 0;

--Disaggregate from the census level to the buildings
CREATE TABLE population_census AS 
WITH x AS (
	SELECT c.gid, new_pop/number_buildings_now pop_building, geom
	FROM census c
	WHERE c.new_pop > 0
)
SELECT row_number() over() AS gid, b.geom, pop_building AS population
FROM  buildings_residential_fusion b, x 
WHERE ST_Intersects(b.geom,x.geom);

ALTER TABLE population_census add primary key(gid);

CREATE INDEX ON population_census USING GIST (geom);

DROP TABLE IF EXISTS non_residential_buildings;
DROP TABLE IF EXISTS intersection_buildings_grid;
DROP TABLE IF EXISTS max_area;
DROP TABLE IF EXISTS buildings_points;
DROP TABLE IF EXISTS buildings_residential_intersect;
DROP TABLE IF EXISTS buildings_residential_fusion;
DROP TABLE IF EXISTS intersect_custom_landuse;




ALTER TABLE census ADD COLUMN built_up_residential NUMERIC;
UPDATE census SET built_up_residential = x.sum_area 
FROM 
(
	SELECT c.gid, sum(b.area) sum_area
	FROM buildings_residential_fusion b, census c 
	WHERE ST_Intersects(b.geom,c.geom)
	GROUP BY c.gid
) x
WHERE census.gid = x.gid;

DROP TABLE census_intersection

CREATE TABLE census_intersection AS 
SELECT row_number() over() as gid, pop, ST_Intersection(s.geom,c.geom) AS geom, c.built_up_residential
FROM study_area s, census c 
WHERE ST_Intersects(s.geom,c.geom)




WITH c AS (
	SELECT row_number() over() as gid, pop, ST_Intersection(s.geom,c.geom) AS geom, c.built_up_residential
	FROM study_area s, census c 
	WHERE ST_Intersects(s.geom,c.geom)
),
b AS (
	SELECT c.gid, sum(b.area) sum_part
	FROM c, buildings_residential_fusion b 
	WHERE ST_Intersects(c.geom,b.geom)
	GROUP BY c.gid
)
SELECT b.sum_part AS built_up_residential, (b.sum_part/c.built_up_residential) * c.pop AS pop, c.geom 
FROM c,b 
WHERE c.gid = b.gid; 
