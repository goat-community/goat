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









/*Performance issues with queries. Ideas for improvement:
- avoid update but rather write to new table
- experiment with HOT-Update
- Check if no residentials landuse from different table can be fused before intersection with buildings

*/

ALTER TABLE buildings ADD COLUMN backup_status TEXT 

UPDATE buildings SET backup_status = residential_status 

UPDATE buildings SET residential_status = backup_status 


UPDATE buildings 
SET residential_status = 'potential_residents'
WHERE residential_status IS NULL; 

DROP TABLE IF EXISTS landuse_residents; 
CREATE TABLE landuse_residents (landuse TEXT, geom geometry);

DROP TABLE IF EXISTS landuse_no_residents; 
CREATE TABLE landuse_no_residents (landuse TEXT, geom geometry);
DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse'
            )
        THEN
			
        	INSERT INTO landuse_residents 
        	SELECT l.landuse, l.geom
			FROM landuse l 
			WHERE l.landuse NOT IN(SELECT UNNEST(select_from_variable_container('custom_landuse_no_residents')))
			AND (name IS NULL OR lower(name) ~~ ANY (SELECT UNNEST(select_from_variable_container('custom_landuse_with_residents_name'))));
        	
			INSERT INTO landuse_no_residents 
        	SELECT l.landuse, l.geom
			FROM landuse l 
			WHERE l.landuse IN(SELECT UNNEST(select_from_variable_container('custom_landuse_no_residents')))
			AND (name IS NULL OR NOT lower(name) ~~ ANY (SELECT UNNEST(select_from_variable_container('custom_landuse_with_residents_name'))));
        	
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
			INSERT INTO landuse_residents 
			SELECT l.landuse, l.geom 
			FROM landuse_additional l 
			WHERE landuse NOT IN (SELECT UNNEST(select_from_variable_container('custom_landuse_additional_no_residents')));
		
			INSERT INTO landuse_no_residents 
			SELECT l.landuse, l.geom 
			FROM landuse_additional l 
			WHERE landuse IN (SELECT UNNEST(select_from_variable_container('custom_landuse_additional_no_residents')));
        END IF ;
    END
$$ ;

DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'landuse_osm'
            )
        THEN
			INSERT INTO landuse_residents 
			SELECT l.landuse, l.geom 
			FROM landuse_osm l
			WHERE landuse NOT IN(SELECT UNNEST(select_from_variable_container('osm_landuse_no_residents')))
			AND (tourism IS NULL OR tourism NOT IN(SELECT UNNEST(select_from_variable_container('tourism_no_residents'))))
			AND (amenity IS NULL OR amenity NOT IN(SELECT UNNEST(select_from_variable_container('amenity_no_residents'))));
					
			INSERT INTO landuse_no_residents 
			SELECT l.landuse, l.geom 
			FROM landuse_osm l
			WHERE landuse IN(SELECT UNNEST(select_from_variable_container('osm_landuse_no_residents')))
			OR tourism IN(SELECT UNNEST(select_from_variable_container('tourism_no_residents')))
			OR amenity IN(SELECT UNNEST(select_from_variable_container('amenity_no_residents')));
        END IF ;
    END
$$ ;


CREATE INDEX ON landuse_residents USING GIST(geom);
CREATE INDEX ON landuse_no_residents USING GIST(geom);

DROP TABLE IF EXISTS gids_contained_residents; 
CREATE TABLE gids_contained_residents AS 
SELECT DISTINCT b.gid   
FROM buildings b, landuse_residents l 
WHERE b.residential_status = 'potential_residents'
AND ST_Intersects(l.geom, b.geom);

ALTER TABLE gids_contained_residents ADD PRIMARY KEY(gid);

UPDATE buildings b
SET residential_status = 'with_residents'
FROM gids_contained_residents g
WHERE b.residential_status = 'potential_residents'
AND b.gid = g.gid;

SELECT b.* 
FROM buildings b, landuse_no_residents l 
WHERE b.residential_status = 'with_residents'
AND ST_Intersects(l.geom, b.geom);


DROP TABLE IF EXISTS gids_intersection; 
CREATE TABLE gids_intersection AS 
SELECT ST_Intersects()
FROM buildings b, landuse_residents l 
WHERE b.residential_status = 'potential_residents'
AND ST_Intersects(l.geom, b.geom)


SELECT * 
FROM buildings 
WHERE residential_status IS NULL 


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



