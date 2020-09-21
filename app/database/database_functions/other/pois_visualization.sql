--THIS FUNCTION CHECKS THE SELECTED ROUTING PROFILE AND IF THE USER INSERTED OPENING HOURS AND EXECUTS THE CORRESPONDING FUNCTION TO CREATE THE GEOSERVER VIEW
DROP FUNCTION IF EXISTS pois_visualization;
CREATE OR REPLACE FUNCTION public.pois_visualization(userid_input integer, amenities_input text[], routing_profile_input text, d integer, h integer, m integer)
 RETURNS SETOF pois_visualization
 LANGUAGE plpgsql
AS $function$
DECLARE 	
	excluded_pois_id integer[] := ids_modified_features(userid_input,1,'pois');
    
BEGIN

    --if no opening hours are provided by the user and routing profile is -not- wheelchair
    IF (d = 9999 OR h = 9999 OR m = 9999) AND routing_profile_input <> 'walking_wheelchair' THEN 
        RETURN query
        SELECT p.gid, p.amenity, p.name,p.osm_id,p.opening_hours,p.origin_geometry,p.geom, 'accessible' AS status,p.wheelchair
		FROM pois_userinput p
        WHERE amenity IN (SELECT UNNEST(amenities_input)) 
        AND (p.userid = userid_input OR p.userid IS NULL)
        AND p.gid NOT IN (SELECT UNNEST(excluded_pois_id))
        ;
    --if no opening hours are provided by the user and routing profile is wheelchair
    ELSEIF (d = 9999 OR h = 9999 OR m = 9999) AND routing_profile_input = 'walking_wheelchair' THEN 
        RETURN query
        SELECT p.gid, p.amenity,p.name,p.osm_id,p.opening_hours,p.origin_geometry,p.geom, 
        CASE WHEN ((p.wheelchair <> 'no' AND p.wheelchair <> 'No') OR p.wheelchair IS NULL) 
        THEN 'accessible' 
        ELSE 'not_accessible' END AS status,p.wheelchair
        FROM pois_userinput p
        WHERE p.amenity IN(SELECT unnest(amenities_input))
        ;
    --if opening hours are provided by the user and routing profile is -not- wheelchair
    ELSEIF d <> 9999 AND h <> 9999 AND m <> 9999 AND routing_profile_input <> 'walking_wheelchair' THEN 
        RETURN query
        WITH pois_status AS 
        (
            SELECT p.gid, p.amenity, p.name,p.osm_id,p.opening_hours,p.origin_geometry,p.geom,
            CASE WHEN check_open(opening_hours,array[d,h,m]) = 'True' 
            THEN 'accessible'
            ELSE 'not_accessible' END AS status,p.wheelchair
            FROM pois_userinput p
            WHERE p.amenity IN(SELECT unnest(amenities_input))
            AND opening_hours IS NOT NULL
        )
        SELECT * FROM pois_status
        ;
    --if opening hours are provided by the user and routing profile is wheelchair
    ELSE 
        RETURN query
        WITH pois_status AS 
        (
            SELECT p.gid,p.amenity,p.name,p.osm_id,p.opening_hours,p.origin_geometry,p.geom,
            CASE WHEN check_open(opening_hours,array[d,h,m]) = 'True' AND ((wheelchair <> 'no' AND wheelchair <> 'No') OR wheelchair IS NULL)
            THEN 'accessible'
            ELSE 'not_accessible' END AS status, p.wheelchair 
            FROM pois_userinput p
            WHERE p.amenity IN(SELECT unnest(amenities_input))
            AND opening_hours IS NOT NULL
        )
        SELECT * FROM pois_status
        ;
    END IF;

END ;
$function$

/* SELECT * FROM 
	(SELECT * FROM regexp_split_to_table(convert_from(decode('cmVzdGF1cmFudCxzdXBlcm1hcmtldA==','base64'),'UTF-8'), ',') AS amenity) x,
	pois_visualization(x.amenity,'walking_wheelchair', 20, 15, 0);
*/

--SELECT * FROM pois_visualization(1,ARRAY['charging_station','bus_stop'],'walking_standard', 9999,9999,9999);



