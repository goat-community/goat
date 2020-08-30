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

	PERFORM pgrouting_edges(cutoffs, ARRAY[[x,y]],speed, userid_input, 1, objectid_input, modus, routing_profile) p;
	
	DROP TABLE IF EXISTS iso_vertices;
	CREATE TEMP TABLE iso_vertices(geom geometry);

	PERFORM plv8_require();
	FOR i IN SELECT unnest(cutoffs)
	LOOP
	counter = counter + 1;
	IF (SELECT count(*) FROM edges WHERE objectid=objectid_input AND cost BETWEEN 0 AND i LIMIT 4) > 3 THEN 
		TRUNCATE iso_vertices;
		INSERT INTO iso_vertices 
		SELECT CASE WHEN start_cost > end_cost THEN st_startpoint(geom) ELSE st_endpoint(geom) END AS geom
		FROM edges
		WHERE COST <= i
		AND objectid = objectid_input; 
		
	  	INSERT INTO isos 
	  	SELECT userid_input, counter, i/60, ST_SETSRID(st_geomfromtext('POLYGON(('||REPLACE(plv8_concaveman(),',4',' 4')||'))'),4326) AS geom;
	  	
	END IF;
	END LOOP;  

  	RETURN query SELECT * FROM isos;
  
END;
$function$
--SELECT * FROM isochrones_alphashape(111,10,11.2493, 48.1804,2,5,0.00003,1,1,1,'walking_standard')
