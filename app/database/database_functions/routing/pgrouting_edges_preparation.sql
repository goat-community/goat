CREATE OR REPLACE FUNCTION public.pgrouting_edges_preparation(cutoffs float[], startpoints float[][], speed numeric, userid_input integer, modus_input integer, routing_profile text)
 RETURNS BIGINT[] 
 LANGUAGE plpgsql
AS $function$
DECLARE
	buffer text;
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
	
  	DROP TABLE IF EXISTS start_vertices;
	CREATE TEMP TABLE start_vertices AS 
  	SELECT c.closest_point, c.fraction, c.wid, 999999999 - (ROW_NUMBER() over()) AS vid
  	FROM (
  		SELECT geom 
		FROM start_geoms
	) p, closest_point_network_geom(p.geom) c; 
	
	SELECT array_agg(vid)::bigint[]
	INTO vids
	FROM start_vertices;

	IF (SELECT vid FROM start_vertices LIMIT 1) IS NOT NULL THEN 
		INSERT INTO temp_fetched_ways(id,cost,reverse_cost,source,target,geom)
		SELECT 99999998-(ROW_NUMBER() OVER())*2, cost*fraction,reverse_cost*fraction,SOURCE,vid,ST_LINESUBSTRING(geom,0,fraction)
		FROM temp_fetched_ways, start_vertices  
		WHERE id = wid
		UNION ALL 
		SELECT 99999999-(ROW_NUMBER() OVER())*2, cost*(1-fraction),reverse_cost*(1-fraction),vid,target,ST_LINESUBSTRING(geom,fraction,1)
		FROM temp_fetched_ways, start_vertices 
		WHERE id = wid;
	END IF;
	
    DELETE FROM temp_fetched_ways 
   	USING start_vertices v
    WHERE id = v.wid;
   	
   	RETURN vids;
END;
$function$;
