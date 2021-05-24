-----------------------------------------------------
--FUCTION GREATEST VALUE IN ARRAY------
CREATE OR REPLACE FUNCTION array_greatest(anyarray)
RETURNS anyelement
LANGUAGE SQL
AS $$
  SELECT max(elements) FROM unnest($1) elements
$$;
---------------------------START_DAY_NOISE---------------------------

DROP TABLE IF EXISTS day_street;
DROP TABLE IF EXISTS day_tram;
DROP TABLE IF EXISTS day_railway;
CREATE TEMP TABLE day_street AS (SELECT * FROM freiburg_noise fn WHERE noise_type = 'day_street');
CREATE TEMP TABLE day_tram AS (SELECT * FROM freiburg_noise fn WHERE noise_type = 'day_tram');
CREATE TEMP TABLE day_railway AS (SELECT * FROM freiburg_noise fn WHERE noise_type = 'day_railway');

DROP TABLE IF EXISTS fp_day_street;
CREATE TEMP TABLE fp_day_street AS 
SELECT ilp.*
FROM intersection_lines_polygons('footpaths_visualization', 'id', 'day_street', 'noise_level_db') ilp, footpaths_visualization fu
WHERE fu.id = ilp.id;

DROP TABLE IF EXISTS fp_day_tram;
CREATE TEMP TABLE fp_day_tram AS 
SELECT ilp.*
FROM intersection_lines_polygons('footpaths_visualization', 'id', 'day_tram', 'noise_level_db') ilp, footpaths_visualization fu
WHERE fu.id = ilp.id;

DROP TABLE IF EXISTS fp_day_railway;
CREATE TEMP TABLE fp_day_railway AS 
SELECT ilp.*
FROM intersection_lines_polygons('footpaths_visualization', 'id', 'day_railway', 'noise_level_db') ilp, footpaths_visualization fu
WHERE fu.id = ilp.id;

INSERT INTO fp_day_railway (id, arr_polygon_attr, arr_shares)
SELECT fds.id, ARRAY[0], ARRAY[100] FROM fp_day_street fds
WHERE fds.id NOT IN (SELECT DISTINCT id FROM fp_day_railway); 


ALTER TABLE fp_day_street
ADD COLUMN main_level_db text; 

UPDATE fp_day_street
SET main_level_db = (
WITH arr_gr AS (SELECT id, array_greatest(arr_shares), arr_shares, arr_polygon_attr  FROM fp_day_street)
SELECT arr_polygon_attr[array_position(arr_shares, array_greatest)] AS noise FROM arr_gr WHERE fp_day_street.id = arr_gr.id);

ALTER TABLE fp_day_tram
ADD COLUMN main_level_db text; 

UPDATE fp_day_tram
SET main_level_db = (
WITH arr_gr AS (SELECT id, array_greatest(arr_shares), arr_shares, arr_polygon_attr  FROM fp_day_tram)
SELECT arr_polygon_attr[array_position(arr_shares, array_greatest)] AS noise FROM arr_gr WHERE fp_day_tram.id = arr_gr.id); 

ALTER TABLE fp_day_railway
ADD COLUMN main_level_db text;  

UPDATE fp_day_railway
SET main_level_db = (
WITH arr_gr AS (SELECT id, array_greatest(arr_shares), arr_shares, arr_polygon_attr  FROM fp_day_railway)
SELECT arr_polygon_attr[array_position(arr_shares, array_greatest)] AS noise FROM arr_gr WHERE fp_day_railway.id = arr_gr.id); 

UPDATE fp_day_street
SET main_level_db = '0'
WHERE main_level_db = 'outside';

UPDATE fp_day_tram
SET main_level_db = '0'
WHERE main_level_db = 'outside';

UPDATE fp_day_railway
SET main_level_db = '0'
WHERE main_level_db = 'outside';

ALTER TABLE footpaths_visualization
ADD COLUMN noise_day float; 

DROP TABLE IF EXISTS noise_d;
CREATE TEMP TABLE noise_d AS (
SELECT fds.id, 10 * log(power(10,(fds.main_level_db::integer)/10)+power(10,(fdt.main_level_db::integer)/10)+power(10,(fdr.main_level_db::integer)/10)) AS med_noise
FROM fp_day_street fds, fp_day_tram fdt, fp_day_railway fdr
WHERE fds.id = fdt.id AND fds.id = fdr.id
);

CREATE INDEX ON noise_d(id);								
								
