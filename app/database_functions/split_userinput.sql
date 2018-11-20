CREATE OR REPLACE FUNCTION public.split_userinput(input_userid integer)
 RETURNS SETOF geometry
 LANGUAGE plpgsql
AS $function$
declare
r geometry;
i integer;
begin
  
  For i IN
      SELECT gid FROM user_input_network WHERE userid = input_userid
   LOOP
  DROP TABLE IF EXISTS new_test;
  DROP TABLE IF EXISTS union_test;
  CREATE TABLE union_test as
  SELECT st_union(y.geometry) as geom 
  FROM user_input_network y 
  WHERE y.gid <> i;
  
  For r IN SELECT (st_dump(ST_CollectionExtract(st_split(x.geometry,u.geom),2))).geom
		FROM union_test u, user_input_network x
		WHERE x.gid = i

  LOOP
  RETURN NEXT r;
  END LOOP;
  end loop;
  DROP TABLE IF EXISTS new_test;
  DROP TABLE IF EXISTS union_test;
  RETURN;
  
END ;
$function$
