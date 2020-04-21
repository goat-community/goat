CREATE OR REPLACE FUNCTION pois_classification(inp_amenity TEXT, col_variable text)
	RETURNS TABLE (
	osm_id int8, origin_geometry text, accesss TEXT, housenumber TEXT, amenity TEXT, shop TEXT, origin TEXT,
	organic TEXT, denomination TEXT, brand TEXT, name TEXT, OPERATOR TEXT, public_transport TEXT, railway TEXT, religion TEXT, 
	opening_hours TEXT, REF TEXT, tags hstore, geom geometry, wheelchair text
	)
	LANGUAGE plpgsql
AS $function$
BEGIN
RETURN QUERY
EXECUTE 'SELECT p.osm_id,'||quote_literal('point')||' as origin_geometry, p.access,"addr:housenumber" as housenumber, '||quote_literal(inp_amenity)||' AS amenity, p.shop, 
	p.tags -> '||quote_literal('origin')||' AS origin, p.tags -> '||quote_literal('organic')||' AS organic, p.denomination,p.brand,p.name, p.operator,p.public_transport,
	p.railway, p.religion, p.tags -> '||quote_literal('opening_hours')||' as opening_hours, p.ref,p.tags, way as geom, p.tags -> '||quote_literal('wheelchair')||' as wheelchair  
	FROM planet_osm_point p
	WHERE '||col_variable||' = '|| quote_literal(inp_amenity)||' UNION
	SELECT p.osm_id,'||quote_literal('polygon')||' as origin_geometry, p.access,"addr:housenumber" as housenumber, '||quote_literal(inp_amenity)||' AS amenity, p.shop, 
	p.tags -> '||quote_literal('origin')||' AS origin, p.tags -> '||quote_literal('organic')||' AS organic, p.denomination,p.brand,p.name, p.operator,p.public_transport,
	p.railway, p.religion, p.tags -> '||quote_literal('opening_hours')||' as opening_hours, p.ref,p.tags, st_centroid(way) as geom, p.tags -> '||quote_literal('wheelchair')||' as wheelchair  
	FROM planet_osm_polygon p
	WHERE '||col_variable||' = '|| quote_literal(inp_amenity)||'';

END;
$function$

SELECT * FROM pois_classification('playground','leisure');



DROP FUNCTION pois_classification


--case 1



SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber" as housenumber, leisure AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE leisure = 'playground'

UNION

SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber" as housenumber, leisure AS amenity, shop, 
tags -> 'origin' AS origin, tags -> 'organic' AS organic, denomination,brand,name,
operator,public_transport,railway,religion,tags -> 'opening_hours' as opening_hours, ref,tags, st_centroid(way) as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE leisure = 'playground'

-- case 2

