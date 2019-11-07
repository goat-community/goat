DROP FUNCTION IF EXISTS pgrouting_edges_biking;
CREATE OR REPLACE FUNCTION public.pgrouting_edges_biking(minutes integer, x numeric, y numeric, user_type varchar, userid_input integer, objectid_input integer)
 RETURNS SETOF type_edges
 LANGUAGE plpgsql
AS $function$
--Declaring the used variables
DECLARE
r type_edges;
seconds numeric;
id_vertex integer;
excluded_class_id text;
u_speed numeric;
u_maxspeed numeric;
u_minspeed numeric;
u_maxslope numeric;
u_fact_distance numeric;
u_fact_slope numeric;
u_fact_street numeric;

tag_no text;
tag_adult text;
tag_senior text;
tag_pedelec text;
tag_dismount text;
tag_private text;

begin
--Defining tags that have influence on the bicycle routing
	tag_no='no';
	tag_dismount='dismount';
	tag_private='private;no';
	tag_adult='biking_group_adult';
	tag_senior='biking_group_senior';
	tag_pedelec='biking_group_pedelec';

	seconds = minutes * 60;

--Selecting the user group specific input parameters from the jsonb variable_object into further used variables
  SELECT variable_object ->> 'user_speed', variable_object ->> 'user_maxspeed', variable_object ->> 'user_minspeed',
		variable_object ->> 'user_maxslope', variable_object ->> 'user_factor_distance', variable_object ->> 'user_factor_slope', 
		variable_object ->> 'user_factor_street', variable_object ->> 'excluded_class'
  into u_speed, u_maxspeed, u_minspeed, u_maxslope, u_fact_distance, u_fact_slope, u_fact_street, excluded_class_id 
  FROM variable_container v
  where v.identifier = user_type;
  
--Snapping to the closest vertex within 50m. If no vertex is within 50m not calculation is started.
  SELECT id into id_vertex
   FROM ways_vertices_pgr v 
           WHERE ST_DWithin(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326), 250)
           ORDER BY ST_Distance(v.geom::geography, ST_SetSRID(ST_Point(x,y)::geography, 4326))
           limit 1;

--Setting the starting point to the above retrieved closest vertex
  update starting_point_isochrones set geometry = v.geom from ways_vertices_pgr v 
  where v.id = id_vertex and starting_point_isochrones.objectid = objectid_input; 

