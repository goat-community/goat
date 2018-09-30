CREATE OR REPLACE FUNCTION public.isochrones_precalculate(minutes integer, x numeric, y numeric, id integer, speed numeric, concavity numeric, snap_tolerance integer)
 RETURNS TABLE(grid_id integer, time_step integer, geometry geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE

begin


  drop table if exists edges_temp;
  create table edges_temp as
  select * from pgrouting_edges_snaptolerance(minutes,x,y,speed,1,1,snap_tolerance); 

  --insert into edges_precalculate_100
  --select id as grid_id,* from edges_temp; 
  
  return query select id,minutes,ST_concavehull(ST_COLLECT(geom),concavity,false)
  from edges_temp 

  Return ;
  
END;
$function$
