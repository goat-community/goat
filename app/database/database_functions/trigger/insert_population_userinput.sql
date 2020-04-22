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