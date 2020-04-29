DROP FUNCTION IF EXISTS insert_population_userinput;
CREATE OR REPLACE FUNCTION public.insert_population_userinput() 
RETURNS TRIGGER AS $table_insert_population$
DECLARE
	average_gross_living_area integer := select_from_variable_container_s('average_gross_living_area');
BEGIN
	

	INSERT INTO population_userinput(building_levels,building_levels_residential,area,population,buildings_modified_id,userid)
	VALUES(NEW.building_levels,NEW.building_levels_residential,ST_Area(NEW.geom::geography)::integer,
	(NEW.building_levels_residential * ST_AREA(NEW.geom::geography))/average_gross_living_area, NEW.gid, NEW.userid);
	
	RETURN NEW;
END;
$table_insert_population$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_insert_population ON buildings_modified; 
CREATE TRIGGER trigger_insert_population AFTER INSERT ON buildings_modified
FOR EACH ROW EXECUTE PROCEDURE insert_population_userinput();

/*
To-do

1. Condition trigger only if building is residential
2. Condition take Centroid building as geometry population
3. take given population if user provides population

*/


DROP TABLE buildings_modified

ALTER TABLE buildings_modified ADD COLUMN new_levels_residential integer 

ALTER TABLE buildings_modified DROP  COLUMN new_levels 

SELECT * FROM buildings_modified

DROP FUNCTION IF EXISTS insert_population_userinput;
CREATE OR REPLACE FUNCTION public.insert_population_userinput() 
RETURNS TRIGGER AS $table_insert_population$
DECLARE
	average_gross_living_area integer := select_from_variable_container_s('average_gross_living_area');
	count_population_geoms_building integer;
BEGIN

	
	IF NEW.building = 'residential' THEN 
		IF NEW.original_id IS NULL THEN 
			INSERT INTO population_userinput(building_levels,building_levels_residential,area,population,buildings_modified_id,userid)
			VALUES(NEW.building_levels,NEW.building_levels_residential,ST_Area(NEW.geom::geography)::integer,
			(NEW.building_levels_residential * ST_AREA(NEW.geom::geography))/average_gross_living_area, NEW.gid, NEW.userid);
		ELSE 
			
			DROP TABLE IF EXISTS original_population;
			CREATE TABLE original_population AS 
			SELECT * 
			FROM population_userinput 
			WHERE building_gid = 120337;
			
			count_population_geoms_building = SELECT count(*) FROM original_population;
			
			centroid_old = ST_Centroid(OLD.geom);
			centroid_new = ST_Centroid(NEW.geom);
		
			WITH updated_levels AS 
			(
				SELECT building_levels, building_levels_residential,	
				(area * building_levels_residential) AS old_gross_living_area, 
				(ST_AREA(NEW.geom::geography)/count_population_geoms_building)::integer * (building_levels_residential + COALESCE(NEW.building_levels_residential)) new_gross_living_area, 
				(ST_AREA(NEW.geom::geography)/count_population_geoms_building)::integer AS area, geom, population
				FROM original_population
			
			)
			SELECT building_levels + COALESCE(NEW.new_building_levels_residential), building_levels_residential +COALESCE(NEW.new_building_levels_residential),
			area, 
			CASE 
			WHEN OLD.geom = NEW.geom THEN geom 
			--Move population geometries with the 
			WHEN OLD.geom <> NEW.geom THEN ST_POINT(ST_X(geom)+(ST_X(centroid_old)-ST_X(centroid_new)),ST_Y(geom)+(ST_Y(centroid_old)-ST_Y(centroid_new)),4326)
				
			END AS geom, 
			CASE 
			WHEN old_gross_living_area = new_gross_living_area THEN population 
			WHEN old_gross_living_area > new_gross_living_area THEN population / (new_gross_living_area/old_gross_living_area)
			WHEN old_gross_living_area < new_gross_living_area THEN population + (new_gross_living_area-old_gross_living_area)*average_gross_living_area,
			END AS population 
			
			
			
			INSERT INTO population_userinput(building_levels,building_levels_residential,area,population,buildings_modified_id,userid)
					
			
			VALUES(NEW.building_levels,NEW.building_levels_residential,ST_Area(NEW.geom::geography)::integer,
			(NEW.building_levels_residential * ST_AREA(NEW.geom::geography))/average_gross_living_area, NEW.gid, NEW.userid);
		
			
		
		END IF;
	
	END IF;

	RETURN NEW;
END;
$table_insert_population$ LANGUAGE plpgsql;






DROP TRIGGER IF EXISTS trigger_insert_population ON buildings_modified; 
CREATE TRIGGER trigger_insert_population AFTER INSERT ON buildings_modified
FOR EACH ROW EXECUTE PROCEDURE insert_population_userinput();





CREATE OR REPLACE FUNCTION public.update_population_userinput()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$

BEGIN
	DELETE FROM population_userinput WHERE population_modified_id = NEW.id;
	INSERT INTO population_userinput(building_levels,building_levels_residential,area,population,buildings_modified_id,userid)
	VALUES(NEW.building_levels,NEW.building_levels_residential,ST_Area(NEW.geom::geography)::integer,
	(NEW.building_levels_residential * ST_AREA(NEW.geom::geography))/average_gross_living_area, NEW.gid, NEW.userid);

	RETURN NEW; 
END;
$function$;


SELECT * 
FROM population_userinput