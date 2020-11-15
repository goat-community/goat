DROP FUNCTION IF EXISTS insert_pois;
CREATE OR REPLACE FUNCTION public.insert_pois_userinput() 
RETURNS TRIGGER AS $table_insert_pois$

BEGIN

	DELETE FROM pois_userinput WHERE pois_modified_id = NEW.gid;

	INSERT INTO pois_userinput(name,amenity,opening_hours,geom,scenario_id,wheelchair,pois_modified_id)	
	VALUES(NEW.name, NEW.amenity, NEW.opening_hours,NEW.geom,NEW.scenario_id,NEW.wheelchair,NEW.gid);

	PERFORM reached_pois_heatmap(ST_BUFFER(NEW.geom,0.0014),0.0014,1,NEW.scenario_id) ;
	
	RETURN NEW;

END;
$table_insert_pois$ LANGUAGE plpgsql;

	
DROP FUNCTION IF EXISTS update_pois_userinput CASCADE;
CREATE OR REPLACE FUNCTION public.update_pois_userinput() 
RETURNS TRIGGER AS $table_update_pois$

BEGIN

	DELETE FROM pois_userinput WHERE pois_modified_id = NEW.gid;

	INSERT INTO pois_userinput(name,amenity,opening_hours,geom,scenario_id,wheelchair,pois_modified_id)	
	VALUES(NEW.name, NEW.amenity, NEW.opening_hours,NEW.geom,NEW.scenario_id,NEW.wheelchair,NEW.gid);
	DELETE FROM reached_pois_heatmap WHERE gid = NEW.gid;
	PERFORM reached_pois_heatmap(ST_BUFFER(NEW.geom,0.0014),0.0014,1,NEW.scenario_id) ;
	
	RETURN NEW;
END;
$table_update_pois$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS delete_pois_userinput CASCADE;
CREATE OR REPLACE FUNCTION public.delete_pois_userinput() 
RETURNS TRIGGER AS $table_delete_pois$

BEGIN
	DELETE FROM pois_userinput WHERE pois_modified_id = OLD.gid;
	RETURN NEW;
END;
$table_delete_pois$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_insert_pois ON pois_modified; 
CREATE TRIGGER trigger_insert_pois AFTER INSERT ON pois_modified
FOR EACH ROW EXECUTE PROCEDURE insert_pois_userinput();

DROP TRIGGER IF EXISTS trigger_update_pois ON pois_modified; 
CREATE TRIGGER trigger_update_pois AFTER UPDATE ON pois_modified
FOR EACH ROW EXECUTE PROCEDURE update_pois_userinput();

DROP TRIGGER IF EXISTS trigger_delete_pois ON pois_modified; 
CREATE TRIGGER trigger_delete_pois AFTER DELETE ON pois_modified
FOR EACH ROW EXECUTE PROCEDURE delete_pois_userinput();