/*Create vector point layer out of dem raster*/
CREATE TABLE dem_vec AS 
SELECT c.geom, c.val  
FROM dem, LATERAL ST_PixelAsCentroids(rast) c;
CREATE INDEX ON dem_vec USING GIST(geom);

/*Remove all ways that are not covered by the dem*/
DROP TABLE IF EXISTS ways_to_remove; 
CREATE TEMP TABLE ways_to_remove AS 
WITH extent AS 
(
	SELECT st_setsrid(st_extent(geom)::geometry, 4326) AS geom 
	FROM dem_vec dv 
) 
SELECT w.id 
FROM ways w
LEFT JOIN extent t
ON ST_Intersects(w.geom,t.geom)
WHERE t.geom IS NULL
UNION ALL 
SELECT w.id 
FROM ways w, extent e 
WHERE ST_Intersects(st_boundary(e.geom), w.geom); 

CREATE INDEX ON ways_to_remove(id);
DELETE FROM ways w
USING ways_to_remove r 
WHERE w.id = r.id; 