
/*--Convert raster to vector
CREATE TABLE elevation AS 
SELECT geom,val 
FROM dem, LATERAL ST_PixelAsCentroids(rast, 1)

ALTER TABLE elevation ADD COLUMN id serial;
ALTER TABLE elevation ADD PRIMARY KEY(id);
CREATE INDEX ON elevation USING gist(geom);

--Function to compute elevation for certain point
CREATE OR REPLACE FUNCTION public.get_elevation(point geometry, snap_distance NUMERIC)
 RETURNS SETOF NUMERIC 
 LANGUAGE plpgsql
AS $function$
DECLARE
	ele NUMERIC;
	geom_ele geometry;
BEGIN
	SELECT val
  	INTO ele, geom_ele
	FROM elevation
	ORDER BY geom <-> point
	LIMIT 1;
  	IF ST_Distance(geom_ele,point)>snap_distance THEN
    	RETURN;
  	END IF;
  	RETURN query SELECT ele;
END ;
$function$;

--Distance in degrees to meters: 0.0009 -->> 100m

EXPLAIN ANALYZE
SELECT get_elevation(ST_SETSRID(ST_POINT(11.5669,48.1546),4326),0.0003)

--Just some code for testing 
WITH x as (
	SELECT length_m::numeric, split_long_way(geom,length_m::numeric,30) AS geom 	
	FROM ways
	WHERE id = 37562
)--,
--ele AS (
	SELECT length_m, geom, get_elevation(ST_STARTPOINT(geom),0.0003) ele, get_elevation(ST_ENDPOINT(geom),0.0003) ele1
	FROM x
)
SELECT length_m, geom, ele, lag(ele,1) OVER (
	PARTITION BY length_m
	ORDER BY geom 
) 
FROM ele

*/