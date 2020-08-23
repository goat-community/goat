DROP TABLE IF EXISTS dem_vec;
CREATE TABLE dem_vec as 
SELECT rid, dp.geom AS geom, dp.val FROM dem, ST_DumpAsPolygons(rast) dp;

CREATE index ON dem_vec USING gist(geom);
ALTER TABLE dem_vec ADD COLUMN id serial;
ALTER TABLE dem_vec ADD PRIMARY KEY(id);