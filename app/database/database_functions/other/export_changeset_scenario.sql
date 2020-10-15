/*This function works for POIs and Ways*/
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
	array_json jsonb = '{}';
BEGIN 
	
	SELECT create_geojson(array_agg(to_jsonb(x) - 'geom'), array_agg(geom))
	INTO pois_json
	FROM 
	(
		SELECT name, amenity, opening_hours, wheelchair, geom,
		CASE WHEN original_id IS NULL THEN 'new' ELSE 'new_modified' END AS edit_type 
		FROM pois_modified pm 
		WHERE scenario_id = scenario_id_input
		UNION ALL 
		SELECT name, amenity, opening_hours, wheelchair, geom, d.edit_type
		FROM pois_userinput p, get_ids_modified_export(scenario_id_input,'pois') d
		WHERE p.gid = d.gid
	) x; 
	
	SELECT create_geojson(array_agg(to_jsonb(x) - 'geom'), array_agg(geom))
	INTO ways_json
	FROM 
	(
		SELECT way_type, surface, wheelchair, lit, street_category, foot, bicycle, geom,  
		CASE WHEN original_id IS NULL THEN 'new' ELSE 'new_modified' END AS edit_type 
		FROM ways_modified pm 
		WHERE scenario_id = scenario_id_input
		UNION ALL 
		SELECT 'road' AS way_type, surface, wheelchair, lit, class_id::text, foot, bicycle, geom, d.edit_type
		FROM ways_userinput p, get_ids_modified_export(scenario_id_input,'ways') d
		WHERE p.id = d.gid 
	) x; 

	SELECT create_geojson(array_agg(to_jsonb(x) - 'geom'), array_agg(geom))
	INTO buildings_json
	FROM 
	(

		SELECT building, building_levels, building_levels_residential, gross_floor_area, population, geom, 'new' AS edit_type  
		FROM buildings_modified
		WHERE scenario_id = scenario_id_input
		UNION ALL 
		SELECT b.building, b.building_levels, b.building_levels_residential, b.area*b.building_levels_residential AS gross_floor_area, 
		sum(p.population) AS population, b.geom, 'deleted' AS edit_type
		FROM buildings b, population_userinput p  
		WHERE scenario_id IS NULL 
		AND ST_Intersects(b.geom,p.geom)
		AND b.gid IN (SELECT UNNEST(deleted_buildings) FROM scenarios WHERE scenario_id = scenario_id_input)
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

	IF pois_json <> '{"type": "FeatureCollection", "features": null}' THEN 
		array_json = array_json || jsonb_build_object('pois',pois_json); 
	END IF;
	
	IF ways_json <> '{"type": "FeatureCollection", "features": null}' THEN 
		array_json = array_json || jsonb_build_object('ways',ways_json); 
	END IF;

	IF buildings_json <> '{"type": "FeatureCollection", "features": null}' THEN 
		array_json = array_json || jsonb_build_object('pois',pois_json); 
	END IF;

	IF buildings_entrances_json <> '{"type": "FeatureCollection", "features": null}' THEN 
		array_json = array_json || jsonb_build_object('buildings_entrances',buildings_entrances_json); 
	END IF;
	
	RETURN array_json;  
END;
$function$


/*SELECT export_changeset_scenario(15) ->> 'pois'*/
