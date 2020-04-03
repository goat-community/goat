DROP FUNCTION IF EXISTS insert_pois_userinput;
CREATE OR REPLACE FUNCTION public.insert_pois_userinput() 
RETURNS TRIGGER AS $table_insert_pois$

BEGIN
	INSERT INTO pois_userinput(name,amenity,opening_hours,geom,userid,wheelchair,pois_modified_id)	
	VALUES(NEW.name, NEW.amenity, NEW.opening_hours,NEW.geom,NEW.userid,NEW.wheelchair,NEW.id);
	
	IF select_from_variable_container_s('heatmap_auto_refresh') = 'yes' THEN 
		DELETE FROM reached_pois_heatmap WHERE userid = NEW.userid;
		PERFORM recompute_influenced_cells(NEW.userid,0.01126126);
	END IF;
	RETURN NEW;

END;
$table_insert_pois$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS update_pois_userinput;
CREATE OR REPLACE FUNCTION public.update_pois_userinput() 
RETURNS TRIGGER AS $table_update_pois$

BEGIN
	DELETE FROM pois_userinput WHERE pois_modified_id = NEW.id;
	INSERT INTO pois_userinput(name,amenity,opening_hours,geom,userid,wheelchair,pois_modified_id)	
	VALUES(NEW.name, NEW.amenity, NEW.opening_hours,NEW.geom,NEW.userid,NEW.wheelchair,NEW.id);

	IF select_from_variable_container_s('heatmap_auto_refresh') = 'yes' THEN 
		DELETE FROM reached_pois_heatmap WHERE userid = NEW.userid;
		PERFORM recompute_influenced_cells(NEW.userid,0.01126126);
	END IF;
	RETURN NEW; 
END;
$table_update_pois$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_insert_pois ON pois_modified; 
CREATE TRIGGER trigger_insert_pois AFTER INSERT ON pois_modified
FOR EACH ROW EXECUTE PROCEDURE insert_pois_userinput();


DROP TRIGGER IF EXISTS trigger_update_pois ON pois_modified; 
CREATE TRIGGER trigger_update_pois AFTER UPDATE ON pois_modified
FOR EACH ROW EXECUTE PROCEDURE update_pois_userinput();