-- what we need as Input: A table called employees.
-- The table MUST contain these columns:
	-- geom::geometry - point geometry representing the location
	-- name::text - name of the company
	-- employed::int - number of persons registered to work for this company
	-- company_type::text - the type of the location (headquarters, multi-branch, single-branch, store, ...) TODO: customize by user

--Optional:
	--employees_adjusted: if the user knows the exact number of employees for a specific point, they can set it and it will not be overwritten.

--What the script does: it adjusts the number of employees, because usually not all workers who are registered at a place actually work there.
-- E.g. 10000 workers are registered at a company's headquarters, but not all work at the headquarters.


CREATE INDEX IF NOT EXISTS index_employees ON employees USING GIST (geom);
SELECT print('Clipping employees table with study area...');
WITH buffer AS
(
	SELECT ST_BUFFER(ST_UNION(study_area.geom), 0.045) FROM study_area
)
DELETE FROM employees AS a
USING buffer AS b
WHERE NOT ST_Intersects(a.geom, b.st_buffer);

ALTER TABLE employees ADD COLUMN IF NOT EXISTS employees_adjusted FLOAT;

-- set a no_auto_adjust flag on points for which the user has already specified an adjusted number of employees
ALTER TABLE employees ADD COLUMN IF NOT EXISTS no_auto_adjust BOOLEAN;
UPDATE employees
SET no_auto_adjust = FALSE 
--FROM employees
WHERE employees.employees_adjusted IS NULL;


-- first it creates a table of employees that are considered save employees.
SELECT print(format('Finding save employees: All workplaces (excluding %s with more than %s employees).', select_from_variable_container('company_types_requiring_employment_adjustment')::TEXT[], (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'save_employees_cutoff')));
DROP TABLE IF EXISTS employees_save;
CREATE TABLE employees_save as
SELECT distinct e.*
FROM employees e
WHERE NOT((e.type IN (SELECT UNNEST(select_from_variable_container('company_types_requiring_employment_adjustment')::TEXT[])))
	   AND e.employed > (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'save_employees_cutoff'))
 ORDER BY e.employed DESC;
 
 
 -- next it creates a table of unsave employees
SELECT print(format('Finding workplaces that need adjustment (%s with more than %s employees).', select_from_variable_container('company_types_requiring_employment_adjustment')::TEXT[], (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'save_employees_cutoff')));
DROP TABLE IF EXISTS employees_unsave;
CREATE TABLE employees_unsave as
SELECT distinct e.*
 FROM employees e
 WHERE    ((e.type IN (SELECT UNNEST(select_from_variable_container('company_types_requiring_employment_adjustment')::TEXT[])))
		AND e.employed > (SELECT variable_simple::integer FROM variable_container WHERE identifier = 'save_employees_cutoff'))
 ORDER BY e.employed DESC;

 
CREATE INDEX index_employees_save ON employees_save  USING GIST (geom);
CREATE INDEX index_employees_unsave ON employees_unsave USING GIST (geom);

 ------------------------------------------------------------------------------------------
------------------create table of buildings that only house save employees-----------------
-------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS all_buildings;
CREATE TABLE all_buildings AS
SELECT osm_id,building, "addr:housenumber",tags,way as geom
FROM planet_osm_polygon 
WHERE building IS NOT NULL;
CREATE INDEX index_all_buildings ON all_buildings  USING GIST (geom);

DROP TABLE IF EXISTS potentially_save_buildings;
CREATE TABLE potentially_save_buildings AS			--Get all buildings that house save employees 
	SELECT DISTINCT a_b.*
	FROM all_buildings a_b, employees_save e_s
	WHERE st_contains(a_b.geom, e_s.geom);
CREATE INDEX index_potentially_save_buildings ON potentially_save_buildings  USING GIST (geom);

DROP TABLE IF EXISTS buildings_save;					--remove buildings that also house unsave employees
CREATE TABLE buildings_save AS
	SELECT DISTINCT sb.*
	FROM 
	potentially_save_buildings AS sb LEFT JOIN
	employees_unsave AS es ON
	ST_Intersects(es.geom, sb.geom)
	WHERE es.gid IS NULL;
CREATE INDEX index_buildings_save ON buildings_save  USING GIST (geom);	
SELECT print(format('There are %s buildings that house exclusively save employees', (SELECT count(*) FROM buildings_save)));

DROP TABLE IF EXISTS potentially_save_buildings;

------------------------------------------------------------------------------------------
------------------calculate the area per employee for these buildings---------------------
------------------------------------------------------------------------------------------
ALTER TABLE buildings_save ADD COLUMN IF NOT EXISTS area_per_employee FLOAT;
ALTER TABLE buildings_save ADD COLUMN IF NOT EXISTS area FLOAT;
ALTER TABLE buildings_save ADD COLUMN IF NOT EXISTS sum_employees FLOAT;

WITH se AS (
		SELECT s.sum, s.osm_id
		FROM (
			SELECT
			buildings_save.osm_id,
			buildings_save.geom,
			coalesce(sum(employees_save.employed), -1) AS sum
			FROM buildings_save  
				LEFT JOIN employees_save
				ON ST_Intersects(buildings_save.geom, employees_save.geom) 
				GROUP BY buildings_save.osm_id, buildings_save.geom, buildings_save.area
				ORDER BY sum DESC
		) s )

UPDATE buildings_save SET sum_employees = se.sum
FROM se
WHERE se.osm_id = buildings_save.osm_id;

UPDATE buildings_save SET
	area = st_area(buildings_save.geom::geography);

