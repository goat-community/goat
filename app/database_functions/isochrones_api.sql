CREATE TYPE type_isochrones_api AS
(
	gid integer, 
	objectid integer, 
	coordinates NUMERIC[],
	step integer,
	speed NUMERIC,
	concavity NUMERIC,
	modus integer,
	parent_id integer,
	sum_pois jsonb, 
	geom geometry
);


CREATE OR REPLACE FUNCTION public.isochrones_api(userid_input integer, minutes integer, x numeric, y numeric, n integer, speed_input numeric, concavity numeric, modus integer, objectid_input integer, parent_id_input integer)
 RETURNS SETOF type_isochrones_api
 LANGUAGE plpgsql
AS $function$

begin
  --The function creating isochrones is executed AND the result is saved INTO the table isochrones
  INSERT INTO isochrones(userid,id,step,geom,speed,concavity,modus,objectid,parent_id) 
  SELECT *,speed_input,concavity,modus,objectid_input,parent_id_input
  FROM isochrones(userid_input,minutes,x,y,n,speed_input,concavity,modus,objectid_input,parent_id_input);
  perform thematic_data_sum(objectid_input);
  --The function, which finds all the pois in range of the created isochrones are saved INTO separated tables
 -- perform pois_data(objectid_input);
  --The Isochrones is SELECT with its corresponding thematic data (This query is the final output of the function!)	
  RETURN query SELECT distinct i.gid,i.objectid,ARRAY[x,y] coordinates,i.step,i.speed,i.concavity,i.modus::integer,i.parent_id,i.sum_pois::jsonb, i.geom 
  FROM isochrones i
  WHERE i.objectid = objectid_input;
END ;
$function$


--SELECT * FROM isochrones_api(32431,15,11.575260,48.148124,3,83.33,0.99,1,12345,1)

