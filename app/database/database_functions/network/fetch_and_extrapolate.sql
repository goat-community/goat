DROP FUNCTION IF EXISTS fetch_ways_routing;
CREATE OR REPLACE FUNCTION public.fetch_ways_routing(buffer_geom text, speed_input numeric, modus_input integer, userid_input integer, routing_profile text)
 RETURNS SETOF type_fetch_ways_routing
 LANGUAGE plpgsql
AS $function$
DECLARE 
	excluded_ways_id text;
	sql_ways_ids text := '';
	sql_userid text := '';
	sql_routing_profile text := '';
	table_name text := 'ways';
	excluded_class_id integer[];
	filter_categories text[];
	category text := jsonb_build_object('walking','foot','cycling','bicycle') ->>  split_part(routing_profile,'_',1);
	sql_cost text := jsonb_build_object(
	'cycling','length_m*(1+COALESCE(s_imp,0)+COALESCE(impedance_surface,0))::float as cost,length_m*(1+COALESCE(rs_imp,0)+COALESCE(impedance_surface,0))::float as reverse_cost',
	'walking', 'length_m as cost, length_m as reverse_cost'
	) ->> split_part(routing_profile,'_',1);
	userid_vertex integer;
	
BEGIN 

	excluded_class_id = select_from_variable_container('excluded_class_id_' || category);
  	filter_categories = select_from_variable_container('categories_no_' || category);

	IF modus_input <> 1 THEN 
		table_name = 'ways_userinput';
		excluded_ways_id = ids_modified_features(userid_input,'ways');

		sql_userid = ' AND userid IS NULL OR userid='||userid_input;
		sql_ways_ids = ' AND NOT id::int4 = any('''|| excluded_ways_id ||''') ';
	END IF;
	
	IF  routing_profile = 'walking_safe_night' THEN
		sql_routing_profile = 'AND (lit_classified = ''yes'' OR lit_classified = ''unclassified'')';
	ELSEIF routing_profile = 'walking_wheelchair' THEN
		sql_routing_profile = 'AND ((wheelchair_classified = ''yes'') OR wheelchair_classified = ''limited''
		OR wheelchair_classified = ''unclassified'')';
	END IF;
	RAISE NOTICE '%',sql_cost;
	RETURN query EXECUTE '
		SELECT  id::integer, source, target,'||sql_cost||',slope_profile,geom 
		FROM '||quote_ident(table_name)||
		' WHERE class_id NOT IN(SELECT UNNEST($1))
    	AND (foot NOT IN(SELECT UNNEST($2)) OR foot IS NULL)
		AND geom && ST_GeomFromText($3)'||sql_userid||sql_ways_ids||sql_routing_profile
	USING excluded_class_id, filter_categories,buffer_geom;
END;
$function$;


/*select fetch_ways_routing(ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.001)),1.33,1,1,'walking_standard');
*/

/*CREATE TABLE ways_safe AS 
select f.*, w.geom FROM ways w, (SELECT * FROM fetch_ways_routing(ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.005)),2.5,'{0,101,102,103,104,105,106,107,501,502,503,504,701,801}','{use_sidepath,no}',1,1,'walking_safe_night') AS ways_routing) f
WHERE w.id = f.id;
*/


DROP TABLE IF EXISTS temp_reached_vertices;
CREATE temp TABLE temp_reached_vertices
(
	start_vertex integer,
	node integer,
	edge integer,
	cnt integer,
	cost NUMERIC,
	geom geometry,
	objectid integer
);
DROP FUNCTION IF EXISTS extrapolate_reached_vertices;
CREATE OR REPLACE FUNCTION public.extrapolate_reached_vertices(max_cost NUMERIC, max_length_links NUMERIC, buffer_geom text, 
	speed NUMERIC ,userid_input integer, modus_input integer, routing_profile text )
RETURNS SETOF type_catchment_vertices_single
 LANGUAGE sql
AS $function$

WITH touching_network AS 
(
	SELECT t.start_vertex, w.id, w.geom, w.source, w.target, t.cost, t.node, t.edge, w.cost AS w_cost, t.objectid
	FROM temp_reached_vertices t, 
	fetch_ways_routing(buffer_geom,speed,modus_input,userid_input,routing_profile) as w 
	WHERE t.node = w.target 
	AND t.node <> w.source
	AND t.cost + (max_length_links/speed) > max_cost
	UNION ALL 
	SELECT t.start_vertex, w.id, w.geom, w.source, w.target, t.cost, t.node, t.edge, w.cost AS w_cost, t.objectid
	FROM temp_reached_vertices t, 
	fetch_ways_routing(buffer_geom,speed,modus_input,userid_input,routing_profile) as w 
	WHERE t.node <> w.target
	AND t.node = w.source
	AND t.cost + (max_length_links/speed) > max_cost
),
not_completely_reached_network AS (
	SELECT source
	FROM (
		SELECT source 
		FROM touching_network t 
		UNION ALL 
		SELECT target
		FROM touching_network t 
	) x
	GROUP BY x.source
	HAVING count(x.source) < 2
)
SELECT t.start_vertex::integer, 99999999 AS node, t.id::integer edges, max_cost AS cost, st_startpoint(st_linesubstring(geom,1-(max_cost-cost)/w_cost,1)) geom, st_linesubstring(geom,1-(max_cost-cost)/w_cost,1) as w_geom,objectid 
FROM touching_network t, not_completely_reached_network n 
WHERE t.SOURCE = n.source 
AND 1-(max_cost-cost)/w_cost BETWEEN 0 AND 1
UNION ALL 
SELECT t.start_vertex::integer, 99999999 AS node, t.id::integer edges, max_cost AS cost, st_endpoint(st_linesubstring(geom,0.0,(max_cost-cost)/w_cost)) geom,st_linesubstring(geom,0.0,(max_cost-cost)/w_cost) as w_geom, objectid
FROM touching_network t, not_completely_reached_network n
WHERE t.target = n.source 
AND (max_cost-cost)/w_cost BETWEEN 0 AND 1 
UNION ALL 
SELECT start_vertex, node, edge, cost, geom, null, objectid FROM temp_reached_vertices;

$function$;

/*select extrapolate_reached_vertices(100, 200, ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.001)), 1.33 ,1, 1, 'walking_standard');
*/