CREATE TABLE pois_mapping AS 
SELECT * FROM pois;

ALTER TABLE pois_mapping add primary key(gid); 
CREATE INDEX ON pois_mapping USING GIST (geom);
CREATE INDEX ON pois_mapping(amenity);