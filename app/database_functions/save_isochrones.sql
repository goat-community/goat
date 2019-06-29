CREATE OR REPLACE FUNCTION public.save_isochrones(userid_input integer, minutes integer, x numeric, y numeric, n integer, speed_input numeric, concavity numeric, modus integer, objectid_input integer, parent_id_input integer)
 RETURNS SETOF type_isochrone_thematic
 LANGUAGE plpgsql
AS $function$

begin
  --The function creating isochrones is executed AND the result is saved INTO the table isochrones
  insert INTO isochrones(userid,id,step,geom,speed,concavity,modus,objectid,parent_id) 
  SELECT *,speed_input,concavity,modus,objectid_input,parent_id_input
  FROM isochrones(userid_input,minutes,x,y,n,speed_input,concavity,modus,objectid_input,parent_id_input);
  perform thematic_data_sum(objectid_input);
  --The function, which finds all the pois in range of the created isochrones are saved INTO separated tables
 -- perform pois_data(objectid_input);
  --The Isochrones is SELECT with its corresponding thematic data (This query is the final output of the function!)	
  return query SELECT distinct i.gid,i.objectid,i.id,i.step,i.geom,i.sum_pois::text FROM isochrones i
  WHERE i.objectid = 99999999999;
END ;
$function$
