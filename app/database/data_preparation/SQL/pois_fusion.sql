
--SELECT * FROM pois;
--SELECT * FROM variable_container vc;
--SELECT * FROM custom_pois;
SELECT * FROM variable_container vc;
-- 01. Select unique amenities and names
ALTER TABLE custom_pois ADD gid int4 NOT NULL DEFAULT nextval('pois_gid_seq'::regclass);

DROP TABLE IF EXISTS pois_targets;
CREATE INDEX IF NOT EXISTS custom_pois_idx ON custom_pois USING btree(gid);
SELECT DISTINCT lower(stand_name) AS name, lower(amenity) AS amenity INTO pois_targets FROM custom_pois WHERE stand_name='raiffeisenbank';
SELECT * FROM pois_targets;

-- 02. Change coordinate system of custom_pois

ALTER TABLE custom_pois
	ALTER COLUMN geom TYPE
	geometry(point, 4326)
	USING ST_Transform(geom,4326);

SELECT pois_fussion(1);

-- 03. Clip custom pois to study area

DROP TABLE IF EXISTS custom_pois_clip;
CREATE TABLE custom_pois_clip (LIKE custom_pois INCLUDING ALL);
INSERT INTO custom_pois_clip
	SELECT p.* FROM custom_pois p
	WHERE ST_Intersects((SELECT ST_Buffer(geom::geography, 1000) FROM study_area_union), p.geom);

-- 04. Loop execution
-- 02. Loop 

CREATE OR REPLACE FUNCTION pois_fussion(value integer)
	RETURNS integer 
	LANGUAGE plpgsql
AS $function$
DECLARE
	curamenity TEXT;
	curname TEXT;
	counter INTEGER := 1;
	rowrec record;
BEGIN
	FOR rowrec IN SELECT pt.amenity, pt.name FROM pois_targets pt LOOP
		curamenity=rowrec.amenity;
		curname = rowrec.name;
		
		-- 01.01. FILTER CASES FOR EACH AMENITY TYPE AND AMENITY NAME IN POIS
		
		--SELECT *
		--FROM pois
		--WHERE lower(name) LIKE ANY(SELECT jsonb_array_elements_text((select_from_variable_container_o ->> 'edeka')::jsonb)
		--FROM select_from_variable_container_o('pois_search_conditions')
		--)
		--AND amenity = 'supermarket';	
	
		DROP TABLE IF EXISTS pois_case;
		CREATE TABLE pois_case (LIKE pois INCLUDING ALL);
		INSERT INTO pois_case SELECT *
			FROM pois p WHERE lower(p.amenity) = rowrec.amenity AND lower(p.name) LIKE ANY (SELECT jsonb_array_elements_text((select_from_variable_container_o ->> rowrec.name)::jsonb)
			FROM select_from_variable_container_o('pois_search_conditions'));
		
		DELETE FROM pois p WHERE lower(p.amenity) = rowrec.amenity AND lower(p.name) LIKE ANY (SELECT jsonb_array_elements_text((select_from_variable_container_o ->> rowrec.name)::jsonb)
			FROM select_from_variable_container_o('pois_search_conditions'));
		
--		SELECT * FROM pois p WHERE lower(p.amenity) = rowrec.amenity AND lower(p.name) LIKE '%' || rowrec.name ||'%';

--		DELETE FROM pois p WHERE lower(p.amenity) = rowrec.amenity AND lower(p.name) LIKE '%' || rowrec.name ||'%';
		
		-- 01.02. FILTER CASES FOR EACH AMENITY TYPE AND AMENITY NAME IN CUSTOM POIS
		
		DROP TABLE IF EXISTS cus_pois_clip_case;
		CREATE TABLE cus_pois_clip_case (LIKE custom_pois_clip INCLUDING ALL);
		INSERT INTO cus_pois_clip_case SELECT * FROM custom_pois_clip WHERE lower(amenity) = rowrec.amenity AND lower(name) LIKE '%' || rowrec.name ||'%';

--		DELETE FROM pois WHERE amenity = 'supermarket' AND name LIKE '%Rewe%';
--		SELECT count(amenity) FROM pois;
--		INSERT INTO cus_pois_clip_case SELECT * FROM custom_pois_clip WHERE lower(amenity) = 'supermarket' AND lower(name) LIKE '%rewe%';
--		INSERT INTO pois_case SELECT * FROM pois p WHERE lower(p.amenity) = 'supermarket' AND lower(p.name) LIKE '%rewe%';

		--02. Data fusion cases
		--02.01. Case 01: Duplicates in OSM, delete duplicates
		--locate and extract duplicates from pois_case
		
		DROP TABLE IF EXISTS pois_case_00_duplicates;
		CREATE TABLE pois_case_00_duplicates (LIKE pois_case INCLUDING ALL);
		ALTER TABLE pois_case_00_duplicates ADD osm_id_2 bigint;
		ALTER TABLE pois_case_00_duplicates ADD distance real;
	
		INSERT INTO pois_case_00_duplicates SELECT o.*, p.osm_id,
			ST_Distance(o.geom,p.geom) AS distance
		FROM pois_case o
		JOIN pois_case p
		ON ST_DWithin( o.geom::geography, p.geom::geography, select_from_variable_container_s('duplicated_lookup_radius')::float)
		AND NOT ST_DWithin(o.geom, p.geom, 0);
