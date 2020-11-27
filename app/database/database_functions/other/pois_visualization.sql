DROP FUNCTION IF EXISTS pois_visualization;
CREATE OR REPLACE FUNCTION public.pois_visualization(scenario_id_input integer, amenities_input text[], routing_profile_input text, modus_input TEXT DEFAULT 'default', d integer default 9999, h integer default 9999, m integer default 9999)
 RETURNS SETOF pois_visualization
 LANGUAGE plpgsql
AS $function$
DECLARE 	
	excluded_pois_id integer[] := ids_modified_features(scenario_id_input,'pois');
	    
BEGIN
	IF modus_input = 'default' THEN
		scenario_id_input = 0;
	END IF;

	IF modus_input = 'default' THEN	
	    RETURN query
	    SELECT p.gid, p.amenity, p.name,p.osm_id,p.opening_hours,p.origin_geometry,p.geom, 'accessible' AS status,p.wheelchair
		FROM pois_userinput p
	    WHERE amenity IN (SELECT UNNEST(amenities_input)) 
	    AND (p.scenario_id = scenario_id_input OR scenario_id IS NULL);
	   	
	ELSEIF modus_input = 'scenario' THEN	
	    RETURN query
	    SELECT p.gid, p.amenity, p.name,p.osm_id,p.opening_hours,p.origin_geometry,p.geom, 'accessible' AS status,p.wheelchair
		FROM pois_userinput p
	    WHERE amenity IN (SELECT UNNEST(amenities_input)) 
	    AND (p.scenario_id = scenario_id_input OR scenario_id IS NULL)
	    AND p.gid NOT IN (SELECT UNNEST(excluded_pois_id))
	   	UNION ALL 
	   	SELECT p.gid, p.amenity, p.name,p.osm_id,p.opening_hours,p.origin_geometry,p.geom, 'not_accessible' AS status,p.wheelchair
		FROM pois_userinput p
	    WHERE amenity IN (SELECT UNNEST(amenities_input)) 
	    AND (p.scenario_id = scenario_id_input OR scenario_id IS NULL)
	    AND p.gid IN (SELECT UNNEST(excluded_pois_id));
	   
    ELSEIF modus_input = 'comparison' THEN 
    	RETURN query
	    SELECT p.gid, p.amenity, p.name,p.osm_id,p.opening_hours,p.origin_geometry,p.geom, 'accessible' AS status,p.wheelchair
		FROM pois_userinput p
	    WHERE amenity IN (SELECT UNNEST(amenities_input)) 
	    AND p.scenario_id = scenario_id_input 
	    AND p.gid NOT IN (SELECT UNNEST(excluded_pois_id))
	   	UNION ALL 
	   	SELECT p.gid, p.amenity, p.name,p.osm_id,p.opening_hours,p.origin_geometry,p.geom, 'not_accessible' AS status,p.wheelchair
		FROM pois_userinput p
	    WHERE amenity IN (SELECT UNNEST(amenities_input)) 
	    AND (p.scenario_id = scenario_id_input OR scenario_id IS NULL)
	    AND p.gid IN (SELECT UNNEST(excluded_pois_id));
    ELSE
    	RAISE NOTICE 'Please pass a correct calculation modus!';
	END IF;
	
END ;
$function$

/* SELECT * FROM 
	(SELECT * FROM regexp_split_to_table(convert_from(decode('cmVzdGF1cmFudCxzdXBlcm1hcmtldA==','base64'),'UTF-8'), ',') AS amenity) x,
	pois_visualization(x.amenity,'walking_wheelchair', 'comparison', 20, 15, 0);
*/
/*
SELECT * FROM pois_visualization(20,ARRAY['nursery'],'walking_standard','comparison', 9999,9999,9999);
*/