-- POIS Native BOG
--- Here you will find the native DATA FOR Bogota VERSION

CREATE OR REPLACE FUNCTION bogota_custom_pois()
	RETURNS VOID
	LANGUAGE plpgsql
AS $function$
DECLARE
BEGIN
	-- 1. Add new categories to pois based on filters, cable car
	INSERT INTO pois
	SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, 'transmicable' AS amenity,  
	tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
	operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom, tags -> 'wheelchair' as wheelchair  
	FROM planet_osm_point
	WHERE aerialway ='station' AND public_transport = 'station';
	
	-- Insert Parks
	
	INSERT INTO pois
	SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber" as housenumber, 'park' AS amenity,  
	tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
	operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, ST_Centroid(way) as geom, tags -> 'wheelchair' as wheelchair  
	FROM planet_osm_polygon
	WHERE leisure = 'park' AND (ACCESS IS NULL OR ACCESS='public');
	
	-- Apply pois full replacement
	PERFORM (SELECT pois_full_replacement('pois_full_replacement','kindergarten','kindergarten'));
	PERFORM (SELECT pois_full_replacement('pois_full_replacement','school','school'));
	PERFORM (SELECT pois_full_replacement('pois_full_replacement','university','university'));
	PERFORM (SELECT pois_full_replacement('pois_full_replacement','sitp','sitp'));
	PERFORM (SELECT pois_full_replacement('pois_full_replacement','transmilenio','transmilenio'));
	PERFORM (SELECT pois_full_replacement('pois_full_replacement','cade','cade'));
	PERFORM (SELECT pois_full_replacement('pois_full_replacement','notary','notary'));

END;
$function$