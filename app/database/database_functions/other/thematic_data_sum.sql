DROP FUNCTION IF EXISTS thematic_data_sum;
CREATE OR REPLACE FUNCTION public.thematic_data_sum(input_objectid integer, userid_input integer, modus integer)
 RETURNS TABLE(gid_isochrone integer, pois_isochrones jsonb)
 LANGUAGE plpgsql
AS $function$
DECLARE 
	pois_one_entrance text[] := select_from_variable_container('pois_one_entrance');
	pois_more_entrances text[] := select_from_variable_container('pois_more_entrances');
	excluded_pois_id integer[];
BEGIN 


IF modus IN(2,4) THEN
	excluded_pois_id = ids_modified_features(userid_input,'pois');
ELSE 
	excluded_pois_id = ARRAY[]::integer[];
	userid_input = 1;
END IF;

WITH yy AS (
	WITH xx AS (
		SELECT a.gid,sum(a.population)::integer+(5-(sum(a.population)::integer%5)) as sum_pop 
		FROM
		(	
			SELECT p.population,i.gid 
	     	FROM population p, isochrones i
	     	WHERE objectid = input_objectid 
	     	AND st_intersects(i.geom,p.geom)
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
	AND (p.userid = userid_input OR p.userid IS NULL)
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
		AND (p.userid = userid_input OR p.userid IS NULL)
		AND p.gid NOT IN (SELECT UNNEST(excluded_pois_id))
		GROUP BY i.gid,amenity,p.name) p
	GROUP BY gid,amenity
)
UPDATE isochrones SET sum_pois = jsonb_object::text 
FROM (
SELECT gid,jsonb_object(array_agg(pois_type),array_agg(count::text)) FROM yy
GROUP BY gid) x 
WHERE isochrones.gid = x.gid;
--Fill population column
UPDATE isochrones 
SET population = (sum_pois::jsonb->>'population')::integer 
WHERE objectid = input_objectid 
AND sum_pois::jsonb->>'population' IS NOT NULL;

END ;
$function$