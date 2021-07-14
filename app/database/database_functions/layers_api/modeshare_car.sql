CREATE OR REPLACE FUNCTION modeshare_car()
RETURNS TABLE (vi_nummer TEXT, share integer, score integer, geom geometry) AS
$$
select name, cast((share_mivd+share_mivp)*100 as integer) as share, 
case when (share_mivd+share_mivp) < 0.21 then 1
when (share_mivd+share_mivp) > 0.20 and (share_mivd+share_mivp) < 0.31 then 2
when (share_mivd+share_mivp) > 0.30 and (share_mivd+share_mivp) < 0.41 then 3
when (share_mivd+share_mivp) > 0.40 then 4
end as score, geom
from modeshare;
$$
LANGUAGE sql;

COMMENT ON FUNCTION modeshare_car() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';