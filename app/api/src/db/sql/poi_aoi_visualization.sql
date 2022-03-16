CREATE OR REPLACE FUNCTION basic.poi_aoi_visualization(user_id_input integer, scenario_id_input integer, modus TEXT, active_upload_ids integer[],
active_study_area_id integer)
RETURNS TABLE (id integer, uid TEXT, category TEXT, name TEXT, opening_hours TEXT, street TEXT, housenumber TEXT, zipcode TEXT, status TEXT, geom geometry)
LANGUAGE plpgsql
AS $function$
DECLARE 	
	aoi_categories TEXT[]; 
	poi_categories jsonb = basic.poi_categories(user_id_input);
	combined_poi_categories text[];
	excluded_pois_id text[] := ARRAY[]::text[]; 
	buffer_geom_study_area geometry; 
BEGIN
	
	/*Get combined poi categories*/
	SELECT ARRAY_AGG(c.category)
	INTO combined_poi_categories
	FROM 	
	(
		SELECT jsonb_array_elements_text(poi_categories -> 'true') category
		UNION ALL 
		SELECT jsonb_array_elements_text(poi_categories -> 'false') category
	) c;

	/*Prepare AOI categories*/
	DROP TABLE IF EXISTS aoi_groups_default; 
	CREATE TEMP TABLE aoi_groups_default AS 
	WITH aoi_groups AS 
	(
		SELECT jsonb_array_elements(basic.select_customization('aoi_groups')) aoi_group
	)
	SELECT jsonb_array_elements(p.aoi_group -> jsonb_object_keys(p.aoi_group) -> 'children') AS aoi_category 
	FROM aoi_groups p;

	SELECT ARRAY_AGG(object_keys) AS aoi_category
	INTO aoi_categories
	FROM aoi_groups_default  p, LATERAL jsonb_object_keys(p.aoi_category) object_keys;  
	
	/*Check if POI scenario*/
	IF modus = 'scenario' OR modus = 'comparison' THEN 
		excluded_pois_id = basic.modified_pois(scenario_id_input);
	END IF; 
	/*Buffer study area to avoid border effects*/
	buffer_geom_study_area = (SELECT buffer_geom_heatmap AS geom FROM basic.study_area s WHERE s.id = active_study_area_id);

    RETURN query
   	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, NULL AS status, p.geom  
	FROM basic.poi p
	WHERE p.category IN (SELECT UNNEST(combined_poi_categories))
	AND p.uid NOT IN (SELECT UNNEST(excluded_pois_id))
	AND p.geom && buffer_geom_study_area;
	
	RETURN query 
	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, NULL AS status, p.geom  
	FROM customer.poi_user p
	WHERE p.category IN (SELECT UNNEST(combined_poi_categories))
	AND p.data_upload_id IN (SELECT UNNEST(active_upload_ids))
	AND p.uid NOT IN (SELECT UNNEST(excluded_pois_id))
	AND p.geom && buffer_geom_study_area;
	
	RETURN query 
	/*No scenarios nor aoi_user is implemented at the moment*/
	SELECT p.id, NULL, p.category, p.name, p.opening_hours, NULL AS street, NULL AS housenumber, NULL AS zipcode, NULL AS status, p.geom
	FROM basic.aoi p 
	WHERE p.category IN (SELECT UNNEST(aoi_categories))
	AND p.geom && buffer_geom_study_area; 
	
	IF modus IN ('scenario', 'comparison') THEN	
	   	RETURN query 
	   	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, NULL AS status, p.geom  
		FROM customer.poi_modified p
		WHERE p.category IN (SELECT UNNEST(combined_poi_categories))
		AND p.geom && buffer_geom_study_area
		AND p.scenario_id = scenario_id_input; 
	   
	END IF; 
	
    IF modus = 'comparison' THEN 
    	RETURN query
    	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, 'not_accessible' AS status, p.geom 
    	FROM basic.poi p 
    	WHERE p.category IN (SELECT UNNEST(combined_poi_categories))
		AND p.geom && buffer_geom_study_area
	    AND p.uid IN (SELECT UNNEST(excluded_pois_id));
	   	
	   	RETURN query
    	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, 'not_accessible' AS status, p.geom 
    	FROM customer.poi_user p 
    	WHERE p.category IN (SELECT UNNEST(combined_poi_categories))
		AND p.geom && buffer_geom_study_area
	    AND p.uid IN (SELECT UNNEST(excluded_pois_id));
	END IF;
	
END ;
$function$;


/*
Modus should be default, scenario, comparison
SELECT * 
FROM basic.poi_aoi_visualization(4, 2, 'default', ARRAY[0], 1)
*/