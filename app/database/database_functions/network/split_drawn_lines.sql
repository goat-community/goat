DROP FUNCTION IF EXISTS split_by_drawn_lines;
CREATE OR REPLACE FUNCTION split_by_drawn_lines(id_input integer)
RETURNS SETOF geometry
 LANGUAGE sql
AS $function$
	SELECT (dump).geom
	FROM 
	(
		SELECT ST_DUMP(ST_CollectionExtract(ST_SPLIT(d.geom,u.geom),2)) AS dump
		FROM drawn_features d, 
		(
			SELECT ST_UNION(geom) AS geom 
			FROM drawn_features 
			WHERE id <> id_input
		) u
		WHERE id = id_input 
		AND ST_INtersects(d.geom,u.geom)
	) d;
$function$;