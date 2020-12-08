
DROP FUNCTION IF EXISTS compute_accessibility;
CREATE OR REPLACE FUNCTION compute_accessibility(scenario_id_input integer)
  RETURNS SETOF void AS
$func$

BEGIN
	DROP TABLE IF EXISTS computed_accessibility; 
	CREATE TEMP TABLE computed_accessibility AS  
	WITH x AS 
	(
		SELECT gid, ((arr_cost @* arr_cost)::real[] @/ -s.sensitivity::real) AS pre_accessibility
		FROM reached_pois_heatmap rph, (SELECT UNNEST(select_from_variable_container('heatmap_sensitivities'))  sensitivity) s 
		WHERE scenario_id = 0 
	)
	SELECT gid, array_agg(vec_pow(exp(1.0)::real,pre_accessibility) @* 10000::REAL)::integer[] AS accessibility_indices 
	FROM x
	GROUP BY gid; 
	
	ALTER TABLE computed_accessibility ADD PRIMARY key(gid);
	
	UPDATE reached_pois_heatmap r SET accessibility_indices = t.accessibility_indices 
	FROM computed_accessibility t 
	WHERE r.gid = t.gid
	AND r.scenario_id = 0;
END;

$func$  LANGUAGE plpgsql;



SELECT compute_accessibility(0)


DROP FUNCTION IF EXISTS insert_pois;
CREATE OR REPLACE FUNCTION public.insert_pois_userinput() 
RETURNS TRIGGER AS $table_insert_pois$

BEGIN

	DELETE FROM pois_userinput WHERE pois_modified_id = NEW.gid;

	INSERT INTO pois_userinput(name,amenity,opening_hours,geom,scenario_id,wheelchair,pois_modified_id)	
	VALUES(NEW.name, NEW.amenity, NEW.opening_hours,NEW.geom,NEW.scenario_id,NEW.wheelchair,NEW.gid);

	--PERFORM reached_pois_heatmap(ST_BUFFER(NEW.geom,0.0014),0.0014,1,NEW.scenario_id) ;
	
	RETURN NEW;

END;
$table_insert_pois$ LANGUAGE plpgsql;



SELECT * FROM grid_ordered 

EXPLAIN ANALYZE 
WITH grids_recompute AS 
(
	CREATE TABLE grids_recompute AS 
	SELECT UNNEST(gridids) grid_id
	FROM changed_grids
)
SELECT ST_UNION(g.geom)
FROM grid_heatmap g, grids_recompute r 
WHERE g.grid_id = r.grid_id;

DROP FUNCTION IF EXISTS recompute_heatmap;
CREATE OR REPLACE FUNCTION recompute_heatmap(scenario_id_input integer)
  RETURNS SETOF VOID AS
$func$
DECLARE 
	speed NUMERIC := 1.33;
	max_cost NUMERIC := 1200.;
	userid_input integer := (SELECT userid FROM scenarios WHERE scenario_id = scenario_id_input);
BEGIN 
	
	DELETE FROM reached_edges_heatmap 
	WHERE scenario_id = scenario_id_input;

	DELETE FROM area_isochrones_scenario
	WHERE scenario_id = scenario_id_input;
	
	DROP TABLE IF EXISTS changed_grids;
	CREATE TEMP TABLE changed_grids AS 
	SELECT * FROM find_changed_grids(scenario_id_input,speed*max_cost);

	PERFORM public.pgrouting_edges_heatmap(ARRAY[max_cost], f.starting_points, speed, f.gridids, 2, 'walking_standard',userid_input, scenario_id_input, section_id)
	FROM changed_grids f;
	
	PERFORM compute_area_isochrone(UNNEST(gridids),scenario_id_input)
	FROM changed_grids;
	
	UPDATE scenarios 
	SET ways_heatmap_computed = TRUE 
	WHERE scenario_id = scenario_id_input;
	
END 	
$func$  LANGUAGE plpgsql;

/*SELECT recompute_heatmap(2)*/


PERFORM reached_pois_heatmap(ST_BUFFER(NEW.geom,0.0014),0.0014,1,NEW.scenario_id)

SELECT * FROM reached_edges_heatmap WHERE scenario_id = 13 

SELECT ST_ASTEXT(ST_UNION(buffer_geom)) FROM changed_grids

SELECT * FROM changed_grids 

SELECT recompute_heatmap(13)

SELECT * FROM start_vertices 

