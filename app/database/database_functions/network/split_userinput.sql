DROP FUNCTION IF EXISTS split_userinput;
CREATE OR REPLACE FUNCTION public.split_userinput()
 RETURNS SETOF geometry
 LANGUAGE plpgsql
AS $function$
declare
r geometry;
i integer;
begin
  
  For i IN
      SELECT id FROM drawn_features 
   LOOP

  DROP TABLE IF EXISTS union_test;
  CREATE TEMP TABLE union_test as
  SELECT st_union(y.geom) as geom 
  FROM drawn_features y 
  WHERE y.id <> i;
  
  For r IN SELECT (st_dump(ST_CollectionExtract(st_split(x.geom,u.geom),2))).geom
		FROM union_test u, drawn_features x
		WHERE x.id = i

  LOOP
  RETURN NEXT r;
  END LOOP;
  end loop;

  DROP TABLE IF EXISTS union_test;
  RETURN;
  
END ;
$function$