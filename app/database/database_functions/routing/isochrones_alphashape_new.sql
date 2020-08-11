
DROP FUNCTION IF EXISTS isochrones_alphashape;
CREATE OR REPLACE FUNCTION public.isochrones_alphashape(userid_input integer, minutes integer, x numeric, y numeric, n integer, speed numeric, shape_precision numeric, modus integer, objectid_input integer, parent_id_input integer, routing_profile text)
 RETURNS SETOF type_isochrone
 LANGUAGE plpgsql
AS $function$
DECLARE
  	counter integer :=0;
  	max_length_links integer;
  	step_isochrone numeric = (minutes*60)/n;
  	i numeric;
 	sql_vertices TEXT;
 	cutoffs float[];
begin
	--If the modus is input the routing tables for the network with userinput have to be choosen
  	speed = speed/3.6;

  	DROP TABLE IF EXISTS isos;
  	CREATE temp TABLE isos OF type_isochrone;
	
	SELECT array_agg(x.border) 
	INTO cutoffs
	FROM (SELECT generate_series(step_isochrone,(minutes*60),step_isochrone)::float border) x; 

	INSERT INTO edges (edge,COST, start_cost, end_cost, geom, objectid)
  	SELECT p.edge, p.COST, p.start_cost, p.end_cost, p.geom, p.objectid
  	FROM pgrouting_edges_new(cutoffs, ARRAY[[x,y]],speed, userid_input, objectid_input, modus, routing_profile) p;

	
	FOR i IN SELECT unnest(cutoffs)
	LOOP
	counter = counter + 1;
	IF (SELECT count(*) FROM edges WHERE objectid=objectid_input AND cost BETWEEN 0 AND i LIMIT 4) > 3 THEN 
		sql_vertices = format('
		SELECT ROW_NUMBER() over()::integer AS id, x, y 
		FROM (
			 SELECT  ST_X(ST_STARTPOINT(geom))::float x, ST_Y(ST_STARTPOINT(geom))::float y 
			 FROM edges WHERE objectid=%s AND cost = start_cost AND cost BETWEEN 0 AND %s
			 UNION ALL 
			 SELECT  ST_X(ST_ENDPOINT(geom))::float x, ST_Y(ST_ENDPOINT(geom))::float y 
			 FROM edges WHERE objectid=%s AND cost = end_cost AND cost BETWEEN 0 AND %s
		) v',objectid_input, i, objectid_input, i
		);
	  	INSERT INTO isos 
	  	SELECT userid_input,counter,i/60, 
	  	ST_SETSRID(pgr_pointsaspolygon (sql_vertices,shape_precision),4326);      
	END IF;
	END LOOP;  
  	DROP TABLE IF EXISTS extrapolated_vertices;
  	RETURN query SELECT * FROM isos;
  
END;
$function$
--SELECT * FROM isochrones_alphashape(111,20,11.7248,48.3386,3,15,0.00003,1,1,1,'cycling_wheelchair')
