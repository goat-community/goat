DROP FUNCTION IF EXISTS split_by_drawn_lines;
CREATE OR REPLACE FUNCTION split_by_drawn_lines(id_input integer, input_geom geometry)
RETURNS SETOF geometry
 LANGUAGE plpgsql
AS $function$
DECLARE 
	union_geom geometry;
BEGIN 
	
	union_geom := (SELECT ST_UNION(geom) AS geom 
	FROM drawn_features 
	WHERE id <> id_input
	AND ST_Intersects(geom,input_geom));

	IF union_geom IS NOT NULL THEN
		RETURN query
		SELECT (dump).geom
		FROM (SELECT ST_DUMP(ST_CollectionExtract(ST_SPLIT(input_geom,union_geom),2)) AS dump) d;
	ELSE 
		RETURN query SELECT input_geom;
	END IF;
END 
$function$;