--		SELECT * FROM pois_case_00_duplicates;
--		SELECT * FROM pois_case;

		--delete duplicates from pois_case

		DELETE FROM pois_case WHERE geom = ANY(
			SELECT	p.geom
			FROM pois_case o
			JOIN pois_case p
			ON ST_DWithin( o.geom::geography, p.geom::geography, select_from_variable_container_s('duplicated_lookup_radius')::float)
			AND NOT ST_DWithin(o.geom, p.geom, 0));

		-- Delete cases where st_distance = duplicate
		
		DELETE FROM
			pois_case_00_duplicates a
		USING pois_case_00_duplicates b
		WHERE
			a.osm_id > b.osm_id
			AND a.distance = b.distance;
		ALTER TABLE pois_case_00_duplicates DROP COLUMN distance;
		ALTER TABLE pois_case_00_duplicates DROP COLUMN osm_id_2;
	
		-- append back in pois_case
	
		INSERT INTO pois_case
			SELECT * FROM  pois_case_00_duplicates;
	
		--02.02. Case 02: Duplicates in custom pois, delete duplicates 
		--locate and extract duplicates from cus_pois_clip_case
		
		DROP TABLE IF EXISTS cus_pois_c00_duplicate;
		CREATE TABLE cus_pois_c00_duplicate (LIKE cus_pois_clip_case INCLUDING ALL);
		ALTER TABLE cus_pois_c00_duplicate ADD distance real;
--		SELECT * FROM cus_pois_clip_case;
--		SELECT * FROM cus_pois_c00_duplicate;
		INSERT INTO cus_pois_c00_duplicate 
		SELECT o.* AS source_id,
			ST_Distance(o.geom,p.geom) AS distance
		FROM cus_pois_clip_case o
		JOIN cus_pois_clip_case p
		ON ST_DWithin( o.geom::geography, p.geom::geography, select_from_variable_container_s('duplicated_lookup_radius')::float)
		AND NOT ST_DWithin(o.geom, p.geom, 0);
	
		-- Delete cases where st_distance = duplicate
		
		DELETE FROM
			cus_pois_c00_duplicate a
			USING cus_pois_c00_duplicate b
		WHERE
			a.gid > b.gid
			AND a.distance = b.distance;
		ALTER TABLE cus_pois_c00_duplicate DROP COLUMN distance;
		
		-- append back in pois_case
	
		INSERT INTO cus_pois_clip_case
			SELECT * FROM  cus_pois_c00_duplicate;

		--02.03. Case 03: Join opening hours from custom to osm
		

			
		DROP TABLE IF EXISTS pois_case_op_hours;
		CREATE TABLE pois_case_op_hours (LIKE pois_case INCLUDING ALL);
		ALTER TABLE pois_case_op_hours ADD opening_ho varchar;
--		SELECT * FROM pois_case;
		
		INSERT INTO pois_case_op_hours
		SELECT p.*, c.opening_hours
			FROM pois_case p
			LEFT OUTER JOIN cus_pois_clip_case c
			ON ST_INTERSECTS(c.geom, ST_Buffer(p.geom::geography, select_from_variable_container_s('tag_new_radius')::float)::geometry)
			ORDER BY c.opening_hours;
		SELECT * FROM pois;
--		SELECT osm_id, count(osm_id)FROM pois_case_op_hours GROUP BY osm_id ORDER BY count(osm_id) DESC ;
--		SELECT * FROM pois_case_op_hours WHERE osm_id = 1741333377 OR osm_id = 3110157711;

		UPDATE pois_case_op_hours SET opening_hours = opening_ho
			WHERE opening_hours IS NULL;
		
		DROP TABLE IF EXISTS pois_case;
		CREATE TABLE pois_case (LIKE pois_case_op_hours INCLUDING ALL);
		
		INSERT INTO pois_case
		SELECT * FROM pois_case_op_hours;

		--02.04. Case 2: Add new points from custom_pois to OSM	
		DROP TABLE IF EXISTS custom_new_pois;
		CREATE TABLE custom_new_pois (LIKE cus_pois_clip_case INCLUDING ALL);

		INSERT INTO custom_new_pois
		SELECT *
		FROM cus_pois_clip_case
		EXCEPT
		SELECT c.*
		FROM pois_case p, cus_pois_clip_case c
		WHERE ST_INTERSECTS( c.geom, ST_Buffer(p.geom::geography, select_from_variable_container_s('tag_new_radius')::float)::geometry);
		
