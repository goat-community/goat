--add the required data to the table test
alter table test ADD COLUMN IF NOT EXISTS tunnel text;
alter table test ADD COLUMN IF NOT EXISTS bridge text;
UPDATE test
set tunnel = p.tunnel,
	bridge = p.bridge
FROM planet_osm_line p
WHERE test.osm_id = p.osm_id;

--add new column to the test table
ALTER TABLE test ADD COLUMN IF NOT EXISTS  cyclepath_classified text;
ALTER TABLE test ADD COLUMN IF NOT EXISTS  obstacle_classified text;

-----------------------------------------------
--add impedance factor for walking speed (was)

	--add specific impedance column
	--was_type_road
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_was_type_road numeric;
	--was_peak_hour
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_was_peak_hour numeric;
	--was_cyclepath
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_was_cyclepath numeric;
	--was_sidewalk
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_was_sidewalk numeric;
	--was_was_obstacle
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_was_obstacle numeric;
	--was_speedlimit	
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_was_speedlimit numeric;
	--was_surface
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_was_surface numeric;
	--was_smoothness
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_was_smoothness numeric;
	
	--Type of road
	UPDATE test SET impedance_was_type_road = (select_from_variable_container_s('was_type_road'))::NUMERIC 
	WHERE highway IS NOT null
	AND (tunnel = 'yes' or bridge = 'yes')
	and highway IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'sidewalk_links');
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath
	with tags as
	(
		SELECT select_from_variable_container_o('class_cyclepath')  AS class_cyclepath
	
	)
	UPDATE test w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_was_cyclepath = (select_from_variable_container_o('was_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_cyclepath')));
	
	--Sidewalks
	UPDATE test SET impedance_was_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'was_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE test w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_was_obstacle = (select_from_variable_container_o('was_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_obstacle')));
	     
	--Surface
	UPDATE test SET impedance_was_surface = (select_from_variable_container_o('was_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_surface')));
	
	--Smoothness
	UPDATE test SET impedance_was_smoothness = (select_from_variable_container_o('was_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_smoothness')));

-----------------------------------------------

-----------------------------------------------
--add impedance factor for walking comfort (wac)

	--add specific impedance column
	--wac_type_road
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_wac_type_road numeric;
	--wac_peak_hour
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_wac_peak_hour numeric;
	--wac_cyclepath
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_wac_cyclepath numeric;
	--wac_sidewalk
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_wac_sidewalk numeric;
	--wac_obstacle
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_wac_obstacle numeric;
	--wac_speedlimit	
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_wac_speedlimit numeric;
	--wac_surface
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_wac_surface numeric;
	--wac_smoothness
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_wac_smoothness numeric;
	
	--Type of road
	UPDATE test SET impedance_wac_type_road = (select_from_variable_container_s('wac_type_road'))::NUMERIC 
	WHERE highway IS NOT null
	AND (tunnel = 'yes' or bridge = 'yes')
	and highway IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'sidewalk_links');
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath
	with tags as
	(
		SELECT select_from_variable_container_o('class_cyclepath')  AS class_cyclepath
	
	)
	UPDATE test w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_wac_cyclepath = (select_from_variable_container_o('wac_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_cyclepath')));
	
	--Sidewalks
	UPDATE test SET impedance_wac_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'wac_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE test w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_wac_obstacle = (select_from_variable_container_o('wac_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_obstacle')));
	     
	--Surface
	UPDATE test SET impedance_wac_surface = (select_from_variable_container_o('wac_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_surface')));
	
	--Smoothness
	UPDATE test SET impedance_wac_smoothness = (select_from_variable_container_o('wac_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_smoothness')));

-----------------------------------------------

-----------------------------------------------
--add impedance factor for cycling speed (cys)

	--add specific impedance column
	--cys_type_road
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cys_type_road numeric;
	--cys_peak_hour
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cys_peak_hour numeric;
	--cys_cyclepath
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cys_cyclepath numeric;
	--cys_sidewalk
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cys_sidewalk numeric;
	--cys_obstacle
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cys_obstacle numeric;
	--cys_speedlimit	
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cys_speedlimit numeric;
	--cys_surface
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cys_surface numeric;
	--cys_smoothness
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cys_smoothness numeric;
	
	--Type of road
	UPDATE test SET impedance_cys_type_road = (select_from_variable_container_s('cys_type_road'))::NUMERIC 
	WHERE highway IS NOT null
	AND (tunnel = 'yes' or bridge = 'yes')
	and highway IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'sidewalk_links');
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath
	with tags as
	(
		SELECT select_from_variable_container_o('class_cyclepath')  AS class_cyclepath
	
	)
	UPDATE test w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_cys_cyclepath = (select_from_variable_container_o('cys_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_cyclepath')));
	
	--Sidewalks
	UPDATE test SET impedance_cys_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'cys_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE test w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_cys_obstacle = (select_from_variable_container_o('cys_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_obstacle')));
	     
	--Surface
	UPDATE test SET impedance_cys_surface = (select_from_variable_container_o('cys_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_surface')));
	
	--Smoothness
	UPDATE test SET impedance_cys_smoothness = (select_from_variable_container_o('cys_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_smoothness')));

-----------------------------------------------

