-- Create the IAPI Impedence Factors

DROP TABLE IF exists impedance_table;
CREATE TABLE impedance_table AS 
select id, osm_id, geom, highway, bicycle, cycleway, wheelchair_classified,length_m,surface, smoothness from ways;

--add the required data to the table impedance_table
alter table impedance_table ADD COLUMN IF NOT EXISTS tunnel text;
alter table impedance_table ADD COLUMN IF NOT EXISTS bridge text;
UPDATE impedance_table
set tunnel = p.tunnel,
	bridge = p.bridge
FROM planet_osm_line p
WHERE impedance_table.osm_id = p.osm_id;

--add new column to the impedance_table table
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  bridge_tunnel_classified text;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  cyclepath_classified text;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  sidewalk_width  text;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  obstacle_classified text;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  extra_park text;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  extra_street_lamp text;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  extra_tree text;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  extra_bicycle_rack text;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  extra_waste_basket text;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS  extra_water text;

	with tags as
	(
		SELECT select_from_variable_container_o('bridge_tunnel')  AS bridge_tunnel
	)
	UPDATE impedance_table w SET bridge_tunnel_classified = x.bridge_tunnel_classified
	from 
		(select w.id, 
		case
			when tunnel IN (SELECT jsonb_array_elements_text((bridge_tunnel ->> 'tunnel')::jsonb)from tags) then 'tunnel'
			when bridge IN (SELECT jsonb_array_elements_text((bridge_tunnel ->> 'bridge')::jsonb)from tags) then 'bridge'
			else 'unclassified'
		end as bridge_tunnel_classified
		from impedance_table w
	) x
	WHERE w.id = x.id;

	with tags as
	(
		SELECT select_from_variable_container_o('class_cyclepath')  AS class_cyclepath
	)
	UPDATE impedance_table w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when (cycleway is not null or bicycle is not null) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from impedance_table w
	) x
	WHERE w.id = x.id;
	
	--
	with tags as
	(
		SELECT select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE impedance_table w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when wheelchair_classified IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'moderate')::jsonb)from tags) then 'moderate'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'light'
		end as obstacle_classified
		from impedance_table w
	) x
	WHERE w.id = x.id;
-----------------------------------------------
--add impedance factor for walking speed (was)

	--add specific impedance column
	--was_type_road
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_type_road numeric;
	--was_peak_hour
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_peak_hour numeric;
	--was_cyclepath
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_cyclepath numeric;
	--was_sidewalk
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_sidewalk numeric;
	--was_was_obstacle
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_obstacle numeric;
	--was_surface
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_surface numeric;
	--was_smoothness
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_smoothness numeric;
	--was_park
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_park numeric;
	--was_street_lamp
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_street_lamp numeric;
	--was_tree
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_tree numeric;
	--was_bench
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_bench numeric;
	--was_bycicle_rack
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_bycicle_rack numeric;
	--was_waste_basket
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_waste_basket numeric;
	--was_water
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was_water numeric;
	--impedance_was
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_was numeric;
	
	--Type of road
	UPDATE impedance_table SET impedance_was_type_road = (select_from_variable_container_o('was_type_road') ->> highway)::NUMERIC 
	WHERE highway IS NOT null
	AND highway IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_type_road')));

	UPDATE impedance_table SET impedance_was_type_road = (select_from_variable_container_o('was_type_road') ->> bridge_tunnel_classified)::NUMERIC 
	WHERE bridge_tunnel_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_type_road')));
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath

	UPDATE impedance_table SET impedance_was_cyclepath = (select_from_variable_container_o('was_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_cyclepath')));

	
	--Sidewalks
	UPDATE impedance_table SET impedance_was_sidewalk = (select_from_variable_container_o('was_sidewalk') ->> sidewalk_width)::NUMERIC 
	WHERE sidewalk_width IS NOT null
	AND sidewalk_width IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_sidewalk')));
	
	--Obstacles

	UPDATE impedance_table SET impedance_was_obstacle = (select_from_variable_container_o('was_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_obstacle')));
	     
	--Surface
	UPDATE impedance_table SET impedance_was_surface = (select_from_variable_container_o('was_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_surface')));
	
	--Smoothness
	UPDATE impedance_table SET impedance_was_smoothness = (select_from_variable_container_o('was_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_smoothness')));

	---Summary of walking speed (was)
	UPDATE impedance_table set impedance_was = COALESCE(impedance_was_type_road,0)
								+COALESCE(impedance_was_peak_hour,0)
								+COALESCE(impedance_was_cyclepath,0)
								+COALESCE(impedance_was_sidewalk,0)
								+COALESCE(impedance_was_obstacle,0)
								+COALESCE(impedance_was_surface,0)
								+COALESCE(impedance_was_smoothness,0)
								+COALESCE(impedance_was_park,0)
								+COALESCE(impedance_was_street_lamp,0)
								+COALESCE(impedance_was_tree,0)
								+COALESCE(impedance_was_bench,0)
								+COALESCE(impedance_was_bycicle_rack,0)
								+COALESCE(impedance_was_waste_basket,0)
								+COALESCE(impedance_was_water,0);
