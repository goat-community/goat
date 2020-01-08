DROP FUNCTION IF EXISTS compute_slope_profile;
CREATE OR REPLACE FUNCTION compute_slope_profile(input_id bigint, table_update BOOLEAN, table_name text)
 RETURNS SETOF type_slope
 LANGUAGE plpgsql
AS $function$
DECLARE
v_slope_profile jsonb[];
v_s_imp numeric;
v_rs_imp numeric;
BEGIN	
	EXECUTE format(
		'WITH w_split AS 
		(
		SELECT length_m, split_long_way(geom,length_m::numeric,30) AS geom 	
		FROM '||quote_ident(table_name)||' 
		WHERE id = '||input_id||'
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
		SELECT array_agg(jsonb_build_object(''geom'',geom,''length'',length_m,''slope'',slope,''imp'',s_imp)) AS slope_profile
		,SUM((length_m/original_length)*s_imp[1])::NUMERIC AS s_imp,SUM((length_m/original_length)*s_imp[2])::NUMERIC AS rs_imp
		INTO v_slope_profile, v_s_imp, v_rs_imp
		FROM split_slope;'
	);
	IF table_update = TRUE 
	THEN 
	EXECUTE format(
		'UPDATE '||quote_ident(table_name)||' w
		SET slope_profile = v_slope_profile, s_imp = v_s_imp, rs_imp = v_rs_imp 
		WHERE w.id = '||input_id
	);
	END IF;
	IF table_update = FALSE THEN 
		RETURN query SELECT v_slope_profile,v_s_imp,v_rs_imp;
	END IF;
END;
$function$

--SELECT * 
--FROM compute_slope_profile(376386,TRUE,'ways')


Testing

DROP FUNCTION IF EXISTS compute_slope_profile;
CREATE OR REPLACE FUNCTION compute_slope_profile(input_id bigint, table_update BOOLEAN, table_name text)
 RETURNS SETOF type_slope
 LANGUAGE plpgsql
AS $function$
DECLARE
	v_slope_profile jsonb[];
	v_s_imp numeric;
	v_rs_imp numeric;
BEGIN	
	RAISE NOTICE 'ss';
	EXECUTE format(
		'WITH w_split AS 
		(
			SELECT length_m, split_long_way(geom,length_m::numeric,30) AS geom 	
			FROM '||quote_ident(table_name)||' 
			WHERE id = '||input_id||'
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
		SELECT array_agg(jsonb_build_object(''geom'',geom,''length'',length_m,''slope'',slope,''imp'',s_imp)) AS slope_profile
		,SUM((length_m/original_length)*s_imp[1])::NUMERIC AS s_imp,SUM((length_m/original_length)*s_imp[2])::NUMERIC AS rs_imp
		INTO v_slope_profile, v_s_imp, v_rs_imp
		FROM split_slope;'
	);

	IF table_update = TRUE 
	THEN 
	EXECUTE format(
		'UPDATE '||quote_ident(table_name)||' w
		SET slope_profile = v_slope_profile, s_imp = v_s_imp, rs_imp = v_rs_imp 
		WHERE w.id = '||input_id
	);
	END IF;
	IF table_update = FALSE THEN 
		RETURN query SELECT v_slope_profile,v_s_imp,v_rs_imp;
	END IF;
END;
$function$

--SELECT * 
--FROM compute_slope_profile(376386,TRUE,'ways')