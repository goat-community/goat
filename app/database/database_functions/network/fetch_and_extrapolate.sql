DROP FUNCTION IF EXISTS fetch_ways_routing;
CREATE OR REPLACE FUNCTION public.fetch_ways_routing(buffer_geom text, modus_input integer, userid_input integer, speed_input numeric, routing_profile text)
 RETURNS SETOF type_fetch_ways_routing
 LANGUAGE plpgsql
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
	transport_mode TEXT := split_part(routing_profile,'_',1);
	cost_function TEXT;
	category text := jsonb_build_object('walking','foot','cycling','bicycle') ->> transport_mode;
	userid_vertex integer;
	sql_select_ways text;
	sql_cost TEXT;
	time_loss_intersections jsonb := '{}'::jsonb;
	
BEGIN 
	
	excluded_class_id = (select_from_variable_container('excluded_class_id_' || transport_mode))::text;
  	filter_categories = (select_from_variable_container('categories_no_' || category))::text;
	
  	IF transport_mode IN ('cycling','ebike') THEN
  		time_loss_intersections = select_from_variable_container_o('cycling_crossings_delay');
  	END IF;
	
	IF routing_profile = 'cycling_pedelec' THEN 
		cost_function = 'ebike';
	ELSE
		cost_function = transport_mode;
	END IF;

	sql_cost = jsonb_build_object(
	'cycling','CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+COALESCE(s_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(s_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s END AS cost,
			   CASE WHEN crossing IS NOT NULL THEN (	''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+COALESCE(rs_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(rs_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s END AS reverse_cost',
	'walking', 'length_m/%1$s as cost, length_m/%1$s as reverse_cost',
	'ebike', 'CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+-greatest(-COALESCE(s_imp,0),0)+COALESCE(impedance_surface,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(impedance_surface,0))::float)/%1$s END AS cost,
			   CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+-greatest(-COALESCE(rs_imp,0),0)+COALESCE(impedance_surface,0))::float)/%1$s)
			   ELSE (length_m*(1+COALESCE(impedance_surface,0))::float)/%1$s END AS reverse_cost'
	) ->> cost_function;

	sql_cost = format(sql_cost, speed_input, time_loss_intersections::text);

  	RAISE NOTICE '%', sql_cost;
  	IF modus_input <> 1 THEN 
		table_name = 'ways_userinput';
		excluded_ways_id = ids_modified_features(userid_input,'ways');

		sql_userid = ' AND( userid IS NULL OR userid='||userid_input||')';
		sql_ways_ids = ' AND NOT id::int4 = any('''|| ids_modified_features(userid_input,'ways')::text ||''') ';
	END IF;

	IF  routing_profile = 'walking_safe_night' THEN
		sql_routing_profile = 'AND (lit_classified = ''yes'' OR lit_classified = ''unclassified'')';
	ELSEIF routing_profile = 'walking_wheelchair' THEN
		sql_routing_profile = 'AND ((wheelchair_classified = ''yes'') OR wheelchair_classified = ''limited''
		OR wheelchair_classified = ''unclassified'')';
	END IF;

	sql_select_ways = 
		'SELECT id::integer, source, target,'||sql_cost||',slope_profile,death_end,geom 
		FROM '||quote_ident(table_name)||
		' WHERE NOT class_id = ANY('''||excluded_class_id||''')
    	AND (NOT '||quote_ident(category)||' = ANY('''||filter_categories||''') 
		OR '||quote_ident(category)||' IS NULL)
		'||sql_geom||sql_userid||sql_ways_ids||sql_routing_profile;
	return query execute sql_select_ways;
END;
$function$;

/*select fetch_ways_routing(ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.001)),1,1,1.33,'walking_standard');
CREATE TABLE test AS 
select *, COST-reverse_cost FROM fetch_ways_routing(ST_ASTEXT(ST_BUFFER(ST_POINT(11.25196,48.18172),0.03)),1,1,1.33,'cycling_standard');

*/

DROP FUNCTION IF EXISTS get_reached_network;
CREATE OR REPLACE FUNCTION public.get_reached_network(objectid_input integer,max_cost NUMERIC, number_isochrones integer, edges_to_exclude bigint[])
RETURNS void AS
$$
DECLARE
	i NUMERIC;
	step_isochrone NUMERIC := max_cost/number_isochrones;
BEGIN
	INSERT INTO edges(edge,node,cost,geom,v_geom,objectid) 
	SELECT w.id,s.node,CASE WHEN s.cost > f.cost THEN s.cost ELSE f.cost END AS cost,w.geom,s.geom AS v_geom,objectid_input
	FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
	WHERE f.node = w.source 
	AND s.node = w.target;
	
	
	FOR i IN SELECT generate_series(step_isochrone,max_cost,step_isochrone)
	LOOP
		INSERT INTO edges 
		SELECT x.id AS edge, x.node, i AS cost, ST_LINESUBSTRING(x.geom,1-((i-x.agg_cost)/x.cost),1) AS geom,
		ST_STARTPOINT(ST_LINESUBSTRING(x.geom,1-((i-x.agg_cost)/x.cost),1)) AS v_geom, objectid_input 
		FROM 
		(
			SELECT w.id, v.node, v.cost agg_cost, w.cost, w.geom
			FROM temp_reached_vertices v, temp_fetched_ways w
			WHERE v.node = w.target
			AND w.death_end IS NULL 
			AND v.cost < i
		) x
		LEFT JOIN (SELECT edge FROM edges e WHERE e.objectid = objectid_input AND cost < i) e
		ON x.id = e.edge 
		WHERE e.edge IS NULL
		AND x.id NOT IN(SELECT UNNEST(edges_to_exclude))
		UNION ALL 
		SELECT x.id AS edge, x.node, i AS cost, ST_LINESUBSTRING(x.geom,0,((i-x.agg_cost)/x.cost)) AS geom,
		ST_ENDPOINT(ST_LINESUBSTRING(x.geom,0,(i-x.agg_cost)/x.cost)) AS v_geom, objectid_input 
		FROM 
		(
			SELECT w.id, v.node, v.cost agg_cost, w.cost, w.geom 
			FROM temp_reached_vertices v, temp_fetched_ways w
			WHERE v.node = w.source
			AND w.death_end IS NULL 
			AND v.cost < i
		) x
		LEFT JOIN (SELECT edge FROM edges e WHERE e.objectid = objectid_input AND cost < i) e
		ON x.id = e.edge 
		WHERE e.edge IS NULL
		AND x.id NOT IN(SELECT UNNEST(edges_to_exclude));
	
	END LOOP;
	
	INSERT INTO edges	
	SELECT w.id AS edge,v.node,CASE WHEN w.SOURCE = v.node THEN v.cost + w.cost ELSE v.cost + w.reverse_cost END AS cost, 
	w.geom,CASE WHEN w.source = v.node THEN ST_ENDPOINT(w.geom) ELSE ST_STARTPOINT(w.geom) END AS v_geom,objectid_input
	FROM temp_reached_vertices v, temp_fetched_ways w 
	WHERE v.death_end = TRUE 
	AND v.node = w.death_end
	AND w.cost < (max_cost-v.cost);
	
END;
$$ LANGUAGE plpgsql;
