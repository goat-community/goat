DROP FUNCTION IF EXISTS fetch_ways_routing_edited;
CREATE OR REPLACE FUNCTION public.fetch_ways_routing_edited(buffer_geom text, speed_input numeric, modus_input integer, userid_input integer, routing_profile text)
 RETURNS SETOF type_fetch_ways_routing
 LANGUAGE plpgsql
AS $function$
DECLARE 
	excluded_ways_id text;
	sql_ways_ids text := '';
	sql_userid text := '';
	sql_routing_profile text := '';
	table_name text := 'ways';
	excluded_class_id text;
	categories_no_foot text;
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

	SELECT select_from_variable_container('excluded_class_id_walking'),
  	select_from_variable_container('categories_no_foot')
  	INTO excluded_class_id, categories_no_foot;

	IF  routing_profile = 'safe_night' THEN
		sql_routing_profile = 'AND (lit_classified = ''yes'' OR lit_classified = ''unclassified'')';
	ELSEIF routing_profile = 'wheelchair' THEN
		sql_routing_profile = 'AND ((wheelchair_classified = ''yes'') OR wheelchair_classified = ''limited''
		OR wheelchair_classified = ''unclassified'')';
	END IF; 

	RETURN query EXECUTE format(
		'SELECT  id::integer, source, target, length_m as cost, geom 
		FROM '||quote_ident(table_name)||
		' WHERE NOT class_id = any(''' || excluded_class_id || ''')
    	AND (NOT foot = any('''||categories_no_foot||''') OR foot IS NULL)
		AND geom && ST_GeomFromText('''||buffer_geom||''')'||sql_userid||sql_ways_ids||sql_routing_profile
	);
END;
$function$

/*select fetch_ways_routing_edited(ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.001)),1.33,'{0,101,102,103,104,105,106,107,501,502,503,504,701,801}','{use_sidepath,no}',1,1,'safe_night');
*/

/*CREATE TABLE ways_safe AS 
select f.*, w.geom FROM ways w, (SELECT * FROM fetch_ways_routing_edited(ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.005)),2.5,'{0,101,102,103,104,105,106,107,501,502,503,504,701,801}','{use_sidepath,no}',1,1,'safe_night') AS ways_routing) f
WHERE w.id = f.id;
*/