-----------------------------------------------

-----------------------------------------------
--add impedance factor for walking speed (wac)

	--add specific impedance column
	--wac_type_road
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_type_road numeric;
	--wac_peak_hour
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_peak_hour numeric;
	--wac_cyclepath
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_cyclepath numeric;
	--wac_sidewalk
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_sidewalk numeric;
	--wac_wac_obstacle
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_obstacle numeric;
	--wac_surface
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_surface numeric;
	--wac_smoothness
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_smoothness numeric;
	--wac_park
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_park numeric;
	--wac_street_lamp
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_street_lamp numeric;
	--wac_tree
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_tree numeric;
	--wac_bench
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_bench numeric;
	--wac_bycicle_rack
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_bycicle_rack numeric;
	--wac_wacte_basket
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_wacte_basket numeric;
	--wac_water
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac_water numeric;
	--impedance_wac
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wac numeric;
	
	--Type of road
	UPDATE impedance_table SET impedance_wac_type_road = (select_from_variable_container_o('wac_type_road') ->> highway)::NUMERIC 
	WHERE highway IS NOT null
	AND highway IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_type_road')));

	UPDATE impedance_table SET impedance_wac_type_road = (select_from_variable_container_o('wac_type_road') ->> bridge_tunnel_classified)::NUMERIC 
	WHERE bridge_tunnel_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_type_road')));
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath

	UPDATE impedance_table SET impedance_wac_cyclepath = (select_from_variable_container_o('wac_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_cyclepath')));

	
	--Sidewalks
	UPDATE impedance_table SET impedance_wac_sidewalk = (select_from_variable_container_o('wac_sidewalk') ->> sidewalk_width)::NUMERIC 
	WHERE sidewalk_width IS NOT null
	AND sidewalk_width IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_sidewalk')));
	
	--Obstacles

	UPDATE impedance_table SET impedance_wac_obstacle = (select_from_variable_container_o('wac_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_obstacle')));
	     
	--Surface
	UPDATE impedance_table SET impedance_wac_surface = (select_from_variable_container_o('wac_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_surface')));
	
	--Smoothness
	UPDATE impedance_table SET impedance_wac_smoothness = (select_from_variable_container_o('wac_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_smoothness')));

	---Summary of walking speed (wac)
	UPDATE impedance_table set impedance_wac = COALESCE(impedance_wac_type_road,0)
								+COALESCE(impedance_wac_peak_hour,0)
								+COALESCE(impedance_wac_cyclepath,0)
								+COALESCE(impedance_wac_sidewalk,0)
								+COALESCE(impedance_wac_obstacle,0)
								+COALESCE(impedance_wac_surface,0)
								+COALESCE(impedance_wac_smoothness,0)
								+COALESCE(impedance_wac_park,0)
								+COALESCE(impedance_wac_street_lamp,0)
								+COALESCE(impedance_wac_tree,0)
								+COALESCE(impedance_wac_bench,0)
								+COALESCE(impedance_wac_bycicle_rack,0)
								+COALESCE(impedance_wac_wacte_basket,0)
								+COALESCE(impedance_wac_water,0);
