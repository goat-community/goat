DROP DOMAIN IF EXISTS aggregate_type;
CREATE DOMAIN aggregate_type AS TEXT
CHECK (
    VALUE IN ('avg', 'sum', 'count', 'min', 'max')
);

DROP FUNCTION IF EXISTS basic.aggregate_points_by_polygon; 
CREATE OR REPLACE FUNCTION basic.aggregate_points_by_polygon(table_to_aggregate text, aggregation_field text, type_of_aggregation aggregate_type, 
table_summary_areas text, group_by_field text, filter_non_spatial TEXT DEFAULT '', filter_geom geometry DEFAULT NULL)
 RETURNS SETOF JSONB 
 LANGUAGE plpgsql
AS $function$
DECLARE 
	query_aggregate TEXT; 
	filter_geom_table TEXT := ''; 
	filter_geom_condition TEXT := ''; 
	first_group_by TEXT;
	second_group_by TEXT;
	first_select_group TEXT; 
	second_select_group TEXT;
	aggregate_expression_1 TEXT;
	aggregate_expression_2 TEXT; 
BEGIN
	
	-- Define the aggregation expression
	aggregate_expression_1 = type_of_aggregation || '(a.' || aggregation_field || ')'; 
	aggregate_expression_2 = type_of_aggregation || '(a.value)'; 

	-- Check if table to aggregate needs to be filtered by a geometry
	IF filter_geom IS NOT NULL THEN 
		DROP TABLE IF EXISTS filter_geom;
		CREATE TABLE filter_geom AS 
		SELECT ST_SUBDIVIDE(filter_geom) geom; 
		CREATE INDEX ON filter_geom USING GIST(geom); 
		
		filter_geom_table = ', filter_geom f';
		filter_geom_condition = 'AND ST_Intersects(a.geom, f.geom)';	
	END IF;

	query_aggregate = '
	SELECT jsonb_object_agg(key, res) 
	FROM 
	( 
		SELECT jsonb_build_object('''|| aggregation_field ||''', value) AS res, key
		FROM 
		(
			SELECT s.'|| group_by_field ||'::text AS key, ' || aggregate_expression_2 || ' AS value
			FROM ' || table_summary_areas || ' s 
			CROSS JOIN LATERAL 
			(
				SELECT '|| aggregate_expression_1 ||' AS value
				FROM '|| table_to_aggregate ||' a ' || filter_geom_table || '
				WHERE ST_Intersects(s.geom, a.geom)
				'|| filter_non_spatial ||'
				'|| filter_geom_condition ||'
			) a 
			GROUP BY ' || group_by_field || '
		) j 
		WHERE value IS NOT NULL
	) t';  

	
	RETURN query EXECUTE query_aggregate; 
END;
$function$;

/*
EXPLAIN ANALYZE 
SELECT *
FROM basic.aggregate_points_by_polygon('basic.population', 'population', 'sum', 'temporal.temp_isochrone_fd316479c0154ccfb983712e01443c6c_subdivided', 'minute')

SELECT *
FROM basic.aggregate_points_by_polygon('basic.poi', 'category', 'count', 'temporal.temp_isochrone_fd316479c0154ccfb983712e01443c6c_subdivided', 'minute', 'category')
*/

-- SELECT *
-- FROM basic.aggregate_points_by_polygon('basic.population', 'population', 'sum', 'temporal.temp_isochrone_fd316479c0154ccfb983712e01443c6c_subdivided', 'minute')

-- DROP FUNCTION IF EXISTS basic.aggregate_points_by_polygon; 
-- CREATE OR REPLACE FUNCTION basic.aggregate_points_by_polygon(table_to_aggregate text, aggregation_field text, type_of_aggregation aggregate_type, 
-- table_summary_areas text, group_by_field text, filter_non_spatial TEXT DEFAULT '', second_group_by_field TEXT DEFAULT NULL, filter_geom geometry DEFAULT NULL)
--  RETURNS SETOF JSONB 
--  LANGUAGE plpgsql
-- AS $function$
-- DECLARE 
-- 	query_aggregate TEXT; 
-- 	filter_geom_table TEXT := ''; 
-- 	filter_geom_condition TEXT := ''; 
-- 	first_group_by TEXT;
-- 	second_group_by TEXT;
-- 	first_select_group TEXT; 
-- 	second_select_group TEXT;
-- 	aggregate_expression_1 TEXT;
-- 	aggregate_expression_2 TEXT; 
-- BEGIN
	
