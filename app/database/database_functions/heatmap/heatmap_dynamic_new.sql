DROP FUNCTION IF EXISTS heatmap_dynamic_new;
CREATE OR REPLACE FUNCTION public.heatmap_dynamic_new(amenities_json jsonb, modus integer DEFAULT 1, userid_input integer DEFAULT 1, scenario_id integer DEFAULT 1)
 RETURNS TABLE(grid_id integer, accessibility_index bigint)
 LANGUAGE plpgsql
AS $function$
DECLARE
	array_amenities text[];
	pois_one_entrance text[] := select_from_variable_container('pois_one_entrance');
	pois_more_entrances text[] := select_from_variable_container('pois_more_entrances');
	sensitivities integer[] := select_from_variable_container('heatmap_sensitivities')::integer[];
	translation_sensitivities jsonb;
	excluded_pois_id integer[];
BEGIN
  	
	SELECT array_agg(_keys)
	INTO array_amenities
	FROM (SELECT jsonb_object_keys(amenities_json) _keys) x;
	
	SELECT jsonb_object_agg(k, (sensitivities  # (v ->> 'sensitivity')::integer)::smallint)
	INTO translation_sensitivities
	FROM jsonb_each(amenities_json) AS u(k, v);

	IF modus = 1 THEN 
		RETURN query 
		SELECT s.grid_id, sum(s.accessibility_index) AS accessibility_index 
		FROM 
		(
			SELECT u.grid_id, u.accessibility_index * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index  
			FROM (
				SELECT gridids, amenity, accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
				FROM reached_pois_heatmap 
				WHERE amenity IN (SELECT UNNEST(pois_one_entrance))
				AND amenity IN (SELECT UNNEST(array_amenities))
			)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
			UNION ALL 
			SELECT u.grid_id, max(u.accessibility_index) * (amenities_json -> x.amenity ->> 'weight')::SMALLINT AS accessibility_index
			FROM (
				SELECT gridids, amenity, name,  accessibility_indices[(translation_sensitivities ->> amenity)::integer:(translation_sensitivities ->> amenity)::integer][1:]
				FROM reached_pois_heatmap
				WHERE amenity IN (SELECT UNNEST(pois_more_entrances))
				AND amenity IN (SELECT UNNEST(array_amenities))
			)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
			GROUP BY u.grid_id, x.amenity, x.name
		) s
		GROUP BY s.grid_id;
	ELSE 
	
	END IF;
END;
$function$;

DROP TABLE test 


SELECT u.grid_id, u.accessibility_index --* (amenities_json -> x.amenity ->> 'weight')::SMALLINT  
FROM (
	SELECT gridids, amenity, accessibility_indices[3:3][1:]
	FROM reached_pois_heatmap 
	WHERE amenity IN (SELECT UNNEST(ARRAY['kindergarten']))
	AND amenity IN (SELECT UNNEST(ARRAY['kindergarten','bus_stop']))
)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
UNION ALL 
SELECT u.grid_id, max(u.accessibility_index) --* (amenities_json -> x.amenity ->> 'weight')::SMALLINT
FROM (
	SELECT gridids, amenity, name,  accessibility_indices[1][1:]
	FROM reached_pois_heatmap
	WHERE amenity IN (SELECT UNNEST(ARRAY['bus_stop']))
	AND amenity IN (SELECT UNNEST(ARRAY['kindergarten','bus_stop']))
)x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
GROUP BY u.grid_id, x.amenity, x.name; 	


SELECT select_from_variable_container('heatmap_sensitivities')

SELECT jsonb_set('{"f1":1,"f2":null}', '{0,f1}','[2,3,4]', false)

EXPLAIN ANALYZE 

SELECT jsonb_object_agg(k,v) 
FROM (
	SELECT jsonb_object_agg(k, (ARRAY[150000,200000,250000,300000,350000,400000,450000] # (v -> 'sensitivity')::integer)::SMALLINT)
	FROM jsonb_each('{"kindergarten":{"sensitivity":250000,"weight":1},"bus_stop":{"sensitivity":250000,"weight":1}}'::jsonb) AS u(k, v)
) x

jsonb_agg

gridids # 233

EXPLAIN ANALYZE 

SELECT * 
FROM heatmap_dynamic_new(1, '{"kindergarten":{"sensitivity":250000,"weight":1},"bus_stop":{"sensitivity":250000,"weight":1}}'::jsonb,1)

SELECT * FROM test 

GROUP BY grid_id 