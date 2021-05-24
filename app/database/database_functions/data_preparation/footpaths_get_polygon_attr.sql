/*This function intersects the footpath table with a polygon table of choice 
and returns the polygon attr and the share of each intersection as arrays. It is expected that there is no overlapping between the polygons. */
DROP FUNCTION IF EXISTS footpaths_get_polygon_attr;
CREATE OR REPLACE FUNCTION footpaths_get_polygon_attr(table_polygon TEXT, polygon_attr TEXT)
RETURNS TABLE(id integer, arr_polygon_attr TEXT[], arr_shares float[])
 LANGUAGE plpgsql
AS $function$
DECLARE
	max_id integer := (SELECT max(f.id) FROM footpath_visualization f);
	min_border integer := 0;
	max_border integer := 0;
	step integer := 5000;
BEGIN 
	
	WHILE min_border < max_id LOOP 
	
		RAISE NOTICE '% out of % calculated.',min_border, max_id;
	
		max_border = min_border + step;
		
		RETURN query EXECUTE 
		
		'WITH paths AS 
		(
			SELECT f.id, geom 
			FROM footpath_visualization f
			WHERE f.id >= $1 AND f.id <= $2
		)
		SELECT p.id, j.arr_polygon_attr, j.arr_intersection 
		FROM paths p
		CROSS JOIN LATERAL 
		(
			SELECT ARRAY_AGG(attr) AS arr_polygon_attr, ARRAY_AGG(share_intersection) AS arr_intersection 
			FROM 
			(
				SELECT '|| quote_ident(polygon_attr) ||'::text AS attr, 
				ST_LENGTH(ST_Intersection(ST_UNION(n.geom),p.geom))/ST_LENGTH(p.geom) AS share_intersection
				FROM '|| quote_ident(table_polygon) ||' n
				WHERE ST_INTERSECTS(p.geom, n.geom) 
				GROUP by ' || quote_ident(polygon_attr) || '
			) x
		) j;' USING min_border, max_border;
		
		min_border = min_border + step;
		
	END LOOP;

END; 
$function$;

/*
CREATE TABLE test AS 
SELECT id, COALESCE(arr_polygon_attr[array_position(arr_shares, array_greatest(arr_shares))]::integer, 0) AS val, 
COALESCE(array_greatest(arr_shares), 0) AS share_intersection
FROM footpaths_get_polygon_attr('noise_day_street','noise_level_db');

Benchmark Test: 25.116 s (68540 paths)
*/
