CREATE OR REPLACE FUNCTION basic.poi_aoi_visualization(user_id_input integer, scenario_id_input integer, active_upload_ids integer[], active_study_area_id integer, 
grouped_multi_entrance boolean = FALSE)
RETURNS TABLE (id integer, uid TEXT, category TEXT, name TEXT, opening_hours TEXT, street TEXT, housenumber TEXT, zipcode TEXT, edit_type TEXT, geom geometry)
LANGUAGE plpgsql
AS $function$
DECLARE 	
	aoi_categories TEXT[]; 
	data_upload_poi_categories TEXT[] = '{}'::TEXT[];
	all_poi_categories text[];
	excluded_pois_id text[] := '{}'::text[]; 
	buffer_geom_study_area geometry; 
BEGIN
	data_upload_poi_categories = basic.poi_categories_data_uploads(user_id_input);
	active_study_area_id = (SELECT u.active_study_area_id FROM customer.user u WHERE u.id = user_id_input);

	IF grouped_multi_entrance = TRUE THEN 
		/*Get combined poi categories*/
		SELECT array_agg(o.category) 
		INTO all_poi_categories 
		FROM basic.active_opportunities(user_id_input, active_study_area_id) o, basic.opportunity_group g 
		WHERE o.category_group = g.GROUP 
		AND g.TYPE = 'poi'
		AND multiple_entrance = grouped_multi_entrance;

		/*Get aoi categories*/
		SELECT ARRAY_AGG(o.category) 
		INTO aoi_categories
		FROM basic.active_opportunities(user_id_input, active_study_area_id) o, basic.opportunity_group g 
		WHERE o.category_group = g.GROUP 
		AND g.TYPE = 'aoi'
		AND multiple_entrance = grouped_multi_entrance;
	ELSE 
		SELECT array_agg(o.category) 
		INTO all_poi_categories 
		FROM basic.active_opportunities(user_id_input, active_study_area_id) o, basic.opportunity_group g 
		WHERE o.category_group = g.GROUP 
		AND g.TYPE = 'poi'; 

		/*Get aoi categories*/
		SELECT ARRAY_AGG(o.category) 
		INTO aoi_categories
		FROM basic.active_opportunities(user_id_input, active_study_area_id) o, basic.opportunity_group g 
		WHERE o.category_group = g.GROUP 
		AND g.TYPE = 'aoi';

	END IF; 

	/*Check if POI scenario*/
	IF scenario_id_input <> 0 THEN 
		excluded_pois_id = basic.modified_pois(scenario_id_input);
	END IF; 
	/*Buffer study area to avoid border effects*/
	buffer_geom_study_area = (SELECT buffer_geom_heatmap AS geom FROM basic.study_area s WHERE s.id = active_study_area_id);

    RETURN query
   	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, 
	NULL AS edit_type, p.geom  
	FROM basic.poi p
	WHERE p.category IN (SELECT UNNEST(all_poi_categories))
	AND p.uid NOT IN (SELECT UNNEST(excluded_pois_id))
	AND ST_Intersects(p.geom, buffer_geom_study_area)
	AND p.category NOT IN (SELECT UNNEST(data_upload_poi_categories));
	
	RETURN query 
	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, 
	NULL AS edit_type, p.geom  
	FROM customer.poi_user p
	WHERE p.category IN (SELECT UNNEST(all_poi_categories))
	AND p.data_upload_id IN (SELECT UNNEST(active_upload_ids))
	AND p.uid NOT IN (SELECT UNNEST(excluded_pois_id))
	AND ST_Intersects(p.geom, buffer_geom_study_area);
	
	RETURN query 
	/*No scenarios nor aoi_user is implemented at the moment*/
	SELECT p.id, NULL, p.category, p.name, p.opening_hours, NULL AS street, NULL AS housenumber, NULL AS zipcode, 
	NULL AS edit_type, p.geom
	FROM basic.aoi p 
	WHERE p.category IN (SELECT UNNEST(aoi_categories))
	AND p.geom && buffer_geom_study_area; 
	
	IF scenario_id_input <> 0 THEN 
	   	RETURN query 
	   	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, 
		p.edit_type, p.geom  
		FROM customer.poi_modified p
		WHERE p.category IN (SELECT UNNEST(all_poi_categories))
		AND ST_Intersects(p.geom, buffer_geom_study_area)
		AND p.scenario_id = scenario_id_input; 
	   	
		RETURN query
	   	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, 
		'd' AS edit_type, p.geom  
		FROM basic.poi p
		WHERE p.category IN (SELECT UNNEST(all_poi_categories))
		AND p.uid IN (SELECT UNNEST(excluded_pois_id))
		AND ST_Intersects(p.geom, buffer_geom_study_area)
		AND p.category NOT IN (SELECT UNNEST(data_upload_poi_categories));
	
		RETURN query 
		SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, 
		'd' AS edit_type, p.geom  
		FROM customer.poi_user p
		WHERE p.category IN (SELECT UNNEST(all_poi_categories))
		AND p.data_upload_id IN (SELECT UNNEST(active_upload_ids))
		AND p.uid IN (SELECT UNNEST(excluded_pois_id))
		AND ST_Intersects(p.geom, buffer_geom_study_area);
	END IF; 
END ;
$function$;

/*
Modus should be default, scenario, comparison
SELECT * 
FROM basic.poi_aoi_visualization(4, 2, 'default', ARRAY[0], 1)
*/
