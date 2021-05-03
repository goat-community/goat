
ALTER TABLE study_area ADD COLUMN IF NOT EXISTS default_building_levels SMALLINT; 
ALTER TABLE study_area ADD COLUMN IF NOT EXISTS default_roof_levels SMALLINT; 

ALTER TABLE study_area ALTER COLUMN sum_pop TYPE integer using sum_pop::integer;
ALTER TABLE study_area DROP COLUMN IF EXISTS area;
ALTER TABLE study_area add column area float;
UPDATE study_area set area = st_area(geom::geography);

DROP TABLE IF EXISTS buildings;
CREATE TABLE buildings 
(
	gid serial,
	osm_id integer,
	building TEXT, 
	amenity TEXT,
	residential_status TEXT,
	housenumber TEXT, 
	street TEXT,
	building_levels SMALLINT,
	building_levels_residential SMALLINT, 
	roof_levels SMALLINT,
	height float,
	area integer, 
	gross_floor_area_residential integer,
	geom geometry,
	CONSTRAINT building_pkey PRIMARY KEY(gid)
);
CREATE INDEX ON buildings USING GIST(geom);

ALTER TABLE buildings_custom ADD COLUMN IF NOT EXISTS building TEXT;
ALTER TABLE buildings_custom ADD COLUMN IF NOT EXISTS amenity TEXT;
ALTER TABLE buildings_custom ADD COLUMN IF NOT EXISTS residential_status TEXT; 
ALTER TABLE buildings_custom ADD COLUMN IF NOT EXISTS housenumber TEXT;
ALTER TABLE buildings_custom ADD COLUMN IF NOT EXISTS street TEXT;
ALTER TABLE buildings_custom ADD COLUMN IF NOT EXISTS building_levels SMALLINT; 
ALTER TABLE buildings_custom ADD COLUMN IF NOT EXISTS roof_Levels SMALLINT;
ALTER TABLE buildings_custom ADD COLUMN IF NOT EXISTS height float;

/*There where some invalid geometries in the dataset*/        	
UPDATE buildings_custom 
SET geom = ST_MAKEVALID(geom)
WHERE ST_ISVALID(geom) IS FALSE;

