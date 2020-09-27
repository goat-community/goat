DROP FUNCTION IF EXISTS isochrones_api;
CREATE OR REPLACE FUNCTION public.isochrones_api(userid_input integer, scenario_id_input integer, minutes integer, x numeric, y numeric, n integer, speed_input numeric, shape_precision numeric, modus_input text, routing_profile text, d integer DEFAULT 9999, h integer DEFAULT 9999, m integer DEFAULT 9999)
 RETURNS SETOF type_isochrones_api
 LANGUAGE plpgsql
AS $function$
DECLARE 
modus integer;
objectid_default integer;
objectid_scenario integer;
sql_execution text;
begin
  --The function creating isochrones is executed AND the result is saved INTO the table isochrones
	/*
	modus = 1 (default calculation)
	modus = 2 (scenario calculation)
	modus = 3 (comparison - default)
	modus = 4 (comparison - scenario)
	*/ 

  /*without or with opening hours*/
  IF d = 9999 OR h = 9999 OR m = 9999
    THEN 
      sql_execution = '';
    ELSE 
      sql_execution = 'public.thematic_data_sum_time(input_objectid integer, d integer, h integer, m integer)';
  END IF;


  IF modus_input = 'comparison' THEN 
		
    /*double calculation - default*/
    objectid_default = random_between(1,900000000);	
    INSERT INTO isochrones(userid,scenario_id,id,step,geom,speed,concavity,modus,objectid,parent_id) 
    SELECT *,speed_input,shape_precision,3,objectid_default,1
    FROM isochrones_alphashape(userid_input,scenario_id_input,minutes,x,y,n,speed_input,shape_precision,3,objectid_default,1,routing_profile);

    PERFORM thematic_data_sum(objectid_default,scenario_id_input,3);
    PERFORM sql_execution;

    /*double calculation - scenario*/
    objectid_scenario = random_between(1,900000000);	
    INSERT INTO isochrones(userid,scenario_id,id,step,geom,speed,concavity,modus,objectid,parent_id) 
    SELECT *,speed_input,shape_precision,4,objectid_scenario,objectid_default
    FROM isochrones_alphashape(userid_input,scenario_id_input,minutes,x,y,n,speed_input,shape_precision,4,objectid_scenario,objectid_default,routing_profile);

    PERFORM thematic_data_sum(objectid_scenario,scenario_id_input,4);
    PERFORM sql_execution;

  ELSE
    
  	IF modus_input = 'default' THEN 
      modus = 1;
    ELSE 
      modus = 2;
    END IF; 
    /*default or scenario*/
  	objectid_default = random_between(1,900000000);
    INSERT INTO isochrones(userid,scenario_id,id,step,geom,speed,concavity,modus,objectid,parent_id) 
    SELECT *,speed_input,shape_precision,modus,objectid_default,1
    FROM isochrones_alphashape(userid_input,scenario_id_input,minutes,x,y,n,speed_input,shape_precision,modus,objectid_default,1,routing_profile);

    PERFORM thematic_data_sum(objectid_default,scenario_id_input,modus);
    PERFORM sql_execution;
	
  END IF ;
  
  UPDATE isochrones i
  SET starting_point = ST_AsText(s.geom)
  FROM (
      SELECT s.geom 
      FROM starting_point_isochrones s
      WHERE s.objectid IN (objectid_default,objectid_scenario)
      LIMIT 1
  ) s
  WHERE i.starting_point IS NULL;
  
  RETURN query SELECT DISTINCT i.gid,i.objectid,ARRAY[x,y] coordinates,i.step,i.speed,
  i.concavity AS shape_precision,i.modus::integer,i.parent_id,i.sum_pois::jsonb, i.geom, i.starting_point 
  FROM isochrones i
  WHERE i.objectid IN (objectid_default,objectid_scenario);
END ;
$function$
--SELECT * FROM isochrones_api(32431,NULL,15,11.2234,48.1848,3,5,0.00003,'default','walking_standard')
