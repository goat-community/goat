CREATE OR REPLACE FUNCTION public.isochrones_precalculate(minutes integer, x numeric, y numeric, id integer, speed numeric, concavity numeric, snap_tolerance integer)
 RETURNS TABLE(grid_id integer, time_step integer, geometry geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE

begin


  DROP TABLE IF EXISTS edges_temp;
  CREATE TABLE edges_temp as
  SELECT * FROM pgrouting_edges_snaptolerance(minutes,x,y,speed,1,1,snap_tolerance); 

  --insert INTO edges_precalculate_100
  --SELECT id as grid_id,* FROM edges_temp; 
  
  return query SELECT id,minutes,ST_CollectionExtract(ST_concavehull(ST_COLLECT(geom),concavity,false),3)
  FROM edges_temp 

  Return ;
  
END;
$function$
