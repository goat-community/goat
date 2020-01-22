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



--- Use alternative split_long_way() approach

CREATE OR REPLACE FUNCTION public.split_long_way2(geom geometry, length_m numeric, max_length integer)
 RETURNS geometry[]
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
DECLARE 
	fraction NUMERIC;
	end_border NUMERIC :=0;
	start_border NUMERIC;
	retval geometry[] = array[]::geometry[];
BEGIN 
	fraction = 1/ceil(length_m/max_length);
	WHILE end_border < 1 LOOP 
		start_border = round(end_border,5);
		end_border = round(end_border+fraction,5);
		retval = array_append(retval,ST_LineInterpolatePoint(geom, start_border)); 
		IF end_border >= 1 THEN 
			end_border = 1;
			retval = array_append(retval,ST_EndPoint(geom));
			exit;
		END IF;
		
	END LOOP; 
	RETURN retval;
	
END;
$function$

-- GROUP BY version 
CREATE OR REPLACE FUNCTION public.compute_ways_slope_profile2(table_update boolean)
 RETURNS SETOF jsonb[]
 LANGUAGE plpgsql
AS $function$
BEGIN	
	
	IF NOT EXISTS(SELECT relname FROM pg_class WHERE relname='w_split_multi2') THEN
		CREATE TEMP TABLE IF NOT EXISTS w_split_multi2(id integer primary key, wid integer, length_m numeric, geom geometry[]); 
		CREATE INDEX IF NOT EXISTS idx_w_split_multi2_wid ON w_split_multi2 USING btree(wid);
	else 
		TRUNCATE w_split_multi2;
	end if;

	EXECUTE format(
		'INSERT INTO w_split_multi2
		WITH x as (
			SELECT id as wid, length_m::numeric, split_long_way2(geom,length_m::numeric,30) AS geom 	
			FROM ways 
			WHERE class_id::text NOT IN(SELECT UNNEST(select_from_variable_container(''excluded_class_id_cycling'')))
			AND length_m >= (SELECT select_from_variable_container_s(''resolution_dem'')::integer)
		)
		SELECT ROW_NUMBER() OVER() AS id, wid, length_m, geom
		FROM x	'	
	);	
	
	RETURN query
	WITH 
	w_unnested as (
		select row_number() over (order by w.wid) as rnum, 
		w.wid, length_m AS original_length, 
		point as start,lead(point) over (partition by wid) as end
		FROM w_split_multi2 w, unnest(w.geom) point
	),
	es AS (
		SELECT w.rnum, w.wid, w.start, d.val e_start, st_distance(w.start::geography,w.end::geography ) as length_m
		FROM w_unnested w, dem_vec d 
		WHERE ST_Contains(d.geom, w.start) and w.end is not null
	),
	ee AS (
		SELECT w.rnum, w.wid, w.original_length, w.end, d.val e_end
		FROM w_unnested w, dem_vec d 
		WHERE ST_Contains(d.geom, w.end) and w.end is not null
	),
	split_slope AS (
		SELECT es.wid, es.start, ee.end, ee.original_length,es.length_m, 
		(es.e_start-ee.e_end)/es.length_m AS slope,
		slope_impedance((100*(es.e_start-ee.e_end)/es.length_m)::NUMERIC) AS s_imp
		FROM es,ee
		WHERE es.rnum = ee.rnum
	),
	x AS (
		SELECT array_agg(jsonb_build_object('start',s.start,'end',s.end,'length',length_m,'slope',slope,'imp',s_imp)) slope_profile,
		SUM((length_m/original_length)*s_imp[1])::NUMERIC s_imp,
		SUM((length_m/original_length)*s_imp[2])::NUMERIC rs_imp,
		wid
		FROM split_slope s
		group by wid
	)
	SELECT jsonb_build_object('s_imp',s_imp,'rs_imp',rs_imp,'id',x.wid) || slope_profile 
	FROM x;
