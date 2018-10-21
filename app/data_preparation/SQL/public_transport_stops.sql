
--------------------------------------------------------------------------
--Create first pois as it is continuing with gid----------------------------
--------------------------------------------------------------------------



--ALTER TABLE hilfstabelle_pois
--ALTER TABLE hilfstabelle_pois add column bus_station integer;
--ALTER TABLE hilfstabelle_pois add column subway_station integer;
--ALTER TABLE hilfstabelle_pois add column tram_station integer;
--ALTER TABLE hilfstabelle_pois add column railway_station integer;


--Create public_transport_stops
DROP TABLE IF EXISTS public_transport_stops;
SELECT *, (SELECT max(gid) FROM pois) + row_number() over() as gid
INTO public_transport_stops FROM (
SELECT 'bus_stop' as public_transport_stop,name,way as geom FROM planet_osm_point 
WHERE highway = 'bus_stop' AND name IS NOT NULL
UNION ALL
SELECT 'bus_stop' as public_transport_stop,name,way as geom FROM planet_osm_point 
WHERE public_transport = 'platform' AND name IS NOT NULL AND tags -> 'bus'='yes'
UNION ALL
SELECT 'tram_stop' as public_transport_stop,name,way as geom FROM planet_osm_point 
WHERE public_transport = 'stop_position' 
AND tags -> 'tram'='yes'
AND name IS NOT NULL
UNION ALL
SELECT  'subway_entrance' as public_transport,name, way as geom FROM planet_osm_point
WHERE railway = 'subway_entrance'
UNION ALL
SELECT 'sbahn_regional' as public_transport,name,way as geom 
FROM planet_osm_point WHERE railway = 'stop'
AND tags -> 'train' ='yes') x;



UPDATE public_transport_stops set name = x.name 
FROM
(SELECT p.geom,x.name,min(st_distance(p.geom::geography,x.geom::geography))
FROM public_transport_stops p,
	(SELECT 'subway' as public_transport,name,way as geom  FROM planet_osm_point 
	WHERE public_transport ='station' AND
	tags -> 'subway' = 'yes' AND railway <> 'proposed') x
WHERE st_dwithin(p.geom::geography,x.geom::geography,500)
GROUP BY p.geom,x.name) x
WHERE public_transport_stops.geom = x.geom
AND public_transport_stop = 'subway_entrance';



ALTER TABLE public_transport_stops add primary key (gid); 
CREATE INDEX index_public_transport_stops ON public_transport_stops USING GIST (geom);
