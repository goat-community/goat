
DROP FUNCTION IF EXISTS thematic_data_sum;
CREATE OR REPLACE FUNCTION public.thematic_data_sum(input_objectid integer, scenario_id_input integer, modus integer)
 RETURNS SETOF void --TABLE(gid_isochrone integer, pois_isochrones jsonb)
 LANGUAGE plpgsql
AS $function$
DECLARE 
	pois_one_entrance text[] := select_from_variable_container('pois_one_entrance');
	pois_more_entrances text[] := select_from_variable_container('pois_more_entrances');
	excluded_pois_id integer[];
	json_aois jsonb;
BEGIN 

	IF modus IN(2,4) THEN
		excluded_pois_id = ids_modified_features(scenario_id_input,'pois');
	ELSE 
		excluded_pois_id = ARRAY[]::integer[];
	END IF;
	
	IF modus IN(1,3) THEN 
		scenario_id_input = 0;
	END IF; 
	
	--Calculate aoi areas
	DROP TABLE IF EXISTS aois_json;
	CREATE TEMP TABLE aois_json AS 
	WITH area_cnt AS 
	(
		SELECT i.gid, amenity, count(*) as cnt, intersec.area 
		FROM isochrones i, aois a, LATERAL (SELECT ST_Area(st_intersection(i.geom,a.geom)::geography)::integer area) AS intersec  
		WHERE objectid = input_objectid
		AND st_intersects(i.geom,a.geom)
		GROUP BY i.gid, amenity, name, intersec.area
	),
	json_area_cnt AS
	(
		SELECT p.gid, p.amenity, jsonb_build_object('cnt',sum(cnt),'area',sum(area)) AS aois_json
		FROM area_cnt p 
		GROUP BY p.gid, p.amenity
	)
	SELECT gid, jsonb_object_agg(amenity, aois_json) aois_json_agg
	FROM json_area_cnt
	GROUP BY gid; 
	
	--Calculate population and pois
	WITH yy AS (
		WITH xx AS (
			SELECT a.gid,sum(a.population)::integer+(5-(sum(a.population)::integer%5)) as sum_pop 
			FROM
			(	
				SELECT p.population,i.gid 
		     	FROM population_userinput p, isochrones i
		     	WHERE objectid = input_objectid 
		     	AND st_intersects(i.geom,p.geom)
		     	AND (p.scenario_id = scenario_id_input OR p.scenario_id IS NULL) 
		     	AND p.building_gid NOT IN (SELECT UNNEST(deleted_buildings) FROM scenarios WHERE scenario_id = scenario_id_input)	
		     ) 
		     a
		     GROUP BY a.gid
		)
		SELECT gid,sum_pop AS count,'population' AS pois_type FROM xx
		UNION ALL
		SELECT i.gid,count(*),amenity 
		FROM isochrones i, pois_userinput p
		WHERE st_intersects(i.geom,p.geom) 
		AND amenity IN (SELECT UNNEST(pois_one_entrance))
		AND objectid=input_objectid
		AND (p.scenario_id = scenario_id_input OR p.scenario_id IS NULL)
		AND p.gid NOT IN (SELECT UNNEST(excluded_pois_id))
		GROUP BY i.gid,amenity
		UNION ALL
		SELECT gid,count(*),amenity
		FROM
			(SELECT i.gid, p.name,amenity,1 as count
			FROM pois_userinput p, isochrones i
			WHERE st_intersects(i.geom,p.geom)
			AND amenity IN (SELECT UNNEST(pois_more_entrances))
			AND i.objectid = input_objectid
			AND (p.scenario_id = scenario_id_input OR p.scenario_id IS NULL)
			AND p.gid NOT IN (SELECT UNNEST(excluded_pois_id))
			GROUP BY i.gid,amenity,p.name) p
		GROUP BY gid,amenity
	),
	json_amenities AS 
	(
		SELECT yy.gid,jsonb_object(array_agg(yy.pois_type),array_agg(yy.count::text)) AS json_pois
		FROM yy
		GROUP by yy.gid
	)
	UPDATE isochrones i 
	SET sum_pois = m.sum_output::text
	FROM (
		SELECT t.gid, t.json_pois || COALESCE(a.aois_json_agg,'{}'::jsonb) AS sum_output
		FROM json_amenities t
		LEFT JOIN aois_json a 
		ON t.gid = a.gid 
	) m
	WHERE m.gid = i.gid;
	
	--Fill population column
	UPDATE isochrones 
	SET population = (sum_pois::jsonb->>'population')::integer 
	WHERE objectid = input_objectid 
	AND sum_pois::jsonb->>'population' IS NOT NULL;

END ;
$function$
/*SELECT thematic_data_sum(591595094, 0, 1)*/