CREATE TABLE muenchen as 

WITH dump AS (
    SELECT                       --columns FROM your multipolygon table 
      (ST_DUMP(st_union)).geom AS geometry 
    FROM (SELECT st_union(way) FROM planet_osm_polygon  WHERE boundary = 'administrative'
AND name LIKE 'Bezirksteil%' ) x                           --the name of your multipolygon table
) 
SELECT 
  geometry::geometry(Polygon,4326)         --type cast using SRID FROM multipolygon
FROM dump;
