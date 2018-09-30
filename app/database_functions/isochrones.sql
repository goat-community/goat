CREATE OR REPLACE FUNCTION public.isochrones(userid_input integer, minutes integer, x numeric, y numeric, n integer, speed numeric, concavity numeric, modus integer, objectid_input integer, parent_id_input integer)
 RETURNS SETOF type_isochrone
 LANGUAGE plpgsql
AS $function$
DECLARE
--Declares the output as type pg_isochrone
r type_isochrone;
counter integer :=0;
upper_limit integer;
under_limit integer;
edges type_edges[];
pg_function varchar:='pgrouting_edges';
begin
--If the modus is input the routing tables for the network with userinput have to be choosen
-- Order matters first
  IF parent_id_input = 2 THEN
    pg_function = 'pgrouting_edges_input';
  ELSIF modus = 2 and parent_id_input > 2 THEN
    pg_function = 'pgrouting_edges_input_double';
  END IF;
  
  
  
--A table called edges is created for saving the reached network
  execute format('insert into edges select *,'||objectid_input||' from '||pg_function||'('||minutes||','||x||','||y||','||speed||','||userid_input||','||objectid_input||')');

--The speed input, time input and step input are used to draw isochrones with the corresponding intervals
  loop
  exit when counter =n;
  counter :=counter +1;
  upper_limit :=(minutes * speed/n)*counter; 
  under_limit :=(minutes * speed/n)*counter - (minutes * speed/n);
  --A concave hull is created (isochrones) the concavity can be set 	
  FOR r IN select userid_input,counter,(upper_limit/speed)::numeric, ST_concavehull(ST_COLLECT(geom),concavity,false)
  from edges where cost between 0 and upper_limit and objectid = objectid_input
  
  LOOP
  RETURN NEXT r;
  END LOOP;
  end loop;
  
  RETURN;
  
END;
$function$
