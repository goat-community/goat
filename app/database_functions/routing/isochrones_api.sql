
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
	geom geometry,
  starting_point text
);

CREATE OR REPLACE FUNCTION public.isochrones_api(userid_input integer, minutes integer, x numeric, y numeric, n integer, speed_input numeric, concavity numeric, modus_input text)
 RETURNS SETOF type_isochrones_api
 LANGUAGE plpgsql
AS $function$
DECLARE 
modus integer;
objectid_default integer;
objectid_scenario integer;
begin
  --The function creating isochrones is executed AND the result is saved INTO the table isochrones
	/*
	modus = 1 (default calculation)
	modus = 2 (input calculation)
	modus = 3 (comparison - default)
	modus = 4 (comparison - input)
	*/ 

  IF modus_input = 'comparison' THEN 
		
    /*double calculation - default*/
    objectid_default = random_between(1,900000000);	
    INSERT INTO isochrones(userid,id,step,geom,speed,concavity,modus,objectid,parent_id) 
    SELECT *,speed_input,concavity,3,objectid_default,1
    FROM isochrones(userid_input,minutes,x,y,n,speed_input,concavity,3,objectid_default,1);
    PERFORM thematic_data_sum(objectid_default);
    /*double calculation - scenario*/
    objectid_scenario = random_between(1,900000000);	
    INSERT INTO isochrones(userid,id,step,geom,speed,concavity,modus,objectid,parent_id) 
    SELECT *,speed_input,concavity,4,objectid_scenario,objectid_default
    FROM isochrones(userid_input,minutes,x,y,n,speed_input,concavity,4,objectid_scenario,objectid_default);
    PERFORM thematic_data_sum(objectid_scenario);

  ELSE
    
  	IF modus_input = 'default' THEN 
      modus = 1;
    ELSE 
      modus = 2;
    END IF; 
    /*default or scenario*/
  	objectid_default = random_between(1,900000000);
    INSERT INTO isochrones(userid,id,step,geom,speed,concavity,modus,objectid,parent_id) 
    SELECT *,speed_input,concavity,modus,objectid_default,1
    FROM isochrones(userid_input,minutes,x,y,n,speed_input,concavity,modus,objectid_default,1);
    PERFORM thematic_data_sum(objectid_default);
	
  END IF ;
  
  UPDATE isochrones i
  SET starting_point = ST_AsText(s.geom)
  FROM starting_point_isochrones s
  WHERE i.objectid = s.objectid 
  AND starting_point IS null;
  
  RETURN query SELECT distinct i.gid,i.objectid,ARRAY[x,y] coordinates,i.step,i.speed,
  i.concavity,i.modus::integer,i.parent_id,i.sum_pois::jsonb, i.geom, i.starting_point 
  FROM isochrones i
  WHERE i.objectid IN (objectid_default,objectid_scenario);
END ;
$function$




--SELECT * FROM isochrones_api(32431,15,11.575260,48.148124,3,83.33,0.99,'default')
--Options for modus: default,scenario,comparison



