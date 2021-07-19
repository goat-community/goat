/*This function returns the sum of all points in an certain snapping distance in meters. 
 There is the option to define also an attribute (e.g. population numbers) that should be grouped by link.*/
DROP FUNCTION IF EXISTS footpaths_get_points_sum;
CREATE OR REPLACE FUNCTION footpaths_get_points_sum(table_point TEXT, snap_distance integer, weight_attr TEXT DEFAULT '')
RETURNS TABLE(id integer, points_sum integer)
 LANGUAGE plpgsql
AS $function$
DECLARE
	max_id integer := (SELECT max(f.id) FROM footpath_visualization f);
	min_border integer := 0;
	max_border integer := 0;
	step integer := 5000;           
	snap_distance_degree float := snap_distance::float * meter_degree();
BEGIN 
	
    IF weight_attr = '' THEN 

        WHILE min_border < max_id LOOP 
        
            RAISE NOTICE '% out of % calculated.',min_border, max_id;
        
            max_border = min_border + step;
            
            RETURN query EXECUTE 
            '
            WITH paths AS 
            (
                SELECT f.id, geom 
                FROM footpath_visualization f
                WHERE f.id >= $1 AND f.id <= $2
            )
            SELECT p.id, j.sum_point::integer
            FROM paths p
            CROSS JOIN LATERAL 
            (
                SELECT count(*) AS sum_point
                FROM '|| quote_ident(table_point) ||' b
                WHERE ST_DWITHIN(p.geom, b.geom, $3)
                HAVING count(*) IS NOT NULL 
                AND count(*) <> 0
            ) j' USING min_border, max_border, snap_distance_degree;
            
            min_border = min_border + step;
	
	    END LOOP;
	
	ELSE
		WHILE min_border < max_id LOOP 
        
            RAISE NOTICE '% out of % calculated.',min_border, max_id;
        
            max_border = min_border + step;
            
            RETURN query EXECUTE 
            '
            WITH paths AS 
            (
                SELECT f.id, geom 
                FROM footpath_visualization f
                WHERE f.id >= $1 AND f.id <= $2
            )
            SELECT p.id, j.sum_point::integer
            FROM paths p
            CROSS JOIN LATERAL 
            (
                SELECT SUM('|| quote_ident(weight_attr) ||') AS sum_point
                FROM '|| quote_ident(table_point) ||' b
                WHERE ST_DWITHIN(p.geom, b.geom, $3)
                HAVING SUM('|| quote_ident(weight_attr) ||') IS NOT NULL 
                AND SUM('|| quote_ident(weight_attr) ||') <> 0
            ) j' USING min_border, max_border, snap_distance_degree;
            
            min_border = min_border + step;
	
	    END LOOP;
	
    END IF; 

END; 
$function$;