END;
$function$
;
drop table temp_slopes;
CREATE TEMP TABLE temp_slopes AS
WITH x AS (
SELECT compute_ways_slope_profile2(TRUE) AS slope_json
)
SELECT (slope_json[1] ->> 'id') AS id, (slope_json[1] ->> 's_imp') AS s_imp, (slope_json[1] ->> 'rs_imp') AS rs_imp, slope_json[2:] AS slope_profile
FROM x;

	
-- cursor version
CREATE OR REPLACE FUNCTION public.compute_ways_slope_profile3(table_update boolean)
 RETURNS SETOF jsonb[]
 LANGUAGE plpgsql
AS $function$
declare 
cur refcursor;
rec record;
way_id integer;
retval jsonb[];
BEGIN	
	
	IF NOT EXISTS(SELECT relname FROM pg_class WHERE relname='w_split_multi3') THEN
		CREATE TEMP TABLE IF NOT EXISTS w_split_multi3(id integer primary key, wid integer, length_m numeric, geom geometry[]); 
		CREATE INDEX IF NOT EXISTS idx_w_split_multi3_wid ON w_split_multi3 USING btree(wid);
	else 
		TRUNCATE w_split_multi3;
	end if;

	EXECUTE format(
		'INSERT INTO w_split_multi3
		WITH x as (
			SELECT id as wid, length_m::numeric, split_long_way2(geom,length_m::numeric,30) AS geom 	
			FROM ways 
			WHERE class_id::text NOT IN(SELECT UNNEST(select_from_variable_container(''excluded_class_id_cycling'')))
			AND length_m >= (SELECT select_from_variable_container_s(''resolution_dem'')::integer)
		)
		SELECT ROW_NUMBER() OVER() AS id, wid, length_m, geom
		FROM x	'	
	);	
	
	open cur for
	select wid from w_split_multi3;

	
	loop 
		fetch cur into way_id;
		EXIT WHEN NOT FOUND;
		
	
		WITH 
		w_unnested as (
			select row_number() over () as rnum, 
			w.wid, length_m AS original_length, 
			point as start,lead(point) over () as end
			FROM w_split_multi3 w, unnest(w.geom) point
			where w.wid = way_id
		),
		es AS (
			SELECT w.rnum, w.wid, w.start, d.val e_start, st_distance(w.start::geography,w.end::geography ) as length_m
			FROM w_unnested w, dem_vec d 
			WHERE ST_Contains(d.geom, w.start) and w.end is not null
		),
		ee AS (
			SELECT w.rnum, w.wid, w.original_length, w.end, d.val e_end
			FROM w_unnested w, dem_vec d 
			WHERE ST_Contains(d.geom, w.end) and w.end is not null
		),
		split_slope AS (
			SELECT es.wid, es.start, ee.end, ee.original_length,es.length_m, 
			(es.e_start-ee.e_end)/es.length_m AS slope,
			slope_impedance((100*(es.e_start-ee.e_end)/es.length_m)::NUMERIC) AS s_imp
			FROM es,ee
			WHERE es.rnum = ee.rnum
		),
		x AS (
			SELECT array_agg(jsonb_build_object('start',s.start,'end',s.end,'length',length_m,'slope',slope,'imp',s_imp)) slope_profile,
			SUM((length_m/original_length)*s_imp[1])::NUMERIC s_imp,
			SUM((length_m/original_length)*s_imp[2])::NUMERIC rs_imp,
			wid
			FROM split_slope s
			group by wid
		)
		SELECT jsonb_build_object('s_imp',s_imp,'rs_imp',rs_imp,'id',x.wid) || slope_profile 
		into retval
		FROM x;
		
		return next retval;

	end loop;
END;
$function$
;

drop table temp_slopes;
CREATE TEMP TABLE temp_slopes AS
WITH x AS (
SELECT compute_ways_slope_profile3(TRUE) AS slope_json
)
SELECT (slope_json[1] ->> 'id') AS id, (slope_json[1] ->> 's_imp') AS s_imp, (slope_json[1] ->> 'rs_imp') AS rs_imp, slope_json[2:] AS slope_profile
FROM x;


-- batch version with loop over 1000(default) ways per iteration

