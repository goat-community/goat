DROP TRIGGER IF EXISTS trigger_insert_pois ON pois_modified; 
CREATE TRIGGER trigger_insert_pois AFTER INSERT ON pois_modified
FOR EACH ROW EXECUTE PROCEDURE insert_pois_userinput();


DROP FUNCTION IF EXISTS insert_pois_userinput;
CREATE OR REPLACE FUNCTION public.insert_pois_userinput() 
RETURNS TRIGGER AS $table_insert_pois$

BEGIN
	INSERT INTO pois_userinput(name,amenity,opening_hours,geom,userid,wheelchair, pois_modified_id)	
	VALUES(NEW.name, NEW.amenity, NEW.opening_hours,NEW.geom,NEW.userid,NEW.wheelchair,NEW.id);
	RETURN NEW; 
END;
$table_insert_pois$ LANGUAGE plpgsql;