DROP FUNCTION IF EXISTS multi_isochrones_api;
CREATE OR REPLACE FUNCTION public.multi_isochrones_api(userid_input integer, scenario_id_input integer, minutes integer, speed_input numeric, 
	n integer, routing_profile_input text, alphashape_parameter_input NUMERIC, modus_input text,region_type text, region text[], amenities text[])

RETURNS SETOF type_pois_multi_isochrones
AS $function$
DECLARE
modus integer;
iso_parent_id integer;
iso_gid integer;
BEGIN
  --The function creating isochrones is executed AND the result is saved INTO the table isochrones
	/*
	modus = 1 (default calculation)
	modus = 2 (scenario calculation)
	modus = 3 (comparison - default)
	modus = 4 (comparison - scenario)
	*/
    IF modus_input = 'comparison' THEN 
		
    /*double calculation*/

        /*default*/
        CREATE TEMP TABLE IF NOT EXISTS x OF type_pois_multi_isochrones;
        TRUNCATE x;
        INSERT INTO x 
        SELECT * FROM pois_multi_isochrones(userid_input,scenario_id_input,minutes,speed_input,n,routing_profile_input,alphashape_parameter_input,3,region_type,region,amenities);
       
        SELECT objectid INTO iso_parent_id FROM x;   
        /*scenario*/
        INSERT INTO x 
        SELECT * FROM pois_multi_isochrones(userid_input,scenario_id_input,minutes,speed_input,n,routing_profile_input,alphashape_parameter_input,4,region_type,region,amenities);
       
        SELECT gid INTO iso_gid FROM x WHERE x.modus = 4;    
        UPDATE x SET parent_id = iso_parent_id WHERE x.modus = 4;
                
        UPDATE multi_isochrones m
        SET parent_id = iso_parent_id
        WHERE m.gid = iso_gid; 

        Return query select * from x;
    ELSE
    
        IF modus_input = 'default' THEN 
        modus = 1;
        ELSE 
        modus = 2;
        END IF; 
        /*default or scenario*/
        RETURN query 
        SELECT * FROM pois_multi_isochrones(userid_input,scenario_id_input,minutes,speed_input,n,routing_profile_input,alphashape_parameter_input,modus,region_type,region,amenities);
	
  END IF;

END;
$function$ LANGUAGE plpgsql;

/*
SELECT *
FROM multi_isochrones_api(1,NULL,15,5.0,3,'walking_wheelchair',0.00003,'scenario','study_area',ARRAY['16.3','16.4'],ARRAY['supermarket','bar']) ;
*/