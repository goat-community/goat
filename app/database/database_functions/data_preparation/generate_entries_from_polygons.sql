---- Polygon_entrances_generator
-------------------------------------

CREATE OR REPLACE FUNCTION generate_entries_from_polygons (amenity_set TEXT[], path_types TEXT[])
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN
	INSERT INTO pois
	WITH aois_type AS (SELECT * FROM aois WHERE amenity = ANY(amenity_set)),
	ways_footpath AS (SELECT * FROM planet_osm_line WHERE highway = ANY(path_types))
		SELECT a.osm_id, a.origin_geometry, a.ACCESS, a.housenumber, a.amenity, a.origin, a.organic, a.denomination, a.brand, a.name, a.OPERATOR, a.public_transport, a.railway,
		a.religion, a.opening_hours, a.REF, a.tags, ST_intersection(ST_Boundary(a.geom),wf.way), a.wheelchair FROM ways_footpath wf 
		LEFT JOIN aois_type a
		ON ST_intersects(a.geom, wf.way) WHERE a.amenity IS NOT NULL 
		AND NOT st_isempty(ST_intersection(ST_Boundary(a.geom),wf.way));
	--- Assign name = osm_id when name = null
	UPDATE pois
	SET name = (CASE WHEN amenity = ANY(amenity_set) AND name IS NULL THEN osm_id::text ELSE name END);
	
END
$function$

/*
SELECT generate_entries_from_polygons(ARRAY['big_park','small_park'],ARRAY['path','footway','cycleway','track','pedestrian','service'])
*/