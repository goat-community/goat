

CREATE OR REPLACE FUNCTION basic.network_modification(scenario_id_input  integer)
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   cnt integer;
   rec record;
   max_id integer; 
BEGIN
	---------------------------------------------------------------------------------------------------------------------
	--Prepare Table
	---------------------------------------------------------------------------------------------------------------------
	
	/*Assumption Translation Meters and Degree: 1m = 0.000009 degree */
	DELETE FROM basic.edge e
	WHERE e.scenario_id = scenario_id_input;
	DELETE FROM basic.node n 
	WHERE n.scenario_id = scenario_id_input; 
	DROP TABLE IF EXISTS split_drawn_features, drawn_features, existing_network, intersection_existing_network, drawn_features_union, new_network, delete_extended_part, vertices_to_assign; 
		
	DROP TABLE IF EXISTS modified_attributes_only;
	CREATE TEMP TABLE modified_attributes_only AS 
	SELECT w.*
	FROM basic.edge e, customer.way_modified w 
	WHERE w.scenario_id = scenario_id_input 
	AND e.id = w.way_id 
	AND ST_ASTEXT(ST_ReducePrecision(w.geom,0.00001)) = ST_ASTEXT(ST_ReducePrecision(e.geom,0.00001))
	AND edit_type = 'm'; 
	CREATE INDEX ON modified_attributes_only USING GIST(geom);

	DROP TABLE IF EXISTS drawn_features; 
	CREATE TEMP TABLE drawn_features as
	SELECT w.id, ST_RemoveRepeatedPoints(w.geom) AS geom, 
	w.way_type, w.surface, w.wheelchair, w.lit, w.foot, w.bicycle, w.scenario_id, w.way_id AS original_id 
	FROM customer.way_modified w
	WHERE w.scenario_id = scenario_id_input
	AND w.edit_type IN ('n', 'm');
	CREATE INDEX ON drawn_features USING GIST(geom);
	
	---------------------------------------------------------------------------------------------------------------------
	--Snap start and end points
	---------------------------------------------------------------------------------------------------------------------
	/*Round start and end point for snapping*/
	DROP TABLE IF EXISTS snapped_drawn_features; 
 	CREATE TEMP TABLE snapped_drawn_features AS 
 	WITH start_end_point AS 
 	(
		SELECT d.id AS did, st_startpoint(d.geom) geom, 's' AS point_type, FALSE AS snapped, NULL::integer AS node_id 
		FROM drawn_features d
		UNION ALL 
		SELECT d.id AS did, st_endpoint(d.geom) geom, 'e' AS point_type, FALSE AS snapped, NULL AS node_id  
		FROM drawn_features d
	),
	clusters AS 
	(
		SELECT did, geom, ST_ClusterDBSCAN(geom, eps := 0.00001, minpoints := 1) OVER() AS cid, point_type
		FROM start_end_point
	),
	grouped AS 
	(
		SELECT ARRAY_AGG(did) AS did, ST_CENTROID(ST_COLLECT(geom)) AS geom, ARRAY_AGG(point_type)::text[] AS point_types
		FROM clusters 
		GROUP BY cid 
	)
	SELECT UNNEST(did) AS did, geom, UNNEST(point_types) AS point_type, FALSE AS snapped, NULL::integer AS node_id, ARRAY_LENGTH(point_types, 1) AS group_size   
	FROM grouped; 
	
	ALTER TABLE snapped_drawn_features ADD COLUMN id serial; 
	CREATE INDEX ON snapped_drawn_features USING GIST(geom);
	CREATE INDEX ON snapped_drawn_features (id);
	
	/*Snapping to existing Nodes*/
	DROP TABLE IF EXISTS snapped_to_node; 
	CREATE TEMP TABLE snapped_to_node AS  
	SELECT r.id, r.did, r.point_type, r.geom original_geom, s.geom node_geom, s.id AS node_id 
	FROM snapped_drawn_features r
	CROSS JOIN LATERAL 
	(
		SELECT n.id, n.geom
		FROM basic.node n
		WHERE ST_Intersects(ST_BUFFER(r.geom,0.00001), n.geom)
		AND n.scenario_id IS NULL 
		ORDER BY r.geom <-> n.geom
		LIMIT 1
	) s;
	CREATE INDEX ON snapped_to_node USING GIST(node_geom); 	

	UPDATE snapped_drawn_features d
	SET geom = node_geom, snapped = TRUE, node_id = s.node_id 
	FROM snapped_to_node s 
	WHERE s.did = d.did 
	AND d.point_type = s.point_type;  
		
	/*Snapping to existing edges*/
	DROP TABLE IF EXISTS snapped_to_edge; 
	CREATE TEMP TABLE snapped_to_edge AS  
	SELECT r.id, r.did, r.point_type, r.geom original_geom, s.geom closest_point_edge 
	FROM snapped_drawn_features r
	CROSS JOIN LATERAL 
	(
		SELECT n.id, ST_CLOSESTPOINT(n.geom, r.geom) AS geom 
		FROM basic.edge n
		WHERE ST_Intersects(ST_BUFFER(r.geom,0.00001), n.geom)
		AND n.scenario_id IS NULL 
		ORDER BY r.geom <-> ST_CLOSESTPOINT(n.geom, r.geom)
		LIMIT 1
	) s
	WHERE r.snapped = False;
	
	/*Update based on snapped to new*/
	UPDATE snapped_drawn_features d
	SET geom = closest_point_edge, snapped = True
	FROM snapped_to_edge s 
	WHERE s.did = d.did 
	AND d.point_type = s.point_type;  
	
	/*Snapping to each other*/
	DROP TABLE IF EXISTS snapped_to_each_other; 
	CREATE TEMP TABLE snapped_to_each_other AS  
	SELECT r.id, r.did, r.point_type, r.geom original_geom, s.geom closest_point_edge 
	FROM snapped_drawn_features r
	CROSS JOIN LATERAL 
	(
		SELECT n.id, ST_CLOSESTPOINT(n.geom, r.geom) AS geom 
		FROM drawn_features n
		WHERE ST_Intersects(ST_BUFFER(r.geom,0.00001), n.geom)
		AND r.did <> n.id 
		ORDER BY r.geom <-> ST_CLOSESTPOINT(n.geom, r.geom)
		LIMIT 1
	) s
	WHERE r.snapped = FALSE
	AND r.group_size = 1
	UNION ALL 
	SELECT s.id, s.did, s.point_type, s.geom, s.geom
	FROM snapped_drawn_features s
	WHERE s.group_size > 1; 

	/*Update based on snapped to each other*/
	UPDATE snapped_drawn_features d
	SET geom = closest_point_edge, snapped = True
	FROM snapped_to_each_other s 
	WHERE s.did = d.did 
	AND d.point_type = s.point_type;  

	/*Update drawn features*/
	UPDATE drawn_features d
	SET geom = st_setpoint(d.geom, 0, s.geom)
	FROM snapped_drawn_features s
	WHERE d.id = s.did 
	AND s.snapped = TRUE 
	AND s.point_type = 's';
	
	UPDATE drawn_features d
	SET geom = st_setpoint(d.geom, -1, s.geom)
	FROM snapped_drawn_features s
	WHERE d.id = s.did 
	AND s.snapped = TRUE 
	AND s.point_type = 'e';

	UPDATE drawn_features d
	SET geom = st_setpoint(d.geom, 0, s.geom)
	FROM snapped_drawn_features s
	WHERE s.snapped = FALSE 
	AND s.point_type = 's'
	AND d.id = s.did; 
	
	UPDATE drawn_features d
	SET geom = st_setpoint(d.geom, -1, s.geom)
	FROM snapped_drawn_features s
	WHERE s.snapped = FALSE 
	AND s.point_type = 'e'
	AND d.id = s.did; 
	
	---------------------------------------------------------------------------------------------------------------------
	--Cut network
	---------------------------------------------------------------------------------------------------------------------

	/*Extend lines to cut network*/		
	DROP TABLE IF EXISTS extended_lines; 
	CREATE TEMP TABLE extended_lines AS  
	WITH agg_snapped_nodes AS 
	(
		SELECT d.id, ARRAY_AGG(point_type) AS point_type 
		FROM snapped_to_node s, drawn_features d 
		WHERE d.id = s.did 
		GROUP BY d.id
	)
	SELECT CASE WHEN ARRAY['e', 's'] && point_type THEN d.geom
	WHEN ARRAY['s'] = point_type THEN basic.extend_line(d.geom, 0.00001, 'end')
	WHEN ARRAY['e'] = point_type THEN basic.extend_line(d.geom, 0.00001, 'start')
	END AS geom, d.original_id
	FROM agg_snapped_nodes a, drawn_features d
	WHERE a.id = d.id 
	AND (d.way_type = 'road' OR d.way_type IS NULL)
	UNION ALL 
	SELECT basic.extend_line(d.geom, 0.00001, 'both'), d.original_id  
	FROM drawn_features d 
	LEFT JOIN snapped_to_node s 
	ON d.id = s.did 
	WHERE s.id IS NULL
	AND (d.way_type = 'road' OR d.way_type IS NULL); 
		
	/*Intersects drawn bridges*/
	DROP TABLE IF EXISTS start_end_bridges;
	CREATE TEMP TABLE start_end_bridges AS 
	SELECT st_startpoint(geom) AS geom 
	FROM drawn_features
	WHERE way_type = 'bridge'
	UNION 
	SELECT ST_endpoint(geom) AS geom 
	FROM drawn_features
	WHERE way_type = 'bridge';
	CREATE INDEX ON start_end_bridges USING GIST(geom);

	/*Intersect drawn ways with existing ways*/
	DROP TABLE IF EXISTS intersection_existing_network;
	CREATE TEMP TABLE intersection_existing_network AS 
	WITH intersection_result AS 
	(
		SELECT (ST_DUMP(ST_Intersection(d.geom, w.geom))).geom AS geom, w.id  
		FROM extended_lines d, basic.edge w 
		WHERE ST_Intersects(ST_BUFFER(d.geom, 0.00001), w.geom)
		AND w.scenario_id IS NULL
	)
	SELECT i.* 
	FROM intersection_result i
	LEFT JOIN extended_lines e
	ON i.id = e.original_id
	WHERE e.original_id IS NULL 
	AND st_geometrytype(i.geom) = 'ST_Point'; 

	INSERT INTO intersection_existing_network
	WITH to_add AS
	(
		SELECT scenario_id_input AS scenario_id, x.closest_point AS geom 
		FROM start_end_bridges s 
		CROSS JOIN LATERAL 
		(
			SELECT ST_CLOSESTPOINT(w.geom,s.geom) AS closest_point, ST_LineLocatePoint(w.geom,s.geom) AS fraction
			FROM basic.edge w 
			WHERE w.scenario_id IS NULL 
			AND ST_Intersects(St_buffer(s.geom,0.00001), w.geom)
			ORDER BY ST_CLOSESTPOINT(geom,s.geom) <-> s.geom
		  	LIMIT 1
		) x
	) 
	SELECT a.geom
	FROM to_add a 
	LEFT JOIN intersection_existing_network i 
	ON ST_Intersects(ST_BUFFER(a.geom, 0.00001), i.geom)
	WHERE i.geom IS NULL;  
	
	DROP TABLE IF EXISTS distinct_intersection_existing_network; 
	CREATE TABLE distinct_intersection_existing_network AS 
	SELECT DISTINCT geom
	FROM intersection_existing_network i;  
	
	CREATE INDEX ON distinct_intersection_existing_network USING GIST(geom);
	ALTER TABLE distinct_intersection_existing_network ADD COLUMN id serial;
	ALTER TABLE distinct_intersection_existing_network ADD PRIMARY key(id);
	
	/*Filter out snapped start or end point*/
	DELETE FROM intersection_existing_network h
	USING 
	(
		SELECT h.geom 
		FROM snapped_to_node n, distinct_intersection_existing_network h 
		WHERE ST_Intersects(ST_BUFFER(n.node_geom,0.00001), h.geom)
	) d 
	WHERE h.geom = d.geom; 

	DROP TABLE IF EXISTS split_drawn_features;
	/*Split network with itself*/
	SELECT count(*) 
	INTO cnt
	FROM drawn_features
	WHERE (way_type IS NULL OR way_type <> 'bridge')
	LIMIT 2;
	
	IF cnt <= 1 THEN
	    CREATE TEMP TABLE split_drawn_features as
	    SELECT id as did, geom, way_type, surface, wheelchair, lit, foot, bicycle, scenario_id, original_id  
		FROM drawn_features;
	ELSE 
		CREATE TEMP TABLE split_drawn_features AS
		SELECT id AS did, basic.split_by_drawn_lines(id::integer, geom) AS geom, way_type, surface, wheelchair, lit, foot, bicycle, scenario_id, original_id  
		FROM drawn_features x
		WHERE (way_type IS NULL OR way_type <> 'bridge')
		UNION ALL 
		SELECT id AS did, geom, way_type, surface, wheelchair, lit, foot, bicycle, scenario_id, original_id  
		FROM drawn_features
		WHERE way_type = 'bridge';
	END IF;
	CREATE INDEX ON split_drawn_features USING GIST(geom);

	/*Create perpendicular lines to split new network*/
	DROP TABLE IF EXISTS perpendicular_split_lines;
	CREATE TEMP TABLE perpendicular_split_lines AS 
	SELECT basic.create_intersection_line(i.geom, 0.000001) AS geom 
	FROM intersection_existing_network i;
	
	DROP TABLE IF EXISTS union_perpendicular_split_lines; 
	CREATE TEMP TABLE union_perpendicular_split_lines AS 
	SELECT ST_Union(geom) AS geom  
	FROM perpendicular_split_lines p; 
	
	/*Split new network with existing network*/
	DROP TABLE IF EXISTS new_network;
	CREATE TEMP TABLE new_network AS
	SELECT d.did, (dp.geom).geom, way_type, surface, wheelchair, lit, foot, bicycle, scenario_id, original_id, 'geom' AS edit_type  
	FROM split_drawn_features d, union_perpendicular_split_lines w, 
	LATERAL (SELECT ST_DUMP(ST_CollectionExtract(ST_SPLIT(d.geom,w.geom),2)) AS geom) dp
	WHERE (d.way_type IS NULL OR d.way_type <> 'bridge');
	CREATE INDEX ON new_network USING GIST(geom);

	/*Delete extended part*/
	DELETE FROM new_network
	WHERE st_length(geom) < 0.0000011;

	/*Inject drawn bridges*/
	INSERT INTO new_network(did, geom, way_type, surface, wheelchair, lit, foot, bicycle, scenario_id, original_id, edit_type) 
	SELECT id, geom, way_type, surface, wheelchair, lit, foot, bicycle, scenario_id, original_id, 'geom'
	FROM drawn_features 
	WHERE way_type = 'bridge';

	ALTER TABLE new_network ADD COLUMN id serial;
	ALTER TABLE new_network ADD COLUMN source integer;
	ALTER TABLE new_network ADD COLUMN target integer;
	
	---------------------------------------------------------------------------------------------------------------------
	--Prepare source and target
	---------------------------------------------------------------------------------------------------------------------
	/*Existing network is split using perpendicular lines*/
	DROP TABLE IF EXISTS existing_network;
	CREATE TEMP TABLE existing_network as 
	SELECT w.id AS original_id, w.class_id, w.surface, w.foot, w.bicycle, (dp.geom).geom, w.source, w.target, 
	w.lit_classified, w.wheelchair_classified, w.impedance_surface
	FROM basic.edge w, union_perpendicular_split_lines p, 
	LATERAL (SELECT ST_DUMP(ST_CollectionExtract(ST_SPLIT(w.geom,p.geom),2)) AS geom) dp
	WHERE ST_Intersects(w.geom, p.geom)
	AND w.scenario_id IS NULL
	AND w.id NOT IN (SELECT way_id FROM modified_attributes_only);
	ALTER TABLE existing_network ADD COLUMN id serial;
	ALTER TABLE existing_network ADD PRIMARY KEY(id);
	CREATE INDEX ON existing_network USING GIST(geom);

	/*Assign vertices that where snapped to new features*/
	UPDATE new_network n
	SET SOURCE = s.node_id
	FROM snapped_drawn_features s
	WHERE n.did = s.did 
	AND s.node_id IS NOT NULL 
	AND s.point_type = 's'
	AND ST_ASTEXT(st_startpoint(n.geom)) = ST_ASTEXT(s.geom); 
	
	UPDATE new_network n
	SET target = s.node_id
	FROM snapped_drawn_features s
	WHERE n.did = s.did 
	AND s.node_id IS NOT NULL 
	AND ST_ASTEXT(st_endpoint(n.geom)) = ST_ASTEXT(s.geom); 

	/*Create new vertices*/
	DROP TABLE IF EXISTS loop_vertices;
	CREATE TEMP TABLE loop_vertices AS
	WITH start_end_point AS 
 	(
		SELECT e.id, st_startpoint(geom) geom, 's' AS point_type 
		FROM new_network e 
		WHERE SOURCE IS NULL 
		UNION ALL 
		SELECT e.id, st_endpoint(geom) geom, 'e' AS point_type 
		FROM new_network e 
		WHERE target IS NULL 
	),
	clusters AS 
	(
		SELECT s.id, s.geom, ST_ClusterDBSCAN(geom, eps := 0.000001, minpoints := 1) OVER() AS cid, point_type
		FROM start_end_point s
	),
	grouped AS 
	(
		SELECT ST_CENTROID(ST_COLLECT(geom)) AS geom, ARRAY_AGG(point_type)::text[] AS point_types, ARRAY_AGG(id)::integer[] new_network_ids
		FROM clusters c
		GROUP BY cid 
	)
	SELECT geom, point_types, new_network_ids
	FROM grouped; 

	DROP TABLE IF EXISTS new_vertices;  
	CREATE TEMP TABLE new_vertices 
	(
		node_id integer,
		new_network_ids integer[],
		point_types text[],
		geom geometry
	);
	/*
	DO $$
	DECLARE 
		rec record;
		max_id integer; 
	BEGIN*/
	FOR rec IN SELECT * FROM loop_vertices v
	LOOP 
		max_id = (SELECT max(id) FROM basic.node);
		WITH i AS 
		(
			INSERT INTO basic.node (id, scenario_id, geom) 
			VALUES(max_id + 1, scenario_id_input, rec.geom)
			RETURNING id, geom
		)
		INSERT INTO new_vertices(node_id, new_network_ids, point_types, geom)
		SELECT i.id, rec.new_network_ids, rec.point_types, i.geom  
		FROM i;			
	END LOOP;
	/*END $$;*/
	CREATE INDEX ON new_vertices USING GIST(geom);
	
	WITH unnest_to_update AS 
	(
		SELECT v.node_id, UNNEST(v.new_network_ids) new_network_id, UNNEST(v.point_types) point_type
		FROM new_vertices v 
	)
	UPDATE new_network n
	SET SOURCE = u.node_id 
	FROM unnest_to_update u
	WHERE n.id = u.new_network_id 
	AND point_type = 's';
	
	WITH unnest_to_update AS 
	(
		SELECT v.node_id, UNNEST(v.new_network_ids) new_network_id, UNNEST(v.point_types) point_type
		FROM new_vertices v 
	)
	UPDATE new_network n  
	SET target = u.node_id 
	FROM unnest_to_update u
	WHERE n.id = u.new_network_id  
	AND point_type = 'e';

	DROP TABLE IF EXISTS new_source_target_existing; 
	CREATE TEMP TABLE new_source_target_existing AS 
	WITH start_and_end AS 
	(
		SELECT e.id, st_startpoint(geom) geom, 's' AS point_type
		FROM existing_network e 
		UNION ALL 
		SELECT e.id,  st_endpoint(geom) geom, 'e' AS point_type  
		FROM existing_network e
	)
	SELECT v.id, point_type, c.node_id, v.geom  
	FROM start_and_end v
	CROSS JOIN LATERAL 
	(
		SELECT n.node_id 
		FROM new_vertices n
		WHERE ST_Intersects(ST_BUFFER(v.geom, 0.00001), n.geom)
		ORDER BY n.geom <-> v.geom 
		LIMIT 1 
	) c;
	
	UPDATE existing_network e
	SET SOURCE = n.node_id 
	FROM new_source_target_existing n 
	WHERE e.id = n.id 
	AND n.point_type = 's';
	
	UPDATE existing_network e
	SET target = n.node_id 
	FROM new_source_target_existing n 
	WHERE e.id = n.id 
	AND n.point_type = 'e';


	DROP TABLE IF EXISTS network_to_add;
	CREATE TEMP TABLE network_to_add AS 
	SELECT original_id, class_id, surface, foot, bicycle, geom, SOURCE, target, lit_classified, wheelchair_classified, impedance_surface  
	FROM existing_network  
	UNION ALL 
	SELECT NULL, 100, surface, foot, bicycle, geom, SOURCE, target, lit, wheelchair, NULL 
	FROM new_network;
	
	CREATE INDEX ON network_to_add USING GIST(geom);
	
	---Attach attributes to vertices
	DROP TABLE IF EXISTS vertices_to_add;
	CREATE TEMP TABLE vertices_to_add AS 
	SELECT vv.node_id, array_remove(array_agg(DISTINCT x.class_id),NULL) class_ids,
	array_remove(array_agg(DISTINCT x.foot),NULL) AS foot,
	array_remove(array_agg(DISTINCT x.bicycle),NULL) bicycle,
	array_remove(array_agg(DISTINCT x.lit_classified),NULL) lit_classified,
	array_remove(array_agg(DISTINCT x.wheelchair_classified),NULL) wheelchair_classified,
	vv.geom
	FROM new_vertices  vv
	LEFT JOIN
	(	
		SELECT v.node_id, w.class_id, w.foot, w.bicycle, w.lit_classified, w.wheelchair_classified 
		FROM new_vertices v, network_to_add w 
		WHERE st_intersects(ST_BUFFER(v.geom,0.00001),w.geom)
	) x
	ON vv.node_id = x.node_id
	GROUP BY vv.node_id, vv.geom;
	CREATE INDEX ON vertices_to_add (node_id);

	----------------------------------------------------------------------------------------------------------------------
	--INSERT NEW VERTICES AND WAYS INTO THE EXISTING TABLES
	----------------------------------------------------------------------------------------------------------------------

	/*DO $$
	DECLARE 
		rec record;
		max_id integer; 
	BEGIN*/
	FOR rec IN SELECT * FROM network_to_add  v
	LOOP 
		max_id = (SELECT max(id) FROM basic.edge);
	
		INSERT INTO basic.edge(id, class_id, source, target, foot, bicycle, wheelchair_classified, lit_classified, impedance_surface, geom, coordinates_3857, length_m, length_3857, scenario_id, edge_id) 
		SELECT max_id + 1, rec.class_id, rec.SOURCE, rec.target, rec.foot, rec.bicycle, rec.wheelchair_classified, 
		rec.lit_classified, rec.impedance_surface, rec.geom, (ST_AsGeoJSON(ST_Transform(rec.geom,3857))::json->'coordinates')::json, 
		ST_LENGTH(rec.geom::geography), ST_LENGTH(ST_TRANSFORM(rec.geom, 3857)), scenario_id_input, rec.original_id
		;		
	END LOOP;
	/*END $$;*/
	
	
    /*Set impedances for existing but now split network
	UPDATE ways_userinput ww
	SET s_imp = w.s_imp, rs_imp = w.rs_imp
	FROM ways_userinput w
	WHERE ww.original_id = w.id 
	AND ww.scenario_id = 1
	AND w.scenario_id IS NULL; 
	
	IF EXISTS
		( SELECT 1
			FROM   information_schema.tables 
			WHERE  table_schema = 'public'
			AND    table_name = 'dem'
		)
	THEN
		WITH impedances AS 
		(
			SELECT w.id, ci.imp, ci.rs_imp
			FROM ways_userinput w,
			LATERAL get_slope_profile(w.id, 10, 'ways_userinput') sp, LATERAL compute_impedances(sp.elevs, sp.linkLength, 10) ci
			WHERE scenario_id = scenario_id_input 
			AND original_id IS NULL 
		)
		UPDATE ways_userinput w
		SET s_imp = i.imp, rs_imp = i.rs_imp 
		FROM impedances i 
		WHERE w.id = i.id;
					
	END IF;
	*/
END
$function$;

