CREATE OR REPLACE FUNCTION basic.trigger_insert_population_modified() 
RETURNS TRIGGER AS $trigger_insert_population_modified$
BEGIN

	PERFORM basic.population_modification(NEW.scenario_id); 
	RETURN NEW;
END;
$trigger_insert_population_modified$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_insert_way_modified ON customer.population_modified; 
CREATE TRIGGER trigger_insert_population_modified AFTER INSERT ON customer.population_modified
FOR EACH ROW EXECUTE PROCEDURE basic.trigger_insert_population_modified();

