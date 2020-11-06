---- Polygon_entrances_generator
-------------------------------------

CREATE OR REPLACE FUNCTION generate_entries_from_polygons (amenity_set TEXT[], path_types TEXT[])
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN
	INSERT INTO pois
	WITH aois_type AS (SELECT * FROM aois WHERE amenity = ANY(amenity_set)),
	ways_footpath AS (
		SELECT pol.*, ST_intersection(ST_boundary(a.geom),pol.way), a.gid AS pol_gid
		FROM planet_osm_line pol, aois_type a 
		WHERE highway = ANY(path_types) AND ST_intersects(ST_boundary(a.geom),pol.way))
	SELECT a.osm_id, a.origin_geometry, a.ACCESS, a.housenumber, a.amenity, a.origin, a.organic, a.denomination, a.brand, a.name, a.OPERATOR, a.public_transport, a.railway,
	a.religion, a.opening_hours, a.REF, a.tags, ST_intersection(ST_Boundary(a.geom),wf.way), a.wheelchair FROM ways_footpath wf 
	LEFT JOIN aois_type a
	ON a.gid = wf.pol_gid WHERE a.amenity IS NOT NULL 
	AND NOT st_isempty(ST_intersection(ST_Boundary(a.geom),wf.way));
	
	--- Assign name = osm_id when name = null
	UPDATE pois
	SET name = (CASE WHEN amenity = ANY(amenity_set) AND name IS NULL THEN (amenity || '-' || gid)::TEXT ELSE name END);
	
END
$function$

/*
SELECT generate_entries_from_polygons(ARRAY['big_park','small_park'],ARRAY['path','footway','cycleway','track','pedestrian','service'])
*/


