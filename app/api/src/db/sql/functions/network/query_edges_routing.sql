CREATE OR REPLACE FUNCTION basic.query_edges_routing(buffer_geom text, modus_input text, scenario_id_input integer, speed_input float, routing_profile TEXT, coordinates_only BOOLEAN)
 RETURNS text
 LANGUAGE plpgsql
AS $function$
DECLARE 
	sql_ways_ids text := '';
	sql_scenario_id text := '';
	sql_routing_profile text := '';
	sql_geom text := format(' AND ST_Intersects(geom, ST_SETSRID(ST_GEOMFROMTEXT(''%1$s''), 4326))', buffer_geom);
	excluded_class_id text;
	filter_categories text;
	transport_mode TEXT := split_part(routing_profile,'_',1);
	cost_function TEXT;
	category text := jsonb_build_object('walking','foot','cycling','bicycle') ->> transport_mode;
	sql_select_ways text;
	sql_cost TEXT;
	time_loss_intersections jsonb := '{}'::jsonb;
	geom_column TEXT = 'geom';
	setting_study_area_id integer;

BEGIN 
	IF modus_input = 'default' THEN 
		scenario_id_input = 0;
	END IF;

	setting_study_area_id = basic.get_reference_study_area(ST_SETSRID(ST_CENTROID(buffer_geom), 4326));
	
	excluded_class_id = (basic.select_customization('excluded_class_id_' || transport_mode, setting_study_area_id))::text;
	excluded_class_id = substr(excluded_class_id, 2, length(excluded_class_id) - 2);

  	filter_categories = replace(basic.select_customization('categories_no_' || category, setting_study_area_id)::TEXT, '"', '''');
	filter_categories = substr(filter_categories, 2, length(filter_categories) - 2);

  	IF transport_mode IN ('cycling','ebike') THEN
  		time_loss_intersections = basic.select_customization('cycling_crossings_delay', setting_study_area_id);
  	END IF;
	
	IF routing_profile = 'cycling_pedelec' THEN 
		cost_function = 'ebike';
	ELSE
		cost_function = transport_mode;
	END IF;

	sql_cost = jsonb_build_object(
	'cycling','CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+COALESCE(s_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(s_imp,0)+COALESCE(impedance_surface,0))::float)/
			   CASE WHEN bicycle IN (''no'', ''dismount'') THEN 1.33 ELSE %1$s END END AS cost,
			   CASE WHEN crossing IS NOT NULL THEN (	''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+COALESCE(rs_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(rs_imp,0)+COALESCE(impedance_surface,0))::float)/
			   CASE WHEN bicycle IN (''no'', ''dismount'') THEN 1.33 ELSE %1$s END END AS reverse_cost',
	'walking', 'length_m/%1$s as cost, length_m/%1$s as reverse_cost',
	'ebike', 'CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+-greatest(-COALESCE(s_imp,0),0)+COALESCE(impedance_surface,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(impedance_surface,0))::float)/
			   CASE WHEN bicycle IN (''no'', ''dismount'') THEN 1.33 ELSE %1$s END END AS cost,
			   CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+-greatest(-COALESCE(rs_imp,0),0)+COALESCE(impedance_surface,0))::float)/%1$s)
			   ELSE (length_m*(1+COALESCE(impedance_surface,0))::float)/
               CASE WHEN bicycle IN (''no'', ''dismount'') THEN 1.33 ELSE %1$s END END AS reverse_cost'
	) ->> cost_function;

	sql_cost = format(sql_cost, speed_input, time_loss_intersections::text);

  	
	sql_scenario_id = ' AND (scenario_id IS NULL OR scenario_id='||scenario_id_input||')';

	IF modus_input = 'scenario' THEN 
		sql_ways_ids = ' AND NOT id::int4 = any('''|| basic.modified_edges(scenario_id_input)::text ||''') ';
	END IF;

	IF  routing_profile = 'walking_safe_night' THEN
		sql_routing_profile = 'AND (lit_classified = ''yes'' OR lit_classified = ''unclassified'')';
	ELSEIF routing_profile = 'walking_wheelchair' THEN
		sql_routing_profile = 'AND ((wheelchair_classified = ''yes'') OR wheelchair_classified = ''limited''
		OR wheelchair_classified = ''unclassified'')';
	END IF;
	
	IF coordinates_only = TRUE THEN
		geom_column = 'coordinates_3857'; 
	END IF; 


	sql_select_ways = 
		'SELECT id::integer, source, target, length_3857,'||sql_cost||',death_end,'||quote_ident(geom_column)||', NULL AS starting_ids, NULL AS starting_geoms
		FROM basic.edge
		WHERE class_id NOT IN ('||excluded_class_id||')
    	AND ('||quote_ident(category)||' NOT IN ('||filter_categories||') 
		OR '||quote_ident(category)||' IS NULL)
		'||sql_geom||sql_scenario_id||sql_ways_ids||sql_routing_profile;
	return sql_select_ways;
END;
$function$;

/*Produces the sql query as text to fetch the network*/
/*
SELECT basic.query_edges_routing(ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.0018)),'default',0,1.33,'walking_standard',true)
*/

