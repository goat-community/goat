DROP FUNCTION IF EXISTS compute_slope_profile;
CREATE OR REPLACE FUNCTION compute_slope_profile(input_id bigint, table_update BOOLEAN, table_name text)
 RETURNS SETOF jsonb[]
 LANGUAGE plpgsql
AS $function$
BEGIN	
	
	CREATE TEMP TABLE IF NOT EXISTS w_split(length_m numeric,geom geometry); 
	DELETE FROM w_split;

	EXECUTE format(
		'INSERT INTO w_split
		SELECT length_m::numeric, split_long_way(geom,length_m::numeric,30) AS geom 	
		FROM '||quote_ident(table_name)||' 
		WHERE id = '||input_id	
	);	
	RETURN query
	WITH es AS (
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
	),
	x AS (
		SELECT array_agg(jsonb_build_object('geom',geom,'length',length_m,'slope',slope,'imp',s_imp)) slope_profile,
		SUM((length_m/original_length)*s_imp[1])::NUMERIC s_imp,
		SUM((length_m/original_length)*s_imp[2])::NUMERIC rs_imp,
		input_id
		FROM split_slope
	)
	SELECT jsonb_build_object('s_imp',s_imp,'rs_imp',rs_imp,'id',x.input_id) || slope_profile 
	FROM x;
END;
$function$