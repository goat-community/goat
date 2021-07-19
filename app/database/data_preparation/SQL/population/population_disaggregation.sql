DROP TABLE IF EXISTS sum_built_up;
CREATE TEMP TABLE sum_built_up AS
SELECT sum(a.gross_floor_area_residential) AS sum_gross_floor_area_residential, s.sum_pop, s.geom  
FROM residential_addresses a, study_area s  
WHERE ST_Intersects(a.geom, s.geom)
GROUP BY s.geom, s.sum_pop ; 

CREATE INDEX ON sum_built_up USING GIST(geom);

DROP TABLE IF EXISTS population; 
CREATE TABLE population AS 
SELECT a.gid, a.geom, NULL AS fixed_population, 
(gross_floor_area_residential::float/sum_gross_floor_area_residential::float) * s.sum_pop AS population, a.building_gid  
FROM residential_addresses a, sum_built_up s 
WHERE ST_Intersects(a.geom,s.geom);

/*Cleaning and adding indices*/
ALTER TABLE population DROP COLUMN gid;
ALTER TABLE population ADD COLUMN gid serial;
ALTER TABLE population add primary key(gid);
CREATE INDEX ON population USING GIST (geom);

DELETE FROM population 
WHERE population < 0;