--The function Pgr_DrivingDistance delivers the reached network. The loop stores all the reached links so that a network is retrieved.
  FOR r IN select * from 
		  (SELECT t1.seq, t1.id1 AS Node, t1.id2 AS Edge, t1.cost, t2.geom FROM PGR_DrivingDistance(
--The routing is done on a modified table where the costs and navigatable network are calculated
		--The maxspeed is limited to the max allowed speed if the max userspeed is larger 
			'WITH user_speed_limits AS
			(SELECT id, length_m, length_dynamic, source, target, class_id, slope, bicycle, foot,
				(CASE WHEN ('||u_maxspeed||') > (maxspeed_forward) THEN (maxspeed_forward) ELSE ('||u_maxspeed||') END) AS u_maxspeed_forward,
				(CASE WHEN ('||u_maxspeed||') > (maxspeed_backward) THEN (maxspeed_backward) ELSE ('||u_maxspeed||') END) AS u_maxspeed_backward
			FROM public.ways),

		'--The actual speed is calculated without slope, with slope and with reverse slope' 
			'calculated_speeds AS
			(SELECT id, length_m, length_dynamic, u_maxspeed_forward, u_maxspeed_backward, source, target, class_id, bicycle, foot,
				(CASE WHEN '||u_speed||' > u_maxspeed_forward THEN u_maxspeed_forward ELSE '||u_speed||' END) AS speed_dt,
				(CASE WHEN slope > '||u_maxslope||' THEN '||u_minspeed||' ELSE 
					(CASE WHEN ((-(('||u_speed||'-'||u_minspeed||')/'||u_maxslope||')*slope)+'||u_speed||') > u_maxspeed_forward THEN u_maxspeed_forward 
						ELSE ((-(('||u_speed||'-'||u_minspeed||')/'||u_maxslope||')*slope)+'||u_speed||') END) END) AS speed_s,
				(CASE WHEN (-slope) > '||u_maxslope||' THEN '||u_minspeed||' ELSE 
					(CASE WHEN ((-(('||u_speed||'-'||u_minspeed||')/'||u_maxslope||')*(-slope))+'||u_speed||') > u_maxspeed_backward THEN u_maxspeed_backward 
						ELSE ((-(('||u_speed||'-'||u_minspeed||')/'||u_maxslope||')*(-slope))+'||u_speed||') END) END) AS reverse_speed_s
			FROM user_speed_limits),

		'--The actual speed is limited to walking speed if specific tags or street types occur' 
			'speeds_considering_walking AS
			(SELECT id, length_m, length_dynamic, u_maxspeed_forward, u_maxspeed_backward, source, target, class_id, bicycle, foot,
				(CASE WHEN '''||user_type||''' IN ('''||tag_adult||''', '''||tag_senior||''', '''||tag_pedelec||''') 
					THEN (CASE WHEN class_id IN (114,119,122) OR (bicycle IN ('''||tag_no||''', '''||tag_dismount||''', '''||tag_private||''') AND (foot IS NULL OR foot != ('''||tag_no||''')))
								THEN '||u_minspeed||' ELSE speed_dt END)
					ELSE (CASE WHEN class_id IN (122) THEN '||u_minspeed||' ELSE speed_dt END)END) AS speed_dt_walking,
				(CASE WHEN '''||user_type||''' IN ('''||tag_adult||''', '''||tag_senior||''', '''||tag_pedelec||''') 
					THEN (CASE WHEN class_id IN (114,119,122) OR (bicycle IN ('''||tag_no||''', '''||tag_dismount||''', '''||tag_private||''') AND (foot IS NULL OR foot != ('''||tag_no||''')))
								THEN '||u_minspeed||' ELSE speed_s END)
					ELSE (CASE WHEN class_id IN (122) THEN '||u_minspeed||' ELSE speed_s END)END) AS speed_s_walking,
				(CASE WHEN '''||user_type||''' IN ('''||tag_adult||''', '''||tag_senior||''', '''||tag_pedelec||''') 
					THEN (CASE WHEN class_id IN (114,119,122) OR (bicycle IN ('''||tag_no||''', '''||tag_dismount||''', '''||tag_private||''') AND (foot IS NULL OR foot != ('''||tag_no||''')))
								THEN '||u_minspeed||' ELSE reverse_speed_s END)
					ELSE (CASE WHEN class_id IN (122) THEN '||u_minspeed||' ELSE reverse_speed_s END)END) AS reverse_speed_s_walking
			FROM calculated_speeds),
			
		'--The costs are calculated from the retrieved speeds using user specific normalized weighting' 
			'calculated_costs AS
			(SELECT id, source, target, class_id, bicycle, foot,
				(((length_m/(speed_dt_walking/3.6)) * '||u_fact_distance||') + 
				((length_dynamic/(speed_dt_walking/3.6)) * '||u_fact_street||') +
				((length_m/(speed_s_walking/3.6)) * '||u_fact_slope||')) AS cost,
				(((length_m/(speed_dt_walking/3.6)) * '||u_fact_distance||') + 
				((length_dynamic/(speed_dt_walking/3.6)) * '||u_fact_street||') +
				((length_m/(reverse_speed_s_walking/3.6)) * '||u_fact_slope||')) AS reverse_cost  
			FROM speeds_considering_walking)
			
		'--The relevant parameters are selected and some street types and tags are excluded from the calculation' 
			'SELECT id::int4, source, target, cost, reverse_cost FROM calculated_costs
			WHERE cost IS NOT NULL
			AND ((bicycle NOT IN ('''||tag_no||''') OR bicycle IS null) AND (foot NOT IN ('''||tag_no||''')OR foot IS NULL))
			AND NOT class_id = any(''' || excluded_class_id || ''')',
  		  id_vertex, 
	       seconds, true, false) t1, ways t2
           WHERE t1.id2 = t2.id) as route
           LOOP
  RETURN NEXT r;
  
  END LOOP;
  RETURN;
END ;
$function$
