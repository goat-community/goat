CREATE OR REPLACE FUNCTION pois_fusion()
	RETURNS VOID
	LANGUAGE plpgsql
AS $function$
DECLARE
	curamenity text;
	curname text;
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
		--02.01. Delete duplicates
		--locate and delete duplicates from pois_case

		PERFORM clean_duplicated_pois('pois_case');

		--locate and delete duplicates from cus_pois_case

		PERFORM clean_duplicated_pois('cus_pois_case');		

		--02.02. Join opening hours from custom to osm
			
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
	
		--02.03. Add new points from custom_pois to OSM	

		INSERT INTO pois_case_op_hours (geom, opening_hours, amenity, name )
		SELECT geom, opening_hours, amenity, stand_name
		FROM cus_pois_case
		EXCEPT
		SELECT c.geom, c.opening_hours, c.amenity, c.stand_name
		FROM pois_case_op_hours p, cus_pois_case c
		WHERE ST_INTERSECTS( c.geom, ST_Buffer(p.geom::geography, select_from_variable_container_s('tag_new_radius')::float)::geometry);

		--03. Append back to pois

		INSERT INTO pois (osm_id , origin_geometry,"access", housenumber, amenity, origin , organic ,denomination ,brand ,"name" ,"operator" , public_transport, railway, religion, opening_hours,"ref", tags, geom, wheelchair )
		SELECT osm_id , origin_geometry,"access", housenumber, amenity, origin , organic ,denomination ,brand ,"name" ,"operator" , public_transport, railway, religion, opening_hours,"ref", tags, geom, wheelchair
		FROM pois_case_op_hours;
	END LOOP;
END;
$function$