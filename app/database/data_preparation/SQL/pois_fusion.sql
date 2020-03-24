ALTER TABLE custom_pois ADD gid int4 NOT NULL DEFAULT nextval('pois_gid_seq'::regclass);
CREATE INDEX IF NOT EXISTS custom_pois_idx ON custom_pois USING btree(gid);

-- 01. Change coordinate system of custom_pois

ALTER TABLE custom_pois
	ALTER COLUMN geom TYPE
	geometry(point, 4326)
	USING ST_Transform(geom,4326);

CREATE OR REPLACE FUNCTION pois_fusion(value integer)
	RETURNS integer 
	LANGUAGE plpgsql
AS $function$
DECLARE
	curamenity text;
	curname text;
	counter integer := 1;
	rowrec record;
	duplicate_gids integer[];
BEGIN
	FOR rowrec IN SELECT DISTINCT lower(stand_name) AS name, lower(amenity) AS amenity FROM custom_pois LOOP
		curamenity = rowrec.amenity;
		curname = rowrec.name;
		
		-- 01.01. CREATE TEMP TABLE FOR ALL POIS THAT ARE MATCHING THE pois_search_condition AND DELETE THOSE FROM POIS

		DROP TABLE IF EXISTS pois_case;
		CREATE TEMP TABLE pois_case (LIKE pois INCLUDING ALL);
		INSERT INTO pois_case 
		SELECT *
		FROM pois p WHERE lower(p.amenity) = rowrec.amenity 
		AND lower(p.name) 
		LIKE ANY (
			SELECT jsonb_array_elements_text((select_from_variable_container_o('pois_search_conditions')->rowrec.amenity->rowrec.name)::jsonb)
			FROM select_from_variable_container_o('pois_search_conditions')
		);

		DELETE FROM pois p 
		WHERE lower(p.amenity) = rowrec.amenity 
		AND lower(p.name) LIKE ANY (
			SELECT jsonb_array_elements_text((select_from_variable_container_o('pois_search_conditions')->rowrec.amenity->rowrec.name)::jsonb)
			FROM select_from_variable_container_o('pois_search_conditions')
		);

		-- 01.02. FILTER CASES FOR EACH AMENITY TYPE AND AMENITY NAME IN CUSTOM POIS
		
		DROP TABLE IF EXISTS cus_pois_case;
		CREATE TEMP TABLE cus_pois_case (LIKE custom_pois INCLUDING ALL);
		INSERT INTO cus_pois_case 
		SELECT * 
		FROM custom_pois 
		WHERE lower(amenity) = rowrec.amenity AND lower(stand_name) LIKE '%' || rowrec.name ||'%';

		--02. Data fusion cases
		--02.01. Case 01: Duplicates in OSM, delete duplicates
		--locate and extract duplicates from pois_case
		
		DROP TABLE IF EXISTS pois_case_00_duplicates;
		CREATE TEMP TABLE pois_case_00_duplicates (LIKE pois_case INCLUDING ALL);
		ALTER TABLE pois_case_00_duplicates ADD osm_id_2 bigint;
		ALTER TABLE pois_case_00_duplicates ADD distance real;
	
		INSERT INTO pois_case_00_duplicates 
		SELECT o.*, p.osm_id,
			ST_Distance(o.geom,p.geom) AS distance
		FROM pois_case o
		JOIN pois_case p
		ON ST_DWithin( o.geom::geography, p.geom::geography, select_from_variable_container_s('duplicated_lookup_radius')::float)
		AND NOT ST_DWithin(o.geom, p.geom, 0);

		-- Delete cases where st_distance = duplicate
		
		DELETE FROM
			pois_case_00_duplicates a
		USING pois_case_00_duplicates b
		WHERE
			a.osm_id > b.osm_id
			AND a.distance = b.distance;
	
		-- Delete duplicated register in pois_case
		
		DELETE FROM pois_case WHERE gid = ANY (SELECT gid FROM pois_case_00_duplicates);

		--02.02. Case 02: Duplicates in custom pois, delete duplicates 
		--locate and extract duplicates from cus_pois_case
