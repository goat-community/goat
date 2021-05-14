/*Performance issues with queries. Ideas for improvement:
- avoid update but rather write to new table
- experiment with HOT-Update
- Check if no residentials landuse from different table can be fused before intersection with buildings

*/

DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse'
            )
        THEN
			--Intersect with custom landuse table
        	ALTER TABLE landuse ADD COLUMN IF NOT EXISTS name text;
      
        	UPDATE buildings b 
        	SET residential_status = 'with_residents'
        	FROM landuse l
        	WHERE ST_Contains(l.geom,b.geom)
        	AND lower(name) ~~ ANY (SELECT UNNEST(select_from_variable_container('custom_landuse_with_residents_name')));
        
        	UPDATE buildings b 
        	SET residential_status = 'with_residents'
        	FROM landuse l
        	WHERE ST_Contains(l.geom,b.geom) = FALSE 
        	AND ST_Intersects(l.geom,b.geom)
			AND ST_Area(ST_Intersection(b.geom, l.geom)) / ST_Area(b.geom) > 0.5
        	AND lower(name) ~~ ANY (SELECT UNNEST(select_from_variable_container('custom_landuse_with_residents_name')));	
        
        	UPDATE buildings b
			SET residential_status = 'no_residents'
			FROM landuse l
			WHERE ST_Contains(l.geom,b.geom)
			AND b.residential_status = 'potential_residents'
			AND l.landuse IN(SELECT UNNEST(select_from_variable_container('custom_landuse_no_residents')));
		
			UPDATE buildings b
			SET residential_status = 'no_residents'
			FROM landuse l 
			WHERE ST_Contains(l.geom,b.geom) = FALSE 
			AND ST_Intersects(l.geom,b.geom)
			AND ST_Area(ST_Intersection(b.geom, l.geom)) / ST_Area(b.geom) > 0.5
			AND b.residential_status = 'potential_residents'
			AND l.landuse IN(SELECT UNNEST(select_from_variable_container('custom_landuse_no_residents')));
			
			/*
			WITH aois_buildings AS 
			(
				SELECT b.gid, b.geom 
				FROM buildings b, aois a
				WHERE ST_Intersects(b.geom, a.geom)
				AND b.residential_status = 'with_residents'
				AND a.amenity IN (SELECT UNNEST(select_from_variable_container('aois_no_residents')))
			),
			no_residents AS 
			(
				SELECT b.gid
				FROM aois_buildings b, landuse l 
				WHERE ST_Intersects(b.geom, l.geom) 
				AND l.landuse IN (SELECT UNNEST(select_from_variable_container('custom_landuse_no_residents'))) 
			)
			UPDATE buildings b SET residential_status = 'no_residents'
			FROM no_residents n
			WHERE b.gid = n.gid; 
			*/
        END IF ;
    END
$$ ;

DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse_additional'
            )
        THEN

			UPDATE buildings b 
			SET residential_status = 'no_residents'
			FROM landuse_additional l
			WHERE landuse IN (SELECT UNNEST(select_from_variable_container('custom_landuse_additional_no_residents')))
			AND ST_CONTAINS(l.geom,b.geom)
			AND b.residential_status = 'potential_residents';

        END IF ;
    END
$$ ;

CREATE TEMP TABLE osm_area_no_residents AS 
SELECT way AS geom 
FROM planet_osm_polygon 
WHERE landuse IN(SELECT UNNEST(select_from_variable_container('osm_landuse_no_residents')))
OR tourism IN(SELECT UNNEST(select_from_variable_container('tourism_no_residents')))
OR amenity IN(SELECT UNNEST(select_from_variable_container('amenity_no_residents')));

CREATE INDEX ON osm_area_no_residents USING GIST(geom);

UPDATE buildings b
SET residential_status = 'no_residents'
FROM osm_area_no_residents l
WHERE ST_Contains(l.geom,b.geom)
AND b.residential_status = 'potential_residents';

