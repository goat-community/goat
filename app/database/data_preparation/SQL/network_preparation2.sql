ALTER TABLE ways ADD COLUMN impedance_surface NUMERIC;
UPDATE ways SET impedance_surface = (select_from_variable_container_o('cycling_surface') ->> surface)::NUMERIC 
WHERE surface IS NOT NULL
AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('cycling_surface')));

--Mark vertices that are on network islands
WITH count_ids AS (
	SELECT count(*), source AS id 
	FROM ways
	GROUP by source
	UNION ALL
	SELECT count(*), target AS id
	FROM ways
	GROUP by target
),
only_once AS (
	SELECT c.id,sum(c.count), v.geom 
	FROM count_ids c, ways_vertices_pgr v
	WHERE c.id = v.id
	GROUP by c.id, v.geom
	having sum(count) < 2
),
vertices_islands AS (
	SELECT w.source, w.target
	FROM only_once o, only_once o1, ways w
	WHERE w.source = o.id 
	and w.target = o1.id
),
vertices_to_update AS (
	SELECT x.id
	FROM (
		SELECT source AS id 
		FROM vertices_islands 
		UNION ALL
		SELECT target AS id 
		FROM vertices_islands 
	) x
	, ways_vertices_pgr v
	WHERE v.id = x.id
)
UPDATE ways_vertices_pgr 
SET class_ids = array[0]
FROM vertices_to_update v
WHERE ways_vertices_pgr.id = v.id;

--Identify death_end in the network
DROP TABLE IF EXISTS death_end_v;
CREATE TEMP TABLE death_end_v AS 
WITH death_end AS (
	SELECT count(source),source 
	FROM (
		SELECT SOURCE 
		FROM ways 
		UNION ALL
		SELECT target 
		FROM ways 
	) x
	GROUP BY SOURCE 
	HAVING count(source) = 1
)
SELECT v.*
FROM ways_vertices_pgr v, death_end d
WHERE v.id = d.SOURCE;

ALTER TABLE ways ADD COLUMN death_end BIGINT;

UPDATE ways w SET death_end = w.target  
FROM death_end_v d 
WHERE d.id = w.SOURCE;

UPDATE ways w SET death_end = w.source 
FROM death_end_v d 
WHERE d.id = w.target;

ALTER TABLE ways_vertices_pgr ADD COLUMN death_end BOOLEAN;
CREATE INDEX ON ways_vertices_pgr (death_end);

WITH s AS (
	SELECT w.id,w.geom,w.target vid 
	FROM ways w, death_end_v v
	WHERE w.SOURCE = v.id
	UNION ALL 
	SELECT w.id,w.geom,w.source vid 
	FROM ways w, death_end_v v
	WHERE w.target = v.id
)
UPDATE ways_vertices_pgr v
SET death_end = TRUE
FROM s 
WHERE v.id = s.vid; 

CREATE INDEX ON ways USING btree(foot);
CREATE INDEX ON ways USING btree(id);
CREATE INDEX ON ways_vertices_pgr USING btree(cnt);

CREATE SEQUENCE ways_vertices_pgr_id_seq;
ALTER TABLE ways_vertices_pgr ALTER COLUMN id SET DEFAULT nextval('ways_vertices_pgr_id_seq');
ALTER SEQUENCE ways_vertices_pgr_id_seq OWNED BY ways_vertices_pgr.id;
SELECT setval('ways_vertices_pgr_id_seq', COALESCE(max(id), 0)) FROM ways_vertices_pgr;

CREATE SEQUENCE ways_id_seq;
ALTER TABLE ways ALTER COLUMN id SET DEFAULT nextval('ways_id_seq');
ALTER SEQUENCE ways_id_seq OWNED BY ways.id;
SELECT setval('ways_id_seq', COALESCE(max(id), 0)) FROM ways;

CREATE TABLE ways_userinput (LIKE ways INCLUDING ALL);
INSERT INTO ways_userinput
SELECT * FROM ways;

CREATE TABLE ways_userinput_vertices_pgr (LIKE ways_vertices_pgr INCLUDING ALL);
INSERT INTO ways_userinput_vertices_pgr
SELECT * FROM ways_vertices_pgr;

ALTER TABLE ways_userinput add column userid int4;
ALTER TABLE ways_userinput_vertices_pgr add column userid int4;
ALTER TABLE ways_userinput add column scenario_id int4;
ALTER TABLE ways_userinput_vertices_pgr add column scenario_id int4;
ALTER TABLE ways_userinput ADD COLUMN original_id BIGINT;
CREATE INDEX ON ways_userinput USING btree (userid);
CREATE INDEX ON ways_userinput_vertices_pgr USING btree (userid);
CREATE INDEX ON ways_userinput USING btree (scenario_id);
CREATE INDEX ON ways_userinput_vertices_pgr USING btree (scenario_id);
CREATE INDEX ON ways_userinput (original_id);

-- add IAPI Impedence Factors to ways

--add the required data to the table ways
alter table ways ADD COLUMN IF NOT EXISTS tunnel text;
alter table ways ADD COLUMN IF NOT EXISTS bridge text;
UPDATE ways
set tunnel = p.tunnel,
	bridge = p.bridge
