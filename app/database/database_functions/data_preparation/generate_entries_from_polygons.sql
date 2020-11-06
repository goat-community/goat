---- Polygon_entrances_generator
-------------------------------------

CREATE OR REPLACE FUNCTION generate_entries_from_polygons (amenity_set TEXT[], path_types TEXT[])
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN
	ALTER TABLE pois ADD COLUMN IF NOT EXISTS pol_gid integer;

	INSERT INTO pois (osm_id, origin_geometry, ACCESS, housenumber, amenity, origin, organic, denomination, brand, name, OPERATOR, public_transport, railway, religion, opening_hours, REF, tags, geom, wheelchair, pol_gid)
	WITH aois_type AS (SELECT * FROM aois WHERE amenity = ANY(amenity_set)),
	ways_footpath AS (
		SELECT pol.*, ST_intersection(ST_boundary(a.geom),pol.way), a.gid AS pol_gid
		FROM planet_osm_line pol, aois_type a 
		WHERE highway = ANY(path_types) AND ST_intersects(ST_boundary(a.geom),pol.way))
	SELECT a.osm_id, a.origin_geometry, a.ACCESS, a.housenumber, a.amenity, a.origin, a.organic, a.denomination, a.brand, a.name, a.OPERATOR, a.public_transport, a.railway,
	a.religion, a.opening_hours, a.REF, a.tags, ST_intersection(ST_Boundary(a.geom),wf.way), a.wheelchair, wf.pol_gid FROM ways_footpath wf
	LEFT JOIN aois_type a
	ON a.gid = wf.pol_gid WHERE a.amenity IS NOT NULL 
	AND NOT st_isempty(ST_intersection(ST_Boundary(a.geom),wf.way));
	
	--- Assign name = osm_id when name = null
	UPDATE pois
	SET name = (CASE WHEN amenity = ANY(amenity_set) AND name IS NULL THEN (amenity || '-' || pol_gid)::TEXT ELSE name END);
	
	--- Drop auxiliary columns
	ALTER TABLE pois DROP COLUMN IF EXISTS pol_gid;
END
$function$

/*
SELECT generate_entries_from_polygons(ARRAY['big_park','small_park'],ARRAY['path','footway','cycleway','track','pedestrian','service'])
*/
