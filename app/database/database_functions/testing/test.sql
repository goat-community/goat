DROP FUNCTION IF EXISTS compute_new_population;
CREATE OR REPLACE FUNCTION compute_new_population(building_gid_input integer, old_geom geometry, new_geom geometry, new_levels integer)
RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE
	
	x_old NUMERIC; 
	y_old NUMERIC;
	x_new NUMERIC;
	y_new NUMERIC;
	x_diff NUMERIC;
	y_diff NUMERIC;
    count_population_geoms_building integer;
   	average_gross_living_area integer := select_from_variable_container_s('average_gross_living_area');
BEGIN 
    
	SELECT ST_X((ST_DUMPPOINTS(old_geom)).geom),ST_Y((ST_DUMPPOINTS(old_geom)).geom)  
	INTO x_old, y_old
	LIMIT 1;
	SELECT ST_X((ST_DUMPPOINTS(new_geom)).geom), ST_Y((ST_DUMPPOINTS(new_geom)).geom)  
	INTO x_new, y_new
	LIMIT 1;
	
	x_diff = x_new - x_old;
	y_diff = y_new - y_old;

	
	RAISE NOTICE '%', x_diff;
	RAISE NOTICE '%', y_diff;

	DROP TABLE IF EXISTS original_population;
    CREATE TABLE original_population AS 
    SELECT * 
    FROM population_userinput p
    WHERE p.building_gid = building_gid_input;

    SELECT count(*) 
   	INTO count_population_geoms_building
    FROM original_population;
   
   	new_levels = COALESCE(new_levels,0);
   
	DROP TABLE updated_population;
	CREATE TABLE updated_population AS 
    WITH updated_levels AS 
    (
        SELECT building_levels, building_levels_residential,	
        (area * building_levels_residential) AS old_gross_living_area, 
        (ST_AREA(new_geom::geography)/count_population_geoms_building)::integer * (building_levels_residential + new_levels) new_gross_living_area, 
        (ST_AREA(new_geom::geography)/count_population_geoms_building)::integer AS area, geom, population
        FROM original_population

    )
    SELECT (building_levels + new_levels) AS building_levels, (building_levels_residential + new_levels) AS building_levels_residential,
    area, geom, old_gross_living_area, new_gross_living_area,
    CASE 
    WHEN old_gross_living_area = new_gross_living_area THEN population 
    WHEN old_gross_living_area > new_gross_living_area THEN population / (new_gross_living_area/old_gross_living_area)
    WHEN old_gross_living_area < new_gross_living_area THEN population + (new_gross_living_area-old_gross_living_area)*average_gross_living_area
    END AS population, population AS pop
    FROM updated_levels;
   
    DROP TABLE test;
   
   	IF ST_ASTEXT(old_geom) = ST_ASTEXT(new_geom) THEN 
   		CREATE TABLE test AS 
   		SELECT * FROM updated_population;
   	ELSEIF ST_ASTEXT(old_geom) <> ST_ASText(new_geom) AND ST_AREA(old_geom::geography)::integer = ST_AREA(new_geom::geography)::integer THEN
   		
   
       --WHEN  OR ST_Intersects(ST_BUFFER(geom,0.0000018), new_geom) THEN geom 
    --Move population geometries with the 
    	CREATE TABLE test AS 
    	SELECT building_levels, building_levels_residential, area, (ST_TRANSLATE(geom,x_diff,y_diff)) AS geom ,
    --ELSE ST_SNAP(geom, new_geom, 1) 
    	old_gross_living_area, new_gross_living_area, population, population AS pop
    	FROM updated_population;
    END IF;
   
   
END 
$function$;
