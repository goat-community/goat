DROP FUNCTION IF EXISTS isochrones_alphashape;
CREATE OR REPLACE FUNCTION public.isochrones_alphashape(userid_input integer, minutes integer, x numeric, y numeric, n integer, speed numeric, shape_precision numeric, modus integer, objectid_input integer, parent_id_input integer, routing_profile text)
 RETURNS SETOF type_isochrone
 LANGUAGE plpgsql
AS $function$
DECLARE
--Declares the output as type type_isochrone
r type_isochrone;
counter integer :=0;
upper_limit integer;
under_limit integer;
edges type_edges[];
max_length_links integer;
begin
--If the modus is input the routing tables for the network with userinput have to be choosen
  speed = speed/3.6;
  DROP TABLE IF EXISTS temp_edges;
  DROP TABLE IF EXISTS isos;
  CREATE temp TABLE isos OF type_isochrone;

--It can not drop the temp_step_vertices table in case of double calculation.
  IF modus <> 4 THEN 
    DROP TABLE IF EXISTS temp_step_vertices;
    CREATE temp TABLE temp_step_vertices (geom geometry);
  ELSE 
    DELETE FROM temp_step_vertices;
  END IF;

  EXECUTE format('CREATE TEMP TABLE extrapolated_vertices AS SELECT * FROM pgrouting_edges('||minutes||','||x||','||y||','||speed||','||userid_input||','||objectid_input||','||modus||','''||routing_profile||''')');

  /*Replacement for show_network goes in here*/
--The speed input, time input AND step input are used to draw isochrones with the corresponding intervals
  LOOP
  exit WHEN counter =n;
  counter :=counter +1;
  upper_limit :=(minutes*60/n)*counter; 
  under_limit :=(minutes*60/n)*counter - (minutes * 60/n);
  --A concave hull is created (isochrones) the concavity can be set 
  DELETE FROM temp_step_vertices;
  INSERT INTO temp_step_vertices 
  SELECT geom  
  FROM extrapolated_vertices 
  WHERE cost BETWEEN 0 AND upper_limit;
 
  IF (SELECT count(*) FROM temp_step_vertices LIMIT 4) > 3 THEN
  	INSERT INTO isos 
	  SELECT userid_input,counter,(upper_limit/60)::numeric, 
	  ST_SETSRID(pgr_pointsaspolygon ('SELECT (row_number() over())::integer as id, ST_X(geom)::float x, ST_Y(geom)::float y 
	  FROM temp_step_vertices',shape_precision),4326);      

  END IF;
  END LOOP;  
  DROP TABLE IF EXISTS extrapolated_vertices;
  RETURN query SELECT * FROM isos;
  
END;
$function$
--SELECT * FROM isochrones_api(111,7,11.543274,48.195524,2,5,0.00003,'default','wheelchair')