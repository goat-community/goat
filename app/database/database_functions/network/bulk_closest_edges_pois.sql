
DROP FUNCTION IF EXISTS pgrouting_edges_preparation_pois;
CREATE OR REPLACE FUNCTION public.pgrouting_edges_preparation_pois(cutoffs double precision[], startpoints double precision[], speed numeric, amenity_input text[], modus_input integer, routing_profile text, userid_input integer DEFAULT 0, scenario_id_input integer DEFAULT 0, heatmap_bulk_calculation boolean DEFAULT false, gids_scenario integer[] DEFAULT ARRAY[]::integer[])
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

	distance = cutoffs[array_upper(cutoffs, 1)] * speed;
	
	DROP TABLE IF EXISTS start_geoms;
	IF gids_scenario = ARRAY[]::integer[] THEN 
		CREATE /*TEMP*/ TABLE start_geoms AS 
		SELECT ST_SETSRID(ST_POINT(point[1], point[2]),4326) AS geom
		FROM (SELECT unnest_2d_1d(startpoints) point) AS points; 
		ALTER TABLE start_geoms ADD COLUMN gid integer;
		alter table start_geoms add column amenity integer;
	ELSE 
		CREATE /*TEMP*/ TABLE start_geoms AS 
		SELECT ST_SETSRID(ST_POINT(point[1], point[2]),4326) AS geom, amenity, gid
		FROM (SELECT unnest_2d_1d(startpoints) point, unnest(amenity_input) amenity, unnest(gids_scenario) gid) AS points; 
	END IF; 

	SELECT ST_ASTEXT(ST_Union(ST_Buffer(geom::geography,distance)::geometry))
	INTO buffer
	FROM start_geoms;
	
	IF routing_profile = 'walking_elderly' THEN 
		routing_profile = 'walking_standard';
	ELSIF routing_profile = 'walking_wheelchair_electric' OR routing_profile = 'walking_wheelchair_standard' THEN 
		routing_profile = 'walking_wheelchair';
 	END IF;
	
	DROP TABLE IF EXISTS temp_fetched_ways;
	CREATE /*TEMP*/ TABLE temp_fetched_ways AS 
	SELECT *
	FROM fetch_ways_routing(buffer,modus_input,scenario_id_input,speed,routing_profile);

  	ALTER TABLE temp_fetched_ways ADD PRIMARY KEY(id);
  	CREATE INDEX ON temp_fetched_ways (target);
  	CREATE INDEX ON temp_fetched_ways (source);
  	CREATE INDEX ON temp_fetched_ways (death_end);
  
	IF heatmap_bulk_calculation = FALSE THEN 
	  	DROP TABLE IF EXISTS start_vertices;
		CREATE /*TEMP*/ TABLE start_vertices AS 
	  	SELECT c.closest_point, c.fraction, c.wid, 999999999 - p.id AS vid, p.amenity, p.gid
	  	FROM (
	  		SELECT (ROW_NUMBER() over()) AS id, geom, amenity, gid 
			FROM start_geoms
		) p, closest_point_network_geom(p.geom) c; 
		
		SELECT array_agg(vid)::bigint[]
		INTO vids
		FROM start_vertices;
		IF (SELECT vid FROM start_vertices LIMIT 1) IS NOT NULL THEN 
			/*Originally fractional cost was computed using the fraction returned from closest_point_network_geom. 
			Though apparently because of differences of metric and kartesian coordinate system the results where sligthly wrong (1-5%). Therefore the length of the partial link is comuted with ::geography*/
			DROP TABLE IF EXISTS artificial_edges;
			CREATE /*TEMP*/ TABLE artificial_edges AS 
			SELECT wid, 999999998-(1+ROW_NUMBER() OVER())*2 AS id, cost*ST_LENGTH(ST_LINESUBSTRING(geom,0,fraction)::geography)/length_m as cost,reverse_cost*ST_LENGTH(ST_LINESUBSTRING(geom,0,fraction)::geography)/length_m AS reverse_cost,SOURCE,vid target,ST_LINESUBSTRING(geom,0,fraction) geom
			FROM temp_fetched_ways w, start_vertices v 
			WHERE w.id = v.wid
			UNION ALL 
			SELECT wid, 999999999-(1+ROW_NUMBER() OVER())*2 AS id, cost*(1-ST_LENGTH(ST_LINESUBSTRING(geom,0,fraction)::geography)/length_m) AS cost,reverse_cost*(1-ST_LENGTH(ST_LINESUBSTRING(geom,0,fraction)::geography)/length_m) AS reverse_cost,vid source,target,ST_LINESUBSTRING(geom,fraction,1) geom
			FROM temp_fetched_ways w, start_vertices v 
			WHERE w.id = v.wid;	
		END IF;
	END IF;

	
	IF heatmap_bulk_calculation = TRUE AND (SELECT count(*) FROM (SELECT * FROM reached_edges_pois LIMIT 1) x) IS NOT NULL THEN 
		IF scenario_id_input = 0 THEN 
			buffer_bulk = (SELECT ST_UNION(geom) FROM pois);
		ELSE
			WITH pois_recompute AS 
			(
				SELECT UNNEST(gids) gid
				FROM changed_pois
			)
			SELECT ST_UNION(g.geom)
			INTO buffer_bulk
			FROM pois g, pois_recompute r 
			WHERE g.gid = r.gid;
		END IF;
	
		DROP TABLE IF EXISTS fetched_ways_bulk;
		CREATE /*TEMP*/ TABLE fetched_ways_bulk AS 
		SELECT *
		FROM fetch_ways_routing(ST_ASTEXT(buffer_bulk),modus_input,scenario_id_input,speed,routing_profile);
		CREATE INDEX ON fetched_ways_bulk USING GIST(geom);
		PERFORM bulk_closest_edges_pois(buffer_bulk);
	END IF;
	
/*Handle artificial edges for single and multi-calculation*/
	IF (SELECT count(*) FROM (SELECT vid FROM start_vertices LIMIT 2) v) = 1 THEN
	/*Single*/
		INSERT INTO temp_fetched_ways(id,cost,reverse_cost,source,target,geom)
		SELECT a.id, a.cost, a.reverse_cost, a.source, a.target, a.geom 
		FROM artificial_edges a;
	ELSE 
	/*Multi*/
		DROP TABLE IF EXISTS ways_to_replace;
		CREATE TABLE ways_to_replace AS 
		SELECT DISTINCT a.wid  
		FROM temp_fetched_ways w, artificial_edges a 
		WHERE w.id = a.wid;
		CREATE INDEX ON ways_to_replace (wid);
		
		DELETE FROM temp_fetched_ways t 
		USING ways_to_replace w 
		WHERE t.id = w.wid;
		
		INSERT INTO temp_fetched_ways(id,source,target,cost,reverse_cost,geom)
		SELECT a.id, SOURCE, target, a.COST, a.reverse_cost, geom  
		FROM artificial_edges a, ways_to_replace w 
		WHERE a.wid = w.wid;
	END IF;

END;
$function$

/*
SELECT pgrouting_edges_preparation(ARRAY[1200.]::FLOAT[], ARRAY[[11.5707,48.1252]],1.33, 2, 'walking_standard',10, 5, FALSE)
*/