-----------------------------------------------
--add impedance factor for cycling comfort (cyc)

	--add specific impedance column
	--cyc_type_road
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cyc_type_road numeric;
	--cyc_peak_hour
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cyc_peak_hour numeric;
	--cyc_cyclepath
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cyc_cyclepath numeric;
	--cyc_sidewalk
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cyc_sidewalk numeric;
	--cyc_obstacle
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cyc_obstacle numeric;
	--cyc_speedlimit	
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cyc_speedlimit numeric;
	--cyc_surface
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cyc_surface numeric;
	--cyc_smoothness
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_cyc_smoothness numeric;
	
	--Type of road
	UPDATE test SET impedance_cyc_type_road = (select_from_variable_container_s('cyc_type_road'))::NUMERIC 
	WHERE highway IS NOT null
	AND (tunnel = 'yes' or bridge = 'yes')
	and highway IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'sidewalk_links');
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath
	with tags as
	(
		SELECT select_from_variable_container_o('class_cyclepath')  AS class_cyclepath
	
	)
	UPDATE test w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_cyc_cyclepath = (select_from_variable_container_o('cyc_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_cyclepath')));
	
	--Sidewalks
	UPDATE test SET impedance_cyc_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'cyc_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE test w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_cyc_obstacle = (select_from_variable_container_o('cyc_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_obstacle')));
	     
	--Surface
	UPDATE test SET impedance_cyc_surface = (select_from_variable_container_o('cyc_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_surface')));
	
	--Smoothness
	UPDATE test SET impedance_cyc_smoothness = (select_from_variable_container_o('cyc_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_smoothness')));

-----------------------------------------------
-----------------------------------------------
--add impedance factor for wheelchair speed (whs)

	--add specific impedance column
	--whs_type_road
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whs_type_road numeric;
	--whs_peak_hour
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whs_peak_hour numeric;
	--whs_cyclepath
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whs_cyclepath numeric;
	--whs_sidewalk
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whs_sidewalk numeric;
	--whs_obstacle
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whs_obstacle numeric;
	--whs_speedlimit	
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whs_speedlimit numeric;
	--whs_surface
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whs_surface numeric;
	--whs_smoothness
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whs_smoothness numeric;
	
	--Type of road
	UPDATE test SET impedance_whs_type_road = (select_from_variable_container_s('whs_type_road'))::NUMERIC 
	WHERE highway IS NOT null
	AND (tunnel = 'yes' or bridge = 'yes')
	and highway IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'sidewalk_links');
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath
	with tags as
	(
		SELECT select_from_variable_container_o('class_cyclepath')  AS class_cyclepath
	
	)
	UPDATE test w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_whs_cyclepath = (select_from_variable_container_o('whs_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_cyclepath')));
	
	--Sidewalks
	UPDATE test SET impedance_whs_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'whs_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE test w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_whs_obstacle = (select_from_variable_container_o('whs_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_obstacle')));
	     
	--Surface
	UPDATE test SET impedance_whs_surface = (select_from_variable_container_o('whs_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_surface')));
	
	--Smoothness
	UPDATE test SET impedance_whs_smoothness = (select_from_variable_container_o('whs_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_smoothness')));

-----------------------------------------------
-----------------------------------------------
--add impedance factor for wheelchair comfort (whc)

	--add specific impedance column
	--whc_type_road
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whc_type_road numeric;
	--whc_peak_hour
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whc_peak_hour numeric;
	--whc_cyclepath
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whc_cyclepath numeric;
	--whc_sidewalk
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whc_sidewalk numeric;
	--whc_obstacle
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whc_obstacle numeric;
	--whc_speedlimit	
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whc_speedlimit numeric;
	--whc_surface
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whc_surface numeric;
	--whc_smoothness
	ALTER TABLE test ADD COLUMN IF NOT EXISTS impedance_whc_smoothness numeric;
	
	--Type of road
	UPDATE test SET impedance_whc_type_road = (select_from_variable_container_s('whc_type_road'))::NUMERIC 
	WHERE highway IS NOT null
	AND (tunnel = 'yes' or bridge = 'yes')
	and highway IN (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'sidewalk_links');
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath
	with tags as
	(
		SELECT select_from_variable_container_o('class_cyclepath')  AS class_cyclepath
	
	)
	UPDATE test w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_whc_cyclepath = (select_from_variable_container_o('whc_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_cyclepath')));
	
	--Sidewalks
	UPDATE test SET impedance_whc_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'whc_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE test w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from test w
	) x
	WHERE w.id = x.id;
	UPDATE test SET impedance_whc_obstacle = (select_from_variable_container_o('whc_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_obstacle')));
	     
	--Surface
	UPDATE test SET impedance_whc_surface = (select_from_variable_container_o('whc_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_surface')));
	
	--Smoothness
	UPDATE test SET impedance_whc_smoothness = (select_from_variable_container_o('whc_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_smoothness')));

-----------------------------------------------

--select fetch test_routing(ST_ASTEXT(ST_BUFFER(ST_POINT(11.543274,48.195524),0.001)),1,1,1.33,'walking_standard');
--CREATE TABLE test AS 
--select *, COST-reverse_cost FROM fetch test_routing(ST_ASTEXT(ST_BUFFER(ST_POINT(11.25196,48.18172),0.03)),1,1,1.33,'cycling_standard');


