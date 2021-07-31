/*Creating building entrances for the residential buildings*/
DROP TABLE IF EXISTS buildings_residential;
CREATE TABLE buildings_residential AS 
SELECT * 
FROM buildings
WHERE residential_status = 'with_residents';

ALTER TABLE buildings_residential ADD PRIMARY KEY(gid);
CREATE INDEX ON buildings_residential USING gist(geom);

/*Add all points labelled as entrances in OSM*/
DROP TABLE IF EXISTS all_addresses; 
CREATE TABLE all_addresses AS 
SELECT osm_id, way AS geom 
FROM planet_osm_point p
WHERE (tags -> 'entrance') IS NOT NULL 
AND (tags -> 'entrance') <> 'emergency'
AND amenity IS NULL 
AND shop IS NULL;

ALTER TABLE all_addresses ADD PRIMARY KEY (osm_id);

/*Add all addresses labelled in OSM*/
INSERT INTO all_addresses 
SELECT p.osm_id, p.way AS geom 
FROM (
	SELECT osm_id, way 
	FROM planet_osm_point p 
	WHERE p."addr:housenumber" IS NOT NULL
	AND amenity IS NULL 
	AND shop IS NULL
) p
LEFT JOIN all_addresses a
ON p.osm_id = a.osm_id
WHERE a.osm_id IS NULL;

CREATE INDEX ON all_addresses USING GIST(geom);

/*Find all addresses that intersect with buildings*/
DROP TABLE IF EXISTS residential_addresses;
CREATE TABLE residential_addresses AS 
SELECT b.gid AS building_gid, a.osm_id, b.gross_floor_area_residential, a.geom
FROM all_addresses a, buildings_residential b
WHERE ST_Intersects(a.geom,b.geom);

ALTER TABLE residential_addresses ADD COLUMN gid serial;
ALTER TABLE residential_addresses ADD PRIMARY KEY (gid);

/*Snap addresses that are close to a building but do not intersect*/
DO $$
	DECLARE 
    	buffer_distance float := 5 * meter_degree(); /*Default buffer at 5 meters*/
    BEGIN 
	    INSERT INTO residential_addresses 
	    WITH not_intersection_addresses AS 
	    (
	    	SELECT a.*
	    	FROM all_addresses a
	    	LEFT JOIN residential_addresses r 
	    	ON a.osm_id = r.osm_id 
	    	WHERE r.osm_id IS NULL 
	    )
		SELECT j.gid AS building_gid, a.osm_id, j.gross_floor_area_residential, j.geom
		FROM not_intersection_addresses a
		CROSS JOIN LATERAL 
		(
			SELECT b.gid, b.gross_floor_area_residential, ST_CLOSESTPOINT(b.geom, a.geom) geom 
			FROM buildings_residential b 
			WHERE ST_DWITHIN(b.geom, a.geom, buffer_distance)
			ORDER BY ST_CLOSESTPOINT(b.geom, a.geom) <-> a.geom
            LIMIT 1     		
		) j;
    END
$$ ;

CREATE INDEX ON residential_addresses USING GIST(geom);
ALTER TABLE residential_addresses DROP COLUMN osm_id;

/*Adjust gross_floor_area_residetial of several addresses are on one building*/
DROP TABLE IF EXISTS cnt_addresses_buildings;
CREATE TEMP TABLE cnt_addresses_buildings AS 
SELECT count(*) cnt, building_gid 
FROM residential_addresses
GROUP BY building_gid
HAVING count(*) > 1;

ALTER TABLE cnt_addresses_buildings ADD PRIMARY key(building_gid);

UPDATE residential_addresses a
SET gross_floor_area_residential = gross_floor_area_residential/ cnt 
FROM cnt_addresses_buildings c
WHERE a.building_gid = c.building_gid;

/*
 Derive centroid of all buildings that do not intersect and snap to the border of the 
 building in the direction of the closest street.
*/
DO $$
	DECLARE 
    	buffer_distance float := 30 * meter_degree(); /*Default buffer at 5 meters*/
    BEGIN 
		INSERT INTO residential_addresses 
		WITH buildings_no_address AS (
			SELECT b.* 
			FROM buildings_residential b
			LEFT JOIN residential_addresses a 
			ON b.gid = a.building_gid
			WHERE a.building_gid IS NULL 
		)
		SELECT a.gid AS building_gid, a.gross_floor_area_residential, ST_CLOSESTPOINT(a.geom, j.geom) AS geom
		FROM buildings_no_address a
		CROSS JOIN LATERAL 
		(
			SELECT ST_CLOSESTPOINT(w.geom, ST_CENTROID(a.geom)) geom 
			FROM ways w 
			WHERE ST_DWITHIN(w.geom, a.geom, buffer_distance)
			ORDER BY ST_CLOSESTPOINT(w.geom, a.geom) <-> a.geom
            LIMIT 1   
		) j;	
	END 
$$;
/*Insert all centroid that where not in the buffer distance of the street network*/
INSERT INTO residential_addresses
SELECT b.gid AS building_gid, b.gross_floor_area_residential, ST_CENTROID(b.geom) geom 
FROM buildings_residential b
LEFT JOIN residential_addresses a 
ON b.gid = a.building_gid
WHERE a.building_gid IS NULL; 

CREATE INDEX ON residential_addresses USING GIST(geom);