-----------------------------------------------
-----------------------------------------------
--add impedance factor for walking speed (cys)

	--add specific impedance column
	--cys_type_road
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_type_road numeric;
	--cys_peak_hour
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_peak_hour numeric;
	--cys_cyclepath
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_cyclepath numeric;
	--cys_sidewalk
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_sidewalk numeric;
	--cys_cys_obstacle
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_obstacle numeric;
	--cys_surface
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_surface numeric;
	--cys_smoothness
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_smoothness numeric;
	--cys_park
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_park numeric;
	--cys_street_lamp
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_street_lamp numeric;
	--cys_tree
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_tree numeric;
	--cys_bench
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_bench numeric;
	--cys_bycicle_rack
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_bycicle_rack numeric;
	--cys_cyste_basket
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_cyste_basket numeric;
	--cys_water
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys_water numeric;
	--impedance_cys
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cys numeric;
	
	--Type of road
	UPDATE impedance_table SET impedance_cys_type_road = (select_from_variable_container_o('cys_type_road') ->> highway)::NUMERIC 
	WHERE highway IS NOT null
	AND highway IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_type_road')));

	UPDATE impedance_table SET impedance_cys_type_road = (select_from_variable_container_o('cys_type_road') ->> bridge_tunnel_classified)::NUMERIC 
	WHERE bridge_tunnel_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_type_road')));
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath

	UPDATE impedance_table SET impedance_cys_cyclepath = (select_from_variable_container_o('cys_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_cyclepath')));

	
	--Sidewalks
	UPDATE impedance_table SET impedance_cys_sidewalk = (select_from_variable_container_o('cys_sidewalk') ->> sidewalk_width)::NUMERIC 
	WHERE sidewalk_width IS NOT null
	AND sidewalk_width IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_sidewalk')));
	
	--Obstacles

	UPDATE impedance_table SET impedance_cys_obstacle = (select_from_variable_container_o('cys_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_obstacle')));
	     
	--Surface
	UPDATE impedance_table SET impedance_cys_surface = (select_from_variable_container_o('cys_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_surface')));
	
	--Smoothness
	UPDATE impedance_table SET impedance_cys_smoothness = (select_from_variable_container_o('cys_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_smoothness')));

	---Summary of walking speed (cys)
	UPDATE impedance_table set impedance_cys = COALESCE(impedance_cys_type_road,0)
								+COALESCE(impedance_cys_peak_hour,0)
								+COALESCE(impedance_cys_cyclepath,0)
								+COALESCE(impedance_cys_sidewalk,0)
								+COALESCE(impedance_cys_obstacle,0)
								+COALESCE(impedance_cys_surface,0)
								+COALESCE(impedance_cys_smoothness,0)
								+COALESCE(impedance_cys_park,0)
								+COALESCE(impedance_cys_street_lamp,0)
								+COALESCE(impedance_cys_tree,0)
								+COALESCE(impedance_cys_bench,0)
								+COALESCE(impedance_cys_bycicle_rack,0)
								+COALESCE(impedance_cys_cyste_basket,0)
								+COALESCE(impedance_cys_water,0);
-----------------------------------------------	
-----------------------------------------------
--add impedance factor for walking speed (cyc)

	--add specific impedance column
	--cyc_type_road
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_type_road numeric;
	--cyc_peak_hour
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_peak_hour numeric;
	--cyc_cyclepath
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_cyclepath numeric;
	--cyc_sidewalk
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_sidewalk numeric;
	--cyc_cyc_obstacle
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_obstacle numeric;
	--cyc_surface
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_surface numeric;
	--cyc_smoothness
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_smoothness numeric;
	--cyc_park
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_park numeric;
	--cyc_street_lamp
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_street_lamp numeric;
	--cyc_tree
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_tree numeric;
	--cyc_bench
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_bench numeric;
	--cyc_bycicle_rack
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_bycicle_rack numeric;
	--cyc_cycte_basket
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_cycte_basket numeric;
	--cyc_water
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc_water numeric;
	--impedance_cyc
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cyc numeric;
	
	--Type of road
	UPDATE impedance_table SET impedance_cyc_type_road = (select_from_variable_container_o('cyc_type_road') ->> highway)::NUMERIC 
	WHERE highway IS NOT null
	AND highway IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_type_road')));

	UPDATE impedance_table SET impedance_cyc_type_road = (select_from_variable_container_o('cyc_type_road') ->> bridge_tunnel_classified)::NUMERIC 
	WHERE bridge_tunnel_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_type_road')));
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath

	UPDATE impedance_table SET impedance_cyc_cyclepath = (select_from_variable_container_o('cyc_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_cyclepath')));

	
	--Sidewalks
	UPDATE impedance_table SET impedance_cyc_sidewalk = (select_from_variable_container_o('cyc_sidewalk') ->> sidewalk_width)::NUMERIC 
	WHERE sidewalk_width IS NOT null
	AND sidewalk_width IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_sidewalk')));
	
	--Obstacles

	UPDATE impedance_table SET impedance_cyc_obstacle = (select_from_variable_container_o('cyc_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_obstacle')));
	     
	--Surface
	UPDATE impedance_table SET impedance_cyc_surface = (select_from_variable_container_o('cyc_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_surface')));
	
	--Smoothness
	UPDATE impedance_table SET impedance_cyc_smoothness = (select_from_variable_container_o('cyc_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_smoothness')));

	---Summary of walking speed (cyc)
	UPDATE impedance_table set impedance_cyc = COALESCE(impedance_cyc_type_road,0)
								+COALESCE(impedance_cyc_peak_hour,0)
								+COALESCE(impedance_cyc_cyclepath,0)
								+COALESCE(impedance_cyc_sidewalk,0)
								+COALESCE(impedance_cyc_obstacle,0)
								+COALESCE(impedance_cyc_surface,0)
								+COALESCE(impedance_cyc_smoothness,0)
								+COALESCE(impedance_cyc_park,0)
								+COALESCE(impedance_cyc_street_lamp,0)
								+COALESCE(impedance_cyc_tree,0)
								+COALESCE(impedance_cyc_bench,0)
								+COALESCE(impedance_cyc_bycicle_rack,0)
								+COALESCE(impedance_cyc_cycte_basket,0)
								+COALESCE(impedance_cyc_water,0);
