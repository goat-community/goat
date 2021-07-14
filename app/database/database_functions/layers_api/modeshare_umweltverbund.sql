CREATE OR REPLACE FUNCTION modeshare_umweltverbund()
RETURNS TABLE (vi_nummer TEXT, share integer, score integer, geom geometry) AS
$$
select name, cast((share_foot+share_bike+share_put)*100 as integer) as share, 
case when (share_foot+share_bike+share_put) < 0.60 then 1
when (share_foot+share_bike+share_put) > 0.59 and (share_foot+share_bike+share_put) < 0.70 then 2
when (share_foot+share_bike+share_put) > 0.69 and (share_foot+share_bike+share_put) < 0.80 then 3
when (share_foot+share_bike+share_put) > 0.79 then 4
end as score, geom
from modeshare;
$$
LANGUAGE sql;

COMMENT ON FUNCTION modeshare_umweltverbund() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';