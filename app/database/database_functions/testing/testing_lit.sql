
DROP TABLE IF EXISTS ways_intersect_street_lamps;
CREATE TABLE ways_intersect_street_lamps AS 
SELECT w.id, min(ST_LENGTH(ST_Intersection(ST_BUFFER(p.way,0.00015), w.geom))) AS length
FROM planet_osm_point p, ways w 
WHERE p.highway = 'street_lamp'
AND ST_Intersects(ST_BUFFER(p.way,0.00015),w.geom)
GROUP BY w.id; 

ALTER TABLE ways_intersect_street_lamps ADD PRIMARY KEY(id);
UPDATE ways w SET lit_classified = 'yes'
FROM ways_intersect_street_lamps l
WHERE (w.lit IS NULL OR w.lit = '')
AND w.id = l.id 
AND ST_Length(w.geom)/3 < l.length

SELECT ST_BUFFER(p.way,0.00015)
FROM planet_osm_point p
WHERE p.highway = 'street_lamp'