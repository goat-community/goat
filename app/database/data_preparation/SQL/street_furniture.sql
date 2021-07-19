
----------------------------------
----Table for street furniture----
----------------------------------
DROP TABLE IF EXISTS street_furniture;
CREATE TABLE street_furniture
(
	gid serial, 
	original_key TEXT, 
	amenity TEXT, 
	data_source TEXT,
	geom geometry,
	CONSTRAINT street_furniture_pkey PRIMARY KEY(gid)
);

INSERT INTO street_furniture(original_key,amenity,data_source,geom)
SELECT p.osm_id AS original_key, p.amenity, 'osm' AS data_source, p.geom
FROM pois p, study_area s
WHERE st_intersects(s.geom,p.geom) 
AND amenity IN ('bench','waste_basket','toilets','fountain','bicycle_parking','bicycle_repair_station','drinking_water');

CREATE INDEX ON street_furniture USING gist(geom);

--Insert street_lamps
INSERT INTO street_furniture(original_key,amenity,data_source,geom)
SELECT p.osm_id AS original_key, p.highway AS amenity, 'osm' AS data_source, p.way AS geom
FROM planet_osm_point p, study_area s
WHERE st_intersects(s.geom,p.way) 
AND highway IN ('street_lamp');

/*Data fusion with custom street_items*/
DO $$
	BEGIN 
		IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'street_items'
            )
        THEN
			DROP TABLE IF EXISTS duplicated_items;
			CREATE TEMP TABLE duplicated_items AS 
			SELECT DISTINCT p.original_key
			FROM street_items p 
			LEFT JOIN street_furniture s 
			ON ST_DWithin(p.geom, s.geom, 0.0001)
			WHERE p.amenity = s.amenity 
			AND ST_Distance(p.geom, s.geom) > 0;

			ALTER TABLE duplicated_items ADD PRIMARY KEY(original_key);

			INSERT INTO street_furniture(original_key,amenity,data_source,geom)
			SELECT i.original_key, i.amenity, i.data_source, i.geom
			FROM street_items i
			LEFT JOIN duplicated_items d 
			ON i.original_key = d.original_key 
			WHERE d.original_key IS NULL
			AND i.amenity IN ('bench','street_lamp','bicycle_parking');
		END IF; 
	END 
$$