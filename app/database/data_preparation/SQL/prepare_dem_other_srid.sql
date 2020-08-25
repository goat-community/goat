DROP TABLE IF EXISTS dem_vec;
CREATE TABLE dem_vec as
SELECT rid, ST_Transform(ST_SETSRID(dp.geom,25832),4326) AS geom , dp.val FROM dem, ST_DumpAsPolygons(rast) dp;

CREATE index ON dem_vec USING gist(geom);
ALTER TABLE dem_vec ADD COLUMN id serial;
ALTER TABLE dem_vec ADD PRIMARY KEY(id);