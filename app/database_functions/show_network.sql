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
  --depending on the modus the default or the input table is used
  if modus_input = 2 then
  ways_table = 'ways_userinput';
  raise notice 'lkxk';
  additional_input = ' and userid is null or userid ='||userid_input;
  
  END IF;
  	
  SELECT variable_array::text
  into excluded_class_id 
  FROM variable_container v
  where v.identifier = 'excluded_class_id_walking';

  return query execute 'with nodes as (
	select node,cost from edges where objectid = '||objectid_input||'
	),
	way as (
	select * from (
	    select w.*,n.cost as calc_cost from '||ways_table||' w, nodes n 
		where w.source = n.node
		or w.target = n.node) x
	where not class_id = any(''' || excluded_class_id || ''') '||additional_input||')
	
    select * from (
		select ST_CollectionExtract(st_intersection(w.geom,i.geom),2) as geom,
		w.calc_cost as cost,step, '||objectid_input||'  
		from way w, isochrones i
		where objectid = '||objectid_input||'
		and i.gid = (select max(gid) from isochrones where objectid = '||objectid_input||')) x
	where st_length(geom) <> 0 ';
--Workaround St_CollectionExtract and filter all with length 0
  RETURN;
END ;
$function$
