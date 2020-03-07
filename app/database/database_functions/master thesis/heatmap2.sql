CREATE OR REPLACE FUNCTION public.heatmap2(userid integer, _dict TEXT)
 RETURNS TABLE(grid_id integer, geom geometry, accessibility_index numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
	dict jsonb;
	i jsonb;
	sql_query text =  'SELECT grid_id,geom,';
	sql_single_query text;
	array_amenities text[];

BEGIN
  


Return query
WITH amenity_sensitivity_weight AS
(
	SELECT jsonb_object_keys(x.jsons::jsonb) AS amenity, ((x.jsons->>jsonb_object_keys(x.jsons::jsonb)::TEXT)::jsonb->>'sensitivity')::NUMERIC AS sensitivity, ((x.jsons->>jsonb_object_keys(x.jsons::jsonb)::TEXT)::jsonb->>'weight')::NUMERIC AS weight
	FROM (
		SELECT value AS jsons FROM jsonb_array_elements(_dict::jsonB)
	)
	AS x
),

user_pois AS
(
	SELECT cell_id, object_id, cost
	FROM reached_points
	WHERE user_id = 1 OR user_id = userid
),

amenity_ids AS
(
	SELECT t1.amenity, gid, sensitivity, weight FROM pois_userinput t1 LEFT JOIN amenity_sensitivity_weight t2 ON t1.amenity=t2.amenity WHERE t2.amenity IS NOT NULL
),

needed_data AS
(
	SELECT user_pois.*, amenity_ids.amenity, sensitivity, weight  FROM user_pois INNER JOIN amenity_ids ON gid = object_id
),

with_impedance_weighted AS
(
	SELECT *, SensitivityFunction(cost, sensitivity) * weight AS weighted_sensitivity_cost FROM needed_data
),

summed_costs AS
(
	SELECT sum(weighted_sensitivity_cost) AS idx, cell_id FROM with_impedance_weighted GROUP BY cell_id
)

SELECT grid_500.grid_id, grid_500.geom, idx AS accessibility_index FROM grid_500 INNER JOIN summed_costs ON grid_500.grid_id = cell_id;





  

END;
$function$
;






SELECT heatmap2(343454, '[{"primary_school":{"sensitivity":-0.004,"weight":1}},{"kindergarten":{"sensitivity":-0.003,"weight":1}},{"secondary_school":{"sensitivity":-0.003,"weight":1}},{"library":{"sensitivity":-0.003,"weight":1}}]')




/*
SELECT jsonb_object_keys(x.jsons::jsonb) AS amenity, ((x.jsons->>jsonb_object_keys(x.jsons::jsonb)::TEXT)::jsonb->>'sensitivity')::NUMERIC AS sensitivity, ((x.jsons->>jsonb_object_keys(x.jsons::jsonb)::TEXT)::jsonb->>'weight')::NUMERIC AS weight
	FROM (
		SELECT value AS jsons FROM json_array_elements('[{"primary_school":{"sensitivity":-0.004,"weight":1}},{"kindergarten":{"sensitivity":-0.003,"weight":1}},{"secondary_school":{"sensitivity":-0.003,"weight":1}},{"library":{"sensitivity":-0.003,"weight":1}}]')
	)
	AS x


*/


