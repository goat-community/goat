CREATE OR REPLACE FUNCTION public.isochrones(userid_input integer, minutes integer, x numeric, y numeric, n integer, speed numeric, concavity numeric, modus integer, objectid_input integer, parent_id_input integer)
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
begin
--If the modus is input the routing tables for the network with userinput have to be choosen
  DROP TABLE IF EXISTS temp_edges;
  IF modus <> 1 THEN
    execute format('CREATE TEMP TABLE temp_edges as SELECT *,'||objectid_input||' FROM pgrouting_edges_input('||minutes||','||x||','||y||','||speed||','||userid_input||','||objectid_input||','||modus||')');
  ELSE 
    execute format('CREATE TEMP TABLE temp_edges as SELECT *,'||objectid_input||' FROM pgrouting_edges('||minutes||','||x||','||y||','||speed||','||userid_input||','||objectid_input||')');
  END IF;
  
  INSERT INTO edges(edge,node,cost,class_id,objectid,geom) 
  SELECT id AS edge,node,cost,class_id,objectid_input,geom  
  FROM show_network(round(minutes*speed,0),modus,userid_input);
  DROP TABLE IF EXISTS temp_edges;
--The speed input, time input AND step input are used to draw isochrones with the corresponding intervals
  loop
  exit when counter =n;
  counter :=counter +1;
  upper_limit :=(minutes * speed/n)*counter; 
  under_limit :=(minutes * speed/n)*counter - (minutes * speed/n);
  --A concave hull is created (isochrones) the concavity can be set 	
  For r IN SELECT userid_input,counter,(upper_limit/speed)::numeric, ST_CollectionExtract(ST_ConcaveHull(ST_Collect(geom),concavity,false),3)
          FROM 
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
          ) x
  LOOP
  RETURN NEXT r;
  END LOOP;
  end loop;
  
  RETURN;
  
END;
$function$


