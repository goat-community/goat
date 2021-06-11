/*Create population points from census without extrapolation*/
DROP TABLE IF EXISTS population; 
CREATE TABLE population AS 
SELECT a.gid, a.geom, NULL AS fixed_population, CASE WHEN sum_gross_floor_area_residential <> 0 THEN 
(a.gross_floor_area_residential::float/c.sum_gross_floor_area_residential::float)*pop 
ELSE 0 END AS population, a.building_gid 
FROM residential_addresses a, census_sum_built_up c 
WHERE ST_Intersects(a.geom,c.geom)
AND c.sum_gross_floor_area_residential <> 0;

/*Cleaning and adding indices*/
ALTER TABLE population DROP COLUMN gid;
ALTER TABLE population ADD COLUMN gid serial;
ALTER TABLE population add primary key(gid);
CREATE INDEX ON population USING GIST (geom);

DELETE FROM population 
WHERE population < 0;
