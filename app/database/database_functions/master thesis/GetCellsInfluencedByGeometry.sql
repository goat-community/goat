-- Returns all cell ids that are within a specified radius of the input geometry

DROP FUNCTION IF EXISTS GetCellsInfluencedByGeometry;
CREATE FUNCTION GetCellsInfluencedByGeometry(g geometry[], influencing_radius numeric) RETURNS integer[] AS
$BODY$
DECLARE
    r integer ARRAY;
BEGIN
    r = (
    	SELECT array_agg(grid_id)
   		FROM grid_500
   		WHERE st_contains(st_buffer(st_union(g), influencing_radius), grid_500.geom)
   	);
    return r;
END;
$BODY$ LANGUAGE plpgsql;


SELECT GetCellsInfluencedByGeometry((SELECT array_agg( geom) FROM pois_modified), 0.01)

CREATE INDEX gid ON grid_500(grid_id)
ALTER TABLE grid_500
ADD COLUMN influenced integer;
EXPLAIN ANALYZE
UPDATE grid_500
SET influenced = 2
WHERE grid_500.grid_id IN (SELECT UNNEST(GetCellsInfluencedByGeometry((SELECT array_agg(geom) FROM pois_modified), 0.01)))