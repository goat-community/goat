--alphashape_parameter NUMERIC = 0.00003;
--region_type 'envelope' or study_area
CREATE OR REPLACE FUNCTION public.pois_multi_isochrones(userid_input integer, minutes integer, speed_input numeric, alphashape_parameter_input NUMERIC, modus_input integer,region_type text, region text[], amenities text[])
RETURNS SETOF type_pois_multi_isochrones
AS $function$ 
DECLARE 	
 	boundary_envelope numeric[];
 	i integer;
 	points_array numeric[][];
 	objectids_array integer [];
 	mask geometry;
 	buffer_mask geometry;
	buffer integer;
 	excluded_class_id integer[];
	categories_no_foot text[];
	population_mask jsonb;
	objectid_multi_isochrone integer;
	BEGIN
	--------------------------------------------------------------------------------------
	----------------------get starting points depending on passed parameters--------------
	--------------------------------------------------------------------------------------	
	SELECT select_from_variable_container('excluded_class_id_walking')::text[],
	select_from_variable_container('categories_no_foot')::text
	INTO excluded_class_id, categories_no_foot;
 	
    buffer = (minutes::numeric/60::numeric)*speed_input*1000;
 
 	IF region_type = 'study_area' THEN
 		--Logic to intersect the amenities with a study area defined by name
		SELECT ST_Union(geom) AS geom, array_to_json(array_agg(jsonb_build_object(name,sum_pop))) 
		INTO mask, population_mask
		FROM study_area
		WHERE name IN (SELECT UNNEST(region));
		
		buffer_mask = ST_buffer(mask::geography,buffer)::geometry;
	
		SELECT array_agg(ARRAY[ST_X(p.geom)::numeric, ST_Y(p.geom)::numeric]) 
		INTO points_array
		FROM pois p
		WHERE p.amenity IN (SELECT UNNEST(amenities))
		AND st_intersects(p.geom, buffer_mask);
 	 
 	ELSE 
		boundary_envelope = region::numeric[];
		
		mask = ST_MakeEnvelope(boundary_envelope[1],boundary_envelope[2],boundary_envelope[3],boundary_envelope[4],4326);
	
		SELECT jsonb_build_object('bounding_box',sum(population)::integer) AS sum_pop
		INTO population_mask
		FROM population p 
		WHERE ST_Intersects(p.geom,mask);		
	
 		SELECT ST_Buffer(mask::geography,buffer)::geometry 
 		INTO buffer_mask;

		SELECT array_agg(ARRAY[ST_X(p.geom)::numeric, ST_Y(p.geom)::numeric]) 
		INTO points_array
		FROM pois p
		WHERE p.amenity IN (SELECT UNNEST(amenities))
 		AND st_intersects(p.geom, buffer_mask);		
 	 END IF;
 	---------------------------------------------------------------------------------
 	--------------------------get catchment of all starting points-------------------
 	---------------------------------------------------------------------------------
 
 	SELECT array_agg(series)
 	INTO objectids_array
 	FROM (
 		SELECT generate_series(1,array_length(points_array,1)) AS series
 	) x;  --create id's array for the points
 	
 	DROP TABLE IF EXISTS temp_catchment_vertices;
    CREATE TEMP TABLE temp_catchment_vertices AS
	SELECT start_vertex,node,edge,cost,geom,objectid 
 	FROM pgrouting_edges_multi(minutes, points_array, speed_input::NUMERIC, objectids_array); -- routing is expensive

 	ALTER TABLE temp_catchment_vertices ADD COLUMN id serial;
 	ALTER TABLE temp_catchment_vertices ADD PRIMARY key(id);
 	CREATE INDEX ON temp_catchment_vertices (objectid);
 	
    ----------------------------------------------------------------------------------------
    -----------------extrapolate the catchment vertices-------------------------------------
    ----------------------------------------------------------------------------------------
 
 	DROP TABLE IF EXISTS extrapolated_reached_vertices;
	CREATE TEMP TABLE extrapolated_reached_vertices AS  --create empty table that will hold the extrapolated vertices
	SELECT * FROM temp_catchment_vertices
	LIMIT 0;
	 	
	FOR i IN SELECT DISTINCT objectid FROM temp_catchment_vertices  --extrapolate each cluster of catchment vertices
 	LOOP

		IF (SELECT count(*)	FROM temp_catchment_vertices LIMIT 4) > 3  THEN 
 	
			DROP TABLE IF EXISTS temp_reached_vertices;	-- this table is used by the extrapolate_reached_vertices function
			CREATE TABLE temp_reached_vertices AS 
			SELECT start_vertex, node, edge, cost, geom, objectid 
			FROM temp_catchment_vertices
			WHERE objectid = i;				
			--ALTER TABLE temp_reached_vertices ADD COLUMN id serial; --we cannot add columns to the table, it would break extrapolate_reached_vertices()
			--ALTER TABLE temp_reached_vertices ADD PRIMARY key(id);
				
			INSERT INTO extrapolated_reached_vertices
			SELECT * 
			FROM extrapolate_reached_vertices(minutes*60,(speed_input/3.6),excluded_class_id,categories_no_foot); 
 	
			END IF;
			
		END LOOP;

		ALTER TABLE extrapolated_reached_vertices ADD COLUMN gid SERIAL;
		ALTER TABLE extrapolated_reached_vertices ADD PRIMARY key(gid);
		CREATE INDEX ON extrapolated_reached_vertices (cost);
	    CREATE INDEX ON extrapolated_reached_vertices (objectid);
		DROP TABLE IF EXISTS isos;
		CREATE TEMP TABLE isos (geom geometry);
		
		----------------------------------------------------------------------------------------
		----------------------create isochrone for each extrapolated point cluster--------------
		----------------------------------------------------------------------------------------	
	
		FOR i IN SELECT DISTINCT objectid FROM extrapolated_reached_vertices
		LOOP
		
			INSERT INTO isos
			SELECT * FROM pgr_pointsaspolygon('SELECT (row_number() over())::integer as id, ST_X(geom)::float x, ST_Y(geom)::float y FROM extrapolated_reached_vertices WHERE objectid = '||i||'',alphashape_parameter_input);
		
		END LOOP;
 		
		objectid_multi_isochrone = random_between(1,900000000);
	
		INSERT INTO multi_isochrones(userid,geom,speed,alphashape_parameter,modus,objectid,parent_id)
		SELECT userid_input,ST_Union(geom) AS geom, speed_input, alphashape_parameter_input, modus_input, objectid_multi_isochrone, 1
		FROM isos;
		
 		IF region_type = 'study_area' THEN
		 	WITH expand_population AS 
			(
				SELECT jsonb_array_elements(population_mask) AS population 
			),
			iso_intersection AS (
				SELECT s.name, m.gid, ST_Intersection(s.geom,ST_SetSrid(m.geom,4326)) AS geom 
				FROM study_area s, multi_isochrones m
				WHERE s.name IN (SELECT UNNEST(region) AS name)
				AND m.objectid = objectid_multi_isochrone
			),
			reached_population AS (
				SELECT i.name, jsonb_build_object(concat(i.name,'_reached'),sum(p.population)::integer) reached_population
				FROM iso_intersection i, population p  
				WHERE ST_intersects(i.geom, p.geom)
				GROUP BY i.name
			)
			UPDATE multi_isochrones m
			SET population = x.new_population
			FROM (
				SELECT array_to_json(array_agg(e.population|| r.reached_population)) new_population
				FROM expand_population e, reached_population r
				WHERE e.population::jsonb ? r.name
			) x 
			WHERE m.objectid = objectid_multi_isochrone;
		
 		ELSE 

 			UPDATE multi_isochrones 
			SET population = population_mask || x.reached_population
			FROM (
				SELECT jsonb_build_object('bounding_box_reached',sum(p.population)::integer) AS reached_population
				FROM population p, multi_isochrones m 
				WHERE ST_Intersects(p.geom,ST_Intersection(mask,ST_SetSrid(m.geom,4326)))
				AND m.objectid = objectid_multi_isochrone
			) x
			WHERE multi_isochrones.objectid = objectid_multi_isochrone;
 		END IF; 
 		RETURN query 
 		SELECT userid,geom geometry,gid,speed,alphashape_parameter,modus,objectid,parent_id,population
 		FROM multi_isochrones
 		WHERE objectid = objectid_multi_isochrone;
	END;