--check join		
		DROP TABLE IF EXISTS cus_pois_c00_duplicate;
		CREATE TEMP TABLE cus_pois_c00_duplicate (LIKE cus_pois_case INCLUDING ALL);
		ALTER TABLE cus_pois_c00_duplicate ADD distance real;
		INSERT INTO cus_pois_c00_duplicate 
		SELECT o.* AS source_id,
			ST_Distance(o.geom,p.geom) AS distance
		FROM cus_pois_case o
		JOIN cus_pois_case p
		ON ST_DWithin( o.geom::geography, p.geom::geography, select_from_variable_container_s('duplicated_lookup_radius')::float)
		AND NOT ST_DWithin(o.geom, p.geom, 0);
--check join
		-- Delete cases where st_distance = duplicate
		
		DELETE FROM
			cus_pois_c00_duplicate a
			USING cus_pois_c00_duplicate b
		WHERE
			a.gid > b.gid
			AND a.distance = b.distance;
		ALTER TABLE cus_pois_c00_duplicate DROP COLUMN distance;
		
		-- Delete duplicated register in cus_pois_case
		DELETE FROM cus_pois_case WHERE gid = ANY (SELECT gid FROM cus_pois_c00_duplicate);
	
		--02.03. Case 03: Join opening hours from custom to osm
			
		DROP TABLE IF EXISTS pois_case_op_hours;
		CREATE TEMP TABLE pois_case_op_hours (LIKE pois_case INCLUDING ALL);
		ALTER TABLE pois_case_op_hours ADD opening_hours_custom varchar;
--
		INSERT INTO pois_case_op_hours
		SELECT p.*, vertices.opening_hours AS custom_opening_hours
			FROM pois_case p
			CROSS JOIN LATERAL
			(SELECT c.geom, c.gid, c.opening_hours
			FROM cus_pois_case c
			WHERE c.geom && ST_Buffer(p.geom, select_from_variable_container_s('tag_new_radius')::float)
			ORDER BY
			p.geom <-> c.geom
			LIMIT 1	) AS vertices;		

		UPDATE pois_case_op_hours SET opening_hours = opening_hours_custom
		WHERE opening_hours IS NULL AND opening_hours_custom <>'None';
-- Improve this section
		
		DROP TABLE IF EXISTS pois_case;
		CREATE TABLE pois_case (LIKE pois_case_op_hours INCLUDING ALL);
		
		INSERT INTO pois_case
		SELECT * FROM pois_case_op_hours;
	
-- end improve
		--02.04. Case 2: Add new points from custom_pois to OSM	
		DROP TABLE IF EXISTS custom_new_pois;
		CREATE TEMP TABLE custom_new_pois (LIKE cus_pois_case INCLUDING ALL);

		INSERT INTO custom_new_pois
		SELECT *
		FROM cus_pois_case
		EXCEPT
		SELECT c.*
		FROM pois_case p, cus_pois_case c
		WHERE ST_INTERSECTS( c.geom, ST_Buffer(p.geom::geography, select_from_variable_container_s('tag_new_radius')::float)::geometry);
	
		INSERT INTO pois_case (geom, opening_hours, amenity, name )
			SELECT geom, opening_hours, amenity, stand_name
			FROM  custom_new_pois;

		--03. Append back to case

		INSERT INTO pois (osm_id , origin_geometry,"access", housenumber, amenity, origin , organic ,denomination ,brand ,"name" ,"operator" , public_transport, railway, religion, opening_hours,"ref", tags, geom, wheelchair )
		SELECT osm_id , origin_geometry,"access", housenumber, amenity, origin , organic ,denomination ,brand ,"name" ,"operator" , public_transport, railway, religion, opening_hours,"ref", tags, geom, wheelchair
		FROM pois_case;

	END LOOP;
RETURN counter;
END;
$function$

SELECT pois_fusion(1);
SELECT count(gid) AS counter FROM pois;

--SELECT * FROM pois_case;
--DROP TABLE IF EXISTS pois_targets;

--Restore
--DELETE FROM pois;

--INSERT INTO pois 
--SELECT * FROM pois_backup;

--
-- Backup
--CREATE TABLE pois_backup (LIKE pois INCLUDING all);

--INSERT INTO pois_backup
--SELECT * FROM pois;
--SELECT count(gid) FROM pois_backup;
