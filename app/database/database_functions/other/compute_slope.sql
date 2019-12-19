DROP FUNCTION IF EXISTS compute_slope_profile;
CREATE OR REPLACE FUNCTION compute_slope_profile(input_id integer)
 RETURNS jsonb[]
 LANGUAGE sql
AS $function$
	WITH w_split AS 
	(
		SELECT split_long_way(geom,length_m::numeric,30) AS geom 	
		FROM ways 
		WHERE id = 376386
	),
	es AS (
		SELECT w.geom,ST_VALUE(d.rast,ST_STARTPOINT(w.geom)) e_start
		FROM w_split w, dem d 
		WHERE ST_Intersects(ST_STARTPOINT(w.geom),rast)
	),
	ee AS (
		SELECT w.geom,ST_VALUE(d.rast,ST_ENDPOINT(w.geom)) e_end
		FROM w_split w, dem d 
		WHERE ST_Intersects(ST_ENDPOINT(w.geom),rast)
	)
	SELECT array_agg(jsonb_build_object('geom',es.geom,'length',ST_Length(es.geom::geography),'slope',(es.e_start-ee.e_end)/ST_Length(es.geom::geography))) AS slope_profile
	FROM es,ee
	WHERE es.geom = ee.geom;
$function$

--SELECT compute_slop_profile(376386)