DROP FUNCTION IF EXISTS fetch_ways_routing;
CREATE OR REPLACE FUNCTION public.fetch_ways_routing(buffer_geom text, speed_input NUMERIC, excluded_class_id text[], categories_no_foot text[], modus_input integer, userid_input integer)
RETURNS SETOF type_fetch_ways_routing
AS $function$
DECLARE 
	excluded_ways_id text;
	sql_ways_ids text := '';
	sql_userid text := '';
	table_name text := 'ways';
BEGIN 
	IF modus_input <> 1 THEN 
		table_name = 'ways_userinput';
		SELECT array_append(array_agg(x.id),0)::text 
		INTO excluded_ways_id 
		FROM (
			SELECT Unnest(deleted_feature_ids)::integer id 
			FROM user_data
			WHERE id = userid_input
			UNION ALL
			SELECT original_id::integer modified
			FROM ways_modified 
			WHERE userid = userid_input AND original_id IS NOT NULL
		) x;
		sql_userid = ' AND userid IS NULL OR userid='||userid_input;
		sql_ways_ids = ' AND NOT id::int4 = any('''|| excluded_ways_id ||''') ';
	END IF;
	RETURN query EXECUTE format(
		'SELECT  id::integer, source, target, length_m as cost 
		FROM '||quote_ident(table_name)||
		' WHERE NOT class_id = any(''' || excluded_class_id::text || ''')
    	AND (NOT foot = any('''||categories_no_foot::text||''') OR foot IS NULL)
		AND geom && ST_GeomFromText('''||buffer_geom||''')'||sql_userid||sql_ways_ids
	);
END;
$function$ LANGUAGE plpgsql;