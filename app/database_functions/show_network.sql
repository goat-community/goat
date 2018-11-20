CREATE OR REPLACE FUNCTION public.show_network(objectid_input integer, modus_input integer, userid_input integer)
 RETURNS TABLE(geom geometry, cost numeric, step integer, objectid integer)
 LANGUAGE plpgsql
AS $function$
DECLARE
--Declares the output as type pg_isochrone

ways_table varchar := 'ways';
additional_input varchar := '';
excluded_class_id text;

begin
  --depending on the modus the default OR the input table is used
  if modus_input = 2 then
  ways_table = 'ways_userinput';
  raise notice 'lkxk';
  additional_input = ' AND userid IS NULL OR userid ='||userid_input;
  
  END IF;
  	
  SELECT variable_array::text
  INTO excluded_class_id 
  FROM variable_container v
  WHERE v.identifier = 'excluded_class_id_walking';

  return query execute 'with nodes as (
	SELECT node,cost FROM edges WHERE objectid = '||objectid_input||'
	),
	way as (
	SELECT * FROM (
	    SELECT w.*,n.cost as calc_cost FROM '||ways_table||' w, nodes n 
		WHERE w.source = n.node
		OR w.target = n.node) x
	WHERE not class_id = any(''' || excluded_class_id || ''') '||additional_input||')
	
    SELECT * FROM (
		SELECT ST_CollectionExtract(st_intersection(w.geom,i.geom),2) as geom,
		w.calc_cost as cost,step, '||objectid_input||'  
		FROM way w, isochrones i
		WHERE objectid = '||objectid_input||'
		AND i.gid = (SELECT max(gid) FROM isochrones WHERE objectid = '||objectid_input||')) x
	WHERE st_length(geom) <> 0 ';
--Workaround St_CollectionExtract AND filter all with length 0
  RETURN;
END ;
$function$
