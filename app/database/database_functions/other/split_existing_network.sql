DROP FUNCTION IF EXISTS split_existing_network;
CREATE OR REPLACE FUNCTION public.split_existing_network()
 RETURNS SETOF integer
 LANGUAGE plpgsql
AS $function$
DECLARE
   i text;
  
BEGIN
   DROP TABLE IF EXISTS pre_network;
   CREATE TABLE pre_network as 
   SELECT w.id,w.class_id,w.source,w.target,w.geom,0 as help 
   FROM ways_userinput w, drawn_features i
   WHERE st_intersects(w.geom,i.geom)
   AND w.userid IS NULL;
   For i IN
      SELECT id FROM drawn_features 
   LOOP
	  execute 
	  	'UPDATE pre_network set help=1 FROM drawn_features i WHERE i.id ='|| i || 
	  	' AND st_intersects(pre_network.geom,i.geom)';
      execute 
      	'insert INTO pre_network(class_id,geom,help) 
		SELECT w.class_id,(st_dump(ST_CollectionExtract(st_split(w.geom,i.geom),2))).geom,0
		FROM pre_network w, drawn_features i
		WHERE i.id=' || i || ' AND st_intersects(w.geom,i.geom)';
      execute
      	'delete FROM pre_network WHERE help = 1';
    END LOOP;
END
$function$