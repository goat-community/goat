CREATE OR REPLACE FUNCTION basic.starting_points_multi_isochrones(user_id_input integer, modus text, minutes integer, speed_input numeric, 
amenities text[], scenario_id_input integer DEFAULT 0, active_upload_ids integer[] DEFAULT '{}'::integer[], region TEXT DEFAULT NULL, study_area_ids integer[] DEFAULT NULL)
RETURNS TABLE (x float[], y float[])
AS $function$

DECLARE 
	excluded_pois_id text[] := ARRAY[]::text[];
	region_geom geometry;  
	buffer_geom geometry; 
	data_upload_poi_categories TEXT[] = '{}'::TEXT[];
	detour_factor numeric = 0.8;
BEGIN 
	data_upload_poi_categories = basic.poi_categories_data_uploads(user_id_input);

	IF region IS NULL AND study_area_ids IS NOT NULL THEN
        SELECT ST_UNION(s.geom)   
        INTO region_geom
        FROM basic.sub_study_area s
        WHERE s.id IN (SELECT UNNEST(study_area_ids));
    ELSEIF region IS NOT NULL AND study_area_ids IS NULL THEN
        SELECT ST_GeomFromText(region) AS geom  
        INTO region_geom;
    ELSE 
        RAISE EXCEPTION 'Please specify either region or study_area_ids but not both.';
    END IF;
	
   	buffer_geom = ST_Buffer(region_geom::geography, speed_input  * 60 * minutes * detour_factor)::geometry;
   
	IF modus = 'scenario' THEN
        excluded_pois_id = basic.modified_pois(scenario_id_input);
    ELSEIF modus = 'default' THEN
    	scenario_id_input = 0; 
    END IF;
	

   	RETURN QUERY 
   	WITH relevant_pois AS 
   	(
		SELECT ST_X(p.geom) x, ST_Y(p.geom) y
		FROM basic.poi p
		WHERE ST_Intersects(buffer_geom, p.geom)
		AND p.category IN (SELECT UNNEST(amenities))
		AND p.uid NOT IN (SELECT UNNEST(excluded_pois_id))
		AND p.category NOT IN (SELECT UNNEST(data_upload_poi_categories))
		UNION ALL 
		SELECT ST_X(p.geom) x, ST_Y(p.geom) y 
		FROM customer.poi_user p
		WHERE ST_Intersects(buffer_geom, p.geom)
		AND p.category IN (SELECT UNNEST(amenities))
		AND p.uid NOT IN (SELECT UNNEST(excluded_pois_id))
		AND p.data_upload_id IN (SELECT UNNEST(active_upload_ids))
		UNION ALL 
		SELECT ST_X(p.geom) x, ST_Y(p.geom) y
		FROM customer.poi_modified p
		WHERE ST_Intersects(buffer_geom, p.geom)
		AND p.category IN (SELECT UNNEST(amenities))
		AND p.scenario_id = scenario_id_input
		AND (p.data_upload_id IN (SELECT UNNEST(active_upload_ids)) OR p.data_upload_id IS NULL)
		AND p.edit_type <> 'd'
	)
	SELECT ARRAY_AGG(r.x) AS x, ARRAY_AGG(r.y) AS y 
	FROM relevant_pois r;
	
END; 
$function$
LANGUAGE plpgsql;


/*
SELECT * 
FROM basic.starting_points_multi_isochrones('default', 10, 1.33, ARRAY['bar','restaurant','pub','french_supermarket','fancy_market'], 0, ARRAY[0], NULL, ARRAY[1,2,3,4])
 */
