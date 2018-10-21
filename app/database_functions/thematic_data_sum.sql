CREATE OR REPLACE FUNCTION public.thematic_data_sum(input_objectid integer)
 RETURNS TABLE(gid_isochrone integer, pois_isochrones jsonb)
 LANGUAGE plpgsql
AS $function$
begin
	
with yy as (
with xx as (
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
SELECT p.* FROM (
	SELECT i.gid,count(*),amenity FROM isochrones i, 
	pois p
	WHERE st_intersects(i.geom,p.geom)  AND objectid=input_objectid
	GROUP BY i.gid,amenity
) p ,variable_container
WHERE amenity = any(variable_array)
AND identifier = 'poi_categories'
UNION ALL
SELECT gid,count(*),public_transport_stop
FROM
	(SELECT i.gid, p.name,public_transport_stop,1 as count
	FROM public_transport_stops p, isochrones i
	WHERE st_intersects(i.geom,p.geom)
	AND i.objectid = input_objectid
	GROUP BY i.gid,public_transport_stop,p.name) p
GROUP BY gid,public_transport_stop)
update isochrones set sum_pois = jsonb_object::text 
FROM (
SELECT gid,jsonb_object(array_agg(pois_type),array_agg(count::text)) FROM yy
GROUP BY gid) x 
WHERE isochrones.gid = x.gid;
END ;
$function$
