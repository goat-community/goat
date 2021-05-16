DROP FUNCTION IF EXISTS intersection_lines_polygons;
CREATE OR REPLACE FUNCTION intersection_lines_polygons(table_lines TEXT, line_attr text, table_polygon TEXT, polygon_attr TEXT)
RETURNS TABLE(id integer, arr_polygon_attr TEXT[], arr_shares integer[])
 LANGUAGE plpgsql
AS $function$
DECLARE
	sql_geometries_outside TEXT;
	sql_within TEXT;
	sql_intersects_outside TEXT;
	sql_intersects_same TEXT;
	sql_intersection TEXT;
BEGIN 
	
	sql_geometries_outside = 'DROP TABLE IF EXISTS outside;
	CREATE TEMP TABLE outside AS 
	SELECT ST_SUBDIVIDE(ST_DIFFERENCE(ST_ENVELOPE(ST_UNION(geom)),ST_UNION(geom))) AS geom
	FROM %1$s;
	CREATE INDEX ON outside USING GIST(geom);	
	';
	sql_geometries_outside = format(sql_geometries_outside, table_polygon);
	
	EXECUTE sql_geometries_outside;

	
	sql_within = 'DROP TABLE IF EXISTS shares_per_line;
		CREATE TEMP TABLE shares_per_line AS 
		SELECT l.%1$s::integer, ARRAY[p.%2$s::text] arr_attributes, ARRAY[100] arr_shares
		FROM %3$s l, %4$s p 
		WHERE ST_INTERSECTS(l.geom,p.geom) 
		AND ST_CONTAINS(p.geom,l.geom);
		ALTER TABLE shares_per_line ADD PRIMARY KEY(%1$s);';
	sql_within = format(sql_within, line_attr, polygon_attr, table_lines, table_polygon);
	
	EXECUTE sql_within;
	
	sql_intersects_outside = 'INSERT INTO shares_per_line
	WITH intersection AS 
	(
		SELECT DISTINCT l.%1$s, p.%2$s::text, 
		ST_LENGTH(ST_Intersection(l.geom, p.geom)) AS intersection_length, ST_LENGTH(l.geom) AS full_length 
		FROM %3$s l, outside o, %4$s p   
		WHERE ST_INTERSECTS(l.geom,o.geom)
		AND ST_INTERSECTS(l.geom, p.geom)
	),
	aggregated AS 
	(
		SELECT %1$s, ARRAY_AGG(%2$s) arr_polygon_attr, ARRAY_AGG(((intersection_length/full_length)*100)::integer) shares
		FROM intersection
		GROUP BY %1$s
	)
	SELECT id, arr_polygon_attr || ARRAY[''outside''] AS arr_polygon_attr, shares || ARRAY[100 - sum_int_array(shares)] shares
	FROM aggregated;';
	sql_intersects_outside = format(sql_intersects_outside, line_attr, polygon_attr, table_lines, table_polygon);
	
	EXECUTE sql_intersects_outside; 

	sql_intersects_same = 'DROP TABLE IF EXISTS cnt_intersects;
	CREATE TEMP TABLE cnt_intersects as 
	WITH l AS 
	(
		SELECT l.*
		FROM %3$s l
		LEFT JOIN shares_per_line s
		ON l.%1$s = s.%1$s
		WHERE s.%1$s IS NULL
	),
	d AS 
	(
		SELECT DISTINCT l.%1$s, p.%2$s::text
		FROM l, %4$s p
		WHERE ST_INTERSECTS(l.geom,p.geom)
	)
	SELECT %1$s line_attr, ARRAY_AGG(%2$s) arr_polygon_attr
	FROM d 
	GROUP BY %1$s;
	ALTER TABLE cnt_intersects ADD PRIMARY KEY(line_attr);
	
	INSERT INTO shares_per_line 
	SELECT line_attr::integer, arr_polygon_attr, ARRAY[100]
	FROM cnt_intersects
	WHERE ARRAY_LENGTH(arr_polygon_attr,1) = 1;
	';
	sql_intersects_same = format(sql_intersects_same, line_attr, polygon_attr, table_lines, table_polygon);
	
	EXECUTE sql_intersects_same;
		
	sql_intersection = 'INSERT INTO shares_per_line 
	WITH i AS 
	(
		SELECT l.%1$s, p.%2$s::text, ST_LENGTH(ST_Intersection(l.geom, p.geom)) AS intersection_length, ST_LENGTH(l.geom) AS full_length
		FROM cnt_intersects c, %3$s l, %4$s p
		WHERE ST_INTERSECTS(l.geom,p.geom)
		AND c.line_attr = l.%1$s
		AND ARRAY_LENGTH(arr_polygon_attr,1) > 1
	)
	SELECT %1$s::integer line_attr, ARRAY_AGG(%2$s) arr_polygon_attr, ARRAY_AGG(((intersection_length/full_length)*100)::integer) shares
	FROM i
	GROUP BY %1$s;';
	sql_intersection = format(sql_intersection, line_attr, polygon_attr, table_lines, table_polygon);
	
	EXECUTE sql_intersection; 
	
	RETURN query EXECUTE 'SELECT * FROM shares_per_line;';

END 
$function$;

/*
SELECT intersection_lines_polygons('ways','id','landuse','landuse'); 

DROP TABLE test;
CREATE TABLE test AS 
SELECT s.*, w.geom 
FROM intersection_lines_polygons('ways','id','landuse','landuse') s, ways w 
WHERE s.id = w.id
*/