-----------------------------------------------
	
-----------------------------------------------
--add impedance factor for walking speed (whs)

	--add specific impedance column
	--whs_type_road
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_type_road numeric;
	--whs_peak_hour
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_peak_hour numeric;
	--whs_cyclepath
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_cyclepath numeric;
	--whs_sidewalk
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_sidewalk numeric;
	--whs_whs_obstacle
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_obstacle numeric;
	--whs_surface
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_surface numeric;
	--whs_smoothness
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_smoothness numeric;
	--whs_park
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_park numeric;
	--whs_street_lamp
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_street_lamp numeric;
	--whs_tree
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_tree numeric;
	--whs_bench
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_bench numeric;
	--whs_bycicle_rack
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_bycicle_rack numeric;
	--whs_whste_basket
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_whste_basket numeric;
	--whs_water
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs_water numeric;
	--impedance_whs
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whs numeric;
	
	--Type of road
	UPDATE impedance_table SET impedance_whs_type_road = (select_from_variable_container_o('whs_type_road') ->> highway)::NUMERIC 
	WHERE highway IS NOT null
	AND highway IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_type_road')));

	UPDATE impedance_table SET impedance_whs_type_road = (select_from_variable_container_o('whs_type_road') ->> bridge_tunnel_classified)::NUMERIC 
	WHERE bridge_tunnel_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_type_road')));
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath

	UPDATE impedance_table SET impedance_whs_cyclepath = (select_from_variable_container_o('whs_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_cyclepath')));

	
	--Sidewalks
	UPDATE impedance_table SET impedance_whs_sidewalk = (select_from_variable_container_o('whs_sidewalk') ->> sidewalk_width)::NUMERIC 
	WHERE sidewalk_width IS NOT null
	AND sidewalk_width IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_sidewalk')));
	
	--Obstacles

	UPDATE impedance_table SET impedance_whs_obstacle = (select_from_variable_container_o('whs_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_obstacle')));
	     
	--Surface
	UPDATE impedance_table SET impedance_whs_surface = (select_from_variable_container_o('whs_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_surface')));
	
	--Smoothness
	UPDATE impedance_table SET impedance_whs_smoothness = (select_from_variable_container_o('whs_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_smoothness')));

	---Summary of walking speed (whs)
	UPDATE impedance_table set impedance_whs = COALESCE(impedance_whs_type_road,0)
								+COALESCE(impedance_whs_peak_hour,0)
								+COALESCE(impedance_whs_cyclepath,0)
								+COALESCE(impedance_whs_sidewalk,0)
								+COALESCE(impedance_whs_obstacle,0)
								+COALESCE(impedance_whs_surface,0)
								+COALESCE(impedance_whs_smoothness,0)
								+COALESCE(impedance_whs_park,0)
								+COALESCE(impedance_whs_street_lamp,0)
								+COALESCE(impedance_whs_tree,0)
								+COALESCE(impedance_whs_bench,0)
								+COALESCE(impedance_whs_bycicle_rack,0)
								+COALESCE(impedance_whs_whste_basket,0)
								+COALESCE(impedance_whs_water,0);

