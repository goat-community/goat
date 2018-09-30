CREATE OR REPLACE FUNCTION public.save_isochrones(userid_input integer, minutes integer, x numeric, y numeric, n integer, speed numeric, concavity numeric, modus integer, objectid_input integer, parent_id_input integer)
 RETURNS SETOF type_isochrone_thematic
 LANGUAGE plpgsql
AS $function$

begin
  --The function creating isochrones is executed and the result is saved into the table isochrones
  insert into isochrones(userid,id,step,geom,speed,concavity,modus,objectid,parent_id) 
  select *,speed,concavity,modus,objectid_input,parent_id_input
  from isochrones(userid_input,minutes,x,y,n,speed,concavity,modus,objectid_input,parent_id_input);
  perform thematic_data_sum(objectid_input);
  --The function, which finds all the pois in range of the created isochrones are saved into separated tables
 -- perform pois_data(objectid_input);
  --The Isochrones is select with its corresponding thematic data (This query is the final output of the function!)	
  return query select distinct i.gid,i.objectid,i.id,i.step,i.geom,i.sum_pois::text from isochrones i
  where i.objectid = 99999999999;
END ;
$function$
