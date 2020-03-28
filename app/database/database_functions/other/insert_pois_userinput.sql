
DROP FUNCTION insert_pois_userinput CASCADE;
CREATE OR REPLACE FUNCTION public.insert_pois_userinput() 
RETURNS TRIGGER AS $table_insert_pois$
DECLARE 
	influenced_cells int[];
	points_array NUMERIC[][];
BEGIN
	INSERT INTO pois_userinput(name,amenity,opening_hours,geom,userid,wheelchair,pois_modified_id)	
	VALUES(NEW.name, NEW.amenity, NEW.opening_hours,NEW.geom,NEW.userid,NEW.wheelchair,NEW.id);
	
	PERFORM PropagateInsert(pois_userinput.gid, NEW.userid, NEW.amenity)
	FROM pois_userinput
	WHERE pois_modified_id = NEW.id;
	--0.01126126
	RETURN NEW; 
END;
$table_insert_pois$ LANGUAGE plpgsql;

DROP FUNCTION update_pois_userinput CASCADE;
CREATE OR REPLACE FUNCTION public.update_pois_userinput() 
RETURNS TRIGGER AS $table_update_pois$

BEGIN																						--new.id = 226
	DELETE FROM reached_points WHERE object_id = (SELECT DISTINCT pois_userinput.gid FROM pois_modified, pois_userinput WHERE pois_modified_id = NEW.id);
	DELETE FROM pois_userinput WHERE pois_modified_id = NEW.id;
	
	INSERT INTO pois_userinput(name,amenity,opening_hours,geom,userid,wheelchair,pois_modified_id)	
	VALUES(NEW.name, NEW.amenity, NEW.opening_hours,NEW.geom,NEW.userid,NEW.wheelchair,NEW.id);
	PERFORM PropagateInsert(pois_userinput.gid, NEW.userid, NEW.amenity)
	FROM pois_userinput
	WHERE pois_modified_id = NEW.id;
	RETURN NEW; 
END;
$table_update_pois$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_insert_pois ON pois_modified; 
CREATE TRIGGER trigger_insert_pois AFTER INSERT ON pois_modified
FOR EACH ROW EXECUTE PROCEDURE insert_pois_userinput();


DROP TRIGGER IF EXISTS trigger_update_pois ON pois_modified; 
CREATE TRIGGER trigger_update_pois AFTER UPDATE ON pois_modified
FOR EACH ROW EXECUTE PROCEDURE update_pois_userinput();



/*DO $$
DECLARE 
	influenced_cells int[];
	points_array NUMERIC[][];
BEGIN
																     --0.01126126
	influenced_cells = SELECT GetCellsInfluencedByGeometry(ARRAY[st_setsrid(ST_POINT(11.2132875648011, 48.194472095658796), 4326)::geometry], 0.01);
	points_array = (SELECT array_agg(ARRAY[ST_X(st_centroid(geom))::numeric,ST_Y(ST_Centroid(geom))::numeric]) FROM grid_500 WHERE grid_id IN (SELECT unnest(influenced_cells)));
	PERFORM precalculate_grid(100, 'grid_500'::TEXT, 15, points_array, 2::NUMERIC, influenced_cells, 1, 'walking_standard'::TEXT);
	--CREATE TABLE points_array AS
	--SELECT * FROM points_array;
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------------------------------------

SELECT GetCellsInfluencedByGeometry(ARRAY[st_setsrid(ST_POINT(11.2132875648011, 48.194472095658796), 4326)::geometry], 0.01);
-- influenced_cells: {7,10,36,43,63,99,126,205,233,249,262,271,281,289,298,304,322,356,387,466,479}
-- points_array: {{11.2159648872149,48.1966022942256},{11.2159648872149,48.1876195666537},{11.2198545923951,48.1921111272717},{11.2140200346248,48.1988477300806},{11.2159648872149,48.1921111272717},{11.217909739805,48.1988477300806},{11.2081854768544,48.1921111272717},{11.217909739805,48.1943567599562},{11.2081854768544,48.1966022942256},{11.2198545923951,48.1966022942256},{11.2159648872149,48.2010930675222},{11.2120751820347,48.1876195666537},{11.2101303294446,48.1943567599562},{11.2120751820347,48.1921111272717},{11.2120751820347,48.1966022942256},{11.2062406242643,48.1943567599562},{11.2140200346248,48.1943567599562},{11.2101303294446,48.1988477300806},{11.2101303294446,48.1898653961712},{11.2140200346248,48.1898653961712},{11.217909739805,48.1898653961712}}
 */
EXPLAIN ANALYZE
SELECT recalculate_grid('grid_500'::TEXT, ARRAY[7])--,10,36,43,63,99,126,205,233,249,262,271,281,289,298,304,322,356,387,466,479]);



DELETE FROM pois_modified;
INSERT INTO pois_modified(name, amenity, opening_hours, geom, userid)	
VALUES('_sArrrrAA', 'kindergarden', NULL, st_setsrid(ST_POINT(11.2132875648011, 48.194472095658796), 4326)::geometry, 10);
	
SELECT precalculate_grid(100, 'grid_500'::TEXT, 1, ARRAY[[11.21402, 48.1943567]], 1::NUMERIC, ARRAY[322], 1, 'walking_standard'::TEXT);

--SELECT * FROM public.precalculate_grid(100, 'grid_500'::TEXT, 15, ARRAY[[11.2570,48.1841]], 5, ARRAY[1], 1, 'walking_standard');

--SELECT ARRAY[ST_X(st_centroid(geom))::numeric,ST_Y(ST_Centroid(geom))::numeric] FROM grid_500 WHERE grid_id IN (SELECT unnest(GetCellsInfluencedByGeometry(ARRAY[st_setsrid(ST_POINT(11.2132875648011, 48.194472095658796), 4326)::geometry], 0.01126126)));

SELECT array_agg(ARRAY[ST_X(st_centroid(geom))::numeric,ST_Y(ST_Centroid(geom))::numeric]) FROM grid_500 WHERE grid_id IN (SELECT unnest(GetCellsInfluencedByGeometry(ARRAY[st_setsrid(ST_POINT(11.2132875648011, 48.194472095658796), 4326)::geometry], 0.01126126)));*/