SELECT * FROM reached_pois_heatmap rph 

SELECT * FROM temp_fetched_ways 

DROP FUNCTION IF EXISTS reached_pois_heatmap;
CREATE OR REPLACE FUNCTION public.reached_pois_heatmap(buffer_geom geometry, snap_distance NUMERIC, combination_scenarios integer DEFAULT 0, scenario_id_input integer DEFAULT 0)
RETURNS VOID
AS $function$
DECLARE
	sensitivities integer[] := select_from_variable_container('heatmap_sensitivities');
	series_sensitivities integer[]; 
	scenario_edges integer := 0;
	scenario_pois integer := 0;

BEGIN 
	/*This is preliminary. We need a better way for handling the scenarios. */
	IF combination_scenarios = 1 THEN /*Only POIs scenario*/
		scenario_edges = 0;
		scenario_pois = scenario_id_input;
	ELSEIF combination_scenarios = 2 THEN /*Only edges scenario*/
		scenario_edges = scenario_id_input;
		scenario_pois = 0;
	ELSEIF combination_scenarios = 3 THEN /*POIs and edges scenario*/
		scenario_edges = scenario_id_input;
		scenario_pois = scenario_id_input;
	END IF; 
	
	series_sensitivities = (SELECT array_agg(x.s)
	FROM (SELECT generate_series(1,ARRAY_LENGTH(select_from_variable_container('heatmap_sensitivities'),1)) s) x);
	/*Match all POIs that have their closest distance to an full edge*/
	DROP TABLE IF EXISTS reached_full_edges;

	IF combination_scenarios = 0 THEN 
		CREATE TEMP TABLE reached_full_edges AS 
		WITH p AS 
	    (
	        SELECT p.gid, p.amenity, p.name, p.geom, e.edge, e.gridids, e.fraction, e.start_cost, e.end_cost
	        FROM pois_userinput p
	        CROSS JOIN LATERAL
	        (
	            SELECT f.edge, f.gridids, ST_LineLocatePoint(f.geom,p.geom) AS fraction, f.start_cost, f.end_cost 
	            FROM reached_edges_heatmap f
	            WHERE f.geom && ST_Buffer(p.geom,snap_distance)
	            AND ST_Intersects(f.geom,ST_BUFFER(buffer_geom,snap_distance))
	            AND f.partial_edge IS FALSE
	            AND f.scenario_id = scenario_edges
	            ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
	            LIMIT 1           
	        ) AS e
	        WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances')))
	        AND ST_Intersects(p.geom,buffer_geom)
	        AND p.scenario_id IS NULL 
	    )
	    SELECT p.gid, p.amenity, p.name, p.gridids, interpolate_cost(fraction,start_cost,end_cost)::integer[] arr_cost, p.edge, p.fraction, scenario_id_input scenario_id 
	    FROM p;
	   
	   	INSERT INTO reached_pois_heatmap(gid, amenity, name, gridids, arr_cost, edge, fraction, scenario_id)
		SELECT * FROM reached_full_edges;
	ELSE 
	
		/*Potential for performance improvements
		 - Run cross join on smaller set of edges by removing unchanged edges
		 - reduce number of POIs checked
		 - experiment with buffer distance
		 - rewrite interpolate_cost in C
		*/
		DROP TABLE IF EXISTS reached_full_edges;
		CREATE TEMP TABLE reached_full_edges AS 
		WITH p AS 
	    (
	        SELECT p.gid, p.amenity, p.name, p.geom, e.edge, e.gridids, e.fraction, e.start_cost, e.end_cost
	        FROM pois_userinput p
	        CROSS JOIN LATERAL
	        (
	            SELECT f.edge, f.gridids, ST_LineLocatePoint(f.geom,p.geom) AS fraction, f.start_cost, f.end_cost 
	            FROM reached_edges_heatmap f
	            WHERE f.geom && ST_Buffer(p.geom,0.0014)
	            AND ST_Intersects(f.geom,ST_BUFFER(ST_SETSRID(ST_GEOMFROMTEXT('POLYGON ((11.766724276349999 48.39306640625, 11.76637243196074 48.389494070215925, 11.765330419975523 48.386059017052254, 11.763638284330577 48.382893253925666, 11.761361052849775 48.38011843933772, 11.758586238261838 48.377841207856925, 11.755420475135246 48.37614907221197, 11.751985421971574 48.37510706022676, 11.7484130859375 48.3747552158375, 11.744840749903426 48.37510706022676, 11.744089150765168 48.375335055332755, 11.743925222559676 48.37535120085176, 11.740490169396004 48.37639321283697, 11.737324406269412 48.378085348481925, 11.734549591681475 48.38036257996272, 11.732272360200673 48.383137394550666, 11.730580224555727 48.386303157677254, 11.72953821257051 48.389738210840925, 11.729186368181251 48.393310546875, 11.72953821257051 48.396882882909075, 11.730580224555727 48.400317936072746, 11.732272360200673 48.403483699199334, 11.734549591681475 48.40625851378728, 11.737324406269412 48.408535745268075, 11.740490169396004 48.41022788091303, 11.743925222559676 48.41126989289824, 11.74749755859375 48.4116217372875, 11.747528076171875 48.4116187315684, 11.74755859375 48.4116217372875, 11.751130929784074 48.41126989289824, 11.751911873727048 48.41103299614306, 11.751985421971574 48.41102575227324, 11.755420475135246 48.40998374028803, 11.758586238261838 48.408291604643075, 11.761361052849775 48.40601437316228, 11.763638284330577 48.403239558574334, 11.765330419975523 48.400073795447746, 11.76637243196074 48.396638742284075, 11.766724276349999 48.39306640625))'),4326),0.0014))
	            AND f.partial_edge IS FALSE
	            AND f.scenario_id = 13
	            ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
	            LIMIT 1      	       	            
	        ) AS e
	        WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance') || select_from_variable_container('pois_more_entrances')))
	        AND ST_Intersects(p.geom,ST_SETSRID(ST_GEOMFROMTEXT('POLYGON ((11.766724276349999 48.39306640625, 11.76637243196074 48.389494070215925, 11.765330419975523 48.386059017052254, 11.763638284330577 48.382893253925666, 11.761361052849775 48.38011843933772, 11.758586238261838 48.377841207856925, 11.755420475135246 48.37614907221197, 11.751985421971574 48.37510706022676, 11.7484130859375 48.3747552158375, 11.744840749903426 48.37510706022676, 11.744089150765168 48.375335055332755, 11.743925222559676 48.37535120085176, 11.740490169396004 48.37639321283697, 11.737324406269412 48.378085348481925, 11.734549591681475 48.38036257996272, 11.732272360200673 48.383137394550666, 11.730580224555727 48.386303157677254, 11.72953821257051 48.389738210840925, 11.729186368181251 48.393310546875, 11.72953821257051 48.396882882909075, 11.730580224555727 48.400317936072746, 11.732272360200673 48.403483699199334, 11.734549591681475 48.40625851378728, 11.737324406269412 48.408535745268075, 11.740490169396004 48.41022788091303, 11.743925222559676 48.41126989289824, 11.74749755859375 48.4116217372875, 11.747528076171875 48.4116187315684, 11.74755859375 48.4116217372875, 11.751130929784074 48.41126989289824, 11.751911873727048 48.41103299614306, 11.751985421971574 48.41102575227324, 11.755420475135246 48.40998374028803, 11.758586238261838 48.408291604643075, 11.761361052849775 48.40601437316228, 11.763638284330577 48.403239558574334, 11.765330419975523 48.400073795447746, 11.76637243196074 48.396638742284075, 11.766724276349999 48.39306640625))'),4326))
	        AND (p.scenario_id IS NULL OR p.scenario_id = 13)        
	    )
	    SELECT p.gid, p.amenity, p.name, p.gridids, interpolate_cost(fraction,start_cost,end_cost)::integer[] AS arr_cost, p.edge, p.fraction, 13 scenario_id 
	    FROM p;
  		

	   	ALTER TABLE reached_full_edges ADD PRIMARY KEY(gid);
	   	CREATE INDEX ON reached_full_edges USING gin (gridids gin__int_ops);
		CREATE INDEX ON reached_full_edges USING gin (arr_cost gin__int_ops);
				    
	END IF;

   	/*Match all POIs that have as closest an partial edge*/
    DROP TABLE IF EXISTS reached_pois_partial; 
   	CREATE TEMP TABLE reached_pois_partial AS 
	SELECT p.gid, p.amenity, p.name, e.gridids, interpolate_cost(p.fraction, e.start_cost, e.end_cost) arr_cost, e.edge, p.fraction, 13 scenario_id
	FROM reached_full_edges p, reached_edges_heatmap e
	WHERE e.partial_edge IS TRUE
	AND e.scenario_id = 13
	AND p.edge = e.edge 
	AND p.fraction BETWEEN least(start_perc,end_perc) AND greatest(start_perc,end_perc)
	AND e.geom && ST_BUFFER(ST_SETSRID(ST_GEOMFROMTEXT('POLYGON ((11.766724276349999 48.39306640625, 11.76637243196074 48.389494070215925, 11.765330419975523 48.386059017052254, 11.763638284330577 48.382893253925666, 11.761361052849775 48.38011843933772, 11.758586238261838 48.377841207856925, 11.755420475135246 48.37614907221197, 11.751985421971574 48.37510706022676, 11.7484130859375 48.3747552158375, 11.744840749903426 48.37510706022676, 11.744089150765168 48.375335055332755, 11.743925222559676 48.37535120085176, 11.740490169396004 48.37639321283697, 11.737324406269412 48.378085348481925, 11.734549591681475 48.38036257996272, 11.732272360200673 48.383137394550666, 11.730580224555727 48.386303157677254, 11.72953821257051 48.389738210840925, 11.729186368181251 48.393310546875, 11.72953821257051 48.396882882909075, 11.730580224555727 48.400317936072746, 11.732272360200673 48.403483699199334, 11.734549591681475 48.40625851378728, 11.737324406269412 48.408535745268075, 11.740490169396004 48.41022788091303, 11.743925222559676 48.41126989289824, 11.74749755859375 48.4116217372875, 11.747528076171875 48.4116187315684, 11.74755859375 48.4116217372875, 11.751130929784074 48.41126989289824, 11.751911873727048 48.41103299614306, 11.751985421971574 48.41102575227324, 11.755420475135246 48.40998374028803, 11.758586238261838 48.408291604643075, 11.761361052849775 48.40601437316228, 11.763638284330577 48.403239558574334, 11.765330419975523 48.400073795447746, 11.76637243196074 48.396638742284075, 11.766724276349999 48.39306640625))'),4326),0.0014);

	CREATE INDEX ON reached_pois_partial (gid);

	IF combination_scenarios <> 0 THEN 
		
		INSERT INTO reached_pois_heatmap(gid, amenity, name, gridids, arr_cost, edge, fraction, scenario_id)
		SELECT f.gid, f.amenity, f.name, c.*, f.edge, f.fraction, 13		
		FROM reached_pois_heatmap r, reached_full_edges f, combine_default_scenario_grids(r.gridids, f.gridids, r.arr_cost, f.arr_cost) c
		WHERE r.gid = f.gid; 
			
		INSERT INTO reached_pois_heatmap(gid, amenity, name, gridids, arr_cost, edge, fraction, scenario_id)
		SELECT f.*
		FROM reached_full_edges f
		LEFT JOIN reached_pois_heatmap r   
		ON f.gid = r.gid
		WHERE r.gid IS NULL; 
		
	END IF; 

    CREATE INDEX ON reached_pois_partial(gid);
   	WITH pois_to_update AS 
	(
		SELECT p.gid, r.gridids, r.gridids # p.gridids[1] arr_position, p.gridids[1] p_gridid, 
		r.arr_cost, p.arr_cost[1] new_cost
		FROM reached_pois_heatmap r, reached_pois_partial p 
		WHERE r.gid = p.gid 
		AND r.gridids && p.gridids
		AND r.arr_cost[r.gridids # p.gridids[1]] > p.arr_cost[1]
		AND r.scenario_id = p.scenario_id
	),
	updated_arrays AS 
	(
		SELECT x.gid, gridids[1:(-1+arr_position)] + p_gridid || gridids[arr_position+1:]  AS gridids, 
		arr_cost[1:(-1+arr_position)] + new_cost || arr_cost[arr_position+1:] AS arr_cost, 13 scenario_id
		FROM pois_to_update x
	)
	UPDATE reached_pois_heatmap r
	SET gridids = u.gridids, arr_cost = u.arr_cost
	FROM updated_arrays u 
	WHERE r.gid = u.gid
	AND r.scenario_id = u.scenario_id;
	
	DROP TABLE IF EXISTS merged;
	CREATE TEMP TABLE merged AS 
	WITH grids_to_add AS 
	(
		SELECT p.gid, p.amenity, p.name, p.gridids[1] gridids, p.arr_cost[1] arr_cost, p.scenario_id 
		FROM reached_pois_heatmap r, reached_pois_partial p  
		WHERE r.gid = p.gid 
		AND (r.gridids && p.gridids) IS FALSE
		AND r.scenario_id = p.scenario_id
		ORDER BY gid, gridids 
	),
	group_cost_ids AS 
	(
		SELECT gid, scenario_id, array_agg(gridids) gridids, array_agg(arr_cost) arr_cost
		FROM grids_to_add 
		GROUP BY gid, scenario_id 
	)
	SELECT g.gid, g.gridids, g.arr_cost, g.scenario_id 
	FROM group_cost_ids g, reached_full_edges r
	WHERE r.gid = g.gid;

	ALTER TABLE merged ADD PRIMARY key(gid);	

	UPDATE reached_pois_heatmap r
	SET gridids = r.gridids || u.gridids::integer[], arr_cost = r.arr_cost || u.arr_cost::integer[]
	FROM merged u 
	WHERE r.gid = u.gid
	AND r.scenario_id = u.scenario_id;

	INSERT INTO reached_pois_heatmap(gid,amenity,name,gridids,arr_cost,edge,fraction,scenario_id)
	SELECT p.* 
	FROM reached_pois_partial p
	LEFT JOIN (SELECT gid FROM reached_pois_heatmap WHERE scenario_id = 13) r
	ON p.gid = r.gid
	WHERE r.gid IS NULL;

	IF scenario_id_input <> 0 THEN
		PERFORM compute_accessibility(13);
	END IF;

END;
$function$ LANGUAGE plpgsql

/*
SELECT reached_pois_heatmap(geom, 0.0014) 
FROM compute_sections 
WHERE section_id = 73
*/

SELECT * FROM reached_pois_heatmap rph WHERE scenario_id = 13



IF combination_scenarios <> 0 THEN 
		
		DROP TABLE test; 
		
		/*
		 Update existing reached pois 
		 Update partial
		 
		 */
		DROP TABLE pois_test;
		CREATE TABLE pois_test AS 
		
		WITH pois_to_check AS 
		(
			SELECT r.*, p.geom 
			FROM reached_pois_heatmap r, reached_full_edges f, pois_userinput p 
			WHERE r.gid = f.gid 
			AND f.gid = p.gid 
			AND (p.scenario_id = 13 OR p.scenario_id IS NULL);
		)
		
		WITH x AS 
		(
			SELECT UNNEST(ARRAY[796,599,923,791,687,44,949,26,1074,1220,1336,1243,511,934,1178,906,1223,859,1267,654,411,40,1219,464,434,824,360,145,361]) AS grid_id,
			UNNEST(ARRAY[775,445,1020,378,1162,635,817,81,601,862,1107,747,1112,606,397,456,670,677,336,934,614,500,1054,538,600,586,582,1087,1035]) AS true_cost
		), 
		y AS (
			SELECT UNNEST(ARRAY[415,63,1008,802,211,434,906,1243,923,1219,511,599,1267,40,361,411,1220,934,360,26,859,464,796,1178,824,1074,791,145,654,1223,158,44,949,854]) AS grid_id,
			UNNEST(ARRAY[1087,1156,862,1077,1169,612,467,984,1031,1065,1140,455,346,500,1047,726,974,714,593,81,790,551,786,397,698,649,377,1099,946,672,987,724,897,1126]) AS true_cost		
		)
		SELECT x.grid_id, y.grid_id, x.true_cost, y.true_cost 
		FROM x,y 
		WHERE x.grid_id = y.grid_id;
		
		CREATE TABLE scenario_edges AS 
		SELECT edge, geom, gridids[gridids # 360], start_cost[gridids # 360], end_cost[gridids # 360] 
		FROM reached_edges_heatmap 
		WHERE scenario_id = 13 
		AND gridids && ARRAY[360]
		
		CREATE TABLE default_edges AS 
		SELECT edge, geom, gridids[gridids # 360], start_cost[gridids # 360], end_cost[gridids # 360] 
		FROM reached_edges_heatmap 
		WHERE scenario_id = 0 
		AND gridids && ARRAY[360]
		
		CREATE TABLE scenario_edges2 AS 
		SELECT edge, geom, gridids[gridids # 1267], start_cost[gridids # 1267], end_cost[gridids # 1267] 
		FROM reached_edges_heatmap 
		WHERE scenario_id = 13 
		AND gridids && ARRAY[1267];
		
		CREATE TABLE default_edges2 AS 
		SELECT edge, geom, gridids[gridids # 1267], start_cost[gridids # 1267], end_cost[gridids # 1267] 
		FROM reached_edges_heatmap 
		WHERE scenario_id = 0 
		AND gridids && ARRAY[1267];
		
		
		CREATE TABLE test AS 
		SELECT r.*--, p.geom  
		FROM reached_pois_heatmap r, reached_full_edges f--, pois_userinput p
		WHERE r.gid = 783
		AND r.gid = f.
		
		SELECT gid,amenity,name, gridids, arr_cost FROM reached_pois_heatmap rph WHERE gid = 783
		UNION ALL 
		SELECT gid,amenity,name, gridids, arr_cost FROM reached_full_edges WHERE gid = 783
		
		SELECT gid,amenity,name, gridids, arr_cost FROM reached_pois_partial WHERE gid = 783
		
		
		AND r.scenario_id = 0
		AND r.gridids <> f.gridids
		AND r.arr_cost <> f.arr_cost
		AND r.edge <> f.edge 
		AND r.gid = p.gid 
		
		CREATE TABLE test_polygon AS 
		SELECT ST_SETSRID(ST_GEOMFROMTEXT('POLYGON ((11.766724276349999 48.39306640625, 11.76637243196074 48.389494070215925, 11.765330419975523 48.386059017052254, 11.763638284330577 48.382893253925666, 11.761361052849775 48.38011843933772, 11.758586238261838 48.377841207856925, 11.755420475135246 48.37614907221197, 11.751985421971574 48.37510706022676, 11.7484130859375 48.3747552158375, 11.744840749903426 48.37510706022676, 11.744089150765168 48.375335055332755, 11.743925222559676 48.37535120085176, 11.740490169396004 48.37639321283697, 11.737324406269412 48.378085348481925, 11.734549591681475 48.38036257996272, 11.732272360200673 48.383137394550666, 11.730580224555727 48.386303157677254, 11.72953821257051 48.389738210840925, 11.729186368181251 48.393310546875, 11.72953821257051 48.396882882909075, 11.730580224555727 48.400317936072746, 11.732272360200673 48.403483699199334, 11.734549591681475 48.40625851378728, 11.737324406269412 48.408535745268075, 11.740490169396004 48.41022788091303, 11.743925222559676 48.41126989289824, 11.74749755859375 48.4116217372875, 11.747528076171875 48.4116187315684, 11.74755859375 48.4116217372875, 11.751130929784074 48.41126989289824, 11.751911873727048 48.41103299614306, 11.751985421971574 48.41102575227324, 11.755420475135246 48.40998374028803, 11.758586238261838 48.408291604643075, 11.761361052849775 48.40601437316228, 11.763638284330577 48.403239558574334, 11.765330419975523 48.400073795447746, 11.76637243196074 48.396638742284075, 11.766724276349999 48.39306640625))'),4326)
		
		
		SELECT * FROM reached_pois_partial
	
		SELECT * FROM scenarios s 
	
		SELECT gid, gridids # UNNEST(gridids), UNNEST(gridids) AS grid_id, UNNEST(arr_cost) AS arr_cost, edge, fraction
		FROM reached_full_edges 
		

		
	END IF; 


SELECT * FROM compute_sections

SELECT reached_pois_heatmap(geom, 0.0014) 
FROM compute_sections 
WHERE section_id = 1

SELECT * FROM reached_pois_heatmap rph 


SELECT * FROM compute_sections 

SELECT * 
FROM reached_pois_heatmap rph 
WHERE scenario_id <> 0

CREATE OR REPLACE FUNCTION public.pgrouting_edges(cutoffs float[], startpoints float[][], speed numeric, userid_input integer, scenario_id_input integer, objectid_input integer, modus_input integer, routing_profile text)


SELECT * 
FROM public.pgrouting_edges(ARRAY[1200.], ARRAY[[11.752762,48.384882]],1.33, 1, 0, 99, 1, 'walking_standard')


DELETE FROM edges 
SELECT * FROM edges 


SELECT * 
FROM public.pgrouting_edges(ARRAY[1200.], ARRAY[[11.752762,48.384882]],1.33, 1, 13, 100, 2, 'walking_standard')



