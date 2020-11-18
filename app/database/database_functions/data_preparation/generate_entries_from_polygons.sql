---- Polygon_entrances_generator
-------------------------------------

CREATE OR REPLACE FUNCTION generate_entries_from_polygons (amenity_set TEXT[], path_types TEXT[])
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN

	INSERT INTO pois (osm_id, origin_geometry, ACCESS, housenumber, amenity, origin, organic, denomination, brand, name, OPERATOR, public_transport, railway, religion, opening_hours, REF, tags, geom, wheelchair)
	SELECT a.osm_id, a.origin_geometry, a.ACCESS, a.housenumber, a.amenity, a.origin, a.organic, a.denomination, a.brand, 
	a.amenity || '-' || a.gid AS name, a.OPERATOR, a.public_transport, a.railway,
	a.religion, a.opening_hours, a.REF, a.tags, ST_intersection(ST_Boundary(a.geom),p.way), a.wheelchair
	FROM aois a, planet_osm_line p 
	WHERE a.amenity IN (SELECT UNNEST(amenity_set))
	AND p.highway IN (SELECT UNNEST(path_types)) 
	AND ST_Intersects(ST_Boundary(a.geom),p.way)
	AND ST_GeometryType(ST_Intersection(ST_Boundary(a.geom),p.way)) IN ('ST_MultiPoint','ST_Point');

END
$function$

/*
SELECT generate_entries_from_polygons(ARRAY['small_forest','big_forest'],ARRAY['path','footway','cycleway','track','pedestrian','service']);
*/
