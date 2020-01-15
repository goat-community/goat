drop table dem_vec;
create table dem_vec as 
select rid, dp.geom , dp.val from dem, ST_DumpAsPolygons(rast) dp;

create index on dem_vec using gist(geom);

ALTER TABLE dem_vec ADD COLUMN id serial;
ALTER TABLE dem_vec ADD PRIMARY KEY(id);

CREATE OR REPLACE FUNCTION public.compute_slope_profile2(input_id bigint, table_update boolean, table_name text)
 RETURNS SETOF jsonb[]
 LANGUAGE plpgsql
AS $function$
BEGIN	
	
	IF NOT EXISTS(SELECT relname FROM pg_class WHERE relname='w_split') THEN
		CREATE TEMP TABLE IF NOT EXISTS w_split(id integer, length_m numeric, geom geometry, e_start geometry, e_end geometry, CONSTRAINT pk_id PRIMARY KEY(id)); 
		CREATE INDEX IF NOT EXISTS index_e_start ON w_split USING gist(e_start);
		CREATE INDEX IF NOT EXISTS index_e_end ON w_split USING gist(e_end);
	else 
		TRUNCATE w_split;
	end if;

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
	

	RETURN query
	WITH es AS (
		SELECT w.geom, d.val e_start, ST_Length(w.geom::geography) AS length_m
		FROM w_split w, dem_vec d 
		WHERE ST_Contains(d.geom, w.e_start)
	),
	ee AS (
		SELECT length_m AS original_length, w.geom, d.val e_end
		FROM w_split w, dem_vec d 
		WHERE ST_Contains(d.geom, w.e_end)
	),
	split_slope AS (
		SELECT es.geom, ee.original_length, es.length_m, 
		(es.e_start-ee.e_end)/es.length_m AS slope,
		slope_impedance((100*(es.e_start-ee.e_end)/es.length_m)::NUMERIC) AS s_imp
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
;


-- Test usage
SELECT compute_slope_profile2(100,TRUE,'ways');


CREATE TEMP TABLE temp_slopes AS
WITH x AS (
SELECT compute_slope_profile2(id,TRUE,'ways') AS slope_json
FROM ways 
WHERE class_id::text NOT IN(SELECT UNNEST(select_from_variable_container('excluded_class_id_cycling')))
AND length_m >= (SELECT select_from_variable_container_s('resolution_dem')::integer)
)
SELECT (slope_json[1] ->> 'id') AS id, (slope_json[1] ->> 's_imp') AS s_imp, (slope_json[1] ->> 'rs_imp') AS rs_imp, slope_json[2:] AS slope_profile
FROM x;


--
-- Batch processing of the entire 'ways' table
--

drop function compute_ways_slope_profile;
CREATE OR REPLACE FUNCTION public.compute_ways_slope_profile(table_update boolean)
 RETURNS SETOF jsonb[]
 LANGUAGE plpgsql
AS $function$
BEGIN	
	
	IF NOT EXISTS(SELECT relname FROM pg_class WHERE relname='w_split_multi') THEN
		CREATE TEMP TABLE IF NOT EXISTS w_split_multi(id integer primary key, wid integer, length_m numeric, geom geometry, e_start geometry, e_end geometry); 
		CREATE INDEX IF NOT EXISTS idx_w_split_multi_e_start ON w_split_multi USING gist(e_start);
		CREATE INDEX IF NOT EXISTS idx_w_split_multi_e_end ON w_split_multi USING gist(e_end);
		CREATE INDEX IF NOT EXISTS idx_w_split_multi_wid ON w_split_multi USING btree(wid);
	else 
		TRUNCATE w_split_multi;
	end if;

	EXECUTE format(
		'INSERT INTO w_split_multi
		WITH x as (
			SELECT id as wid, length_m::numeric, split_long_way(geom,length_m::numeric,30) AS geom 	
			FROM ways 
			WHERE class_id::text NOT IN(SELECT UNNEST(select_from_variable_container(''excluded_class_id_cycling'')))
			AND length_m >= (SELECT select_from_variable_container_s(''resolution_dem'')::integer)
		)
		SELECT ROW_NUMBER() OVER() AS id, wid, length_m, geom, ST_STARTPOINT(geom) e_start, ST_ENDPOINT(geom) e_end
		FROM x'	
	);	
	
	RETURN query
	WITH es AS (
		SELECT w.wid, w.geom, d.val e_start, ST_Length(w.geom::geography) AS length_m
		FROM w_split_multi w, dem_vec d 
		WHERE ST_Contains(d.geom, w.e_start)
	),
	ee AS (
		SELECT w.wid, length_m AS original_length, w.geom, d.val e_end
		FROM w_split_multi w, dem_vec d 
		WHERE ST_Contains(d.geom, w.e_end)
	),
	split_slope AS (
		SELECT es.wid, es.geom, ee.original_length,es.length_m, 
		(es.e_start-ee.e_end)/es.length_m AS slope,
		slope_impedance((100*(es.e_start-ee.e_end)/es.length_m)::NUMERIC) AS s_imp
		FROM es,ee
		WHERE es.wid = ee.wid and es.geom = ee.geom
	),
	x AS (
		SELECT array_agg(jsonb_build_object('geom',geom,'length',length_m,'slope',slope,'imp',s_imp)) slope_profile,
		SUM((length_m/original_length)*s_imp[1])::NUMERIC s_imp,
		SUM((length_m/original_length)*s_imp[2])::NUMERIC rs_imp,
		wid
		FROM split_slope
		group by wid
	)
	SELECT jsonb_build_object('s_imp',s_imp,'rs_imp',rs_imp,'id',x.wid) || slope_profile 
	FROM x;
END;
$function$
;

-- Test usage
CREATE TEMP TABLE temp_slopes AS
WITH x AS (
SELECT compute_ways_slope_profile(TRUE) AS slope_json
)
SELECT (slope_json[1] ->> 'id') AS id, (slope_json[1] ->> 's_imp') AS s_imp, (slope_json[1] ->> 'rs_imp') AS rs_imp, slope_json[2:] AS slope_profile
FROM x;



