DROP FUNCTION IF EXISTS compute_slope_profile;
CREATE OR REPLACE FUNCTION compute_slope_profile(input_id integer)
 RETURNS TABLE(slope_profile jsonb[],s_imp NUMERIC ,rs_imp NUMERIC )
 LANGUAGE sql
AS $function$
	WITH w_split AS 
	(
		SELECT length_m, split_long_way(geom,length_m::numeric,30) AS geom 	
		FROM ways 
		WHERE id = input_id
	),
	es AS (
		SELECT w.geom,ST_VALUE(d.rast,ST_STARTPOINT(w.geom)) e_start
		FROM w_split w, dem d 
		WHERE ST_Intersects(ST_STARTPOINT(w.geom),rast)
	),
	ee AS (
		SELECT length_m AS original_length, w.geom,ST_VALUE(d.rast,ST_ENDPOINT(w.geom)) e_end
		FROM w_split w, dem d 
		WHERE ST_Intersects(ST_ENDPOINT(w.geom),rast)
	),
	split_slope AS (
		SELECT es.geom, ee.original_length,ST_Length(es.geom::geography) AS length_m, 
		(es.e_start-ee.e_end)/ST_Length(es.geom::geography) AS slope,
		slope_impedance((100*(es.e_start-ee.e_end)/ST_Length(es.geom::geography))::NUMERIC) AS s_imp
		FROM es,ee
		WHERE es.geom = ee.geom
	)
	SELECT array_agg(jsonb_build_object('geom',geom,'length',length_m,'slope',slope,'s_imp',s_imp)) AS slope_profile
	,SUM((length_m/original_length)*s_imp[1])::NUMERIC AS s_imp,SUM((length_m/original_length)*s_imp[2])::NUMERIC AS rs_imp
	FROM split_slope;
$function$

--SELECT * 
--FROM compute_slope_profile(376386)