UPDATE buildings b
SET residential_status = 'no_residents'
FROM osm_area_no_residents l 
WHERE ST_Contains(l.geom,b.geom) = FALSE 
AND ST_Intersects(l.geom,b.geom)
AND ST_Area(ST_Intersection(b.geom, l.geom)) / ST_Area(b.geom) > 0.5
AND b.residential_status = 'potential_residents';

DROP TABLE IF EXISTS osm_area_no_residents ;

--Label all buildings that are not intersecting the custom land-use
DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse'
            )
        THEN					
        	UPDATE buildings
        	SET residential_status = 'no_residents'
        	FROM (
	        	SELECT b.gid
	        	FROM buildings b
	        	LEFT JOIN landuse l 
	        	ON st_intersects(b.geom,l.geom)
	        	WHERE l.gid IS NULL 
	        	AND b.residential_status = 'potential_residents'
        	) x
        	WHERE buildings.gid = x.gid;
 	
        END IF ;
    END
$$ ;

UPDATE buildings 
SET area = ST_AREA(geom::geography);

UPDATE buildings
SET residential_status = 'no_residents'
WHERE buildings.area < (SELECT select_from_variable_container_s('minimum_building_size_residential')::integer)
AND residential_status <> 'with_residents';

--Substract one level when POI on building (more classification has to be done in the future)

WITH x AS (
    SELECT DISTINCT b.gid
    FROM buildings b, pois p 
    WHERE st_intersects(b.geom,p.geom)
)
UPDATE buildings b
SET building_levels_residential = building_levels - 1
FROM x
WHERE b.gid = x.gid;

UPDATE buildings 
set building_levels_residential = building_levels
WHERE building_levels_residential IS NULL;

UPDATE buildings 
SET residential_status = 'with_residents'
WHERE residential_status = 'potential_residents';
 
UPDATE buildings 
SET gross_floor_area_residential = (building_levels_residential * area) + (roof_levels/2) * area 
WHERE residential_status = 'with_residents';







ALTER TABLE buildings ADD COLUMN backup_status TEXT 

UPDATE buildings SET backup_status = residential_status 

UPDATE buildings SET residential_status = backup_status 


UPDATE buildings 
SET residential_status = 'potential_residents'
WHERE residential_status IS NULL; 


DROP TABLE IF EXISTS buildings_classification;
CREATE TABLE buildings_classification 
(
	gid integer, 
	landuse_residential_status integer[],
	landuse_gids integer[],
	landuse_additional_residential_status integer[],
	landuse_additional_gids integer[],
	landuse_osm_residential_status integer[],
	landuse_osm_gids integer[]
);

UPDATE buildings 
SET area = ST_AREA(geom::geography);

UPDATE buildings
SET residential_status = 'no_residents'
WHERE buildings.area < (SELECT select_from_variable_container_s('minimum_building_size_residential')::integer)
AND residential_status <> 'potential_residential';

INSERT INTO buildings_classification 
SELECT gid 
FROM buildings
WHERE residential_status = 'potential_residents'; 

ALTER TABLE buildings_classification ADD PRIMARY KEY(gid);


DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse'
            )
        THEN
        	
        	DROP TABLE IF EXISTS landuse_subdivide; 
        	CREATE TABLE landuse_subdivide AS 
        	SELECT landuse, ST_SUBDIVIDE(geom, 200) AS geom
        	FROM landuse; 
        
        	ALTER TABLE landuse_subdivide ADD COLUMN gid serial;
        	ALTER TABLE landuse_subdivide ADD PRIMARY KEY(gid);
    		CREATE INDEX ON landuse_subdivide USING GIST(geom);
     		
    		DROP TABLE IF EXISTS buildings_landuse;
        	CREATE TABLE buildings_landuse AS 
        	WITH buildings_intersects AS 
        	(
				SELECT b.gid, CASE WHEN l.landuse IS NULL THEN 2 
				ELSE (select_from_variable_container('custom_landuse_no_residents') && ARRAY[l.landuse])::integer END AS residential_status, l.gid landuse_gid
				FROM (
					SELECT * 
					FROM buildings 
					WHERE residential_status = 'potential_residents'
				) b
				LEFT JOIN landuse_subdivide l
				ON ST_INTERSECTS(l.geom, b.geom)
			) 
			SELECT gid, ARRAY_AGG(residential_status) AS landuse_residential_status, ARRAY_AGG(landuse_gid) AS landuse_gids			
			FROM buildings_intersects
			GROUP BY gid; 
			
			ALTER TABLE buildings_landuse ADD PRIMARY KEY(gid);

			UPDATE buildings_classification c
			SET landuse_residential_status = l.landuse_residential_status,
			landuse_gids = l.landuse_gids
			FROM buildings_landuse l
			WHERE c.gid = l.gid; 
		
        END IF ;
    END
