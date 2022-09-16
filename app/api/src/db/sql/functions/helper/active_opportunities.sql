CREATE OR REPLACE FUNCTION basic.active_opportunities(user_id_input integer, active_study_area_id integer)
 RETURNS TABLE(category TEXT, category_group TEXT, icon TEXT, color TEXT[], multiple_entrance bool, data_upload_id integer, sensitivity integer)
 LANGUAGE plpgsql
AS $function$
DECLARE 
	active_data_upload_ids integer[] = (SELECT active_data_upload_ids FROM customer.USER WHERE id = user_id_input); 
BEGIN 
	RETURN QUERY 
	WITH first_combination AS 
	(
		SELECT CASE WHEN u.category IS NULL THEN s.category ELSE u.category END AS category,
		CASE WHEN u.GROUP IS NULL THEN s."group" ELSE u."group" END AS "group",
		CASE WHEN u.icon IS NULL THEN s.icon ELSE u.icon END AS icon,
		CASE WHEN u.color IS NULL THEN s.color ELSE u.color END AS color, s.is_active, u.data_upload_id,
		CASE WHEN u.multiple_entrance IS NULL THEN s.multiple_entrance END AS multiple_entrance,
		CASE WHEN u.sensitivity IS NULL THEN s.sensitivity END AS sensitivity
		FROM (
			SELECT y.*, g."group" 
			FROM basic.opportunity_study_area_config y, basic.opportunity_group g
			WHERE y.study_area_id = active_study_area_id
			AND g.id = y.opportunity_group_id
		) s
		FULL JOIN (
			SELECT x.*, g."group" 
			FROM customer.opportunity_user_config x, basic.opportunity_group g
			WHERE x.user_id = user_id_input	
			AND x.study_area_id = active_study_area_id
			AND (x.data_upload_id IN (SELECT UNNEST(ARRAY[active_data_upload_ids])) OR x.data_upload_id IS NULL) 
			AND g.id = x.opportunity_group_id
		) u
		ON s.category = u.category 
	),
	second_combination AS 
	(
		SELECT CASE WHEN s.category IS NULL THEN o.category ELSE s.category END AS category,
		CASE WHEN s."group" IS NULL THEN o."group" ELSE s."group" END AS "group",
		CASE WHEN s.icon IS NULL THEN o.icon ELSE s.icon END AS icon,
		CASE WHEN s.color IS NULL THEN o.color ELSE s.color END AS color, s.is_active, s.data_upload_id,
		CASE WHEN s.multiple_entrance IS NULL THEN o.multiple_entrance END AS multiple_entrance,
		CASE WHEN s.sensitivity IS NULL THEN o.sensitivity END AS sensitivity
		FROM (
			SELECT x.*, g."group" 
			FROM basic.opportunity_default_config x, basic.opportunity_group g
			WHERE g.id = x.opportunity_group_id
		) o 
		FULL JOIN first_combination s 
		ON o.category = s.category 
	)
	SELECT s.category, s."group", s.icon, s.color, s.multiple_entrance, s.data_upload_id, s.sensitivity 
	FROM second_combination s 
	WHERE (is_active IS NULL OR is_active IS TRUE); 

END ;
$function$

/*
SELECT * FROM basic.active_opportunities(40, 91620000)
*/
