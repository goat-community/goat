---- POIS displacements
-----------------------------------------
CREATE OR REPLACE FUNCTION pois_displacement (amenity_set TEXT[], ssrid integer)
	RETURNS void
	LANGUAGE plpgsql
AS $function$
BEGIN
	DROP TABLE IF EXISTS pois_duplicated;
	CREATE TABLE pois_duplicated (LIKE pois INCLUDING ALL);
	INSERT INTO pois_duplicated
	WITH pois_filtered AS (SELECT * FROM pois WHERE amenity = ANY(amenity_set))
		SELECT p.* FROM pois_filtered p 
		LEFT JOIN pois_filtered p2
		ON p.osm_id = p2.osm_id
		WHERE ST_Equals(p.geom, p2.geom) AND p.amenity != p2.amenity ORDER BY p.geom;
	
	DROP TABLE IF EXISTS pois_extract_coordinates;
	CREATE TABLE pois_extract_coordinates (osm_id int8, origin_geometry TEXT, amenity TEXT, geometry geometry, row_no int8, x_coord float8, y_coord float8);
	INSERT INTO pois_extract_coordinates
		SELECT osm_id, origin_geometry, amenity, ST_Transform(geom, ssrid) AS geometry, row_number() over(PARTITION BY geom ORDER BY amenity desc) AS row_no , 
		ST_X(ST_Transform(geom, ssrid)) AS x_coord, ST_Y(ST_Transform(geom, ssrid)) AS y_coord FROM pois_duplicated;
	
	UPDATE pois_extract_coordinates
	SET x_coord = (CASE WHEN row_no = 1 OR row_no = 4 THEN x_coord+5
    	WHEN row_no = 2 OR row_no = 3 THEN x_coord-5 
        ELSE x_coord END),
	y_coord = (CASE WHEN row_no = 1 OR row_no = 3 THEN y_coord+5
		WHEN row_no = 2 OR row_no = 4 THEN y_coord-5
        ELSE y_coord END);

	UPDATE pois_extract_coordinates
	SET geometry = ST_SetSRID(ST_MakePoint(x_coord, y_coord),ssrid);
	
	UPDATE pois
	SET geom = (CASE WHEN pois.osm_id = ANY (SELECT DISTINCT osm_id FROM pois_extract_coordinates) THEN ST_transform(subquery.mod_geometry, (SELECT ST_SRID(geom) FROM pois LIMIT 1))
	ELSE geom END)
	FROM (SELECT osm_id, amenity, geometry AS mod_geometry FROM pois_extract_coordinates) AS subquery
	WHERE pois.osm_id = subquery.osm_id AND pois.amenity = subquery.amenity;
END
$function$
/* SELECT pois_displacement(ARRAY['primary_school','secondary_school'], 31468) */