$$ ;


DO $$                  
    DECLARE 
    	categories_no_residents TEXT[] := select_from_variable_container('custom_landuse_additional_no_residents');
	BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse_additional'
            )
        THEN     
        	DROP TABLE IF EXISTS landuse_additional_subdivide ; 
        	CREATE TABLE landuse_additional_subdivide  AS 
        	SELECT landuse, ST_SUBDIVIDE(geom, 200) AS geom
        	FROM landuse_additional; 
        
        	ALTER TABLE landuse_additional_subdivide ADD COLUMN gid serial;
        	ALTER TABLE landuse_additional_subdivide  ADD PRIMARY KEY(gid);
    		CREATE INDEX ON landuse_additional_subdivide  USING GIST(geom);
     		
    		DROP TABLE IF EXISTS buildings_landuse;
        	CREATE TABLE buildings_landuse AS 
        	WITH buildings_intersects AS 
        	(
				SELECT b.gid, CASE WHEN l.landuse IS NULL THEN 2 
				ELSE (categories_no_residents && ARRAY[l.landuse])::integer END AS residential_status, l.gid landuse_gid
				FROM (
					SELECT * 
					FROM buildings 
					WHERE residential_status = 'potential_residents'
				) b 
				LEFT JOIN landuse_additional_subdivide l
				ON ST_INTERSECTS(l.geom, b.geom)
			) 
			SELECT gid, ARRAY_AGG(residential_status) AS landuse_residential_status, ARRAY_AGG(landuse_gid) AS landuse_gids		
			FROM buildings_intersects
			GROUP BY gid; 
			
			ALTER TABLE buildings_landuse ADD PRIMARY KEY(gid);
		
			UPDATE buildings_classification c
			SET landuse_additional_residential_status = l.landuse_residential_status,
			landuse_additional_gids = l.landuse_gids
			FROM buildings_landuse l
			WHERE c.gid = l.gid; 
        END IF ;
    END
$$ ;

DO $$
	DECLARE 
    	categories_no_residents TEXT[] := select_from_variable_container('osm_landuse_no_residents') 
    		|| select_from_variable_container('tourism_no_residents')
    		|| select_from_variable_container('amenity_no_residents');
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse_osm'
            )
        THEN
			
			DROP TABLE IF EXISTS landuse_osm_subdivide ; 
        	CREATE TABLE landuse_osm_subdivide AS 
			SELECT landuse, ST_SUBDIVIDE(geom, 200) AS geom
			FROM landuse_osm l
			WHERE landuse IS NOT NULL;
	
        	ALTER TABLE landuse_osm_subdivide ADD COLUMN gid serial;
        	ALTER TABLE landuse_osm_subdivide  ADD PRIMARY KEY(gid);
    		CREATE INDEX ON landuse_osm_subdivide  USING GIST(geom);
     		
    		DROP TABLE IF EXISTS buildings_landuse;
        	CREATE TABLE buildings_landuse AS 
        	WITH buildings_intersects AS 
        	(
				SELECT b.gid, CASE WHEN l.landuse IS NULL THEN 2 
				ELSE (categories_no_residents && ARRAY[l.landuse])::integer END AS residential_status, l.gid landuse_gid
				FROM (
					SELECT * 
					FROM buildings 
					WHERE residential_status = 'potential_residents'
				) b
				LEFT JOIN landuse_osm_subdivide l
				ON ST_INTERSECTS(l.geom, b.geom)
			) 
			SELECT gid, ARRAY_AGG(residential_status) AS landuse_residential_status, ARRAY_AGG(landuse_gid) AS landuse_gids		
			FROM buildings_intersects
			GROUP BY gid; 
			
			ALTER TABLE buildings_landuse ADD PRIMARY KEY(gid);

			UPDATE buildings_classification c
			SET landuse_osm_residential_status = l.landuse_residential_status,
			landuse_osm_gids = l.landuse_gids
			FROM buildings_landuse l
			WHERE c.gid = l.gid; 
		
		
        END IF ;
    END
