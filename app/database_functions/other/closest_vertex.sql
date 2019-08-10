CREATE OR REPLACE FUNCTION public.closest_vertex(x NUMERIC,y NUMERIC, snap_distance NUMERIC, excluded_classes text)
 RETURNS SETOF text[]
 LANGUAGE plpgsql
AS $function$
DECLARE
point geometry;
geom_vertex geometry;
excluded_class_id text;
id_vertex bigint;
begin

  -- input point
  point:= ST_SetSRID(ST_MakePoint(x,y), 4326);
  
  SELECT variable_array::text
  INTO excluded_class_id 
  FROM variable_container v
  WHERE v.identifier = excluded_classes;
  
  SELECT w.id, w.geom INTO id_vertex, geom_vertex
  FROM ways_vertices_pgr w
  WHERE (class_ids <@ excluded_class_id::int[]) IS false
  ORDER BY geom <-> point
  LIMIT 1;
  IF ST_Distance(geom_vertex,point)>snap_distance THEN
    RETURN;
  END IF;
	
  RETURN query SELECT ARRAY[id_vertex::text, geom_vertex::text];
END ;
$function$;