/**/

*Performance issues with queries. Ideas for improvement:
- avoid update but rather write to new table
- experiment with HOT-Update
- Check if no residentials landuse from different table can be fused before intersection with buildings

*/

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


SELECT count(*) 
FROM buildings_classification bc 

/* 0 ==> residential
 * 1 ==> not_residential
 * 2 ==> no landuse
 * */

DROP TABLE test; 

CREATE TABLE test AS 

EXPLAIN ANALYZE 
SELECT b.*
FROM buildings_classification c, buildings b
WHERE c.landuse_residential_status = ARRAY[0]
AND c.landuse_additional_residential_status = ARRAY[0]
AND c.landuse_osm_residential_status = ARRAY[0]
AND c.gid = b.gid 


CREATE TABLE test AS 
SELECT count(*)
FROM buildings_classification c, buildings b
WHERE c.landuse_residential_status = ARRAY[1]
AND c.landuse_additional_residential_status = ARRAY[1]
AND c.landuse_osm_residential_status = ARRAY[1]
AND c.gid = b.gid 

DROP TABLE test; 

CREATE TABLE test AS 
SELECT geom
FROM buildings_classification c, buildings b
WHERE c.landuse_residential_status = ARRAY[1]
AND c.landuse_additional_residential_status = ARRAY[1]
AND c.landuse_osm_residential_status = ARRAY[2]
AND c.gid = b.gid 

EXPLAIN ANALYZE 

WITH x AS 
(	
	SELECT classify_building(landuse_residential_status,landuse_additional_residential_status,landuse_osm_residential_status) AS residential_status
	FROM buildings_classification bc 
)
SELECT residential_status, count(*) 
FROM x
GROUP BY residential_status

SELECT uniq(ARRAY[[1,2],[2,3]])


SELECT DISTINCT landuse FROM landuse l 

EXPLAIN ANALYZE 
SELECT uniq(ARRAY[1,2])


DROP FUNCTION IF EXISTS classify_building;
CREATE OR REPLACE FUNCTION classify_building(bgid integer, categorization jsonb[])
 RETURNS void --text
AS $$
DECLARE
   categorization_unique integer[][] := ARRAY[[]]::integer[][];
   cnt integer := 0;
BEGIN

	FOR cnt IN 1..ARRAY_LENGTH(categorization,1) 
	LOOP   		
      	IF ARRAY_LENGTH(uniq(categorization[cnt]),1) > 1 THEN 	
      		categorization_unique = ARRAY_APPEND(categorization_unique,multiple_landuse_intersection(bgid,categorization[cnt],landuse_gids[cnt],landuse_tables[cnt])); 
		ELSE 
			categorization_unique = categorization;
		END IF;
   	END LOOP;
	 
	RAISE NOTICE '%', categorization_unique; 
	
	
	
END
$$ LANGUAGE plpgsql IMMUTABLE;


SELECT jsonb_build_array(jsonb_build_object('categorization',landuse_residential_status,'landuse_gid', landuse_gids, 'table','landuse'),
jsonb_build_object('categorization',landuse_additional_residential_status,'landuse_additional_gid', landuse_additional_gids, 'table','landuse_additional') ,
jsonb_build_object('categorization',landuse_osm_residential_status,'landuse_osm_gid', landuse_osm_gids, 'table','landuse_osm')) 
FROM buildings_classification b

SELECT * FROM buildings_classification bc 

SELECT classify_building(24,ARRAY[landuse_residential_status, landuse_additional_residential_status, landuse_osm_residential_status],
ARRAY[landuse_gids, landuse_additional_gids, landuse_osm_gids],ARRAY['landuse','landuse_additional','landuse_osm'])
FROM buildings_classification bc 
LIMIT 100



IF unique_classes = ARRAY[0] THEN 
	RETURN 'with_residents';
ELSEIF unique_classes = ARRAY[1] THEN
	RETURN 'no_residents';
END IF;

IF uniq(categorization[1] || categorization[2]) = ARRAY[0] THEN 
	RETURN 'with_residents';
ELSEIF uniq(categorization[1] || categorization[2]) = ARRAY[1] 
	RETURN 'potential_residents';
END IF;




SELECT array_length(ARRAY[1,2],1) 

CREATE OR REPLACE FUNCTION derive_dominant_class(bgid integer, categorization integer[][], landuse_gids integer[][], landuse_table TEXT)
 RETURNS integer
