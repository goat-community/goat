CREATE OR REPLACE FUNCTION clean_duplicated_amenities_in_pois(amenity_name TEXT , lookup_radius numeric)
	RETURNS VOID
	LANGUAGE plpgsql
AS $function$
BEGIN
	DROP TABLE IF EXISTS pois_amenity_duplicated;
	CREATE TEMP TABLE pois_amenity_duplicated (gid integer, distance NUMERIC);

	INSERT INTO pois_amenity_duplicated
	WITH category AS (SELECT * FROM pois WHERE amenity = amenity_name)
	SELECT min(gid) AS gid, distance FROM (
		SELECT o.*, ST_Distance(o.geom, p.geom) AS distance
		FROM category o
		JOIN category p 
		ON ST_DWithin(o.geom::geography, p.geom::geography, lookup_radius)
		AND NOT ST_DWithin(o.geom, p.geom, 0)) x
	GROUP BY distance;
	DELETE FROM pois WHERE gid = any(SELECT gid FROM pois_amenity_duplicated);
END;
$function$