UPDATE footpaths_visualization fu --footpath_visalization
SET noise_day = med_noise
FROM noise_d nd
WHERE fu.id = nd.id;
-----------------END_DAY_NOISE-----------------------------------

-----------------START_NIGHT_NOISE-------------------------------
DROP TABLE IF EXISTS night_street;
DROP TABLE IF EXISTS night_tram;
DROP TABLE IF EXISTS night_railway;
CREATE TEMP TABLE night_street AS (SELECT * FROM freiburg_noise fn WHERE noise_type = 'night_street');
CREATE TEMP TABLE night_tram AS (SELECT * FROM freiburg_noise fn WHERE noise_type = 'night_tram');
CREATE TEMP TABLE night_railway AS (SELECT * FROM freiburg_noise fn WHERE noise_type = 'night_railway');

DROP TABLE IF EXISTS fp_night_street;
CREATE TEMP TABLE fp_night_street AS 
SELECT ilp.*
FROM intersection_lines_polygons('footpaths_visualization', 'id', 'night_street', 'noise_level_db') ilp, footpaths_visualization fu
WHERE fu.id = ilp.id;

DROP TABLE IF EXISTS fp_night_tram;
CREATE TEMP TABLE fp_night_tram AS 
SELECT ilp.*
FROM intersection_lines_polygons('footpaths_visualization', 'id', 'night_tram', 'noise_level_db') ilp, footpaths_visualization fu
WHERE fu.id = ilp.id;

DROP TABLE IF EXISTS fp_night_railway;
CREATE TEMP TABLE fp_night_railway AS 
SELECT ilp.*
FROM intersection_lines_polygons('footpaths_visualization', 'id', 'night_railway', 'noise_level_db') ilp, footpaths_visualization fu
WHERE fu.id = ilp.id;

INSERT INTO fp_night_railway (id, arr_polygon_attr, arr_shares)
SELECT fds.id, ARRAY[0], ARRAY[100] FROM fp_night_street fds
WHERE fds.id NOT IN (SELECT DISTINCT id FROM fp_night_railway); 

ALTER TABLE fp_night_street
ADD COLUMN main_level_db text; 

UPDATE fp_night_street
SET main_level_db = (
WITH arr_gr AS (SELECT id, array_greatest(arr_shares), arr_shares, arr_polygon_attr  FROM fp_night_street)
SELECT arr_polygon_attr[array_position(arr_shares, array_greatest)] AS noise FROM arr_gr WHERE fp_night_street.id = arr_gr.id);

ALTER TABLE fp_night_tram
ADD COLUMN main_level_db text; 

UPDATE fp_night_tram
SET main_level_db = (
WITH arr_gr AS (SELECT id, array_greatest(arr_shares), arr_shares, arr_polygon_attr  FROM fp_night_tram)
SELECT arr_polygon_attr[array_position(arr_shares, array_greatest)] AS noise FROM arr_gr WHERE fp_night_tram.id = arr_gr.id); 

ALTER TABLE fp_night_railway
ADD COLUMN main_level_db text;  

UPDATE fp_night_railway
SET main_level_db = (
WITH arr_gr AS (SELECT id, array_greatest(arr_shares), arr_shares, arr_polygon_attr  FROM fp_night_railway)
SELECT arr_polygon_attr[array_position(arr_shares, array_greatest)] AS noise FROM arr_gr WHERE fp_night_railway.id = arr_gr.id); 

UPDATE fp_night_street
SET main_level_db = '0'
WHERE main_level_db = 'outside';

UPDATE fp_night_tram
SET main_level_db = '0'
WHERE main_level_db = 'outside';

UPDATE fp_night_railway
SET main_level_db = '0'
WHERE main_level_db = 'outside';

ALTER TABLE footpaths_visualization
ADD COLUMN noise_night float; 

DROP TABLE IF EXISTS noise_n;
CREATE TEMP TABLE noise_n AS (
SELECT fns.id, 10 * log(power(10,(fns.main_level_db::integer)/10)+power(10,(fnt.main_level_db::integer)/10)+power(10,(fnr.main_level_db::integer)/10)) AS med_noise
FROM fp_night_street fns, fp_night_tram fnt, fp_night_railway fnr
WHERE fns.id = fnt.id AND fns.id = fnr.id
);

CREATE INDEX ON noise_n(id);								
								
UPDATE footpaths_visualization fu --footpath_visalization
SET noise_night = med_noise
FROM noise_n nn
WHERE fu.id = nn.id;

--------------------------END_NIGHT_NOISE-----------------------------