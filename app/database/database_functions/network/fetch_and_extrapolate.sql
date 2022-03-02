DROP FUNCTION IF EXISTS fetch_ways_routing;
CREATE OR REPLACE FUNCTION public.fetch_ways_routing(buffer_geom text, modus_input integer, scenario_id_input integer, speed_input numeric, routing_profile text)
 RETURNS SETOF type_fetch_ways_routing
 LANGUAGE plpgsql
AS $function$
DECLARE 
	excluded_ways_id text;
	sql_ways_ids text := '';
	sql_scenario_id text := '';
	sql_routing_profile text := '';
	sql_geom text := format(' AND geom && ST_GeomFromText(''%s'')',buffer_geom);
	table_name text := 'ways';
	excluded_class_id text;
	filter_categories text;
	transport_mode TEXT := split_part(routing_profile,'_',1);
	cost_function TEXT;
	category text := jsonb_build_object('walking','foot','cycling','bicycle') ->> transport_mode;
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
	ELSEif routing_profile = 'walking_comfort' THEN
		cost_function = 'walk_comfort';
	ELSEif routing_profile = 'cycling_comfort' THEN
		cost_function = 'cyc_comfort';
	ELSEif routing_profile = 'walking_wheelchair_comfort' THEN
		cost_function = 'whe_comfort';
	ELSE	
		cost_function = transport_mode;
	end IF;

	sql_cost = jsonb_build_object(
	'cycling','CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+COALESCE(s_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(s_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s END AS cost,
			   CASE WHEN crossing IS NOT NULL THEN (	''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+COALESCE(rs_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(rs_imp,0)+COALESCE(impedance_surface,0))::float)/%1$s END AS reverse_cost',
	'walking', 'length_m/%1$s as cost, length_m/%1$s as reverse_cost',
	'ebike', 'CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+-greatest(-COALESCE(s_imp,0),0)+COALESCE(impedance_surface,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(impedance_surface,0))::float)/%1$s END AS cost,
			   CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+-greatest(-COALESCE(rs_imp,0),0)+COALESCE(impedance_surface,0))::float)/%1$s)
			   ELSE (length_m*(1+COALESCE(impedance_surface,0))::float)/%1$s END AS reverse_cost',
	'walk_comfort','length_m*(1+COALESCE(impedance_was_type_road,0)+COALESCE(impedance_wac_type_road,0)
								+COALESCE(impedance_was_peak_hour,0)+COALESCE(impedance_wac_peak_hour,0)
								+COALESCE(impedance_was_cyclepath,0)+COALESCE(impedance_wac_cyclepath,0)
								+COALESCE(impedance_was_obstacle,0)+COALESCE(impedance_wac_obstacle,0)
								+COALESCE(impedance_was_sidewalk,0)+COALESCE(impedance_wac_sidewalk,0)
								+COALESCE(impedance_was_speedlimit,0)+COALESCE(impedance_wac_speedlimit,0))::float/%1$s AS cost,
					length_m*(1+COALESCE(impedance_was_type_road,0)+COALESCE(impedance_wac_type_road,0)
								+COALESCE(impedance_was_peak_hour,0)+COALESCE(impedance_wac_peak_hour,0)
								+COALESCE(impedance_was_cyclepath,0)+COALESCE(impedance_wac_cyclepath,0)
								+COALESCE(impedance_was_obstacle,0)+COALESCE(impedance_wac_obstacle,0)
								+COALESCE(impedance_was_sidewalk,0)+COALESCE(impedance_wac_sidewalk,0)
								+COALESCE(impedance_was_speedlimit,0)+COALESCE(impedance_wac_speedlimit,0))::float/%1$s AS reverse_cost',
	'cyc_comfort','CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+COALESCE(impedance_was_type_road,0)+COALESCE(impedance_wac_type_road,0)
								+COALESCE(impedance_was_peak_hour,0)+COALESCE(impedance_wac_peak_hour,0)
								+COALESCE(impedance_was_cyclepath,0)+COALESCE(impedance_wac_cyclepath,0)
								+COALESCE(impedance_was_obstacle,0)+COALESCE(impedance_wac_obstacle,0)
								+COALESCE(impedance_was_sidewalk,0)+COALESCE(impedance_wac_sidewalk,0)
								+COALESCE(impedance_was_speedlimit,0)+COALESCE(impedance_wac_speedlimit,0))::float)/%1$s) 
			   ELSE (length_m*(1+COALESCE(impedance_was_type_road,0)+COALESCE(impedance_wac_type_road,0)
								+COALESCE(impedance_was_peak_hour,0)+COALESCE(impedance_wac_peak_hour,0)
								+COALESCE(impedance_was_cyclepath,0)+COALESCE(impedance_wac_cyclepath,0)
								+COALESCE(impedance_was_obstacle,0)+COALESCE(impedance_wac_obstacle,0)
								+COALESCE(impedance_was_sidewalk,0)+COALESCE(impedance_wac_sidewalk,0)
								+COALESCE(impedance_was_speedlimit,0)+COALESCE(impedance_wac_speedlimit,0))::float)/%1$s END AS cost,
			   CASE WHEN crossing IS NOT NULL THEN (''%2$s''::jsonb ->> (''delay_'' || crossing_delay_category))::integer + ((length_m*(1+COALESCE(impedance_was_type_road,0)+COALESCE(impedance_wac_type_road,0)
								+COALESCE(impedance_was_peak_hour,0)+COALESCE(impedance_wac_peak_hour,0)
								+COALESCE(impedance_was_cyclepath,0)+COALESCE(impedance_wac_cyclepath,0)
								+COALESCE(impedance_was_obstacle,0)+COALESCE(impedance_wac_obstacle,0)
								+COALESCE(impedance_was_sidewalk,0)+COALESCE(impedance_wac_sidewalk,0)
								+COALESCE(impedance_was_speedlimit,0)+COALESCE(impedance_wac_speedlimit,0))::float)/%1$s)
			   ELSE (length_m*(1+COALESCE(impedance_was_type_road,0)+COALESCE(impedance_wac_type_road,0)
								+COALESCE(impedance_was_peak_hour,0)+COALESCE(impedance_wac_peak_hour,0)
								+COALESCE(impedance_was_cyclepath,0)+COALESCE(impedance_wac_cyclepath,0)
								+COALESCE(impedance_was_obstacle,0)+COALESCE(impedance_wac_obstacle,0)
								+COALESCE(impedance_was_sidewalk,0)+COALESCE(impedance_wac_sidewalk,0)
								+COALESCE(impedance_was_speedlimit,0)+COALESCE(impedance_wac_speedlimit,0))::float)/%1$s END AS reverse_cost',
	'whe_comfort','length_m*(1+COALESCE(impedance_was_type_road,0)+COALESCE(impedance_wac_type_road,0)
								+COALESCE(impedance_was_peak_hour,0)+COALESCE(impedance_wac_peak_hour,0)
								+COALESCE(impedance_was_cyclepath,0)+COALESCE(impedance_wac_cyclepath,0)
								+COALESCE(impedance_was_obstacle,0)+COALESCE(impedance_wac_obstacle,0)
								+COALESCE(impedance_was_sidewalk,0)+COALESCE(impedance_wac_sidewalk,0)
								+COALESCE(impedance_was_speedlimit,0)+COALESCE(impedance_wac_speedlimit,0))::float/%1$s AS cost,
					length_m*(1+COALESCE(impedance_was_type_road,0)+COALESCE(impedance_wac_type_road,0)
								+COALESCE(impedance_was_peak_hour,0)+COALESCE(impedance_wac_peak_hour,0)
								+COALESCE(impedance_was_cyclepath,0)+COALESCE(impedance_wac_cyclepath,0)
								+COALESCE(impedance_was_obstacle,0)+COALESCE(impedance_wac_obstacle,0)
								+COALESCE(impedance_was_sidewalk,0)+COALESCE(impedance_wac_sidewalk,0)
								+COALESCE(impedance_was_speedlimit,0)+COALESCE(impedance_wac_speedlimit,0))::float/%1$s AS reverse_cost'
) ->> cost_function;

	sql_cost = format(sql_cost, speed_input, time_loss_intersections::text);

  	RAISE NOTICE '%', sql_cost;
  	IF modus_input IN (2,4) THEN 
		table_name = 'ways_userinput';
		excluded_ways_id = ids_modified_features(scenario_id_input,'ways');

		sql_scenario_id = ' AND (scenario_id IS NULL OR scenario_id='||scenario_id_input||')';
		sql_ways_ids = ' AND NOT id::int4 = any('''|| ids_modified_features(scenario_id_input,'ways')::text ||''') ';
	END IF;

	IF  routing_profile = 'walking_safe_night' THEN
		sql_routing_profile = 'AND (lit_classified = ''yes'' OR lit_classified = ''unclassified'')';
	ELSEIF routing_profile = 'walking_wheelchair' THEN
		sql_routing_profile = 'AND ((wheelchair_classified = ''yes'') OR wheelchair_classified = ''limited''
		OR wheelchair_classified = ''unclassified'')';
	END IF;

	sql_select_ways = 
		'SELECT id::integer, source, target,length_m,'||sql_cost||',death_end,geom 
		FROM '||quote_ident(table_name)||
		' WHERE NOT class_id = ANY('''||excluded_class_id||''')
    	AND (NOT '||quote_ident(category)||' = ANY('''||filter_categories||''') 
		OR '||quote_ident(category)||' IS NULL)
		'||sql_geom||sql_scenario_id||sql_ways_ids||sql_routing_profile;
	return query execute sql_select_ways;
END;
$function$;


/*DROP TABLE IF exists test;
--select fetch_ways_routing(ST_ASTEXT(ST_BUFFER(ST_POINT(9.17979058,45.4721027),0.001)),1,1,1.33,'walking_standard');
CREATE TABLE test AS 
-- walking_comfort, cycling_comfort, walking_wheelchair_comfort
select *, COST-reverse_cost FROM fetch_ways_routing(ST_ASTEXT(ST_BUFFER(ST_POINT(9.17979058,45.4721027),0.03)),1,1,1.33,'cycling_comfort');
select * from test;
*/