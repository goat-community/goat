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
		SELECT value AS jsons FROM jsonb_array_elements(_dict::jsonb)
	)
	AS x
),

user_pois AS
(
	SELECT * FROM
	(
		SELECT cell_id, object_id, cost
		FROM reached_points LEFT JOIN (SELECT UNNEST(deleted_feature_ids) AS deleted_feature_ids FROM user_data WHERE user_data.userid = heatmap2.userid AND layer_name = 'pois') AS hidden_features ON hidden_features.deleted_feature_ids = reached_points.object_id
		WHERE (user_id IS NULL  AND hidden_features.deleted_feature_ids IS NULL) OR user_id = userid
	) AS user_pois_deleted LEFT JOIN pois_modified ON object_id = original_id
	WHERE original_id IS NULL
	-- last join could be avoided, if modified original_pois were marked as 'deleted' in the user_data table.
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






--SELECT heatmap2(343454, '[{"kindergarten":{"sensitivity":-0.003,"weight":1}},{"primary_school":{"sensitivity":-0.003,"weight":1}},{"secondary_school":{"sensitivity":-0.003,"weight":1}},{"library":{"sensitivity":-0.003,"weight":1}},{"bar":{"sensitivity":-0.003,"weight":1}},{"biergarten":{"sensitivity":-0.003,"weight":1}},{"cafe":{"sensitivity":-0.003,"weight":1}},{"pub":{"sensitivity":-0.003,"weight":1}},{"fast_food":{"sensitivity":-0.003,"weight":1}},{"ice_cream":{"sensitivity":-0.003,"weight":1}},{"restaurant":{"sensitivity":-0.003,"weight":1}},{"nightclub":{"sensitivity":-0.003,"weight":1}},{"bicycle_rental":{"sensitivity":-0.003,"weight":1}},{"car_sharing":{"sensitivity":-0.003,"weight":1}},{"charging_station":{"sensitivity":-0.003,"weight":1}},{"bus_stop":{"sensitivity":-0.003,"weight":1}},{"tram_stop":{"sensitivity":-0.003,"weight":1}},{"subway_entrance":{"sensitivity":-0.003,"weight":1}},{"rail_station":{"sensitivity":-0.003,"weight":1}},{"taxi":{"sensitivity":-0.003,"weight":1}},{"hairdresser":{"sensitivity":-0.003,"weight":1}},{"atm":{"sensitivity":-0.003,"weight":1}},{"bank":{"sensitivity":-0.003,"weight":1}},{"dentist":{"sensitivity":-0.003,"weight":1}},{"doctors":{"sensitivity":-0.003,"weight":1}},{"pharmacy":{"sensitivity":-0.003,"weight":1}},{"post_box":{"sensitivity":-0.003,"weight":1}},{"fuel":{"sensitivity":-0.003,"weight":1}},{"recycling":{"sensitivity":-0.003,"weight":1}},{"bakery":{"sensitivity":-0.003,"weight":1}},{"butcher":{"sensitivity":-0.003,"weight":1}},{"clothes":{"sensitivity":-0.003,"weight":1}},{"convenience":{"sensitivity":-0.003,"weight":1}},{"greengrocer":{"sensitivity":-0.003,"weight":1}},{"kiosk":{"sensitivity":-0.003,"weight":1}},{"mall":{"sensitivity":-0.003,"weight":1}},{"shoes":{"sensitivity":-0.003,"weight":1}},{"supermarket":{"sensitivity":-0.003,"weight":1}},{"discount_supermarket":{"sensitivity":-0.003,"weight":1}},{"international_supermarket":{"sensitivity":-0.003,"weight":1}},{"hypermarket":{"sensitivity":-0.003,"weight":1}},{"chemist":{"sensitivity":-0.003,"weight":1}},{"organic":{"sensitivity":-0.003,"weight":1}},{"marketplace":{"sensitivity":-0.003,"weight":1}},{"cinema":{"sensitivity":-0.003,"weight":1}},{"theatre":{"sensitivity":-0.003,"weight":1}},{"museum":{"sensitivity":-0.003,"weight":1}},{"hotel":{"sensitivity":-0.003,"weight":1}},{"hostel":{"sensitivity":-0.003,"weight":1}},{"guest_house":{"sensitivity":-0.003,"weight":1}},{"gallery":{"sensitivity":-0.003,"weight":1}}]')




/*
SELECT jsonb_object_keys(x.jsons::jsonb) AS amenity, ((x.jsons->>jsonb_object_keys(x.jsons::jsonb)::TEXT)::jsonb->>'sensitivity')::NUMERIC AS sensitivity, ((x.jsons->>jsonb_object_keys(x.jsons::jsonb)::TEXT)::jsonb->>'weight')::NUMERIC AS weight
	FROM (
		SELECT value AS jsons FROM json_array_elements('[{"primary_school":{"sensitivity":-0.004,"weight":1}},{"kindergarten":{"sensitivity":-0.003,"weight":1}},{"secondary_school":{"sensitivity":-0.003,"weight":1}},{"library":{"sensitivity":-0.003,"weight":1}}]')
	)
	AS x


*/