-- 	-- Define the aggregation expression
-- 	aggregate_expression_1 = type_of_aggregation || '(a.' || aggregation_field || ')'; 
-- 	aggregate_expression_2 = type_of_aggregation || '(a.value)'; 

-- 	-- Check if table to aggregate needs to be filtered by a geometry
-- 	IF filter_geom IS NOT NULL THEN 
-- 		DROP TABLE IF EXISTS filter_geom;
-- 		CREATE TABLE filter_geom AS 
-- 		SELECT ST_SUBDIVIDE(filter_geom) geom; 
-- 		CREATE INDEX ON filter_geom USING GIST(geom); 
		
-- 		filter_geom_table = ', filter_geom f';
-- 		filter_geom_condition = 'AND ST_Intersects(a.geom, f.geom)';	
-- 	END IF;

	
-- 	-- Build query for aggregation depending if there is one or two group by fields
-- 	IF second_group_by_field IS NULL THEN 
-- 		query_aggregate = '
-- 		SELECT jsonb_object_agg(key, res) 
-- 		FROM 
-- 		( 
-- 			SELECT jsonb_build_object('''|| aggregation_field ||''', value) AS res, key
-- 			FROM 
-- 			(
-- 				SELECT s.'|| group_by_field ||'::text AS key, ' || aggregate_expression_2 || ' AS value
-- 				FROM ' || table_summary_areas || ' s 
-- 				CROSS JOIN LATERAL 
-- 				(
-- 					SELECT '|| aggregate_expression_1 ||' AS value
-- 					FROM '|| table_to_aggregate ||' a ' || filter_geom_table || '
-- 					WHERE ST_Intersects(s.geom, a.geom)
-- 					'|| filter_non_spatial ||'
-- 					'|| filter_geom_condition ||'
-- 				) a 
-- 				GROUP BY ' || group_by_field || '
-- 			) j 
-- 		) t';  
	
-- 	ELSE 
-- 		query_aggregate = '
-- 		SELECT jsonb_object_agg(key, res) 
-- 		FROM 
-- 		( 
-- 			SELECT jsonb_object_agg(' || second_group_by_field || ', value) AS res, key
-- 			 FROM 
-- 			(
-- 				SELECT s.'|| group_by_field ||'::text AS key, ' || aggregate_expression_2 || ' AS value, ' || second_group_by_field ||'
-- 				FROM ' || table_summary_areas || ' s 
-- 				CROSS JOIN LATERAL 
-- 				(
-- 					SELECT '|| aggregate_expression_1 ||' AS value,' || second_group_by_field ||' 
-- 					FROM '|| table_to_aggregate ||' a ' || filter_geom_table || '
-- 					WHERE ST_Intersects(s.geom, a.geom)
-- 					'|| filter_geom_condition ||'
-- 					GROUP BY ' || second_group_by_field || '
-- 				) a 
-- 				GROUP BY ' || group_by_field || ', ' || second_group_by_field || '
-- 			) j 
-- 			GROUP BY key
-- 		) t'
-- 		;  
-- 	END IF; 
	
-- 	RETURN query EXECUTE query_aggregate; 
-- END;
-- $function$;

-- /*
-- EXPLAIN ANALYZE 
-- SELECT *
-- FROM basic.aggregate_points_by_polygon('basic.population', 'population', 'sum', 'temporal.temp_isochrone_fd316479c0154ccfb983712e01443c6c_subdivided', 'minute')

-- SELECT *
-- FROM basic.aggregate_points_by_polygon('basic.poi', 'category', 'count', 'temporal.temp_isochrone_fd316479c0154ccfb983712e01443c6c_subdivided', 'minute', 'category')
-- */
