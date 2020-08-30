
CREATE OR REPLACE FUNCTION public.pgrouting_edges_preparation(cutoffs double precision[], startpoints double precision[], speed numeric, modus_input integer, routing_profile text, userid_input integer DEFAULT 0, scenario_id integer DEFAULT 0, heatmap_bulk_calculation boolean DEFAULT false)
 RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE
	buffer text;
	buffer_bulk TEXT;
	distance numeric;
	userid_vertex integer;
	vids bigint[];
BEGIN 
	IF modus_input IN(1,3)  THEN
		userid_vertex = 1;
		userid_input = 1;
	ELSEIF modus_input = 2 THEN
		userid_vertex = userid_input;
	ELSEIF modus_input = 4 THEN  	 
		userid_vertex = 1;
	END IF;
	
	distance = cutoffs[array_upper(cutoffs, 1)] * speed;
	
	DROP TABLE IF EXISTS start_geoms;
	CREATE TEMP TABLE start_geoms AS 
	SELECT ST_SETSRID(ST_POINT(point[1], point[2]),4326) AS geom
	FROM (SELECT unnest_2d_1d(startpoints) point) AS points; 
	
	SELECT ST_ASTEXT(ST_Union(ST_Buffer(geom::geography,distance)::geometry))
	INTO buffer
	FROM start_geoms;
	
	IF routing_profile = 'walking_elderly' THEN 
		routing_profile = 'walking_standard';
	ELSIF routing_profile = 'walking_wheelchair_electric' OR routing_profile = 'walking_wheelchair_standard' THEN 
		routing_profile = 'walking_wheelchair';
 	END IF;
	
	DROP TABLE IF EXISTS temp_fetched_ways;
	CREATE TEMP TABLE temp_fetched_ways AS 
	SELECT *
	FROM fetch_ways_routing(buffer,modus_input,userid_input,speed,routing_profile);

  	ALTER TABLE temp_fetched_ways ADD PRIMARY KEY(id);
  	CREATE INDEX ON temp_fetched_ways (target);
  	CREATE INDEX ON temp_fetched_ways (source);
  	CREATE INDEX ON temp_fetched_ways (death_end);
  
	IF heatmap_bulk_calculatIon = FALSE THEN 
	  	DROP TABLE IF EXISTS start_vertices;
		CREATE TEMP TABLE start_vertices AS 
	  	SELECT c.closest_point, c.fraction, c.wid, 999999999 - p.id AS vid
	  	FROM (
	  		SELECT (ROW_NUMBER() over()) AS id, geom 
			FROM start_geoms
		) p, closest_point_network_geom(p.geom) c; 
		
		SELECT array_agg(vid)::bigint[]
		INTO vids
		FROM start_vertices;
		IF (SELECT vid FROM start_vertices LIMIT 1) IS NOT NULL THEN 
			DROP TABLE IF EXISTS artificial_edges;
			CREATE TEMP TABLE artificial_edges AS 
			SELECT wid, 999999998-(1+ROW_NUMBER() OVER())*2 AS id, cost*fraction AS cost,reverse_cost*fraction AS reverse_cost,SOURCE,vid target,ST_LINESUBSTRING(geom,0,fraction) geom
			FROM temp_fetched_ways w, start_vertices v 
			WHERE w.id = v.wid
			UNION ALL 
			SELECT wid, 999999999-(1+ROW_NUMBER() OVER())*2 AS id, cost*(1-fraction) AS cost,reverse_cost*(1-fraction) AS reverse_cost,vid source,target,ST_LINESUBSTRING(geom,fraction,1) geom
			FROM temp_fetched_ways w, start_vertices v 
			WHERE w.id = v.wid;
			
			INSERT INTO temp_fetched_ways(id,cost,reverse_cost,source,target,geom)
			SELECT a.id, a.cost, a.reverse_cost, a.source, a.target, a.geom 
			FROM artificial_edges a;
		END IF;
	ELSE 
		IF (SELECT count(*) FROM (SELECT * FROM reached_edges_heatmap LIMIT 1) x) <> 1 THEN 
			buffer_bulk = (SELECT ST_ASTEXT(ST_UNION(geom)) FROM grid_heatmap);
			DROP TABLE IF EXISTS fetched_ways_bulk;
			CREATE TEMP TABLE fetched_ways_bulk AS 
			SELECT *
			FROM fetch_ways_routing(buffer_bulk,modus_input,userid_input,speed,routing_profile);
			CREATE INDEX ON fetched_ways_bulk USING GIST(geom);
			PERFORM bulk_closest_edges();
			raise notice 'bulk';
		END IF;
		DROP TABLE IF EXISTS ways_to_replace;
		CREATE TABLE ways_to_replace AS 
		SELECT DISTINCT a.wid  
		FROM temp_fetched_ways w, artificial_edges a 
		WHERE w.id = a.wid;
		CREATE INDEX ON ways_to_replace (wid);
		
		DELETE FROM temp_fetched_ways t 
		USING ways_to_replace w 
		WHERE t.id = w.wid;
		
		INSERT INTO temp_fetched_ways 
		SELECT a.id, SOURCE, target, a.COST, a.reverse_cost, NULL, NULL, geom  
		FROM artificial_edges a, ways_to_replace w 
		WHERE a.wid = w.wid;
	END IF;

END;
$function$


/*
SELECT pgrouting_edges_preparation(ARRAY[1200.]::FLOAT[], array_agg(starting_points)::FLOAT[], 
1.33, 1, 'walking_standard',0, 0, true)
FROM (SELECT * FROM grid_ordered WHERE id BETWEEN 151 AND 300) g

*/