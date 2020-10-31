DROP FUNCTION IF EXISTS export_changeset_scenario;
CREATE OR REPLACE FUNCTION public.export_changeset_scenario(scenario_id_input integer)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE 
	pois_json jsonb;
	ways_json jsonb;
	buildings_json jsonb;
	buildings_entrances_json jsonb;
	all_layers_json jsonb = '{}';
	deleted_buildings_ids integer[];
BEGIN 
	
	SELECT create_geojson(array_agg(to_jsonb(x) - 'geom'), array_agg(geom))
	INTO pois_json
	FROM 
	(
		SELECT name, amenity, opening_hours, wheelchair, geom,
		CASE WHEN original_id IS NULL THEN 'new' ELSE 'new_modified' END AS edit_type, original_id 
		FROM pois_modified pm 
		WHERE scenario_id = scenario_id_input
		UNION ALL 
		SELECT name, amenity, opening_hours, wheelchair, geom, d.edit_type, p.gid AS original_id
		FROM pois_userinput p, get_ids_modified_export(scenario_id_input,'pois') d
		WHERE p.gid = d.gid
	) x; 
	
	SELECT create_geojson(array_agg(to_jsonb(x) - 'geom'), array_agg(geom))
	INTO ways_json
	FROM 
	(
		SELECT way_type, surface, wheelchair, lit, street_category, foot, bicycle, geom,  
		CASE WHEN original_id IS NULL THEN 'new' ELSE 'new_modified' END AS edit_type, original_id 
		FROM ways_modified pm 
		WHERE scenario_id = scenario_id_input
		UNION ALL 
		SELECT 'road' AS way_type, surface, wheelchair, lit, class_id::text, foot, bicycle, geom, d.edit_type, p.id AS original_id
		FROM ways_userinput p, get_ids_modified_export(scenario_id_input,'ways') d
		WHERE p.id = d.gid 
	) x; 

	SELECT deleted_buildings 
	INTO deleted_buildings_ids
	FROM scenarios 
	WHERE scenario_id = scenario_id_input;

	SELECT create_geojson(array_agg(to_jsonb(x) - 'geom'), array_agg(geom))
	INTO buildings_json
	FROM 
	(

		SELECT building, building_levels, building_levels_residential, gross_floor_area, population, geom, 'new' AS edit_type, original_id 
		FROM buildings_modified
		WHERE scenario_id = scenario_id_input
		UNION ALL 
		SELECT b.building, b.building_levels, b.building_levels_residential, b.area*b.building_levels_residential AS gross_floor_area, 
		sum(p.population) AS population, b.geom, 'deleted' AS edit_type, b.gid AS original_id 
		FROM buildings b, population_userinput p  
		WHERE scenario_id IS NULL 
		AND ST_Intersects(b.geom,p.geom)
		AND b.gid IN (SELECT UNNEST(deleted_buildings_ids))
		GROUP BY b.gid
	) x;
	
	SELECT create_geojson(array_agg(to_jsonb(x) - 'geom'), array_agg(geom))
	INTO buildings_entrances_json
	FROM 
	(
		SELECT population, geom  
		FROM population_userinput
		WHERE scenario_id = scenario_id_input 
	) x; 

	all_layers_json = append_geojson(all_layers_json, pois_json, 'pois');
	all_layers_json = append_geojson(all_layers_json, ways_json, 'ways');
	all_layers_json = append_geojson(all_layers_json, buildings_json, 'buildings');
	all_layers_json = append_geojson(all_layers_json, buildings_entrances_json, 'buildings_entrances');

	RETURN all_layers_json;  
END;
$function$

/*SELECT export_changeset_scenario(15) ->> 'pois'*/
