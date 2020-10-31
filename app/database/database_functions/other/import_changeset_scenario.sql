DROP FUNCTION IF EXISTS import_changeset_scenario;
CREATE OR REPLACE FUNCTION public.import_changeset_scenario(scenario_id_input integer, userid_input integer, import_object jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE 
	attr_object jsonb := '{
	"pois":["name","amenity","opening_hours","wheelchair","original_id","edit_type"],
	"ways":["lit","foot","bicycle","surface","way_type","wheelchair","street_category","original_id","edit_type"],
	"buildings": ["building","population","building_levels","gross_floor_area","building_levels_residential","original_id","edit_type"],
	"buildings_entrances": ["population"]
	}'::jsonb;
	attr TEXT;
	sql_attr TEXT := '';
	layer TEXT := jsonb_object_keys(import_object)::text;
	layer_object jsonb;
	sql_import_table text;
	sql_update_deleted TEXT;
	pois_json jsonb;
	ways_json jsonb;
	buildings_json jsonb;
	buildings_entrances_json jsonb;
	all_layers_json jsonb := '{}';
BEGIN 
	
	IF (SELECT scenario_id FROM scenarios WHERE scenario_id = scenario_id_input) IS NULL THEN 
		INSERT INTO scenarios(scenario_id,userid) VALUES (scenario_id_input,userid_input);
	END IF;
	

	FOR attr IN SELECT jsonb_array_elements_text(attr_object -> layer)
	LOOP
		sql_attr = sql_attr || format('feat->''properties'' ->> ''%1$s'' AS %1$s,',attr);
	END LOOP;
	
	DROP TABLE IF EXISTS temp_features;
	CREATE TEMP TABLE temp_features AS 
	SELECT jsonb_array_elements(import_object -> layer -> 'features') AS feat;

	sql_import_table = format('DROP TABLE IF EXISTS import_%1$s; 
	CREATE TEMP TABLE import_%1$s AS 
	SELECT
	  row_number() OVER () AS gid, %2$s  NULL AS new_original_id,
	  ST_SETSRID(ST_GeomFromGeoJSON(feat->>''geometry''),4326) AS geom, %3$s scenario_id
	FROM (
	  SELECT * FROM temp_features
	) AS f;
	ALTER TABLE import_%1$s ADD PRIMARY KEY(gid);', layer, sql_attr, scenario_id_input);
	
	EXECUTE sql_import_table;

	/*#######################################################################*/
	/*Inject POIs*/
	/*#######################################################################*/
	IF layer = 'pois' THEN 
		UPDATE import_pois i 
		SET new_original_id = u.new_original_id 
		FROM (
			SELECT p.gid AS new_original_id, original_id
			FROM pois_userinput p, import_pois i  
			WHERE p.amenity = i.amenity 
			AND p.name = i.name 
			AND i.edit_type IN ('old_modified', 'deleted') 
			AND ST_EQUALS(ST_ASTEXT(ST_QuantizeCoordinates(p.geom,6)),ST_ASTEXT(ST_QuantizeCoordinates(i.geom,6)))
			AND p.geom && i.geom
		) u
		WHERE i.original_id = u.original_id
		AND i.edit_type IN ('old_modified', 'deleted', 'new_modified'); 
		
		DROP TABLE IF EXISTS import_pois_gid;
		CREATE TEMP TABLE import_pois_gid AS 
		WITH new_with_gid AS 
		(
			INSERT INTO pois_modified(name,amenity,opening_hours,wheelchair,geom,scenario_id, original_id) 
			SELECT i.name,i.amenity,i.opening_hours,i.wheelchair,i.geom,i.scenario_id, i.new_original_id::integer  
			FROM import_pois i
			WHERE edit_type = 'new'
			RETURNING gid,name,amenity,opening_hours,wheelchair,geom,scenario_id,original_id
		), 
		new_modified_with_gid AS 
		(
			INSERT INTO pois_modified(name,amenity,opening_hours,wheelchair,geom,scenario_id, original_id) 
			SELECT i.name,i.amenity,i.opening_hours,i.wheelchair,i.geom,i.scenario_id, i.new_original_id::integer  
			FROM import_pois i		
			WHERE edit_type = 'new_modified' 
			AND new_original_id IS NOT NULL
			RETURNING gid,name,amenity,opening_hours,wheelchair,geom,scenario_id,original_id
		)
		SELECT gid,name,amenity,opening_hours,wheelchair,'new' AS edit_type,geom,scenario_id,original_id,'successful' AS upload_status 
		FROM new_with_gid
		UNION ALL
		SELECT gid,name,amenity,opening_hours,wheelchair,'new_modified' AS edit_type,geom,scenario_id,original_id,'successful' AS upload_status 
		FROM new_modified_with_gid
		UNION ALL 
		SELECT new_original_id::integer AS gid, name,amenity,opening_hours,wheelchair,edit_type,geom,scenario_id::integer,new_original_id::integer, 
		CASE WHEN new_original_id IS NOT NULL THEN 'successful' ELSE 'not_successful' END AS upload_status 
		FROM import_pois
		WHERE edit_type = 'deleted'
		UNION ALL 
		SELECT new_original_id::integer AS gid, name,amenity,opening_hours,wheelchair,edit_type,geom,scenario_id::integer,new_original_id::integer, 
		CASE WHEN new_original_id IS NOT NULL THEN 'successful' ELSE 'not_successful' END AS upload_status 
		FROM import_pois
		WHERE edit_type = 'old_modified';

		SELECT create_geojson(array_agg(to_jsonb(import_pois_gid) - 'geom'), array_agg(geom))
		INTO pois_json
		FROM import_pois_gid;
	
		all_layers_json = append_geojson(all_layers_json, pois_json, 'pois');
	
	/*#######################################################################*/
	/*Inject Ways*/
	/*#######################################################################*/
	ELSEIF layer = 'ways' THEN 
	
		UPDATE import_ways i 
		SET new_original_id = u.new_original_id 
		FROM (
			SELECT p.id AS new_original_id, i.original_id
			FROM ways_userinput p, import_ways i  
			WHERE i.edit_type IN ('old_modified', 'deleted') 
			AND ST_EQUALS(ST_ASTEXT(ST_QuantizeCoordinates(p.geom,6)),ST_ASTEXT(ST_QuantizeCoordinates(i.geom,6)))
			AND p.geom && i.geom
		) u
		WHERE i.original_id = u.original_id
		AND i.edit_type IN ('old_modified', 'deleted', 'new_modified'); 
	
		DROP TABLE IF EXISTS import_ways_gid;
		CREATE TEMP TABLE import_ways_gid AS 
		WITH new_with_gid AS 
		(
			INSERT INTO ways_modified(lit,foot,bicycle,surface,way_type,wheelchair,street_category,geom,scenario_id, original_id) 
			SELECT lit, foot, bicycle, surface, way_type, wheelchair, street_category, geom, scenario_id, new_original_id::integer  
			FROM import_ways 
			WHERE edit_type = 'new'
			RETURNING gid,lit, foot, bicycle, surface, way_type, wheelchair, street_category, geom, scenario_id, original_id
		), 
		new_modified_with_gid AS 
		(
			INSERT INTO ways_modified(lit,foot,bicycle,surface,way_type,wheelchair,street_category,geom,scenario_id, original_id) 
			SELECT lit, foot, bicycle, surface, way_type, wheelchair, street_category, geom, scenario_id, original_id::integer  
			FROM import_ways 	 
			WHERE edit_type = 'new_modified' 
			AND new_original_id IS NOT NULL
			RETURNING gid,lit, foot, bicycle, surface, way_type, wheelchair, street_category, geom, scenario_id, original_id
		)
		SELECT gid, lit, foot, bicycle, surface, way_type, wheelchair, street_category, geom,
		'new' AS edit_type, scenario_id, original_id::integer, 'successful' AS upload_status  
		FROM new_with_gid
		UNION ALL
		SELECT gid, lit, foot, bicycle, surface, way_type, wheelchair, street_category, geom,
		'new_modified' AS edit_type, scenario_id, original_id::integer,'successful' AS upload_status   
		FROM new_modified_with_gid
		UNION ALL 
		SELECT original_id::integer AS gid, lit, foot, bicycle, surface, way_type, wheelchair, street_category, geom,
		'deleted' AS edit_type, scenario_id, new_original_id::integer,
		CASE WHEN new_original_id IS NOT NULL THEN 'successful' ELSE 'not_successful' END AS upload_status 
		FROM import_ways
		WHERE edit_type = 'deleted'
		UNION ALL 
		SELECT original_id::integer AS gid, lit, foot, bicycle, surface, way_type, wheelchair, street_category, geom,
		'old_modified' AS edit_type, scenario_id, new_original_id::integer,
		CASE WHEN new_original_id IS NOT NULL THEN 'successful' ELSE 'not_successful' END AS upload_status 
		FROM import_ways
		WHERE edit_type = 'old_modified';
	
		SELECT create_geojson(array_agg(to_jsonb(import_ways_gid) - 'geom'), array_agg(geom))
		INTO ways_json
		FROM import_ways_gid;
	
		all_layers_json = append_geojson(all_layers_json, ways_json, 'ways');	
	
	/*#######################################################################*/
	/*Inject Buildings*/
	/*#######################################################################*/
	ELSEIF layer = 'buildings' THEN
	
		UPDATE import_buildings i 
		SET new_original_id = u.new_original_id 
		FROM (
			SELECT p.gid AS new_original_id, i.original_id
			FROM buildings p, import_buildings i  
			WHERE i.edit_type IN ('deleted') 
			AND ST_EQUALS(ST_ASTEXT(ST_QuantizeCoordinates(p.geom,6)),ST_ASTEXT(ST_QuantizeCoordinates(i.geom,6)))
			AND p.geom && i.geom
		) u
		WHERE i.original_id = u.original_id
		AND i.edit_type IN ('deleted'); 
	
		DROP TABLE IF EXISTS import_buildings_gid;
		CREATE TEMP TABLE import_buildings_gid AS 
		WITH with_gid AS 
		(
			INSERT INTO buildings_modified(building, population,building_levels,gross_floor_area,building_levels_residential,geom,scenario_id, original_id) 
			SELECT building, population::numeric,building_levels::numeric,gross_floor_area::numeric,building_levels_residential::numeric, geom, i.scenario_id, new_original_id::integer  
			FROM import_buildings i
			WHERE edit_type = 'new'
			RETURNING gid, building, population, building_levels, gross_floor_area, building_levels_residential, geom, scenario_id, original_id
		) 
		SELECT gid, building, population, building_levels, gross_floor_area, building_levels_residential, 'new' AS edit_type, 
		geom, scenario_id, original_id, 'successful' AS upload_status 
		FROM with_gid 
		UNION ALL 
		SELECT new_original_id::integer AS gid, building, population::numeric, building_levels::numeric, gross_floor_area::numeric, building_levels_residential::numeric, 
		'deleted' AS edit_type, geom, scenario_id::integer, original_id::integer,
		CASE WHEN new_original_id IS NOT NULL THEN 'successful' ELSE 'not_successful' END AS upload_status  
		FROM import_buildings i
		WHERE i.edit_type = 'deleted';
	
		SELECT create_geojson(array_agg(to_jsonb(import_buildings_gid) - 'geom'), array_agg(geom))
		INTO buildings_json
		FROM import_buildings_gid;
	
		all_layers_json = append_geojson(all_layers_json, buildings_json, 'buildings');
	
	/*#######################################################################*/
	/*Inject Buildings entrances*/
	/*#######################################################################*/
	ELSEIF layer = 'buildings_entrances' THEN  

		DROP TABLE IF EXISTS import_buildings_entrances_gid;
		CREATE TEMP TABLE import_buildings_entrances_gid AS 
		WITH with_gid AS 
		(
			INSERT INTO population_modified(population,geom,scenario_id) 
			SELECT population::numeric, geom, scenario_id_input 
			FROM import_buildings_entrances
			RETURNING gid, population, geom, scenario_id
		)
		SELECT * FROM with_gid;
		
		UPDATE population_modified p
		SET building_gid = b.gid 
		FROM buildings b 
		WHERE ST_Intersects(b.geom, p.geom)
		AND scenario_id = scenario_id_input 
		AND building_gid IS NULL;  
	
		SELECT create_geojson(array_agg(to_jsonb(x) - 'geom'), array_agg(geom))
		INTO buildings_entrances_json 
		FROM 
		(
			SELECT *, 'successful' AS upload_status
			FROM import_buildings_entrances_gid
		) x; 
		all_layers_json = append_geojson(all_layers_json, buildings_entrances_json, 'buildings_entrances');

	ELSE 
		RAISE NOTICE 'Please pass a valid layer name!';
	END IF;

	IF layer <> 'buildings_entrances' THEN 
		sql_update_deleted = format('UPDATE scenarios s
		SET deleted_%1$s = s.deleted_%1$s || d.deleted_%1$s 
		FROM 
		(
			SELECT array_agg(new_original_id::bigint) AS deleted_%1$s  
			FROM import_%1$s
			WHERE edit_type = ''deleted''
		) d
		WHERE scenario_id = %2$s;',layer,scenario_id_input);
		EXECUTE sql_update_deleted;
	END IF;
	
	RETURN all_layers_json; 

END;
$function$

/*
SELECT import_changeset_scenario(19,42, jsonb_build_object('buildings',export_changeset_scenario(18) -> 'buildings'))
*/