UPDATE buildings_save SET
	area_per_employee = area/sum_employees
		WHERE sum_employees > 0;
	
DROP TABLE IF EXISTS employees_save;
------------------------------------------------------------------------------------------
------------------create table of buildings that house unsave_employees-------------------
------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS buildings_unsave;
CREATE TABLE buildings_unsave AS
 	SELECT DISTINCT all_buildings.*
 	FROM all_buildings, employees_unsave
 	WHERE st_contains(all_buildings.geom, employees_unsave.geom);
 
ALTER TABLE buildings_unsave ADD COLUMN IF NOT EXISTS area FLOAT;
UPDATE buildings_unsave
SET area = st_area(buildings_unsave.geom::geography);
DROP TABLE IF EXISTS all_buildings;

------------------------------------------------------------------------------------------
------------------get median of area per employee for save employees----------------------
------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS median;
CREATE TABLE median AS 
	SELECT PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY area_per_employee)
	FROM buildings_save;
SELECT print(format('These buildings have on average %s m² per employee', (SELECT percentile_disc FROM median)));
DROP TABLE IF EXISTS buildings_save;
	

------------------------------------------------------------------------------------------
-------------adjust number of unsave employees according to area per employee ratio-------
------------------------------------------------------------------------------------------
ALTER TABLE employees_unsave ADD COLUMN IF NOT EXISTS area FLOAT;

WITH b AS (
	SELECT st_area(b.geom::geography), b.geom
	FROM buildings_unsave b)

UPDATE employees_unsave
SET area = b.st_area
FROM b
WHERE st_contains(b.geom, employees_unsave.geom);

SELECT print('Adjusting the number of employees at unsave workplaces using the average area per employee...');
ALTER TABLE employees_unsave ADD COLUMN IF NOT EXISTS employees_adjusted FLOAT;
UPDATE employees_unsave
SET employees_adjusted = area/median.percentile_disc
FROM median;
DROP TABLE IF EXISTS median;
DROP TABLE IF EXISTS buildings_unsave;
------------------------------------------------------------------------------------------
-------------put number of adjusted employees into original employees table.-------
-------------keep possible manual entries for employees_adjusted----------------
------------------------------------------------------------------------------------------

UPDATE employees
SET employees_adjusted = employees_unsave.employees_adjusted
FROM employees_unsave
WHERE employees.no_auto_adjust = FALSE AND employees_unsave.gid = employees.gid;

UPDATE employees
SET employees_adjusted = employees.employed
WHERE employees.employees_adjusted IS NULL;

SELECT print('Adjusting employees is done.');

DROP TABLE IF EXISTS employees_unsave;




-----------------------------------------------------------------------------
-----------------insert number of employees into poi table-------------------
-----------------------------------------------------------------------------
DROP TABLE IF EXISTS poi_employees;
CREATE TABLE poi_employees AS 
SELECT * FROM (
	WITH info AS
	(
		SELECT KEY AS amenity, value::int AS employees
		FROM jsonb_each ((SELECT  variable_object FROM variable_container WHERE variable_container.identifier = 'poi_employees'))
		AS x
	)
	SELECT r_pois.geom::geometry, r_pois.name, r_pois.amenity, info.employees
	FROM pois
	LEFT JOIN info ON r_pois.amenity = info.amenity
	WHERE employees IS NOT NULL
) a;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS amenity TEXT;
SELECT print(format('Adding %s employees from %s pois to employee table...', (SELECT sum(employees) FROM poi_employees), (SELECT count(*) FROM poi_employees)));
INSERT INTO employees (geom, name, amenity, employees_adjusted)
SELECT poi_employees.geom, poi_employees.name, poi_employees.amenity, poi_employees.employees
FROM poi_employees;
DROP TABLE poi_employees;

SELECT print(format('There are a total of %s employees in the study area. It was set in the config that there should be %s employees in the study area.', (SELECT SUM(employees_adjusted) FROM employees), 874000))
SELECT print(format('The values will be matched by multiplying employees of POIs and %s with a factor.', select_from_variable_container('company_types_requiring_employment_adjustment')::TEXT[]))


WITH adjustable_sum AS
(
	SELECT sum(employees_adjusted )
	FROM employees
	WHERE employees.amenity IS NOT NULL OR employees.type IN (SELECT UNNEST(select_from_variable_container('company_types_requiring_employment_adjustment')::TEXT[]))
)
UPDATE employees 
SET employees_adjusted = employees_adjusted::numeric * (( (SELECT sum FROM adjustable_sum)::numeric + ((SELECT variable_simple::numeric FROM variable_container WHERE identifier = 'total_employees')::numeric - (SELECT SUM(employees_adjusted) FROM employees)::numeric )) / (SELECT sum FROM adjustable_sum)::numeric)::numeric
FROM adjustable_sum
WHERE employees.amenity IS NOT NULL OR employees.type IN (SELECT UNNEST(select_from_variable_container('company_types_requiring_employment_adjustment')::TEXT[]));

SELECT print(format('There are now %s employees in the study area', (SELECT sum(employees_adjusted) FROM employees))); 






--SELECT round(gid/30, 0) * 30 FROM pois GROUP BY round(gid/30, 0) * 30


--TODO: find way to delete duplicate entries after adding pois (point already existed in employees shapefile)
--Idea: you would have to check in close proximity for every added POI if there is another point with the same name.
--DELETE from employees
--where name in (select name from employees group by name having count(name) > 1 ORDER BY name)

