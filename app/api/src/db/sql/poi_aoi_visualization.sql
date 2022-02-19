CREATE OR REPLACE FUNCTION basic.poi_aoi_visualization(user_id_input integer, scenario_id_input integer, amenities_input text[], modus TEXT, active_upload_ids integer[],
active_study_area_id integer)
RETURNS TABLE (id integer, uid TEXT, category TEXT, name TEXT, opening_hours TEXT, street TEXT, housenumber TEXT, zipcode TEXT, status TEXT, geom geometry)
LANGUAGE plpgsql
AS $function$
DECLARE 	
	aoi_categories_object jsonb; 
	aoi_categories jsonb; 
	intersected_aoi_categories TEXT[]; 
	poi_categories jsonb = basic.poi_categories(user_id_input);
	pois_one_entrance jsonb = poi_categories -> 'false'; 
	pois_more_entrance jsonb = poi_categories -> 'true';
	excluded_pois_id text[] := ARRAY[]::text[]; 
	intersected_poi_categories text[] := basic.intersection_poi_categories((pois_one_entrance || pois_more_entrance), amenities_input); 
	buffer_study_area integer := 2000; 
	buffer_geom_study_area geometry; 
	
BEGIN
	
	/*Prepare AOI categories*/
	SELECT (default_setting -> TYPE)  
	INTO aoi_categories_object 
	FROM customer.customization c  
	WHERE TYPE = 'aoi_group';
	
	SELECT JSONB_AGG(aoi_category) 
	INTO aoi_categories 
	FROM jsonb_object_keys(aoi_categories_object) cat, LATERAL jsonb_object_keys((aoi_categories_object -> cat -> 'children')) aoi_category; 
	
	intersected_aoi_categories = basic.intersection_poi_categories(aoi_categories, amenities_input);
	
	/*Check if POI scenario*/
	IF modus = 'scenario' OR modus = 'comparison' THEN 
		excluded_pois_id = basic.modified_pois(scenario_id_input);
	END IF; 
	/*Buffer study area to avoid border effects*/
	buffer_geom_study_area = (SELECT ST_BUFFER(ST_ENVELOPE(s.geom)::geography, 2000)::geometry AS geom FROM basic.study_area s WHERE s.id = active_study_area_id);

    RETURN query
   	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, NULL AS status, p.geom  
	FROM basic.poi p
	WHERE p.category IN (SELECT UNNEST(intersected_poi_categories))
	AND p.uid NOT IN (SELECT UNNEST(excluded_pois_id))
	AND p.geom && buffer_geom_study_area;
	
	RETURN query 
	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, NULL AS status, p.geom  
	FROM customer.poi_user p
	WHERE p.category IN (SELECT UNNEST(intersected_poi_categories))
	AND p.data_upload_id IN (SELECT UNNEST(active_upload_ids))
	AND p.uid NOT IN (SELECT UNNEST(excluded_pois_id))
	AND p.geom && buffer_geom_study_area;
	
	RETURN query 
	/*No scenarios nor aoi_user is implemented at the moment*/
	SELECT p.id, NULL, p.category, p.name, p.opening_hours, NULL AS street, NULL AS housenumber, NULL AS zipcode, NULL AS status, p.geom
	FROM basic.aoi p 
	WHERE p.category IN (SELECT UNNEST(intersected_aoi_categories))
	AND p.geom && buffer_geom_study_area; 
	
	IF modus IN ('scenario', 'comparison') THEN	
	   	RETURN query 
	   	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, NULL AS status, p.geom  
		FROM customer.poi_modified p
		WHERE p.category IN (SELECT UNNEST(intersected_poi_categories))
		AND p.geom && buffer_geom_study_area
		AND p.scenario_id = scenario_id_input; 
	   
	END IF; 
	
	RAISE NOTICE '%', excluded_pois_id;
    IF modus = 'comparison' THEN 
    	RETURN query
    	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, 'not_accessible' AS status, p.geom 
    	FROM basic.poi p 
    	WHERE p.category IN (SELECT UNNEST(intersected_poi_categories))
		AND p.geom && buffer_geom_study_area
	    AND p.uid IN (SELECT UNNEST(excluded_pois_id));
	   	
	   	RETURN query
    	SELECT p.id, p.uid, p.category, p.name, p.opening_hours, p.street, p.housenumber, p.zipcode, 'not_accessible' AS status, p.geom 
    	FROM customer.poi_user p 
    	WHERE p.category IN (SELECT UNNEST(intersected_poi_categories))
		AND p.geom && buffer_geom_study_area
	    AND p.uid IN (SELECT UNNEST(excluded_pois_id));
	END IF;
	
END ;
$function$;

/*
Modus should be default, scenario, comparison
SELECT * 
FROM basic.poi_aoi_visualization(4, 2, ARRAY['supermarket', 'discount_supermarket', 'park', 'restaurant', 'kindergarten'], 'default', ARRAY[0], 1)
*/
