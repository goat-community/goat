DROP FUNCTION IF EXISTS recompute_influenced_cells;
CREATE FUNCTION recompute_influenced_cells(userid_input integer, influencing_radius numeric) 
RETURNS SETOF void AS
$BODY$
DECLARE
    _grid_id integer;
   	_iso_geom geometry;
    _poi_geom geometry; 
    buffer geometry;
BEGIN
	
	DROP TABLE IF EXISTS pois_to_check;
	CREATE TEMP TABLE pois_to_check AS
	SELECT * 
	FROM pois_userinput 
	WHERE userid = userid_input;
	CREATE INDEX ON pois_to_check USING GIST(geom);
	
	SELECT ST_BUFFER(ST_UNION(geom),influencing_radius)
	INTO buffer
	FROM pois_to_check;

	FOR _grid_id, _iso_geom IN SELECT grid_id,iso_geom FROM grid_500 WHERE ST_Intersects(buffer,geom) 
	LOOP
		INSERT INTO reached_pois_heatmap(poi_gid,amenity,name,cost,geom,grid_id,userid) 
		SELECT x.gid, x.amenity, x.name, pois_return_cost(x.geom, x._grid_id, 0.0009), x.geom, x._grid_id, x.userid_input
		FROM (
			SELECT gid, amenity, name, geom, _grid_id, userid_input 
			FROM pois_to_check p
			WHERE ST_Intersects(p.geom,_iso_geom)
		) x;
	END LOOP;
END;
$BODY$ LANGUAGE plpgsql;
--SELECT recompute_influenced_cells(602589,0.01126126);
