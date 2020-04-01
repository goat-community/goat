CREATE OR REPLACE FUNCTION clean_duplicated_pois(table_name text)
	RETURNS void
	LANGUAGE plpgsql
AS $function$
DECLARE
	radius text := 'duplicated_lookup_radius';
BEGIN
	DROP TABLE IF EXISTS pois_duplicated;
	EXECUTE 'CREATE TEMP TABLE pois_duplicated (LIKE '|| quote_ident(table_name) ||' INCLUDING ALL)';
	ALTER TABLE pois_duplicated ADD distance real;
	EXECUTE 'INSERT INTO pois_duplicated 
			SELECT o.*, ST_Distance(o.geom,p.geom) AS distance
			FROM '|| quote_ident(table_name) ||' o
			JOIN '|| quote_ident(table_name) ||' p
			ON ST_DWithin( o.geom::geography, p.geom::geography, select_from_variable_container_s('|| quote_literal('duplicated_lookup_radius') ||')::float)
			AND NOT ST_DWithin(o.geom, p.geom, 0)';
	DELETE FROM
			pois_duplicated a
			USING pois_duplicated b
		WHERE
			a.gid > b.gid
			AND a.distance = b.distance;
	EXECUTE 'DELETE FROM '||quote_ident(table_name)||' WHERE gid = ANY (SELECT gid FROM pois_duplicated)';
END;
$function$;

CREATE OR REPLACE FUNCTION pois_fusion()
	RETURNS void 
	LANGUAGE plpgsql
AS $function$
DECLARE
	curamenity text;
	curname text;
	dummie TEXT;
	rowrec record;
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

		PERFORM clean_duplicated_pois('pois_case');

		--02.02. Case 02: Duplicates in custom pois, delete duplicates 
		--locate and extract duplicates from cus_pois_case

		PERFORM clean_duplicated_pois('cus_pois_case');		

		--02.03. Case 03: Join opening hours from custom to osm
			
		DROP TABLE IF EXISTS pois_case_op_hours;
		CREATE TEMP TABLE pois_case_op_hours (LIKE pois_case INCLUDING ALL);
		ALTER TABLE pois_case_op_hours ADD opening_hours_custom varchar;
--
		INSERT INTO pois_case_op_hours
		SELECT p.*, vertices.opening_hours AS custom_opening_hours
		FROM pois_case p
		CROSS JOIN LATERAL
		(	
			SELECT c.geom, c.gid, c.opening_hours
			FROM cus_pois_case c
			WHERE c.geom && ST_Buffer(p.geom, select_from_variable_container_s('tag_new_radius')::float)
			ORDER BY
			p.geom <-> c.geom
			LIMIT 1	
		) AS vertices;		

		UPDATE pois_case_op_hours SET opening_hours = opening_hours_custom
		WHERE opening_hours IS NULL AND opening_hours_custom <>'None';
		
		DROP TABLE IF EXISTS pois_case;
		CREATE TABLE pois_case (LIKE pois_case_op_hours INCLUDING ALL);
		
		INSERT INTO pois_case
		SELECT * FROM pois_case_op_hours;
	
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

		--03. Append back to pois

		INSERT INTO pois (osm_id , origin_geometry,"access", housenumber, amenity, origin , organic ,denomination ,brand ,"name" ,"operator" , public_transport, railway, religion, opening_hours,"ref", tags, geom, wheelchair )
		SELECT osm_id , origin_geometry,"access", housenumber, amenity, origin , organic ,denomination ,brand ,"name" ,"operator" , public_transport, railway, religion, opening_hours,"ref", tags, geom, wheelchair
		FROM pois_case;
	END LOOP;

END;
$function$

SELECT pois_fusion();
