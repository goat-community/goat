--THIS FUNCTION CHECKS IF THE USER INSERTED OPENING HOURS OR NOT AND EXECUTS THE CORRESPONDING FUNCTION TO CREATE THE GEOSERVER VIEW
DROP FUNCTION IF EXISTS pois_visualization;
CREATE OR REPLACE FUNCTION public.pois_visualization(amenities_input text, d integer, h integer, m integer)
 RETURNS SETOF pois_visualization
 LANGUAGE plpgsql
AS $function$
begin

DROP TABLE IF EXISTS visualization_pois;

--if no opening hours are provided by the user
    IF d = 9999 OR h = 9999 OR m = 9999 THEN 
        RETURN query
        SELECT p.name,p.osm_id,p.opening_hours,p.orgin_geometry,p.geom, NULL AS status
        FROM pois p,variable_container v 
        WHERE p.amenity IN(amenities_input)
        AND v.identifier = 'poi_categories'
        UNION ALL 
        SELECT pt.name,NULL AS osm_id,NULL AS orgin_geometry,NULL AS opening_hours,pt.geom , NULL AS status
        FROM public_transport_stops pt WHERE public_transport_stop IN(amenities_input);
    --if opening hours are provided by the user
    ELSE
        RETURN query
        WITH pois_status AS 
        (
            SELECT p.name,p.osm_id,p.opening_hours,p.orgin_geometry,p.geom,check_open(p.opening_hours,array[d,h,m]) AS status
            FROM pois p
            WHERE p.amenity IN(amenities_input)
            AND opening_hours IS NOT NULL
        )
        SELECT * FROM pois_status
        WHERE status = 'True'
        UNION ALL
        SELECT pt.name,NULL AS osm_id, NULL AS opening_hours, NULL AS orgin_geometry,pt.geom, NULL AS status
        FROM public_transport_stops pt 
        WHERE public_transport_stop IN(amenities_input);
    END IF;

END ;
$function$
