CREATE OR REPLACE FUNCTION public.split_userinput(input_userid integer)
 RETURNS SETOF geometry
 LANGUAGE plpgsql
AS $function$
declare
r geometry;
i integer;
begin
  
  FOR i IN
      select gid from user_input_network where userid = input_userid
   LOOP
  drop table if exists new_test;
  drop table if exists union_test;
  create table union_test as
  select st_union(y.geometry) as geom 
  from user_input_network y 
  where y.gid <> i;
  
  FOR r IN select (st_dump(ST_CollectionExtract(st_split(x.geometry,u.geom),2))).geom
		from union_test u, user_input_network x
		where x.gid = i

  LOOP
  RETURN NEXT r;
  END LOOP;
  end loop;
  drop table if exists new_test;
  drop table if exists union_test;
  RETURN;
  
END ;
$function$