$$ ;

CREATE INDEX ON buildings_classification USING gin (landuse_residential_status gin__int_ops);
CREATE INDEX ON buildings_classification USING gin (landuse_additional_residential_status gin__int_ops);
CREATE INDEX ON buildings_classification USING gin (landuse_osm_residential_status gin__int_ops);

DROP TABLE IF EXISTS buildings_to_update;
CREATE TABLE buildings_to_update (gid integer, residential_status text);
ALTER TABLE buildings_to_update ADD PRIMARY KEY(gid);

INSERT INTO buildings_to_update
SELECT b.gid, 'with_residents'
FROM buildings_classification c, buildings b
WHERE c.landuse_residential_status = ARRAY[0]
AND c.landuse_additional_residential_status = ARRAY[0]
AND c.landuse_osm_residential_status = ARRAY[0]
AND c.gid = b.gid; 

INSERT INTO buildings_to_update 
SELECT b.gid, 'no_residents'
FROM buildings_classification c, buildings b
WHERE c.landuse_residential_status = ARRAY[1]
AND c.landuse_additional_residential_status = ARRAY[1]
AND c.landuse_osm_residential_status = ARRAY[1]
AND c.gid = b.gid; 

INSERT INTO buildings_to_update 
SELECT b.gid, 'no_residents'
FROM buildings_classification c, buildings b
WHERE c.landuse_residential_status = ARRAY[2]
AND c.landuse_additional_residential_status = ARRAY[2]
AND c.landuse_osm_residential_status = ARRAY[2]
AND c.gid = b.gid; 

INSERT INTO buildings_to_update
WITH classification AS 
(
	SELECT c.gid, classify_building(c.gid, 
		jsonb_build_array(jsonb_build_object('categorization',c.landuse_residential_status,'landuse_gid', c.landuse_gids, 'table','landuse'),
		jsonb_build_object('categorization',c.landuse_osm_residential_status,'landuse_osm_gid', c.landuse_osm_gids, 'table','landuse_osm'),
		jsonb_build_object('categorization',c.landuse_additional_residential_status,'landuse_additional_gid', c.landuse_additional_gids, 'table','landuse_additional'))
	) 
	FROM buildings_classification c
	LEFT JOIN buildings_to_update u 
	ON c.gid = u.gid 
	WHERE u.gid IS NULL 
)
SELECT gid, CASE WHEN classify_building = 0 THEN 'with_residents' ELSE 'no_residents' END AS residential_status 
FROM classification;

UPDATE buildings b 
SET residential_status = u.residential_status
FROM buildings_to_update u 
WHERE b.gid = u.gid; 
--Substract one level when POI on building (more classification has to be done in the future)

WITH x AS (
    SELECT DISTINCT b.gid
    FROM buildings b, pois p 
    WHERE st_intersects(b.geom,p.geom)
)
UPDATE buildings b
SET building_levels_residential = building_levels - 1
FROM x
WHERE b.gid = x.gid;

UPDATE buildings 
set building_levels_residential = building_levels
WHERE building_levels_residential IS NULL;

UPDATE buildings 
SET residential_status = 'with_residents'
WHERE residential_status = 'potential_residents';
 
UPDATE buildings 
SET gross_floor_area_residential = (building_levels_residential * area) + (roof_levels/2) * area 
WHERE residential_status = 'with_residents';




