CREATE OR REPLACE FUNCTION basic.split_by_drawn_lines(id_input integer, input_geom geometry)
RETURNS SETOF geometry
 LANGUAGE plpgsql
AS $function$
DECLARE 
	union_geom geometry;
	does_intersect boolean := FALSE; 
BEGIN 
	
	does_intersect = (
		SELECT TRUE 
		FROM drawn_features d 
		WHERE ST_Intersects(d.geom, (SELECT geom FROM drawn_features WHERE id = 82))
		LIMIT 1
	); 
	
	IF does_intersect = TRUE THEN 
		union_geom = 
		(
			SELECT ST_UNION(geom) AS geom 
			FROM drawn_features 
			WHERE id <> id_input
			AND ST_Intersects(geom, input_geom)
			AND (way_type IS NULL OR way_type <> 'bridge') 
		);
	END IF; 

	IF union_geom IS NOT NULL THEN
		RETURN query
		SELECT (dump).geom
		FROM (SELECT ST_DUMP(ST_CollectionExtract(ST_SPLIT(input_geom,union_geom),2)) AS dump) d;
	ELSE 
		RETURN query SELECT input_geom;
	END IF;
END 
$function$;