--		SELECT * FROM custom_new_pois;
--		SELECT * FROM pois_case;
		
		INSERT INTO pois_case (geom, opening_hours, amenity, name )
			SELECT geom, opening_hours, amenity, name
			FROM  custom_new_pois;
		

		ALTER TABLE pois_case DROP COLUMN opening_ho;
		--03. Append back to case

		INSERT INTO pois (osm_id , orgin_geometry,"access", housenumber, amenity, origin , organic ,denomination ,brand ,"name" ,"operator" , public_transport, railway, religion, opening_hours,"ref", tags, geom, wheelchair )
		SELECT osm_id , orgin_geometry,"access", housenumber, amenity, origin , organic ,denomination ,brand ,"name" ,"operator" , public_transport, railway, religion, opening_hours,"ref", tags, geom, wheelchair
		FROM pois_case;
		
--		SELECT * FROM pois;
	
		--04. Delete tables used in the loop
		DROP TABLE IF EXISTS pois_case;
		DROP TABLE IF EXISTS custom_pois_clip_case;
		DROP TABLE IF EXISTS pois_case_00_duplicates;
		DROP TABLE IF EXISTS cus_pois_c00_duplicate;
		DROP TABLE IF EXISTS custom_new_pois;
		DROP TABLE IF EXISTS cus_pois_clip_case;
		DROP TABLE IF EXISTS pois_case_op_hours;
	END LOOP;
RETURN counter;
END;
$function$

SELECT pois_fussion(1);
DROP TABLE IF EXISTS pois_targets;
DROP TABLE IF EXISTS custom_pois_clip;



-- script should stop here!!!!

-- TESTS
	SELECT * FROM variable_container;
	--- simple numbers
SELECT * FROM select_from_variable_container_s('building_types_residential');
SELECT * FROM select_from_variable_container_s('duplicated_lookup_radius');
SELECT * FROM select_from_variable_container_s('tag_new_radius');
	--- variable_object
SELECT * FROM select_from_variable_container_o('max_length_links');
	--- variable_array
SELECT * FROM select_from_variable_container('building_types_residential');

-- FUNCTION TO lookup simmilar in arrays
SELECT jsonb_array_elements((select_from_variable_container_o ->> 'rewe')::jsonb)::text
FROM select_from_variable_container_o('search_conditions');


-- FUNCTION TO lookup similar in arrays (to replace in function)
SELECT *
FROM pois
WHERE lower(name) LIKE ANY(SELECT jsonb_array_elements_text((select_from_variable_container_o ->> 'edeka')::jsonb)
FROM select_from_variable_container_o('pois_search_conditions')
)
AND amenity = 'supermarket';

SELECT * FROM pois WHERE amenity = 'supermarket';

SELECT (jsonb_arr2text_arr((select_from_variable_container_o ->> 'rewe')::jsonb))
FROM select_from_variable_container_o('search_conditions')


-- POIS Backup

DELETE FROM pois;
INSERT INTO pois SELECT * FROM pois_backup;
SELECT count(gid) FROM pois;


SELECT count(gid)FROM pois_backup;


SELECT count(osm_id) FROM pois;
CREATE TABLE pois_backup (LIKE pois INCLUDING all);
INSERT INTO pois_backup SELECT * FROM pois;
SELECT * FROM pois_backup;
SELECT count(gid)FROM pois_backup;

DROP TABLE custom_pois;

--- closest point testing

DROP TABLE IF EXISTS pois_testcase_dm;
DROP TABLE IF EXISTS custom_pois_testcase_dm;

SELECT * INTO pois_testcase_dm FROM pois p WHERE amenity='chemist' AND lower(name) LIKE 'dm' AND (ST_Intersects((SELECT ST_Buffer(s.geom::geometry, 1000) FROM study_area_union s), p.geom)) ;
SELECT * INTO custom_pois_testcase_dm FROM custom_pois_clip WHERE amenity ='chemist' AND lower(stand_name)= 'dm';

-- identify closer points

SELECT st_shortestline(p.geom, c.geom), p.gid AS gid_pois, c.gid AS gid_custom, st_length(st_shortestline(p.geom, c.geom)::geography) AS len 
	INTO tag_lines FROM pois_testcase_dm p, custom_pois_testcase_dm c 
	WHERE ST_DWithin (p.geom::geography, c.geom::geography, 130) ORDER BY gid_custom, len;

-- identify duplicates 
HAVING count(gid_custom)>1
SELECT gid_custom, count(gid_custom) FROM tag_lines GROUP BY gid_custom  ORDER BY gid_custom;
SELECT gid_custom, count(gid_custom), len FROM tag_lines GROUP BY gid_custom, len ORDER BY gid_custom;

DELETE FROM 
	tag_lines a
		USING tag_lines b
WHERE 
	a.len>b.len
	AND (a.gid_pois = b.gid_pois);
--tag lines contains the lines that have to be updated in pois for a specific amenity, 

-- next step, join using gid_custom
-- tag opening hours
-- replace in database

SELECT * FROM tag_lines ORDER BY gid_pois;
SELECT * FROM pois_testcase_dm;
SELECT * FROM custom_pois_testcase_dm;

DROP TABLE IF EXISTS tag_lines;
SELECT * FROM pois_testcase_dm;