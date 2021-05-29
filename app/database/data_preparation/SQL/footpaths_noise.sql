/*For each footpath noise levels (day and night) are derived an aggregated for different sound sources*/

DROP TABLE IF EXISTS noise_levels_footpaths;
CREATE TEMP TABLE noise_levels_footpaths 
(
  gid serial, 
  footpath_id integer, 
  noise_level_db integer, 
  noise_type text,
  CONSTRAINT noise_levels_footpaths_pkey PRIMARY KEY (gid)
);

DO $$     
	DECLARE 
		noise_key TEXT;
    BEGIN     
	    FOR noise_key IN SELECT DISTINCT noise_type FROM noise  	
		LOOP
			RAISE NOTICE 'Following noise type will be calculated: %', noise_key;
			DROP TABLE IF EXISTS noise_subdivide;
			CREATE TEMP TABLE noise_subdivide AS 
			SELECT ST_SUBDIVIDE((ST_DUMP(geom)).geom, 50) AS geom, noise_level_db  
			FROM noise fn 
			WHERE noise_type = noise_key;
			
			ALTER TABLE noise_subdivide ADD COLUMN gid serial;
			ALTER TABLE noise_subdivide ADD PRIMARY KEY(gid);
			CREATE INDEX ON noise_subdivide USING GIST(geom);
			
			INSERT INTO noise_levels_footpaths(footpath_id,noise_level_db,noise_type)
			SELECT id, 
			COALESCE(arr_polygon_attr[array_position(arr_shares, array_greatest(arr_shares))]::integer, 0) AS val, noise_key
			FROM footpaths_get_polygon_attr('noise_subdivide','noise_level_db');
			
		END LOOP;
    END
$$ ;

ALTER TABLE footpath_visualization ADD COLUMN noise_day float; 
WITH noise_day AS 
(
	SELECT footpath_id, (10 * LOG(SUM(power(10,(noise_level_db::float/10))))) AS noise 
	FROM noise_levels_footpaths
	WHERE noise_type LIKE '%day%'
	GROUP BY footpath_id
)
UPDATE footpath_visualization f
SET noise_day = n.noise 
FROM noise_day n  
WHERE f.id = n.footpath_id; 

ALTER TABLE footpath_visualization ADD COLUMN noise_night float; 
WITH noise_night AS 
(
	SELECT footpath_id, (10 * LOG(SUM(power(10,(noise_level_db::float/10))))) AS noise 
	FROM noise_levels_footpaths
	WHERE noise_type LIKE '%night%'
	GROUP BY footpath_id
)
UPDATE footpath_visualization f
SET noise_night = n.noise 
FROM noise_night n  
WHERE f.id = n.footpath_id; 