FROM planet_osm_line p
WHERE ways.osm_id = p.osm_id;

--add new column to the ways table
ALTER TABLE ways ADD COLUMN IF NOT EXISTS  cyclepath_classified text;
ALTER TABLE ways ADD COLUMN IF NOT EXISTS  obstacle_classified text;

-----------------------------------------------
--add impedance factor for walking speed (was)

	--add specific impedance column
	--was_type_road
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_was_type_road numeric;
	--was_peak_hour
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_was_peak_hour numeric;
	--was_cyclepath
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_was_cyclepath numeric;
	--was_sidewalk
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_was_sidewalk numeric;
	--was_was_obstacle
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_was_obstacle numeric;
	--was_speedlimit	
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_was_speedlimit numeric;
	--was_surface
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_was_surface numeric;
	--was_smoothness
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_was_smoothness numeric;
	
	--Type of road
	UPDATE ways SET impedance_was_type_road = (select_from_variable_container_s('was_type_road'))::NUMERIC 
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
	UPDATE ways w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_was_cyclepath = (select_from_variable_container_o('was_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_cyclepath')));
	
	--Sidewalks
	UPDATE ways SET impedance_was_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'was_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE ways w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_was_obstacle = (select_from_variable_container_o('was_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_obstacle')));
	     
	--Surface
	UPDATE ways SET impedance_was_surface = (select_from_variable_container_o('was_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_surface')));
	
	--Smoothness
	UPDATE ways SET impedance_was_smoothness = (select_from_variable_container_o('was_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('was_smoothness')));

-----------------------------------------------

-----------------------------------------------
--add impedance factor for walking comfort (wac)

	--add specific impedance column
	--wac_type_road
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_wac_type_road numeric;
	--wac_peak_hour
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_wac_peak_hour numeric;
	--wac_cyclepath
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_wac_cyclepath numeric;
	--wac_sidewalk
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_wac_sidewalk numeric;
	--wac_obstacle
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_wac_obstacle numeric;
	--wac_speedlimit	
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_wac_speedlimit numeric;
	--wac_surface
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_wac_surface numeric;
	--wac_smoothness
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_wac_smoothness numeric;
	
	--Type of road
	UPDATE ways SET impedance_wac_type_road = (select_from_variable_container_s('wac_type_road'))::NUMERIC 
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
	UPDATE ways w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_wac_cyclepath = (select_from_variable_container_o('wac_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_cyclepath')));
	
	--Sidewalks
	UPDATE ways SET impedance_wac_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'wac_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE ways w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_wac_obstacle = (select_from_variable_container_o('wac_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_obstacle')));
	     
	--Surface
	UPDATE ways SET impedance_wac_surface = (select_from_variable_container_o('wac_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_surface')));
	
	--Smoothness
	UPDATE ways SET impedance_wac_smoothness = (select_from_variable_container_o('wac_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('wac_smoothness')));

-----------------------------------------------

-----------------------------------------------
--add impedance factor for cycling speed (cys)

	--add specific impedance column
	--cys_type_road
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cys_type_road numeric;
	--cys_peak_hour
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cys_peak_hour numeric;
	--cys_cyclepath
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cys_cyclepath numeric;
	--cys_sidewalk
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cys_sidewalk numeric;
	--cys_obstacle
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cys_obstacle numeric;
	--cys_speedlimit	
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cys_speedlimit numeric;
	--cys_surface
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cys_surface numeric;
	--cys_smoothness
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cys_smoothness numeric;
	
	--Type of road
	UPDATE ways SET impedance_cys_type_road = (select_from_variable_container_s('cys_type_road'))::NUMERIC 
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
	UPDATE ways w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_cys_cyclepath = (select_from_variable_container_o('cys_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_cyclepath')));
	
	--Sidewalks
	UPDATE ways SET impedance_cys_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'cys_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE ways w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_cys_obstacle = (select_from_variable_container_o('cys_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_obstacle')));
	     
	--Surface
	UPDATE ways SET impedance_cys_surface = (select_from_variable_container_o('cys_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_surface')));
	
	--Smoothness
	UPDATE ways SET impedance_cys_smoothness = (select_from_variable_container_o('cys_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('cys_smoothness')));

-----------------------------------------------

-----------------------------------------------
--add impedance factor for cycling comfort (cyc)

	--add specific impedance column
	--cyc_type_road
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cyc_type_road numeric;
	--cyc_peak_hour
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cyc_peak_hour numeric;
	--cyc_cyclepath
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cyc_cyclepath numeric;
	--cyc_sidewalk
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cyc_sidewalk numeric;
	--cyc_obstacle
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cyc_obstacle numeric;
	--cyc_speedlimit	
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cyc_speedlimit numeric;
	--cyc_surface
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cyc_surface numeric;
	--cyc_smoothness
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_cyc_smoothness numeric;
	
	--Type of road
	UPDATE ways SET impedance_cyc_type_road = (select_from_variable_container_s('cyc_type_road'))::NUMERIC 
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
	UPDATE ways w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_cyc_cyclepath = (select_from_variable_container_o('cyc_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_cyclepath')));
	
	--Sidewalks
	UPDATE ways SET impedance_cyc_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'cyc_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE ways w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_cyc_obstacle = (select_from_variable_container_o('cyc_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_obstacle')));
	     
	--Surface
	UPDATE ways SET impedance_cyc_surface = (select_from_variable_container_o('cyc_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_surface')));
	
	--Smoothness
	UPDATE ways SET impedance_cyc_smoothness = (select_from_variable_container_o('cyc_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('cyc_smoothness')));

-----------------------------------------------
-----------------------------------------------
--add impedance factor for wheelchair speed (whs)

	--add specific impedance column
	--whs_type_road
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whs_type_road numeric;
	--whs_peak_hour
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whs_peak_hour numeric;
	--whs_cyclepath
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whs_cyclepath numeric;
	--whs_sidewalk
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whs_sidewalk numeric;
	--whs_obstacle
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whs_obstacle numeric;
	--whs_speedlimit	
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whs_speedlimit numeric;
	--whs_surface
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whs_surface numeric;
	--whs_smoothness
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whs_smoothness numeric;
	
	--Type of road
	UPDATE ways SET impedance_whs_type_road = (select_from_variable_container_s('whs_type_road'))::NUMERIC 
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
	UPDATE ways w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_whs_cyclepath = (select_from_variable_container_o('whs_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_cyclepath')));
	
	--Sidewalks
	UPDATE ways SET impedance_whs_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'whs_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE ways w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_whs_obstacle = (select_from_variable_container_o('whs_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_obstacle')));
	     
	--Surface
	UPDATE ways SET impedance_whs_surface = (select_from_variable_container_o('whs_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_surface')));
	
	--Smoothness
	UPDATE ways SET impedance_whs_smoothness = (select_from_variable_container_o('whs_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('whs_smoothness')));

-----------------------------------------------
-----------------------------------------------
--add impedance factor for wheelchair comfort (whc)

	--add specific impedance column
	--whc_type_road
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whc_type_road numeric;
	--whc_peak_hour
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whc_peak_hour numeric;
	--whc_cyclepath
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whc_cyclepath numeric;
	--whc_sidewalk
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whc_sidewalk numeric;
	--whc_obstacle
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whc_obstacle numeric;
	--whc_speedlimit	
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whc_speedlimit numeric;
	--whc_surface
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whc_surface numeric;
	--whc_smoothness
	ALTER TABLE ways ADD COLUMN IF NOT EXISTS impedance_whc_smoothness numeric;
	
	--Type of road
	UPDATE ways SET impedance_whc_type_road = (select_from_variable_container_s('whc_type_road'))::NUMERIC 
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
	UPDATE ways w SET cyclepath_classified = x.cyclepath_classified
	from 
		(select w.id, 
		case
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_yes')::jsonb)from tags) then 'segregated_yes'
			when cycleway IN (SELECT jsonb_array_elements_text((class_cyclepath ->> 'segregated_no')::jsonb)from tags) then 'segregated_no'
			else 'unclassified'
		end as cyclepath_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_whc_cyclepath = (select_from_variable_container_o('whc_cyclepath') ->> cyclepath_classified)::NUMERIC 
	WHERE cyclepath_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_cyclepath')));
	
	--Sidewalks
	UPDATE ways SET impedance_whc_sidewalk = (SELECT UNNEST(variable_array) from variable_container WHERE identifier = 'whc_sidewalk')::NUMERIC
	where sidewalk is not null 
	and sidewalk IN ('both','left','right');
	--AND (sidewalk_both_width <= 1.80 OR sidewalk_left_width <= 1.80 OR sidewalk_right_width <= 1.80)
	
	--Obstacles
	with tags as
	(
		SELECT	select_from_variable_container_o('class_obstacle')  AS class_obstacle
	)
	UPDATE ways w SET obstacle_classified = x.obstacle_classified
	from 
		(select w.id, 
		case
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'light')::jsonb)from tags) then 'light'
			when highway IN (SELECT jsonb_array_elements_text((class_obstacle ->> 'strong')::jsonb)from tags) then 'strong'
			else 'unclassified'
		end as obstacle_classified
		from ways w
	) x
	WHERE w.id = x.id;
	UPDATE ways SET impedance_whc_obstacle = (select_from_variable_container_o('whc_obstacle') ->> obstacle_classified)::NUMERIC 
	WHERE obstacle_classified IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_obstacle')));
	     
	--Surface
	UPDATE ways SET impedance_whc_surface = (select_from_variable_container_o('whc_surface') ->> surface)::NUMERIC 
	WHERE surface IS NOT NULL
	AND surface IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_surface')));
	
	--Smoothness
	UPDATE ways SET impedance_whc_smoothness = (select_from_variable_container_o('whc_smoothness') ->> smoothness)::NUMERIC 
	WHERE smoothness IS NOT NULL
	AND smoothness IN(SELECT jsonb_object_keys(select_from_variable_container_o('whc_smoothness')));

-----------------------------------------------