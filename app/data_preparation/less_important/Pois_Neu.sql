

SELECT p.* FROM (
SELECT i.gid,count(*),amenity FROM isochrones i, 
pois p
WHERE st_intersects(i.geom,p.geom)  AND objectid=2217719 AND shop IS NULL
GROUP BY i.gid,amenity
UNION ALL
SELECT i.gid,count(*),shop FROM isochrones i, 
pois p
WHERE st_intersects(i.geom,p.geom)  AND objectid=2217719 AND amenity IS NULL
GROUP BY i.gid,shop
UNION ALL
SELECT gid,count(*),public_transport_stop
FROM
(SELECT i.gid, p.name,public_transport_stop,1 as count
FROM public_transport_stops p, isochrones i
WHERE st_intersects(i.geom,p.geom)
AND i.objectid = 2217719
GROUP BY i.gid,public_transport_stop,p.name) p
GROUP BY gid,public_transport_stop) p,variable_container
WHERE amenity = any(variable_array)
AND identifier = 'poi_categories';
