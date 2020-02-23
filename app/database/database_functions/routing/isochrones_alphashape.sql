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
begin
--If the modus is input the routing tables for the network with userinput have to be choosen
  speed = speed/3.6;

  DROP TABLE IF EXISTS isos;
  CREATE temp TABLE isos OF type_isochrone;

--It can not drop the temp_step_vertices table in case of double calculation.

  PERFORM pgrouting_edges(minutes,x,y,speed,n,userid_input,objectid_input,modus,routing_profile);

  FOR i IN SELECT generate_series(step_isochrone,(minutes*60),step_isochrone)
	LOOP
    counter = counter + 1;
    IF (SELECT count(*) FROM edges WHERE objectid=objectid_input AND cost BETWEEN 0 AND i LIMIT 4) > 3 THEN 
      INSERT INTO isos 
      SELECT userid_input,counter,i/60, 
      ST_SETSRID(pgr_pointsaspolygon ('SELECT (row_number() over())::integer as id, ST_X(v_geom)::float x, ST_Y(v_geom)::float y 
      FROM edges WHERE objectid='||objectid_input||'AND cost BETWEEN 0 AND '||i,shape_precision),4326);      
    END IF;
    
  END LOOP;  
  DROP TABLE IF EXISTS extrapolated_vertices;
  RETURN query SELECT * FROM isos;
  
END;
$function$
--SELECT * FROM isochrones_alphashape(111,7,11.543274,48.195524,2,5,0.00003,1,1,1,'walking_wheelchair')