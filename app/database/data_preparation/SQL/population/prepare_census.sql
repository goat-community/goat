ALTER TABLE residential_addresses ADD COLUMN IF NOT EXISTS fixed_population float;
DO $$                  
    BEGIN 
        IF EXISTS
            ( SELECT 1
              FROM   information_schema.tables 
              WHERE  table_schema = 'public'
              AND    table_name = 'fixed_population'
            )
        THEN
            WITH fixed_population AS (
				SELECT b.geom, f.population AS fixed_population
				FROM buildings_residential b, fixed_population f
				WHERE ST_Intersects(f.geom,b.geom)
			)
			UPDATE residential_addresses b
			SET fixed_population = f.fixed_population
			FROM fixed_population f
			WHERE ST_Intersects(b.geom,f.geom);
        END IF ;
    END
$$ ;

ALTER TABLE census DROP COLUMN IF EXISTS gid; 
ALTER TABLE census ADD COLUMN IF NOT EXISTS gid serial; 
ALTER TABLE census ADD PRIMARY KEY(gid);

/*Compute built up area per census tract*/
DROP TABLE IF EXISTS census_sum_built_up;
CREATE TABLE census_sum_built_up AS 
SELECT DISTINCT c.gid, COALESCE(c.pop,0) pop, COALESCE(c.sum_gross_floor_area_residential,0) AS sum_gross_floor_area_residential, c.number_buildings_now, c.geom 
FROM study_area s
INNER JOIN LATERAL 
(
	SELECT c.gid, sum(a.gross_floor_area_residential) sum_gross_floor_area_residential, count(a.gid) AS number_buildings_now, c.pop, c.geom  
	FROM census c, residential_addresses a 
	WHERE ST_Intersects(s.geom, c.geom)
	AND ST_Intersects(c.geom, a.geom) 
	GROUP BY c.gid, c.pop, c.geom  
) c ON TRUE;

ALTER TABLE census_sum_built_up  ADD PRIMARY KEY (gid);