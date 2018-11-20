CREATE OR REPLACE FUNCTION public.split_existing_network()
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
  
BEGIN
   DROP TABLE IF EXISTS pre_network;
   CREATE TABLE pre_network as 
   SELECT w.id id,class_id,source,target,geom,0 as help 
   FROM ways_userinput w, user_input_network i
   WHERE st_intersects(w.geom,i.geometry)
   AND w.userid IS NULL;
   For i IN
      SELECT gid FROM user_input_network 
   LOOP
	  execute 
	  	'UPDATE pre_network set help=1 FROM user_input_network i WHERE i.gid ='|| i || 
	  	' AND st_intersects(pre_network.geom,i.geometry)';
      execute 
      	'insert INTO pre_network(class_id,geom,help) 
		SELECT w.class_id,(st_dump(ST_CollectionExtract(st_split(w.geom,i.geometry),2))).geom,0
		FROM pre_network w, user_input_network i
		WHERE i.gid=' || i || ' AND st_intersects(w.geom,i.geometry)';
      execute
      	'delete FROM pre_network WHERE help = 1';
      
		
    END LOOP;
END
$function$
