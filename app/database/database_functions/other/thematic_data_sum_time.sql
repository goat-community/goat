DROP FUNCTION IF EXISTS thematic_data_sum_time;
CREATE OR REPLACE FUNCTION public.thematic_data_sum_time(input_objectid integer, day text, hour text)
 RETURNS TABLE(objectid_out integer, gid_out integer, sum_pois_time_out text)
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
		WHERE st_intersects(i.geom,p.geom)  
		AND objectid=input_objectid
		and amenity in ('convenience','international_supermarket','discount_supermarket','hypermarket','organic','supermarket','bakery','chemist','pharmacy','butcher','restaurant','bar','pub','fast_food','cafe','ice_cream','biergarten','museum','hairdresser','library','beverages','art','books','fuel')
		AND new_opening_hours ->> 'Th' is not null 
		and not (new_opening_hours @> '{"Th": ["closed"]}')
		and 
		((time_range1_th && concat('[2019-01-20 ',hour,', 2019-01-20 ',hour,':01)')::tsrange
		or time_range1_th && concat('[2019-01-20 ',hour,', 2019-01-20 ',hour,':01)')::tsrange)
		or 
		(time_range1_th && concat('[2019-01-21 ',hour,', 2019-01-21 ',hour,':01)')::tsrange
		or 
		time_range2_th && concat('[2019-01-21 ',hour,', 2019-01-21 ',hour,':01)')::tsrange)
		)
		GROUP BY i.gid,amenity
		) p ,variable_container
		WHERE amenity = any(variable_array)
		AND identifier = 'poi_categories'
	)
	update isochrones set sum_pois_time = jsonb_object::text 
	FROM (
	SELECT gid,jsonb_object(array_agg(pois_type),array_agg(count::text)) FROM yy
	GROUP BY gid) x 
	WHERE isochrones.gid = x.gid;
	return query SELECT i.objectid, i.gid, i.sum_pois_time FROM isochrones i WHERE objectid=input_objectid;

END ;
$function$