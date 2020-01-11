DROP FUNCTION IF EXISTS compute_slope_profile;
CREATE OR REPLACE FUNCTION compute_slope_profile(input_id bigint, table_update BOOLEAN, table_name text)
 RETURNS SETOF jsonb[]
 LANGUAGE plpgsql
AS $function$
BEGIN	
	
	CREATE TEMP TABLE IF NOT EXISTS w_split(id integer, length_m numeric, geom geometry, e_start geometry, e_end geometry, CONSTRAINT pk_id PRIMARY KEY(id)); 
	DELETE FROM w_split;
	
	EXECUTE format(
		'INSERT INTO w_split
		WITH x as (
			SELECT length_m::numeric, split_long_way(geom,length_m::numeric,30) AS geom 	
			FROM '||quote_ident(table_name)||' 
			WHERE id = '||input_id||'
		)
		SELECT ROW_NUMBER() OVER() AS id, length_m, geom, ST_STARTPOINT(geom) e_start, ST_ENDPOINT(geom) e_end
		FROM x'	
	);	
	CREATE INDEX IF NOT EXISTS index_e_start ON w_split USING gist(e_start);
	CREATE INDEX IF NOT EXISTS index_e_end ON w_split USING gist(e_end);

	RETURN query
	WITH es AS (
		SELECT w.geom,ST_VALUE(d.rast,w.e_start) e_start
		FROM w_split w, dem d 
		WHERE w.e_start && rast
	),
	ee AS (
		SELECT length_m AS original_length, w.geom,ST_VALUE(d.rast,w.e_end) e_end
		FROM w_split w, dem d 
		WHERE w.e_start && rast
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


/*This is how the function can be executed
DROP TABLE IF EXISTS temp_slopes;
CREATE TEMP TABLE temp_slopes AS
WITH x AS (
	SELECT compute_slope_profile(id,TRUE,'ways') AS slope_json
	FROM ways 
	WHERE class_id::text NOT IN(SELECT UNNEST(select_from_variable_container('excluded_class_id_cycling')))
	AND length_m >= (SELECT select_from_variable_container_s('resolution_dem')::integer)
)
SELECT (slope_json[1] ->> 'id') AS id, (slope_json[1] ->> 's_imp') AS s_imp, (slope_json[1] ->> 'rs_imp') AS rs_imp, slope_json[2:] AS slope_profile
FROM x;
ALTER TABLE temp_slopes ADD PRIMARY key(id);

UPDATE ways w 
SET slope_profile = t.slope_profile,
s_imp = t.s_imp::numeric,
rs_imp = t.rs_imp::numeric
FROM temp_slopes t 
WHERE w.id = t.id::bigint;
*/