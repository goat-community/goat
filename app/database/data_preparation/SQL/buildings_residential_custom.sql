ALTER TABLE study_area ALTER COLUMN sum_pop TYPE integer using sum_pop::integer;
ALTER TABLE study_area DROP COLUMN IF EXISTS area;
ALTER TABLE study_area add column area float;
UPDATE study_area set area = st_area(geom::geography);

ALTER TABLE buildings ADD COLUMN IF NOT EXISTS building_levels integer;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS roof_levels integer;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS building_levels_residential integer;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS area numeric;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS residential_status text;
ALTER TABLE buildings ADD COLUMN IF NOT EXISTS building text;


UPDATE buildings 
SET building_levels = CASE WHEN trunc(height/3)::integer = 0 THEN 1 ELSE trunc(height/3)::integer END, 
area = ST_AREA(geom::geography)::integer,
roof_levels = NULL; 

UPDATE buildings 
SET residential_status = 'potential_residential';

UPDATE buildings b
SET residential_status = 'no_residents'
FROM landuse l
WHERE ST_Intersects(b.geom,l.geom)
AND l.landuse IN(SELECT UNNEST(variable_array) FROM variable_container WHERE identifier = 'custom_landuse_no_residents');

UPDATE buildings SET residential_status = 'no_residents'
WHERE ST_Area(geom::geography) < (SELECT select_from_variable_container_s('minimum_building_size_residential')::integer);

UPDATE buildings
SET residential_status = 'no_residents'
FROM (
	SELECT b.gid
	FROM buildings b
	LEFT JOIN landuse l 
	ON ST_intersects(b.geom,l.geom)
	WHERE l.gid IS NULL 
	AND b.residential_status = 'potential_residents'
) x
WHERE buildings.gid = x.gid;

WITH b AS (
    SELECT DISTINCT b.gid
    FROM buildings b, pois p 
    WHERE ST_intersects(b.geom,p.geom)
)
UPDATE buildings 
SET building_levels_residential = building_levels - 1
FROM b
WHERE buildings.gid = b.gid;
UPDATE buildings 
SET building_levels_residential = building_levels
WHERE building_levels_residential IS NULL;

CREATE TABLE landuse_osm AS 
SELECT ROW_NUMBER() OVER() AS gid, landuse, tourism, amenity, name, tags, way AS geom 
FROM planet_osm_polygon 
WHERE landuse IS NOT NULL;

CREATE INDEX ON landuse_osm USING GIST(geom);
ALTER TABLE landuse_osm ADD PRIMARY key(gid);

UPDATE buildings b SET residential_status = 'no_residents'
FROM landuse_osm l
WHERE l.landuse IN (SELECT UNNEST(select_from_variable_container('osm_landuse_no_residents')))
AND ST_INTERSECTS(l.geom,b.geom)
AND b.residential_status = 'potential_residential';

/*Temporary fix*/
UPDATE buildings 
SET residential_status = 'with_residents'
WHERE residential_status = 'potential_residential';


/*ALTER TABLE study_area ADD COLUMN IF NOT EXISTS default_building_levels SMALLINT;
ALTER TABLE study_area ADD COLUMN IF NOT EXISTS default_roof_levels SMALLINT;

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
	roof_levels SMALLINT,
	height float,
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

DO 
$$
	DECLARE
		all_default_building_levels integer := 4;
		all_default_roof_levels integer := 1;
		height_per_level float := 3.5; 
	BEGIN 
		
		
		IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'buildings_custom'
            )
        THEN	
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
				WHEN c.height IS NOT NULL THEN (c.height/height_per_level)::smallint 
				WHEN o.building_levels IS NOT NULL THEN o.building_levels
				WHEN s.default_building_levels IS NOT NULL THEN s.default_building_levels
				ELSE all_default_building_levels END AS building_levels, 	
			CASE 
				WHEN c.roof_levels IS NOT NULL THEN c.roof_levels 
				WHEN o.roof_levels IS NOT NULL THEN o.roof_levels 
				WHEN s.default_building_levels IS NOT NULL THEN s.default_building_levels
				ELSE all_default_roof_levels END AS roof_levels, 
			c.geom
			FROM buildings_custom c
			LEFT JOIN buildings_osm o 
			ON ST_Intersects(c.geom, o.geom)
			LEFT JOIN study_area s 
			ON ST_Intersects(c.geom,s.geom)
			WHERE ST_AREA(ST_Intersection(c.geom,o.geom))/ST_AREA(c.geom) > 0.5;
		ELSE 
			INSERT INTO buildings
			SELECT * 
			FROM buildings_osm;
		END IF;
	END
$$;

*/