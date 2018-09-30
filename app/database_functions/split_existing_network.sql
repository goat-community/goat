CREATE OR REPLACE FUNCTION public.split_existing_network()
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
  
BEGIN
   drop table if exists pre_network;
   create table pre_network as 
   select w.id id,class_id,source,target,geom,0 as help 
   from ways_userinput w, user_input_network i
   where st_intersects(w.geom,i.geometry)
   and w.userid is null;
   FOR i IN
      SELECT gid from user_input_network 
   LOOP
	  execute 
	  	'update pre_network set help=1 from user_input_network i where i.gid ='|| i || 
	  	' and st_intersects(pre_network.geom,i.geometry)';
      execute 
      	'insert into pre_network(class_id,geom,help) 
		select w.class_id,(st_dump(ST_CollectionExtract(st_split(w.geom,i.geometry),2))).geom,0
		from pre_network w, user_input_network i
		where i.gid=' || i || ' and st_intersects(w.geom,i.geometry)';
      execute
      	'delete from pre_network where help = 1';
      
		
    END LOOP;
END
$function$
