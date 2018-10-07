create table muenchen as 

WITH dump AS (
    SELECT                       --columns from your multipolygon table 
      (ST_DUMP(st_union)).geom AS geometry 
    FROM (select st_union(way) from planet_osm_polygon  where boundary = 'administrative'
and name LIKE 'Bezirksteil%' ) x                           --the name of your multipolygon table
) 
SELECT 
  geometry::geometry(Polygon,4326)         --type cast using SRID from multipolygon
FROM dump;
