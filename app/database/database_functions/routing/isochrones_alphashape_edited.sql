DROP FUNCTION IF EXISTS isochrones_alphashape_edited;
CREATE OR REPLACE FUNCTION public.isochrones_alphashape_edited(userid_input integer, minutes integer, x numeric, y numeric, n integer, speed numeric, shape_precision numeric, modus integer, objectid_input integer, parent_id_input integer, routing_profile text)
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

  IF modus <> 1 THEN
    execute format('CREATE TEMP TABLE temp_edges as SELECT *,'||objectid_input||' FROM pgrouting_edges_input('||minutes||','||x||','||y||','||speed||','||userid_input||','||objectid_input||','||modus||')');
  ELSE 
    execute format('SELECT *,'||objectid_input||' FROM pgrouting_edges_edited('||minutes||','||x||','||y||','||speed||','||userid_input||','||objectid_input||','||modus||','''||routing_profile||''')');
  END IF;
  

  INSERT INTO edges(edge,node,cost,class_id,objectid,geom) 
  SELECT id AS edge,node,cost,class_id,objectid_input,geom  
  FROM show_network(round(minutes*60,0),modus,userid_input);
  DROP TABLE IF EXISTS temp_edges;
--The speed input, time input AND step input are used to draw isochrones with the corresponding intervals
  LOOP
  exit WHEN counter =n;
  counter :=counter +1;
  upper_limit :=(minutes*60/n)*counter; 
  under_limit :=(minutes*60/n)*counter - (minutes * 60/n);
  --A concave hull is created (isochrones) the concavity can be set 
  DELETE FROM temp_step_vertices;
  INSERT INTO temp_step_vertices 
  SELECT * FROM   
  (
      SELECT st_startpoint(geom) geom
      FROM edges
      WHERE cost between 0 AND upper_limit
      AND objectid = objectid_input
      UNION ALL 
      SELECT st_endpoint(geom)
      FROM edges
      WHERE cost between 0 AND upper_limit
      AND objectid = objectid_input
  ) x;
  IF (SELECT count(*) FROM temp_step_vertices LIMIT 4) > 3 THEN
  	  INSERT INTO isos 
	  SELECT userid_input,counter,(upper_limit/60)::numeric, 
	  ST_SETSRID(pgr_pointsaspolygon ('SELECT (row_number() over())::integer as id, ST_X(geom)::float x, ST_Y(geom)::float y 
	  FROM temp_step_vertices',shape_precision),4326);      

  END IF;
  DELETE FROM temp_step_vertices;
  END LOOP;  
  RETURN query SELECT * FROM isos;
  
END;
$function$
--SELECT * FROM isochrones_alphashape_edited(111,7,11.543274,48.195524,2,5,0.00003,1,44435,1,'wheelchair')