-----------------------------------------------
--add impedance factor for walking speed (whc)

	--add specific impedance column
	--whc_type_road
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_type_road numeric;
	--whc_peak_hour
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_peak_hour numeric;
	--whc_cyclepath
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_cyclepath numeric;
	--whc_sidewalk
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_sidewalk numeric;
	--whc_whc_obstacle
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_obstacle numeric;
	--whc_surface
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_surface numeric;
	--whc_smoothness
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_smoothness numeric;
	--whc_park
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_park numeric;
	--whc_street_lamp
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_street_lamp numeric;
	--whc_tree
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_tree numeric;
	--whc_bench
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_bench numeric;
	--whc_bycicle_rack
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_bycicle_rack numeric;
	--whc_whcte_basket
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_whcte_basket numeric;
	--whc_water
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc_water numeric;
	--impedance_whc
	ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_whc numeric;
	
	--Type of road
	UPDATE impedance_table SET impedance_whc_type_road = (select_from_variable_container_o('whc_type_road') ->> highway)::NUMERIC 
	WHERE highway IS NOT null
	AND highway IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_type_road')));

	UPDATE impedance_table SET impedance_whc_type_road = (select_from_variable_container_o('whc_type_road') ->> bridge_tunnel_classified)::NUMERIC 
	WHERE bridge_tunnel_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_type_road')));
	
	--Peak hour 
	--DON'T KNOW INFO YET!
	
	--Cyclepath

	UPDATE impedance_table SET impedance_whc_cyclepath = (select_from_variable_container_o('whc_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_cyclepath')));

	
	--Sidewalks
	UPDATE impedance_table SET impedance_whc_sidewalk = (select_from_variable_container_o('whc_sidewalk') ->> sidewalk_width)::NUMERIC 
	WHERE sidewalk_width IS NOT null
	AND sidewalk_width IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_sidewalk')));
	
	--Obstacles

	UPDATE impedance_table SET impedance_whc_obstacle = (select_from_variable_container_o('whc_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_obstacle')));
	     
	--Surface
	UPDATE impedance_table SET impedance_whc_surface = (select_from_variable_container_o('whc_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_surface')));
	
	--Smoothness
	UPDATE impedance_table SET impedance_whc_smoothness = (select_from_variable_container_o('whc_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_smoothness')));

	---Summary of walking speed (whc)
	UPDATE impedance_table set impedance_whc = COALESCE(impedance_whc_type_road,0)
								+COALESCE(impedance_whc_peak_hour,0)
								+COALESCE(impedance_whc_cyclepath,0)
								+COALESCE(impedance_whc_sidewalk,0)
								+COALESCE(impedance_whc_obstacle,0)
								+COALESCE(impedance_whc_surface,0)
								+COALESCE(impedance_whc_smoothness,0)
								+COALESCE(impedance_whc_park,0)
								+COALESCE(impedance_whc_street_lamp,0)
								+COALESCE(impedance_whc_tree,0)
								+COALESCE(impedance_whc_bench,0)
								+COALESCE(impedance_whc_bycicle_rack,0)
								+COALESCE(impedance_whc_whcte_basket,0)
								+COALESCE(impedance_whc_water,0);
-----------------------------------------------
-----------------------------------------------
--add summary of impedance factors
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_walking_comfort numeric;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_cycling_comfort numeric;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_wheelchair_comfort numeric;
ALTER TABLE impedance_table ADD COLUMN IF NOT EXISTS impedance_total numeric;

update impedance_table set impedance_walking_comfort = coalesce(impedance_was,0)+ coalesce(impedance_wac,0);
update impedance_table set impedance_cycling_comfort = coalesce(impedance_cys,0)+ coalesce(impedance_cyc,0);
update impedance_table set impedance_wheelchair_comfort = coalesce(impedance_whs,0)+ coalesce(impedance_whc,0);
update impedance_table set impedance_total = coalesce(impedance_walking_comfort,0)+coalesce(impedance_cycling_comfort,0)+coalesce(impedance_wheelchair_comfort,0);



	