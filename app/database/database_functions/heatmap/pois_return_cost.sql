DROP FUNCTION IF EXISTS pois_return_cost;
CREATE FUNCTION pois_return_cost(point geometry, grid_id_input integer, snap_distance numeric) 
RETURNS SETOF NUMERIC AS
$BODY$
DECLARE
	v_geom geometry;
	v_cost NUMERIC;
BEGIN
	
	SELECT geom, cost 
	INTO v_geom, v_cost
	FROM reached_vertices_heatmap v
	WHERE grid_id = grid_id_input
	ORDER BY geom <-> point
	LIMIT 1;
	IF ST_Distance(v_geom,point) < snap_distance THEN
		RETURN QUERY SELECT v_cost;
	END IF;

END;
$BODY$ LANGUAGE plpgsql;