$function$ LANGUAGE plpgsql;


/*
CREATE OR REPLACE FUNCTION pois_multi_isochrones (pois text,userid integer, minutes integer,step integer, speed numeric,concavity numeric,modus integer,parent_id integer)
  RETURNS TABLE (geom geometry,population_administrative integer, reached_population integer, share_population float, step integer, name varchar, pois jsonb)
AS $$
 pois_array = [];
 pois_input = pois.split(',')
 poi_categories = list(plpy.execute("SELECT variable_array FROM variable_container WHERE identifier = 'poi_categories'")[0]["variable_array"])
 array_x = []
 array_y = [] 
 for i in pois_input:
 	if i in poi_categories:
 		pois_array.append(i)
 pois_array = str(pois_array)
 
 buffer_study_area = str(minutes * speed) 
 query = "SELECT ST_x(p.geom) x,ST_y(p.geom) y FROM pois p, study_area s \
		  WHERE p.geom && ST_Buffer(s.geom::geography,"+buffer_study_area+")::geometry \
		  AND p.amenity IN ("+pois_array[1:-1]+") UNION ALL "
 query = query + "SELECT ST_x(p.geom) x,ST_y(p.geom) y \
				  FROM public_transport_stops p, study_area s \
				  WHERE p.geom && ST_Buffer(s.geom::geography,"+buffer_study_area+")::geometry \
				  AND p.public_transport_stop IN ("+pois_array[1:-1]+");"
 for i in plpy.execute(query):
 	array_x.append(i["x"])
 	array_y.append(i["y"])
 query = "SELECT * FROM \
		  multi_isochrones ($1, $2, '{"+str(array_x)[1:-1]+"}','{"+str(array_y)[1:-1]+"}',$3, $4,$5,$6,$7)"
 plan = plpy.prepare(query,["integer","integer","integer","numeric","numeric","integer","integer"])
 response = plpy.execute(plan,[userid,minutes,step,speed,concavity,modus,parent_id])
 row_count  = response.nrows() 
 return response[0:row_count]
$$ LANGUAGE plpython3u;

*/