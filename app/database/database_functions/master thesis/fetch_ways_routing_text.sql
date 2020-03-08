DROP FUNCTION IF EXISTS fetch_ways_routing_text;
CREATE OR REPLACE FUNCTION public.fetch_ways_routing_text(buffer_geom text, modus_input integer, userid_input integer, routing_profile text)
 RETURNS TEXT
 
AS $function$
DECLARE 
	excluded_ways_id text;
	sql_ways_ids text := '';
	sql_userid text := '';
	sql_routing_profile text := '';
	sql_geom text := format(' AND geom && ST_GeomFromText(''%s'')',buffer_geom);
	table_name text := 'ways';
	excluded_class_id text;
	filter_categories text;
	category text := jsonb_build_object('walking','foot','cycling','bicycle') ->>  split_part(routing_profile,'_',1);
	sql_cost text := jsonb_build_object(
	'cycling','length_m*(1+COALESCE(s_imp,0)+COALESCE(impedance_surface,0))::float as cost,length_m*(1+COALESCE(rs_imp,0)+COALESCE(impedance_surface,0))::float as reverse_cost',
	'walking', 'length_m as cost, length_m as reverse_cost'
	) ->> split_part(routing_profile,'_',1);
	userid_vertex integer;
	sql_select_ways text;
	
BEGIN 

	excluded_class_id = (select_from_variable_container('excluded_class_id_' || split_part(routing_profile,'_',1)))::text;
  	filter_categories = (select_from_variable_container('categories_no_' || category))::text;

	IF modus_input <> 1 THEN 
		table_name = 'ways_userinput';
		excluded_ways_id = ids_modified_features(userid_input,'ways');

		sql_userid = ' AND( userid IS NULL OR userid='||userid_input||')';
		sql_ways_ids = ' AND NOT id::int4 = any('''|| ids_modified_features(userid_input,'ways')::text ||''') ';
	END IF;
	
	raise notice '%',sql_ways_ids;

	IF  routing_profile = 'walking_safe_night' THEN
		sql_routing_profile = 'AND (lit_classified = ''yes'' OR lit_classified = ''unclassified'')';
	ELSEIF routing_profile = 'walking_wheelchair' THEN
		sql_routing_profile = 'AND ((wheelchair_classified = ''yes'') OR wheelchair_classified = ''limited''
		OR wheelchair_classified = ''unclassified'')';
	END IF;
	RAISE NOTICE '%',category;

	sql_select_ways = 
		'SELECT id::integer, source, target,'||sql_cost||',slope_profile,death_end, st_x(st_startpoint(geom)) AS x1, st_y(st_startpoint(geom)) AS y1, st_x(st_endpoint(geom)) AS x2, st_y(st_endpoint(geom)) AS y2, geom  
		FROM '||quote_ident(table_name)||
		' WHERE NOT class_id = ANY('''||excluded_class_id||''')
    	AND (NOT '||quote_ident(category)||' = ANY('''||filter_categories||''') 
		OR '||quote_ident(category)||' IS NULL)
		'||sql_geom||sql_userid||sql_ways_ids||sql_routing_profile;

	return sql_select_ways;
END;
$function$
LANGUAGE plpgsql;



SELECT fetch_ways_routing_text(st_astext(st_buffer(geom, 0.01)), 1, 1, 'walking_standard')
FROM pois_userinput 
WHERE gid = 4128



-------------------------------------------------------
DROP TABLE IF EXISTS chunk;
CREATE TABLE chunk AS
SELECT id::integer, source, target,length_m as cost, length_m as reverse_cost,slope_profile,death_end, st_x(st_startpoint(geom)) AS x1, st_y(st_startpoint(geom)) AS y1, st_x(st_endpoint(geom)) AS x2, st_y(st_endpoint(geom)) AS y2, geom  
		FROM ways WHERE NOT class_id = ANY('{0,101,102,103,104,105,106,107,501,502,503,504,701,801}')
    	AND (NOT foot = ANY('{use_sidepath,no}') 
		OR foot IS NULL)
		 AND geom && ST_GeomFromText('POLYGON((11.2436966160431 48.1853912579027,11.2435044688472 48.1834403546825,11.2429354113683 48.181564423579,11.2420113121662 48.1798355555725,11.240767683855 48.1783201900908,11.2392523183733 48.1770765617796,11.2375234503668 48.1761524625776,11.2356475192633 48.1755834050986,11.2336966160431 48.1753912579027,11.231745712823 48.1755834050986,11.2298697817195 48.1761524625776,11.2281409137129 48.1770765617796,11.2266255482313 48.1783201900908,11.2253819199201 48.1798355555725,11.224457820718 48.181564423579,11.2238887632391 48.1834403546825,11.2236966160431 48.1853912579027,11.2238887632391 48.1873421611228,11.224457820718 48.1892180922263,11.2253819199201 48.1909469602329,11.2266255482313 48.1924623257145,11.2281409137129 48.1937059540257,11.2298697817195 48.1946300532278,11.231745712823 48.1951991107067,11.2336966160431 48.1953912579027,11.2356475192633 48.1951991107067,11.2375234503668 48.1946300532278,11.2392523183733 48.1937059540257,11.240767683855 48.1924623257145,11.2420113121662 48.1909469602329,11.2429354113683 48.1892180922263,11.2435044688472 48.1873421611228,11.2436966160431 48.1853912579027))')




