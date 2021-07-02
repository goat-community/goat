/*
This script is fusing buildings from OSM and a custom building layer. 
Per default the priority is given to the custom file, however if no information exists for the custom building layer, then OSM is used.
The following attributes can be defined in the custom building layer:

building == has this building a certain building type (e.g. garages)
amenity == has this building a special amenity type (e.g. school)
residential_status == is the building residential?. You can define the following status: "with_residents", "potential_residents", "no_residents"
housenumber == housenumber of the building
street == street name
building_levels == number of building levels
roof_Levels == number of roof levels
height == height of the building

*/
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

DO 
$$
	DECLARE
		average_building_levels integer := select_from_variable_container_s('average_building_levels')::integer;
		average_roof_levels integer := select_from_variable_container_s('average_roof_levels')::integer;
		average_height_per_level float := select_from_variable_container_s('average_height_per_level')::float;
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
						
        	/*Priority geometry buildings custom*/
        	DROP TABLE IF EXISTS match_osm;
        	CREATE TEMP TABLE match_osm AS  
        	SELECT o.osm_id, c.gid AS custom_gid, ST_AREA(ST_Intersection(o.geom,c.geom)) AS area_intersection, ST_Intersection(o.geom,c.geom) AS geom         	
        	FROM buildings_custom c, buildings_osm o 
        	WHERE ST_Intersects(o.geom,c.geom); 
        
        	ALTER TABLE match_osm ADD COLUMN gid serial;
        	ALTER TABLE match_osm ADD PRIMARY KEY(gid);    
              	
        	/*Count number of intersections with OSM*/
        	DROP TABLE IF EXISTS cnt_intersections;
        	CREATE TEMP TABLE cnt_intersections AS 
        	SELECT count(osm_id) cnt_osm_id, custom_gid
        	FROM match_osm 
        	GROUP BY custom_gid; 
			
        	ALTER TABLE cnt_intersections ADD COLUMN gid serial;
        	ALTER TABLE cnt_intersections ADD PRIMARY KEY(gid);
        
        	DROP TABLE IF EXISTS selected_buildings; 
        	CREATE TEMP TABLE selected_buildings AS 
        	WITH m AS 
        	(
				SELECT m.custom_gid, m.osm_id, m.area_intersection, m.geom 
	        	FROM cnt_intersections c, match_osm m  
	        	WHERE c.custom_gid = m.custom_gid
	        	AND c.cnt_osm_id = 1
        	)        	
    		SELECT c.gid custom_gid, m.osm_id, c.geom 
        	FROM m, buildings_custom c
        	WHERE m.custom_gid = c.gid 
        	AND m.area_intersection/ST_AREA(c.geom) > 0.35;
        
        	DROP TABLE IF EXISTS sum_multi_intersection;
        	CREATE TEMP TABLE sum_multi_intersection AS 
        	SELECT m.osm_id, m.custom_gid, SUM(m.area_intersection) area_intersection
        	FROM match_osm m, cnt_intersections c 
        	WHERE c.cnt_osm_id > 1
        	AND m.custom_gid = c.custom_gid
        	GROUP BY m.osm_id, m.custom_gid;

        	INSERT INTO selected_buildings
        	WITH dominant_osm_building AS 
        	(
	        	SELECT s.custom_gid, NULL::FLOAT AS share_intersection, get_id_for_max_val(ARRAY_AGG((s.area_intersection*10000000000000)::integer), ARRAY_AGG(s.osm_id::integer)) osm_id
	        	FROM sum_multi_intersection s
	        	GROUP BY custom_gid 
        	)
			SELECT d.custom_gid, d.osm_id, c.geom 
			FROM dominant_osm_building d, buildings_custom c 
			WHERE d.custom_gid = c.gid; 
			
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
			DROP TABLE IF EXISTS selected_buildings;
		ELSE 
			INSERT INTO buildings(osm_id,building,amenity,residential_status,street,housenumber,area,building_levels,roof_levels,geom)
			SELECT b.osm_id,b.building,b.amenity,b.residential_status,b.street,b.housenumber,b.area,
			CASE WHEN b.building_levels IS NOT NULL THEN b.building_levels ELSE average_building_levels END AS building_levels,
			CASE WHEN b.roof_levels IS NOT NULL THEN b.roof_levels ELSE average_roof_levels END AS roof_levels,b.geom
			FROM buildings_osm b
			LEFT JOIN study_area s
			ON ST_Intersects(s.geom,b.geom);
		END IF;
	END
$$;