AS $$
DECLARE
   bgeom geometry := (SELECT geom FROM buildings WHERE gid = bgid);
   dominant_class integer;
BEGIN
	IF landuse_table = 'landuse' THEN 
		SELECT cat
		INTO dominant_class
		FROM (SELECT UNNEST(categorization) cat, UNNEST(landuse_gids) gid) c, landuse_subdivide l 
		WHERE l.gid = c.gid
		GROUP BY cat 
		ORDER BY ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom))) 
		LIMIT 1;
	ELSEIF landuse_table = 'landuse_additional' THEN 
		SELECT cat
		INTO dominant_class
		FROM (SELECT UNNEST(categorization) cat, UNNEST(landuse_gids) gid) c, landuse_additional_subdivide l 
		WHERE l.gid = c.gid
		GROUP BY cat 
		ORDER BY ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom)))
		LIMIT 1;
	ELSEIF landuse_table = 'landuse_osm' THEN 
		SELECT cat
		INTO dominant_class
		FROM (SELECT UNNEST(categorization) cat, UNNEST(landuse_gids) gid) c, landuse_osm_subdivide l 
		WHERE l.gid = c.gid
		GROUP BY cat 
		ORDER BY ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom))) 
		LIMIT 1;
	ELSE 
		RAISE NOTICE 'No valid landuse table was selected.';
	END IF; 

	RETURN dominant_class;
END
$$ LANGUAGE plpgsql;


SELECT cat
--INTO dominant_class
FROM (SELECT UNNEST(categorization) cat, UNNEST(landuse_gids) gid) c, landuse l 
WHERE l.gid = c.gid
GROUP BY cat 
ORDER BY ST_AREA(ST_INTERSECTION(bgeom, ST_UNION(l.geom))); 

SELECT 

SELECT * FROM test_classes


DROP FUNCTION multiple_landuse_intersection

EXPLAIN ANALYZE 
SELECT multiple_landuse_intersection(24,ARRAY[0,0,0,0,0,1,0],ARRAY[4293,4412,9376,9458,9459,9472,9554],'landuse')





SELECT * 
FROM landuse
WHERE gid IN (SELECT UNNEST(ARRAY[4293,4412,9376,9458,9459,9472,9554]))


DROP TABLE test 

CREATE TABLE test AS 
SELECT * 
FROM buildings
WHERE gid = 24

SELECT * FROM buildings_classification bc 


SELECT categorization, ST_UNION(l.geom) AS geom 
FROM (SELECT UNNEST(ARRAY[1,2]) categorization, UNNEST(ARRAY[1,2]) gid) c, landuse l 
WHERE l.gid = c.gid
GROUP BY categorization 

DROP TABLE test 

CREATE TABLE test AS 
SELECT c.gid, b.geom 
FROM buildings_classification c, buildings b
WHERE uniq(c.landuse_residential_status) = ARRAY[0,1]
AND c.gid = b.gid 

SELECT ARRAY[1] && ARRAY[1] && ARRAY[1]

SELECT * 
FROM buildings_classification bc 
WHERE gid = 36886



UNION ALL 
SELECT b.geom 
FROM buildings b 
WHERE b.residential_status = 'with_residents'

CREATE INDEX ON landuse_residents USING GIST(geom);
CREATE INDEX ON landuse_no_residents USING GIST(geom);

DROP TABLE IF EXISTS gids_contained_residents; 
CREATE TABLE gids_contained_residents AS 
SELECT DISTINCT b.gid   
FROM buildings b, landuse_residents l 
WHERE b.residential_status = 'potential_residents'
AND ST_Intersects(l.geom, b.geom);

ALTER TABLE gids_contained_residents ADD PRIMARY KEY(gid);

UPDATE buildings b
SET residential_status = 'with_residents'
FROM gids_contained_residents g
WHERE b.residential_status = 'potential_residents'
AND b.gid = g.gid;

SELECT b.* 
FROM buildings b, landuse_no_residents l 
WHERE b.residential_status = 'with_residents'
AND ST_Intersects(l.geom, b.geom);


DROP TABLE IF EXISTS gids_intersection; 
CREATE TABLE gids_intersection AS 
SELECT ST_Intersects()
FROM buildings b, landuse_residents l 
WHERE b.residential_status = 'potential_residents'
AND ST_Intersects(l.geom, b.geom)


SELECT * 
FROM buildings 
WHERE residential_status IS NULL 


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