drop function compute_ways_slope_profile4;
CREATE OR REPLACE FUNCTION public.compute_ways_slope_profile4(subsample_size int default 1000, table_update boolean default false)
 RETURNS SETOF jsonb[]
 LANGUAGE plpgsql
AS $function$
declare 
i integer = 0;
BEGIN	
	
	IF NOT EXISTS(SELECT relname FROM pg_class WHERE relname='w_split_multi4') THEN
		CREATE TEMP TABLE IF NOT EXISTS w_split_multi4(id integer primary key, wid integer, length_m numeric, geom geometry[]); 
		CREATE INDEX IF NOT EXISTS idx_w_split_multi4_wid ON w_split_multi4 USING btree(wid);
	else 
		TRUNCATE w_split_multi4;
	end if;

	-- table for result set
	IF NOT EXISTS(SELECT relname FROM pg_class WHERE relname='ways_slope_profiles') THEN
		CREATE TEMP TABLE IF NOT EXISTS ways_slope_profiles(sp jsonb[]); 
	else 
		TRUNCATE ways_slope_profiles;
	end if; 
	

	INSERT INTO w_split_multi4
		WITH x as (
			SELECT id as wid, length_m::numeric, split_long_way2(geom,length_m::numeric,30) AS geom 	
			FROM ways 
			WHERE class_id::text NOT IN(SELECT UNNEST(select_from_variable_container('excluded_class_id_cycling')))
			AND length_m >= (SELECT select_from_variable_container_s('resolution_dem')::integer)
		)
		SELECT ROW_NUMBER() OVER() AS id, wid, length_m, geom
		FROM x	; 	
	
	loop 		
		insert into ways_slope_profiles
		with w_split as (
			select wid, length_m, geom 
			FROM w_split_multi4 w
			order by wid
			limit subsample_size offset subsample_size*i
		),
		w_unnested as (
			select row_number() over (order by w.wid) as rnum, 
			w.wid, length_m AS original_length, 
			point as start,lead(point) over (partition by wid) as end
			FROM w_split w, unnest(w.geom) point
		),
		es AS (
			SELECT w.rnum, w.wid, w.start, d.val e_start, st_distance(w.start::geography,w.end::geography ) as length_m
			FROM w_unnested w, dem_vec d 
			WHERE ST_Contains(d.geom, w.start) and w.end is not null
		),
		ee AS (
			SELECT w.rnum, w.wid, w.original_length, w.end, d.val e_end
			FROM w_unnested w, dem_vec d 
			WHERE ST_Contains(d.geom, w.end) and w.end is not null
		),
		split_slope AS (
			SELECT es.wid, es.start, ee.end, ee.original_length,es.length_m, 
			(es.e_start-ee.e_end)/es.length_m AS slope,
			slope_impedance((100*(es.e_start-ee.e_end)/es.length_m)::NUMERIC) AS s_imp
			FROM es,ee
			WHERE es.rnum = ee.rnum
		),
		x AS (
			SELECT array_agg(jsonb_build_object('start',s.start,'end',s.end,'length',length_m,'slope',slope,'imp',s_imp)) slope_profile,
			SUM((length_m/original_length)*s_imp[1])::NUMERIC s_imp,
			SUM((length_m/original_length)*s_imp[2])::NUMERIC rs_imp,
			wid
			FROM split_slope s
			group by wid
		)
		SELECT jsonb_build_object('s_imp',s_imp,'rs_imp',rs_imp,'id',x.wid) || slope_profile 
		FROM x;
		
		EXIT WHEN NOT FOUND;
		i = i+1;
	end loop;
	return query
	select sp from ways_slope_profiles;
	
END;
$function$
;

drop table temp_slopes;
CREATE TEMP TABLE temp_slopes AS
WITH x AS (
SELECT compute_ways_slope_profile4(10000) AS slope_json
)
SELECT (slope_json[1] ->> 'id') AS id, (slope_json[1] ->> 's_imp') AS s_imp, (slope_json[1] ->> 'rs_imp') AS rs_imp, slope_json[2:] AS slope_profile
FROM x;