DO 
$$
	DECLARE
		average_building_levels integer := 4;
		average_roof_levels integer := 1;
		average_height_per_level float := 3.5; 
		inject_not_duplicated_osm TEXT := 'yes';
		inject_not_duplicated_custom TEXT := 'no';
	BEGIN 
		
		IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'buildings_custom'
            )
        THEN	
			
        	/*Priority geometry buildings custom*/
        	DROP TABLE IF EXISTS match_osm;
        	CREATE TEMP TABLE match_osm AS 
        	SELECT o.osm_id, c.gid AS custom_gid, ST_Intersection(o.geom,c.geom) AS geom         	
        	FROM buildings_custom c, buildings_osm o 
        	WHERE ST_Intersects(o.geom,c.geom); 
        
        	ALTER TABLE match_osm ADD COLUMN gid serial;
        	ALTER TABLE match_osm ADD PRIMARY KEY(gid);    
        
        	DROP TABLE IF EXISTS sum_custom_intersection;
        	CREATE TEMP TABLE sum_custom_intersection AS 
        	SELECT gid, SUM(ST_AREA(geom)) AS area_intersection 
        	FROM match_osm 
        	GROUP BY gid;
        	
        	/*Count number of intersections with OSM*/
        	DROP TABLE IF EXISTS cnt_intersections;
        	CREATE TEMP TABLE cnt_intersections AS 
        	SELECT count(osm_id) cnt_osm_id, gid AS custom_gid
        	FROM match_osm 
        	GROUP BY gid; 
			
        	ALTER TABLE cnt_intersections ADD COLUMN gid serial;
        	ALTER TABLE cnt_intersections ADD PRIMARY KEY(gid);
        
        	DROP TABLE IF EXISTS selected_buildings; 
        	CREATE TEMP TABLE selected_buildings AS 
        	WITH i AS 
        	(
	        	SELECT c.gid, s.area_intersection/ST_AREA(c.geom) AS share_intersection, c.geom 
	        	FROM sum_custom_intersection s, buildings_custom c
	        	WHERE c.gid = s.gid 
	        	AND s.area_intersection/ST_AREA(c.geom) > 0.35
        	)
        	SELECT i.gid AS custom_gid, m.osm_id, m.geom 
        	FROM cnt_intersections c, i, match_osm m  
        	WHERE c.custom_gid = i.gid
        	AND i.gid = m.gid
        	AND c.cnt_osm_id = 1;
        	
        	INSERT INTO selected_buildings
        	WITH i AS 
        	(
				SELECT m.osm_id, max(ST_AREA(m.geom)) 
				FROM cnt_intersections c, match_osm m
				WHERE c.custom_gid = m.gid
				AND c.cnt_osm_id > 1
				GROUP BY osm_id
        	)
        	SELECT m.gid AS custom_gid, i.osm_id, m.geom
        	FROM i, match_osm m
        	WHERE i.osm_id = m.osm_id; 
        				         	
        	CREATE INDEX ON selected_buildings (osm_id);
        	CREATE INDEX ON selected_buildings (custom_gid);
        	CREATE INDEX ON selected_buildings USING GIST(geom);
        	
        	/*Inject buildings from OSM that do not intersect custom buildings*/
        	IF inject_not_duplicated_osm = 'yes' THEN 
	        	INSERT INTO selected_buildings 
	        	SELECT o.osm_id, NULL AS custom_gid, o.geom  
	        	FROM buildings_osm o
	        	LEFT JOIN selected_buildings s 
	        	ON o.osm_id = s.osm_id
	        	WHERE s.osm_id IS NULL;
        	END IF; 
        	
        	/*Inject buildings from custom that do not intersect osm buildings*/
        	IF inject_not_duplicated_custom = 'yes' THEN 
	        	INSERT INTO selected_buildings 
	        	SELECT NULL AS osm_id, c.gid AS custom_gid, c.geom  
	        	FROM buildings_custom c
	        	LEFT JOIN selected_buildings s 
	        	ON c.gid = s.custom_gid
	        	WHERE s.custom_gid IS NULL;	
            END IF; 
           
        	INSERT INTO buildings(osm_id,building,amenity,residential_status,housenumber,street,building_levels,roof_levels,geom)
			SELECT o.osm_id,			
			CASE 
				WHEN c.building IS NOT NULL THEN c.building ELSE o.building END AS building,
			CASE 
				WHEN c.amenity IS NOT NULL THEN c.amenity ELSE o.amenity END AS amenity, 
			CASE 
				WHEN c.residential_status IS NOT NULL THEN c.residential_status ELSE o.residential_status END AS residential_status, 
			CASE 
				WHEN c.housenumber IS NOT NULL THEN c.housenumber ELSE o.housenumber END AS housenumber,
			CASE 
				WHEN c.street IS NOT NULL THEN c.street ELSE c.street END AS street,
			CASE 
				WHEN c.building_levels IS NOT NULL THEN c.building_levels
				WHEN c.height IS NOT NULL THEN (c.height/average_height_per_level)::smallint 
				WHEN o.building_levels IS NOT NULL THEN o.building_levels
				WHEN s.default_building_levels IS NOT NULL THEN s.default_building_levels
				ELSE average_building_levels END AS building_levels, 	
			CASE 
				WHEN c.roof_levels IS NOT NULL THEN c.roof_levels 
				WHEN o.roof_levels IS NOT NULL THEN o.roof_levels 
				WHEN s.default_roof_levels IS NOT NULL THEN s.default_roof_levels
				ELSE average_roof_levels END AS roof_levels, 
			b.geom
			FROM selected_buildings b
			LEFT JOIN buildings_osm o
			ON b.osm_id = o.osm_id
			LEFT JOIN buildings_custom c
			ON b.custom_gid = c.gid
			LEFT JOIN study_area s
			ON ST_Intersects(s.geom,b.geom);
		
		ELSE 
			INSERT INTO buildings
			SELECT * 
			FROM buildings_osm;
		END IF;
	END
$$;












